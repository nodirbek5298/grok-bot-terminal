"""Ma'lumot manbalari. DexFeed: DexScreener + RugCheck (kalitsiz, ommaviy API).
DemoFeed: internetsiz sinov uchun tasodifiy ma'lumot."""
import asyncio
import random
import time
import uuid

DEX = "https://api.dexscreener.com"
RUG = "https://api.rugcheck.xyz"


class DexFeed:
    def __init__(self):
        import httpx
        self.http = httpx.AsyncClient(timeout=10, headers={"User-Agent": "grok-bot-terminal/1.0"})
        self.done = set()

    async def _get(self, url):
        r = await self.http.get(url)
        r.raise_for_status()
        return r.json()

    async def candidates(self):
        prof = await self._get(f"{DEX}/token-profiles/latest/v1")
        out = []
        for t in prof[:30]:
            mint = t.get("tokenAddress")
            if t.get("chainId") != "solana" or not mint or mint in self.done:
                continue
            self.done.add(mint)
            if len(self.done) > 5000:
                self.done.clear()
            d = await self._get(f"{DEX}/latest/dex/tokens/{mint}")
            pairs = [p for p in d.get("pairs") or [] if p.get("chainId") == "solana"]
            if not pairs:
                continue
            p = max(pairs, key=lambda x: (x.get("liquidity") or {}).get("usd") or 0)
            price = float(p.get("priceUsd") or 0)
            created = p.get("pairCreatedAt")
            if price <= 0 or not created:
                continue
            v = p.get("volume") or {}
            m5, h1 = v.get("m5") or 0, v.get("h1") or 0
            volx = min(99.0, m5 / (h1 / 12)) if h1 > 0 else (99.0 if m5 > 0 else 0.0)
            tx = (p.get("txns") or {}).get("m5") or {}
            b, s = tx.get("buys", 0), tx.get("sells", 0)
            out.append(dict(
                sym="$" + (p.get("baseToken") or {}).get("symbol", "?")[:8].upper(),
                mint=mint, pair=p["pairAddress"], price=price,
                liq=(p.get("liquidity") or {}).get("usd") or 0,
                age_min=(time.time() * 1000 - created) / 60000,
                volx=volx, buy_pct=100 * b / (b + s) if b + s else 0.0))
            await asyncio.sleep(0.3)   # limitlarni hurmat qilamiz
        return out

    async def rug(self, mint, cfg):
        d = await self._get(f"{RUG}/v1/tokens/{mint}/report/summary")
        lp = d.get("lpLockedPct")
        lp_i = int(lp) if lp is not None else 0
        danger = [x for x in d.get("risks") or [] if x.get("level") == "danger"]
        if danger:
            return False, danger[0].get("name", "danger risk"), lp_i
        score = d.get("score_normalised")
        if score is not None and score > cfg.max_rug_score:
            return False, f"rug score {score:g} > {cfg.max_rug_score:g}", lp_i
        if lp is not None and lp < cfg.min_lp_locked:
            return False, f"LP locked {lp_i}% < {cfg.min_lp_locked:g}%", lp_i
        return True, "", lp_i

    async def price(self, pair, mint):
        d = await self._get(f"{DEX}/latest/dex/pairs/solana/{pair}")
        p = (d.get("pairs") or [d.get("pair")])[0]
        return float(p["priceUsd"])


class DemoFeed:
    SYL = ["zo", "rbi", "lu", "mo", "waf", "fl", "do", "zy", "chi", "fro", "tof", "uu", "kek", "nib"]

    def __init__(self):
        self.px = {}

    async def candidates(self):
        out = []
        for _ in range(random.randint(1, 3)):
            sym = "$" + "".join(random.choices(self.SYL, k=3)).upper()[:6]
            mint = "demo" + uuid.uuid4().hex[:8]
            price = random.uniform(1e-5, 1e-3)
            self.px[mint] = price
            out.append(dict(sym=sym, mint=mint, pair=mint, price=price,
                            liq=random.uniform(6e3, 60e3), age_min=random.uniform(1, 40),
                            volx=random.uniform(1, 7), buy_pct=random.uniform(40, 85)))
        return out

    async def rug(self, mint, cfg):
        x = random.random()
        if x < .12:
            return False, "honeypot: sell sim failed", 0
        if x < .28:
            return False, "Top 10 holders high ownership", random.randint(0, 50)
        return True, "", random.randint(85, 100)

    async def price(self, pair, mint):
        self.px[pair] *= 1 + random.gauss(0.002, 0.03)
        return self.px[pair]
