"""Paper-trading engine: Scanner -> Rug check -> Sizer -> Executor -> Logger -> Equity.
Haqiqiy pul ishlatilmaydi. LIVE rejim ataylab yozilmagan."""
import asyncio
import json
import os
import time
from collections import deque
from pathlib import Path


def env(k, d):
    v = os.getenv(k)
    return float(v) if v not in (None, "") else d


class Cfg:
    start_balance = env("START_BALANCE", 133.70)
    size_pct = env("SIZE_PCT", 10.0)        # har bir bitimga equity'ning % i
    slip_cap = env("SLIP_CAP", 2.0)         # taxminiy slippage limiti, %
    stop = env("STOP_LOSS", 6.0)            # %
    tp = env("TAKE_PROFIT", 9.0)            # %
    max_hold = env("MAX_HOLD_MIN", 30.0) * 60
    fee_rt = env("FEE_ROUNDTRIP", 0.4)      # kirish+chiqish komissiyasi, %
    min_liq = env("MIN_LIQ_USD", 8000.0)
    min_volx = env("MIN_VOLX", 2.5)         # 5 daqiqalik hajm / soatlik o'rtacha
    min_buy = env("MIN_BUY_PCT", 55.0)
    max_age = env("MAX_AGE_MIN", 60.0)
    max_rug_score = env("MAX_RUG_SCORE", 50.0)   # RugCheck 0-100, yuqori = xavfli
    min_lp_locked = env("MIN_LP_LOCKED", 80.0)   # %, faqat ma'lumot kelsa tekshiriladi
    scan_every = env("SCAN_EVERY", 20.0)
    mon_every = env("MONITOR_EVERY", 5.0)
    data_dir = Path(os.getenv("DATA_DIR", "data"))


