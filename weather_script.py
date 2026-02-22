import requests
import os
from datetime import datetime, timedelta

# Secrets from GitHub
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_KEY = os.getenv("WEATHER_API_KEY")

# Pompano Beach Coordinates
LAT = 26.2379
LON = -80.1248

def check_weather():
    # 1. Get Forecast
    url = f"https://api.openweathermap.org/data/3.0/onecall?lat={LAT}&lon={LON}&appid={API_KEY}&units=imperial"
    data = requests.get(url).json()

    tomorrow = datetime.now() + timedelta(days=1)
    found_fog = False
    report = []

    # 2. Check 6AM - 10AM tomorrow
    for hour in data.get('hourly', []):
        dt = datetime.fromtimestamp(hour['dt'])
        if dt.date() == tomorrow.date() and 6 <= dt.hour <= 10:
            condition = hour['weather'][0]['description']
            vis_meters = hour.get('visibility', 10000)
            
            # Trigger if 'fog' is in description or visibility < 2000 meters
            if "fog" in condition.lower() or "mist" in condition.lower() or vis_meters < 2000:
                found_fog = True
                report.append(f"⏰ {dt.strftime('%I %p')}: {condition.capitalize()}")

    # 3. Send Telegram Alert
    if found_fog:
        alert_text = "🌫️ *Pompano Fog Alert for Tomorrow*\n\n" + "\n".join(report)
        send_msg(alert_text)

def send_msg(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}
    requests.post(url, data=payload)

if __name__ == "__main__":
    check_weather()
