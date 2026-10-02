import os
import requests
import yfinance as yf
from datetime import datetime
import pytz

# إعدادات التليجرام
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def send_telegram_message(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials not found.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("Message sent successfully.")
    except Exception as e:
        print(f"Error sending message: {e}")

def analyze_egx():
    # قائمة ببعض أسهم البورصة المصرية الشهيرة للمتابعة
    tickers = ["COMI.CA", "HELI.CA", "PHDC.CA", "EGTS.CA", "FWRY.CA", "AMOC.CA", "ESRS.CA", "ETRS.CA"]
    
    report = "📊 *تقرير تحليل السوق وصانع السوق (EGX)*\n\n"
    active_alerts = False

    cairo_tz = pytz.timezone('Africa/Cairo')
    current_time = datetime.now(cairo_tz).strftime('%Y-%m-%d %I:%M %p')
    report += f"🕒 وقت التقرير: {current_time}\n\n"

    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="5d")
            if hist.empty or len(hist) < 2:
                continue
            
            current_price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[-2]
            price_change = ((current_price - prev_price) / prev_price) * 100
            
            current_volume = hist['Volume'].iloc[-1]
            avg_volume = hist['Volume'].iloc[:-1].mean()
            
            # فحص حجم التداول والطلبات (صانع السوق)
            if current_volume > (avg_volume * 1.5):
                active_alerts = True
                report += f"🐋 *كشف أمر جبل / نشاط صانع السوق:*\n"
                report += f"السهم `{ticker.replace('.CA', '')}` يشهد ضغط شراء قوي جداً وتداولات مكثفة (الحجم الحالي يتجاوز المتوسط بنسبة كبيرة).\n"
                report += f"🔹 السعر الحالي: `{current_price:.2f}` (تغير: `{price_change:+.2f}%`)\n"
                report += f"🔹 حجم التداول: `{int(current_volume):,}` سهم\n\n"
            elif price_change >= 3.0:
                active_alerts = True
                report += f"🎯 *فرصة مضاربة سريعة (Target 3-4%):*\n"
                report += f"السهم `{ticker.replace('.CA', '')}` حقق ارتفاعاً بنسبة `{price_change:+.2f}%` وجاهز لتحقيق الهدف!\n"
                report += f"🔹 السعر: `{current_price:.2f}` | الحجم: `{int(current_volume):,}`\n\n"

        except Exception as e:
            print(f"Error processing {ticker}: {e}")

    if not active_alerts:
        report += "ℹ️ لا توجد تحركات غير عادية أو إشارات لصانع السوق مطابقة للشروط في الجلسة الحالية، السوق يتحرك في نطاق هادئ."

    send_telegram_message(report)

if __name__ == "__main__":
    analyze_egx()
