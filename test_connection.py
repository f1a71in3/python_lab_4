import requests

try:
    r = requests.get("https://api.telegram.org", timeout=10)
    print(" Доступ к Telegram API есть")
except:
    print("Нет доступа к Telegram API")