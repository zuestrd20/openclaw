import requests
from datetime import datetime
from zoneinfo import ZoneInfo
import time

def get_weather_openmeteo(city_name, lat, lon):
    """使用 Open-Meteo API 獲取天氣資料
    
    完全免費，無需 API key，開源專案
    包含當前天氣 + 早中晚溫度預測
    """
    
    try:
        # 使用 Open-Meteo API (完全免費，無需 key)
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            'latitude': lat,
            'longitude': lon,
            'current': 'temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m',
            'hourly': 'temperature_2m,weather_code',
            'timezone': 'Asia/Taipei',
            'temperature_unit': 'celsius',
            'wind_speed_unit': 'kmh',
            'forecast_days': 1
        }
        
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        # 解析當前天氣
        current = data['current']
        
        temp = round(current['temperature_2m'])
        feels_like = round(current['apparent_temperature'])
        humidity = current['relative_humidity_2m']
        wind_speed = round(current['wind_speed_10m'], 1)
        weather_code = current['weather_code']
        
        # 根據 WMO Weather Code 獲取天氣描述和 emoji
        description, emoji = get_weather_info_from_wmo_code(weather_code)
        
        # 更新時間
        update_time = datetime.fromisoformat(current['time']).strftime('%H:%M')
        
        # 解析每小時預報，提取早中晚溫度
        hourly = data.get('hourly', {})
        hourly_times = hourly.get('time', [])
        hourly_temps = hourly.get('temperature_2m', [])
        hourly_codes = hourly.get('weather_code', [])
        
        # 找出早中晚的溫度 (早上8點、中午12點、晚上18點)
        morning_temp = None
        noon_temp = None
        evening_temp = None
        morning_weather = None
        noon_weather = None
        evening_weather = None
        
        for i, time_str in enumerate(hourly_times):
            hour = datetime.fromisoformat(time_str).hour
            if hour == 8 and morning_temp is None:
                morning_temp = round(hourly_temps[i])
                morning_weather = get_weather_info_from_wmo_code(hourly_codes[i])[1]
            elif hour == 12 and noon_temp is None:
                noon_temp = round(hourly_temps[i])
                noon_weather = get_weather_info_from_wmo_code(hourly_codes[i])[1]
            elif hour == 18 and evening_temp is None:
                evening_temp = round(hourly_temps[i])
                evening_weather = get_weather_info_from_wmo_code(hourly_codes[i])[1]
        
        # 組合天氣訊息
        weather_text = f"""
📍 <b>{city_name}</b>
{emoji} {description}
🌡️ 現在：{temp}°C（體感 {feels_like}°C）
💧 濕度：{humidity}%
💨 風速：{wind_speed} km/h

<b>今日溫度預測：</b>"""
        
        if morning_temp is not None:
            weather_text += f"\n  🌅 早上 08:00  {morning_weather} {morning_temp}°C"
        if noon_temp is not None:
            weather_text += f"\n  ☀️ 中午 12:00  {noon_weather} {noon_temp}°C"
        if evening_temp is not None:
            weather_text += f"\n  🌆 傍晚 18:00  {evening_weather} {evening_temp}°C"
        
        weather_text += f"\n🕐 更新時間：{update_time}\n"
        
        return weather_text
        
    except requests.exceptions.Timeout:
        return f"\n📍 <b>{city_name}</b>\n   ⚠️ 無法獲取天氣資訊：請求超時\n"
    except requests.exceptions.RequestException as e:
        return f"\n📍 <b>{city_name}</b>\n   ⚠️ 無法獲取天氣資訊：{str(e)[:100]}\n"
    except Exception as e:
        return f"\n📍 <b>{city_name}</b>\n   ⚠️ 無法獲取天氣資訊：{str(e)[:100]}\n"

def get_weather_info_from_wmo_code(code):
    """根據 WMO Weather Code 返回天氣描述和 emoji
    
    WMO Code 標準：
    0: Clear sky
    1-3: Mainly clear, partly cloudy, overcast
    45-48: Fog
    51-55: Drizzle
    61-65: Rain
    71-75: Snow
    80-82: Rain showers
    95-99: Thunderstorm
    """
    
    weather_map = {
        0: ("晴朗", "☀️"),
        1: ("大致晴朗", "🌤️"),
        2: ("部分多雲", "⛅"),
        3: ("陰天", "☁️"),
        45: ("有霧", "🌫️"),
        48: ("濃霧", "🌫️"),
        51: ("小雨", "🌦️"),
        53: ("中雨", "🌧️"),
        55: ("大雨", "🌧️"),
        56: ("凍雨", "🌧️"),
        57: ("凍雨", "🌧️"),
        61: ("小雨", "🌦️"),
        63: ("中雨", "🌧️"),
        65: ("大雨", "🌧️"),
        66: ("凍雨", "🌧️"),
        67: ("凍雨", "🌧️"),
        71: ("小雪", "❄️"),
        73: ("中雪", "❄️"),
        75: ("大雪", "❄️"),
        77: ("雪粒", "❄️"),
        80: ("陣雨", "🌦️"),
        81: ("陣雨", "🌧️"),
        82: ("豪雨", "🌧️"),
        85: ("陣雪", "❄️"),
        86: ("陣雪", "❄️"),
        95: ("雷雨", "⛈️"),
        96: ("雷雨冰雹", "⛈️"),
        99: ("雷雨冰雹", "⛈️")
    }
    
    return weather_map.get(code, ("未知天氣", "🌤️"))

def send_telegram_message(message, chat_id, bot_token):
    """發送 Telegram 訊息"""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return True, "訊息發送成功"
    except Exception as e:
        return False, f"發送失敗：{str(e)}"

def main():
    print("🔄 正在獲取天氣資料...")
    
    # 城市座標
    cities = {
        '桃園': (24.9936, 121.3010),
        '台中': (24.1477, 120.6736)
    }
    
    # 收集所有城市的天氣資訊
    weather_messages = []
    
    for city_name, (lat, lon) in cities.items():
        print(f"   正在獲取 {city_name} 的天氣...")
        weather_text = get_weather_openmeteo(city_name, lat, lon)
        weather_messages.append(weather_text)
        time.sleep(0.5)  # 避免 API 限流
    
    # 組合完整訊息（使用台灣時區）
    taipei_tz = ZoneInfo('Asia/Taipei')
    now = datetime.now(taipei_tz)
    weekday_zh = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekday = weekday_zh[now.weekday()]
    
    full_message = f"""🌤️ <b>每日天氣預報</b>
📅 {now.strftime('%Y年%m月%d日')} {weekday}
==============================
"""
    
    for weather in weather_messages:
        full_message += weather
    
    full_message += "\n✨ 祝你有美好的一天！"
    
    print("📝 格式化訊息...")
    
    # Telegram Bot 設定
    BOT_TOKEN = "8542634056:AAEwAorsNCqdBXJOHFnXq0Lk25fVzvWxJN8"
    CHAT_ID = "984882424"
    
    print("📤 發送 Telegram 訊息...")
    success, message = send_telegram_message(full_message, CHAT_ID, BOT_TOKEN)
    
    if success:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")
    
    print("\n預覽訊息內容：")
    print("-" * 50)
    # 移除 HTML 標籤以便在 console 預覽
    preview = full_message.replace('<b>', '').replace('</b>', '').replace('<i>', '').replace('</i>', '')
    print(preview)

if __name__ == "__main__":
    main()
