# XAUUSD M1 + M5 Terminal (paper rejim)

**▶ Jonli sahifa: https://nodirbek5298.github.io/grok-bot-terminal/**

Oltin/dollar (XAUUSD) uchun M1 va M5 shamlarini birga tahlil qiladi, qaysi vaqt oralig‘ida strategiya so‘nggi paytlarda yaxshiroq ishlaganini o‘lchaydi va bot o‘shanisini ishlatadi. Savdo **soxta pul** bilan (paper).
Sahifada: sham grafigi, EMA20/EMA50, RSI, MACD, ATR, qarshilik va qo‘llab-quvvat, o‘zbekcha signal sabablari, M1 va M5 solishtirish jadvali, bitimlar va signal tarixi.

Serversiz: hammasi brauzerda ishlaydi, GitHub Pages yetarli. Haqiqiy pul ishlatilmaydi, birjaga ulanmaydi.

## Avto tanlov qanday ishlaydi
1. Asos sifatida M1 shamlari olinadi, M5 ulardan yig‘iladi.
2. Ikkala vaqt oralig‘ida bir xil qoidalar so‘nggi ~33 soatlik narxlarda “qayta o‘ynab” ko‘riladi (spred bilan). Natija R birligida (R = stop masofasi).
3. O‘rtacha natijasi yaxshiroq bo‘lgan vaqt oralig‘i tanlanadi. Farq kamida 0.10R bo‘lsa almashadi (tez-tez o‘zgarmasligi uchun). Har birida kamida 10 ta tarixiy bitim bo‘lmasa, standart M5.
4. Ikkala natija ham manfiy bo‘lsa, sahifa ogohlantiradi. “Tarixiy natija manfiy bo‘lsa savdo qilma” katagi bilan botni to‘xtatish mumkin.
5. Qo‘lda “Faqat M1” yoki “Faqat M5” tanlash ham mumkin.

## Ma’lumot manbalari
- **Avto (standart):** PAXG/USDT, Binance (kalitsiz). PAXG oltin bilan bog‘langan token: narxi XAUUSD ga yaqin, lekin aynan o‘zi emas va 24/7 savdo qilinadi (XAUUSD hafta oxiri yopiq).
- **XAU/USD, Twelve Data:** haqiqiy spot oltin. twelvedata.com da bepul kalit oling (8 so‘rov/daqiqa, 800/kun), sahifadagi “Ma’lumot manbai” bo‘limiga kiriting. Kalit faqat sizning brauzeringizda saqlanadi, repoga tushmaydi. Sahifa har 2 daqiqada bitta so‘rov yuboradi.
- **Demo:** tasodifiy narx, internetsiz sinash uchun.

## Strategiya (oddiy, tushuntiriladigan)
5 omil: EMA trend, EMA20 qiyaligi, RSI, MACD, yaqin oraliqdan chiqish. 3 va undan ko‘pi bir tomonga bo‘lsa signal. RSI haddan tashqari baland/past bo‘lsa va bozor juda sokin bo‘lsa, bot kirmaydi.
Stop-loss = 1.5 × ATR, maqsad = 2.25 × ATR. Har bir bitimda balansning 1% i xavf ostiga qo‘yiladi, spred $0.35 hisobga olinadi, 24 ta shamdan keyin vaqt bo‘yicha yopiladi.

## Cheklovlar (halol)
- Tarixiy natija kelajakni kafolatlamaydi. Bitimlar soni kam bo‘lsa, M1 va M5 orasidagi farq tasodif bo‘lishi mumkin. Strategiya oddiy indikatorlarga asoslangan va uzoq muddatli sinovdan o‘tkazilmagan.
- Spred (qat’iy $0.35) M1 ga nisbatan kuchliroq ta’sir qiladi. Haqiqiy broker spredi va Binance komissiyasi (PAXG uchun) boshqacha bo‘lishi mumkin.
- Bot **sahifa ochiq turganda** ishlaydi. Holat brauzerda (localStorage) saqlanadi. 24/7 ishlashi uchun alohida server yoki rejalashtirilgan ish kerak.
- Bozor yopiq bo‘lsa, Twelve Data eski sham beradi: sahifa ogohlantiradi.
- Bu savdo maslahati emas.

## Eski Solana versiyasi
`engine.py`, `feeds.py`, `server.py`, `Dockerfile`, `requirements.txt`, `.env.example` Solana memecoinlar uchun yozilgan eski bot. Yangi sahifa (`docs/index.html`) ularga bog‘liq emas. Eski sahifa kodi git tarixida (commit `f82f257`) saqlangan.
