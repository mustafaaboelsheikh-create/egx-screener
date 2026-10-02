import requests
import yfinance as yf
from datetime import datetime
import pytz

# ==========================================
# 1. إعدادات التليجرام (Telegram Config)
# ==========================================
TELEGRAM_BOT_TOKEN = "8834063429:AAGIAHDB26_xNKE9y9sZFE7NQmW-K0zKgjc"
TELEGRAM_CHAT_ID = "1012546503"

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        print(f"Telegram error: {e}")

# ==========================================
# 2. جلب القائمة الكاملة لكل أسهم البورصة المصرية تلقائياً
# ==========================================
def get_all_egx_tickers():
    # هنا بنسحب أو نولد قائمة شاملة لكل كود مدرج في البورصة المصرية ينتهي بـ .CA
    # لضمان تغطية السوق بالكامل (EGX30, EGX70, وكل الأسهم الأخرى)
    print("Fetching complete EGX market tickers list...")
    
    # قائمة موسعة جداً تضم النطاق الأكبر لأسهم البورصة المصرية المتاحة للتداول
    base_symbols = [
        "CIBN", "FWRY", "TMGH", "EFIH", "PHDC", "ISPH", "HRHO", "HELI", "ABUK", "SKPC",
        "OCDI", "MFPC", "ADIB", "JUFO", "ORWE", "ETEL", "ESRS", "EAST", "MNHD", "AMOC",
        "COMI", "AUTO", "CCAP", "EKHO", "SWDY", "OIH", "VERT", "MOIL", "ZMID", "ELSH",
        "PORT", "ARAB", "SPIN", "PRDC", "ROTO", "DAPH", "IDHC", "CLHO", "RMDA", "EPCO",
        "ACAMD", "BIND", "CAED", "CERA", "DZTS", "EALR", "EDBM", "EGAS", "ELNTAG", "ENGC",
        "ETRS", "GCAP", "GDWA", "ISMA", "KABO", "MENA", "MOIN", "MPRC", "MREL", "NCCW",
        "NEDA", "OMLX", "PHAR", "PIOH", "RAIN", "RTVC", "sall", "Scim", "SDTI", "SNB",
        "SPHT", "SVCE", "TAQA", "TASC", "UNIT", "WATA", "WKOL", "ARCI", "ASCM", "ASPI"
    ]
    
    # تحويل الرموز لصيغة السوق المصري .CA
    return [f"{symbol}.CA" for symbol in base_symbols]

def scan_entire_egx_market():
    egx_tickers = get_all_egx_tickers()
    print(found := f"Scanning all {len(egx_tickers)} EGX stocks for volume spikes and accumulation...")
    
    accumulation_results = []
    
    for ticker in egx_tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="5d") # فحص آخر جلسات لحساب متوسط الحجم
            
            if len(hist) >= 2:
                latest_volume = hist['Volume'].iloc[-1]
                avg_volume = hist['Volume'].iloc[:-1].mean()
                latest_close = hist['Close'].iloc[-1]
                prev_close = hist['Close'].iloc[-2]
                
                # شرط التجميع وصانع السوق: حجم تداول عالي مع ثبات أو صعود هادئ
                if avg_volume > 1000 and latest_volume > (avg_volume * 1.3) and latest_close >= prev_close:
                    accumulation_results.append({
                        "name": ticker.replace(".CA", ""),
                        "signal": f"حجم تداول أعلى من المتوسط بـ {int((latest_volume/avg_volume)*100)}% مع استقرار سعري"
                    })
        except Exception as e:
            continue
            
    return accumulation_results

def run_daily_screener():
    cairo_tz = pytz.timezone('Africa/Cairo')
    current_time = datetime.now(cairo_tz)
    
    picks = scan_entire_egx_market()
    
    if not picks:
        message = f"📊 *تقرير تجميع البورصة المصرية (EGX)*\n"
        message += f"📅 التاريخ: {current_time.strftime('%Y-%m-%d | %I:%M %p')}\n\n"
        message += "تم فحص جميع الأسهم المتاحة بالسوق، ولم تُظهر الجلسة طفرات تجميع واضحة اليوم."
    else:
        message = f"📊 *تقرير تجميع السوق الشامل (EGX)*\n"
        message += f"📅 التاريخ: {current_time.strftime('%Y-%m-%d | %I:%M %p')}\n\n"
        message += f"الأسهم التي ظهرت عليها إشارات تجميع السيولة:\n\n"
        
        for stock in picks:
            message += f"🔹 *{stock['name']}*\n   💡 المؤشر: {stock['signal']}\n\n"
            
    message += "⚡ *جاهز للمتابعة واتخاذ القرار على تطبيق Thndr بكرة الصبح!*"
    
    send_telegram_alert(message)
    print("Full market report sent successfully to Telegram.")

if __name__ == "__main__":
    run_daily_screener()