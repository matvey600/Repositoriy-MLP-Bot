import requests
from dotenv import load_dotenv
import os

load_dotenv()

token = os.getenv("BOT_TOKEN")

url = f"https://api.telegram.org/bot{token}/getMe"

r = requests.get(url, timeout=15)

print(r.status_code)
print(r.text)