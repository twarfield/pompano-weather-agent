import requests
import os
from datetime import datetime, timedelta

# Telegram Secrets from GitHub Actions
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def check_weather():
    # Pompano Beach Coordinates
    lat, lon = 26.2379, -80.1248
    
    # We pull Visibility (meters) and Cloud Cover Low (%)
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=visibility,cloud_cover_low&forecast_days=2"
    
    response = requests.get(url).json()
    hourly = response.get('hourly', {})
    
    # Calculate "Tomorrow" date string
    tomorrow_str = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    alert_details = []

    # Loop through the forecast hours
    for i, time_val in enumerate(hourly.get('time', [])):
        if tomorrow_str in time_val:
            dt = datetime.fromisoformat(time_val)
            
            # Focus on 6:00 AM to 10:00 AM
            if 6 <= dt.hour <= 10:
                vis_meters = hourly['visibility'][i]
                low_clouds = hourly['cloud_cover_low'][i]
                
                # CRITERIA: Visibility < 3000m (approx 1.8 miles) OR Low Clouds > 85%
                if vis_meters < 3000 or low_clouds > 85 or True:
                    time_label = dt.strftime('%I:%M %p')
                    vis_miles = round(vis_meters / 1609.34, 1)
                    alert_details.append(f"☁️ {time_label}: Low Cloud {low_clouds}% (Vis: {vis_miles} mi)")

    if alert_details:
        message = "🌫️ *Pompano Fog/Low Cloud Alert*\nForecast for tomorrow morning:\n\n" + "\n".join(alert_details)
        send_telegram(message)
    else:
        print("No fog/low clouds expected. No message sent.")

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}
    requests.post(url, data=payload)

if __name__ == "__main__":
    check_weather()
