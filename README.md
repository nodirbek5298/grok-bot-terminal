# XAUUSD M5 Terminal (paper rejim)

**▶ Jonli sahifa: https://nodirbek5298.github.io/grok-bot-terminal/**

Oltin/dollar (XAUUSD) uchun 5 daqiqalik (M5) sham tahlili va **soxta pul bilan** ishlaydigan sinov bot.
Sahifada: sham grafigi, EMA20/EMA50, RSI, MACD, ATR, qarshilik va qo‘llab-quvvat darajalari, o‘zbekcha signal sabablari, bitimlar va signal tarixi.

Serversiz: hammasi brauzerda ishlaydi, GitHub Pages yetarli. Haqiqiy pul ishlatilmaydi, birjaga ulanmaydi.

## Ma’lumot manbalari
- **Avto (standart):** PAXG/USDT, Binance (kalitsiz). PAXG oltin bilan bog‘langan token: narxi XAUUSD ga yaqin, lekin aynan o‘zi emas va 24/7 savdo qilinadi (XAUUSD hafta oxiri yopiq).
- **XAU/USD, Twelve Data:** haqiqiy spot oltin. twelvedata.com da bepul kalit oling (8 so‘rov/daqiqa, 800/kun), sahifadagi “Ma’lumot manbai” bo‘limiga kiriting. Kalit faqat sizning brauzeringizda saqlanadi, repoga tushmaydi.
- **Demo:** tasodifiy narx, internetsiz sinash uchun.

## Strategiya (oddiy, tushuntiriladigan)
5 omil: EMA trend, EMA20 qiyaligi, RSI, MACD, yaqin oraliqdan chiqish. 3 va undan ko‘pi bir tomonga bo‘lsa signal. RSI haddan tashqari baland/past bo‘lsa va bozor juda sokin bo‘lsa, bot kirmaydi.
Stop-loss = 1.5 × ATR, maqsad = 2.25 × ATR. Har bir bitimda balansning 1% i xavf ostiga qo‘yiladi, spred $0.35 hisobga olinadi, 2 soatdan keyin vaqt bo‘yicha yopiladi.

## Cheklovlar (halol)
- Bot **sahifa ochiq turganda** ishlaydi. Holat brauzerda (localStorage) saqlanadi. 24/7 ishlashi uchun alohida server yoki rejalashtirilgan ish kerak.
- Strategiya oddiy indikatorlarga asoslangan va **tarixiy sinovdan (backtest) o‘tkazilmagan**. Foyda kafolati yo‘q.
- Bozor yopiq bo‘lsa, Twelve Data eski sham beradi: sahifa ogohlantiradi.
- Bu savdo maslahati emas.

## Eski Solana versiyasi
`engine.py`, `feeds.py`, `server.py`, `Dockerfile`, `requirements.txt`, `.env.example` Solana memecoinlar uchun yozilgan eski bot. Yangi sahifa (`docs/index.html`) ularga bog‘liq emas. Eski sahifa kodi git tarixida (commit `f82f257`) saqlangan.
