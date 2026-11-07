# Grok Bot Terminal (paper rejim)

Yangi Solana tokenlarini qidiradi, firibgarlik belgilarini tekshiradi va **soxta pul bilan** savdo qiladi.
Scanner → Rug Check → Sizer → Executor → Logger → Equity. Haqiqiy bitim ochish kodi ataylab yozilmagan.

Ma’lumot: DexScreener (narx/hajm) + RugCheck (xavf bayroqlari), ikkalasi ham kalitsiz.

## GitHub nima qiladi va nima qilmaydi
- GitHub kodni **saqlaydi** va **GitHub Pages** orqali `docs/index.html` ni ko‘rsatadi.
- Pages faqat statik sahifa: u yerda dashboard **DEMO rejimda** (tasodifiy ma’lumot, server yo‘q) ishlaydi.
- Haqiqiy bot (Python server) GitHub’da **ishlamaydi**. Uni o‘z kompyuteringizda yoki hosting’da (VPS, Railway, Fly.io, Render) ishga tushirasiz.
  Bepul tarifdagi hostinglar ko‘pincha “uxlab qoladi”, bot esa 24/7 ishlashi kerak, shuning uchun arzon VPS ishonchliroq.

## GitHub Pages’ni yoqish (demo)
Repo → Settings → Pages → Branch: `main`, papka: `/docs` → Save.
Manzil: `https://<username>.github.io/<repo>/`
(Bepul akkauntda Pages faqat **public** repo uchun ishlaydi. Kod ichida maxfiy narsa yo‘q: `.env` repoga kirmaydi.)

## Lokal ishga tushirish
    python3 -m venv .venv && source .venv/bin/activate     # Python 3.10+
    pip install -r requirements.txt
    cp .env.example .env        # sinash uchun DEMO=1, OWNER_ID bo'sh
    uvicorn server:app --port 8000
Brauzerda http://localhost:8000

## Hostingda (Docker)
    docker build -t grok-bot-terminal .
    docker run -p 8000:8000 --env-file .env -v $(pwd)/data:/app/data grok-bot-terminal
`data/` papkasi balans va jurnalni saqlaydi.

## Telegram Mini App
1. @BotFather → /newbot → `BOT_TOKEN`.
2. O‘z Telegram ID’ingiz (@userinfobot) → `OWNER_ID`. Shundan keyin API’ga faqat siz kira olasiz.
3. Mini App https manzil talab qiladi: hosting manzili yoki `cloudflared tunnel --url http://localhost:8000`. Uni `PUBLIC_URL` ga yozing.
4. Botga /start → “Terminalni ochish”. Buyruqlar: /status, /pause, /resume.

## Muhim
- `OWNER_ID` bo‘sh bo‘lsa API himoyasiz: internetga ochmang.
- Slippage taxminiy formula bilan hisoblanadi, honeypot “sotib ko‘rish” testi yo‘q. Real natija yomonroq bo‘lishi mumkin.
- Memecoin segmenti juda xavfli. Paper natijasi real foydani kafolatlamaydi.
- Real savdoga o‘tishdan oldin: bir necha hafta paper, alohida kichik hamyon, asosiy kalitlarni hech qachon botga bermang.