class Engine:
    def __init__(self, feed, cfg=Cfg, notify=None):
        self.feed, self.c, self.notify = feed, cfg, notify
        cfg.data_dir.mkdir(parents=True, exist_ok=True)
        self.sf = cfg.data_dir / "state.json"
        self.lf = cfg.data_dir / "night.log.jsonl"
        self.paused = False
        self._init()
        self._load()

    def _init(self):
        self.recent = deque(maxlen=4)
        self.logs = deque(maxlen=200)
        self.pos = None
        self.act, self.last_rug = "scan", "—"
        self.bal = self.c.start_balance
        self.tr = self.w = self.l = self.filt = self.skip = self.n = 0
        self.eq = [self.bal]

    # ---------- saqlash ----------
    def _load(self):
        if self.sf.exists():
            d = json.loads(self.sf.read_text())
            for k in ("bal", "tr", "w", "l", "filt", "skip", "n", "eq"):
                setattr(self, k, d[k])
        if self.lf.exists():
            for line in self.lf.read_text().splitlines()[-40:]:
                self.logs.appendleft(json.loads(line))

    def _save(self):
        d = {k: getattr(self, k) for k in ("bal", "tr", "w", "l", "filt", "skip", "n", "eq")}
        d["eq"] = d["eq"][-500:]
        self.sf.write_text(json.dumps(d))

    def reset(self):
        self._init()
        self.lf.write_text("")
        self._save()

    # ---------- logger ----------
    def log(self, tag, sym, reason, res):
        self.n += 1
        e = dict(time=time.strftime("%H:%M:%S"), tag=tag, sym=sym, reason=reason, res=res)
        self.logs.appendleft(e)
        with self.lf.open("a") as f:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
        self._save()

    async def _tell(self, text):
        if self.notify:
            try:
                await self.notify(text)
            except Exception:
                pass

    # ---------- asosiy sikllar ----------
    async def run(self):
        await asyncio.gather(self._scan_loop(), self._mon_loop())

    async def _scan_loop(self):
        while True:
            if not self.paused and not self.pos:
                try:
                    await self.scan_once()
                except Exception as e:
                    self.log("ERROR", "engine", f"{type(e).__name__}: {e}"[:140], "retry")
            await asyncio.sleep(self.c.scan_every)

    async def scan_once(self):
        c = self.c
        self.act = "scan"
        for t in await self.feed.candidates():
            # Scanner: faqat belgilaydi, savdo qilmaydi
            if not (t["liq"] >= c.min_liq and t["volx"] >= c.min_volx
                    and t["buy_pct"] >= c.min_buy and t["age_min"] <= c.max_age):
                continue
            chip = dict(sym=t["sym"], vol=f"{t['volx']:.1f}", lp=0, state="ok")
            self.recent.appendleft(chip)
            # Rug check: o'tmasa bitim yo'q (xato bo'lsa ham o'tkazmaymiz)
            self.act = "rug"
            try:
                ok, why, lp = await self.feed.rug(t["mint"], c)
            except Exception as e:
                ok, why, lp = False, f"rugcheck mavjud emas ({type(e).__name__})", 0
            chip["lp"] = lp
            if not ok:
                chip["state"] = "no"
                self.filt += 1
                self.last_rug = f"filtrlandi {t['sym']}"
                self.log("FILTERED", t["sym"], why, "not traded")
                continue
            self.last_rug = f"o‘tdi {t['sym']}"
            # Sizer: balansdan hajm; slippage taxmini (constant-product)
            size = self.bal * c.size_pct / 100
            slip = 0.3 + size / (t["liq"] / 2) * 100
            self.act = "exec"
            if slip > c.slip_cap:
                chip["state"] = "no"
                self.skip += 1
                self.log("SKIP", t["sym"], f"est. slip {slip:.1f}% > {c.slip_cap:.1f}% cap", "no order")
                continue
            # Executor (paper)
            why = f"new pair {t['age_min']:.0f}m old · buys {t['buy_pct']:.0f}% of flow"
            self.pos = dict(sym=t["sym"], mint=t["mint"], pair=t["pair"], size=size, slip=slip,
                            entry=t["price"] * (1 + slip / 100), last=t["price"], pnl=0.0,
                            t0=time.time(), fails=0, why=why)
            self.log("ENTER", t["sym"], why, f"size {c.size_pct:.0f}%")
            await self._tell(f"ENTER {t['sym']} · ${size:.2f} · {why}")
            return

    async def _mon_loop(self):
        c = self.c
        while True:
            await asyncio.sleep(c.mon_every)
            p = self.pos
            if not p:
                continue
            try:
                price = await self.feed.price(p["pair"], p["mint"])
            except Exception:
                price = None
            if price:
                p["last"], p["fails"] = price, 0
            else:
                p["fails"] += 1
            p["pnl"] = (p["last"] / p["entry"] - 1) * 100 - c.fee_rt
            why = None
            if p["pnl"] <= -c.stop:
                why = f"stop-loss −{c.stop:g}%"
            elif p["pnl"] >= c.tp:
                why = f"take-profit +{c.tp:g}%"
            elif time.time() - p["t0"] >= c.max_hold:
                why = "time exit · momentum faded"
            elif p["fails"] >= 5:
                why = "price feed lost"
            if why:
                await self._close(why)

    async def _close(self, why):
        p, self.pos = self.pos, None
        usd = p["size"] * p["pnl"] / 100
        self.bal = max(0.0, self.bal + usd)
        self.tr += 1
        if usd > 0:
            self.w += 1
        else:
            self.l += 1
        self.eq.append(self.bal)
        self.act = "log"
        sgn = "+" if usd >= 0 else "−"
        self.log("EXIT", p["sym"], f"{why} · {p['pnl']:+.1f}%", f"{sgn}${abs(usd):.2f}")
        await self._tell(f"EXIT {p['sym']} · {why} · {p['pnl']:+.1f}% · balans ${self.bal:.2f}")

    # ---------- dashboard uchun holat ----------
    def state(self):
        p = self.pos
        pos = p and {k: p[k] for k in ("sym", "entry", "size", "slip", "pnl", "why")}
        return dict(bal=round(self.bal, 2), tr=self.tr, w=self.w, l=self.l, pos=pos,
                    logs=list(self.logs)[:40], filt=self.filt, skip=self.skip, eq=self.eq[-200:],
                    recent=list(self.recent), n=self.n, act=self.act, done=False,
                    lastRug=self.last_rug, clock=time.strftime("%H:%M:%S"), paused=self.paused,
                    sp=self.c.size_pct, cap=self.c.slip_cap, start=self.c.start_balance)
