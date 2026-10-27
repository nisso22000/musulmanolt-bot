# MusulmanoltBot

Daily Arabic Hadith and Italian AI translation at **08:00 Algeria time** via GitHub Actions.

## Setup

1. Revoke the Telegram token previously exposed in chat using @BotFather.
2. Add @MusulmanoltBot to your Telegram group and allow it to post.
3. Get the group chat ID and a Gemini API key from https://aistudio.google.com/apikey.
4. In **Settings → Secrets and variables → Actions**, create:
   - `TELEGRAM_BOT_TOKEN` — new bot token
   - `TELEGRAM_CHAT_ID` — target group ID
   - `GEMINI_API_KEY` — Gemini API key
5. Enable GitHub Actions if prompted.

The bot fetches Arabic hadiths from the community-maintained https://github.com/fawazahmed0/hadith-api dataset (Sahih al-Bukhari and Sahih Muslim editions), alternating between them and selecting successive entries. Numbering follows the dataset and may vary between editions. AI only translates the Arabic; it never invents the source text.

**Important:** AI translation can contain errors; human review is recommended for religious publishing. If fetching or translating fails, the bot does not post. Very long texts are skipped to avoid truncation. GitHub scheduled runs may be late or occasionally skipped; the schedule is 07:00 UTC, corresponding to 08:00 Algeria time.

Manual workflow runs outside the 08:00 hour intentionally skip posting unless FORCE_SEND=true is explicitly set in the workflow environment for testing. Never commit secrets or share them in chat.
