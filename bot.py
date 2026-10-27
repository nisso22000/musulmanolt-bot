"""Daily Arabic Hadith + Italian translation Telegram publisher."""
import datetime as dt
import json
import os
import urllib.request
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Africa/Algiers")
START_DATE = dt.date(2026, 10, 28)
EDITIONS = [("ara-bukhari", "Sahih al-Bukhari"), ("ara-muslim", "Sahih Muslim")]
BASE_URL = "https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/"

def get_json(url, payload=None, headers=None):
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"User-Agent": "MusulmanoltBot/1.0", **(headers or {})})
    with urllib.request.urlopen(req, timeout=60) as response:
        return json.load(response)

def select_hadith(date):
    day = (date - START_DATE).days
    if day < 0:
        raise RuntimeError("The start date has not arrived")
    code, source = EDITIONS[day % len(EDITIONS)]
    edition = get_json(BASE_URL + code + ".json")
    entries = [h for h in edition["hadiths"] if h.get("text", "").strip() and h.get("hadithnumber") is not None]
    if not entries:
        raise RuntimeError("No Hadith entries found")
    item = entries[(day // len(EDITIONS)) % len(entries)]
    return item["text"].strip(), source, item["hadithnumber"]

def translate(arabic):
    key = os.environ["GEMINI_API_KEY"]
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    prompt = (
        "Traduci fedelmente in italiano il seguente hadith arabo. "
        "Non aggiungere commenti, spiegazioni, riferimenti o frasi non presenti nel testo. "
        "Restituisci soltanto la traduzione italiana.\n\n" + arabic
    )
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    result = get_json(url, {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.1}
    }, {"x-goog-api-key": key, "Content-Type": "application/json"})
    candidates = result.get("candidates", [])
    if not candidates:
        raise RuntimeError("Gemini did not return a translation")
    translation = "".join(part.get("text", "") for part in candidates[0].get("content", {}).get("parts", [])).strip()
    if len(translation) < 10:
        raise RuntimeError("Invalid translation")
    return translation

def publish(text):
    if len(text) > 4096:
        raise RuntimeError("Message too long for Telegram; not truncating the Hadith")
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    result = get_json(f"https://api.telegram.org/bot{token}/sendMessage", {
        "chat_id": os.environ["TELEGRAM_CHAT_ID"],
        "text": text,
        "disable_web_page_preview": True
    }, {"Content-Type": "application/json"})
    if not result.get("ok"):
        raise RuntimeError("Telegram rejected the message")

def main():
    now = dt.datetime.now(TZ)
    if now.hour != 8 and os.getenv("FORCE_SEND") != "true":
        print("Not 08:00 in Algeria; skipping")
        return
    arabic, source, number = select_hadith(now.date())
    italian = translate(arabic)
    message = (
        f"📖 حديث اليوم | Hadith del giorno\n\n{arabic}\n\n"
        f"🇮🇹 Traduzione italiana (IA):\n{italian}\n\n"
        f"📚 Fonte: {source}, hadith n. {number}\n"
        "Nota: traduzione automatica; per precisione consultare l'originale arabo."
    )
    publish(message)
    print(f"Sent {source} #{number} on {now.date()}")

if __name__ == "__main__":
    main()
