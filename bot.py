import os
import time
import requests
import easyocr
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Cargar credenciales de Telegram desde los secretos de GitHub
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram_alert(message):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Error: Faltan las credenciales de Telegram en los secretos.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("✅ Alerta enviada con éxito a Telegram.")
        else:
            print(f"⚠️ Error al enviar a Telegram: {response.text}")
    except Exception as e:
        print(f"⚠️ Excepción en Telegram: {e}")

# ==========================================
# LISTA DE 12 OBJETIVOS (3 ACTIVOS X 4 TEMPORALIDADES)
# ==========================================
TARGETS = [
    # --- BITCOIN (BTCUSD) ---
    {"name": "BTCUSD - 15m", "url": "https://www.tradingview.com/chart/GW9AnMQd/?symbol=CRYPTO%3ABTCUSD&interval=15"},
    {"name": "BTCUSD - 30m", "url": "https://www.tradingview.com/chart/GW9AnMQd/?symbol=CRYPTO%3ABTCUSD&interval=30"},
    {"name": "BTCUSD - 45m", "url": "https://www.tradingview.com/chart/GW9AnMQd/?symbol=CRYPTO%3ABTCUSD&interval=45"},
    {"name": "BTCUSD - 1h",   "url": "https://www.tradingview.com/chart/GW9AnMQd/?symbol=CRYPTO%3ABTCUSD&interval=60"},
    
    # --- ETHEREUM (ETHUSD) ---
    {"name": "ETHUSD - 15m", "url": "https://www.tradingview.com/chart/GW9AnMQd/?symbol=CRYPTO%3AETHUSD&interval=15"},
    {"name": "ETHUSD - 30m", "url": "https://www.tradingview.com/chart/GW9AnMQd/?symbol=CRYPTO%3AETHUSD&interval=30"},
    {"name": "ETHUSD - 45m", "url": "https://www.tradingview.com/chart/GW9AnMQd/?symbol=CRYPTO%3AETHUSD&interval=45"},
    {"name": "ETHUSD - 1h",   "url": "https://www.tradingview.com/chart/GW9AnMQd/?symbol=CRYPTO%3AETHUSD&interval=60"},
    
    # --- ORO (XAUUSD) ---
    {"name": "XAUUSD - 15m", "url": "https://www.tradingview.com/chart/GW9AnMQd/?symbol=OANDA%3AXAUUSD&interval=15"},
    {"name": "XAUUSD - 30m", "url": "https://www.tradingview.com/chart/GW9AnMQd/?symbol=OANDA%3AXAUUSD&interval=30"},
    {"name": "XAUUSD - 45m", "url": "https://www.tradingview.com/chart/GW9AnMQd/?symbol=OANDA%3AXAUUSD&interval=45"},
    {"name": "XAUUSD - 1h",   "url": "https://www.tradingview.com/chart/GW9AnMQd/?symbol=OANDA%3AXAUUSD&interval=60"},
]

def main():
    print("🚀 Iniciando escaneo multi-activo y multi-temporalidad (12 gráficos)...")
    
    # Configurar Selenium en modo headless para Linux/GitHub Actions
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    reader = easyocr.Reader(['en'], gpu=False)
    
    keywords = ["LONG", "SHORT", "ENTRADA", "TP", "SL"]

    try:
        for target in TARGETS:
            name = target["name"]
            url = target["url"]
                
            print(f"\n🔍 Analizando mercado: {name}")
            try:
                driver.get(url)
                # Esperar 12 segundos a que TradingView cargue velas, canvas e indicadores
                time.sleep(12)
                
                screenshot_path = "screenshot.png"
                driver.save_screenshot(screenshot_path)
                
                # Ejecutar OCR en la captura
                results = reader.readtext(screenshot_path)
                detected_text = " ".join([res[1] for res in results]).upper()
                print(f"📝 Texto detectado en {name}: {detected_text[:100]}...")
                
                # Verificar si alguna palabra clave está presente
                found_keywords = [kw for kw in keywords if kw in detected_text]
                
                if found_keywords:
                    alerta_msg = (
                        f"🚨 ¡SEÑAL DETECTADA!\n"
                        f"📊 Activo/TF: {name}\n"
                        f"🔑 Coincidencias: {', '.join(found_keywords)}\n"
                        f"🔗 Gráfico: {url}"
                    )
                    print(alerta_msg)
                    send_telegram_alert(alerta_msg)
                else:
                    print(f"ℹ️ Sin señales activas en {name}.")
                    
            except Exception as e:
                print(f"❌ Error al procesar {name}: {e}")
                
    finally:
        driver.quit()
        print("\n🏁 Escaneo completo finalizado.")

if __name__ == "__main__":
    main()
