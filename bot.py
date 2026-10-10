import os
import time
import requests
import easyocr
from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID   = os.environ.get("TELEGRAM_CHAT_ID")
TRADINGVIEW_URL    = os.environ.get("TRADINGVIEW_URL")

def enviar_alerta_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensaje,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=10)
        print("✅ Alerta enviada con éxito a Telegram.")
    except Exception as e:
        print(f"❌ Error al conectar con Telegram: {e}")

def main():
    print("🚀 Iniciando escaneo automatizado en la nube...")
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--mute-audio')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        print(f"🌐 Abriendo gráfico de TradingView...")
        driver.get(TRADINGVIEW_URL)
        time.sleep(25)

        png_data = driver.get_screenshot_as_png()
        image = Image.open(BytesIO(png_data))

        ancho, alto = image.size
        region_analisis = image.crop((int(ancho * 0.40), 0, ancho, alto))

        bytes_img = BytesIO()
        region_analisis.save(bytes_img, format='PNG')
        
        print("🧠 Analizando texto visualmente...")
        reader = easyocr.Reader(['es', 'en'], gpu=False)
        resultados = reader.readtext(bytes_img.getvalue(), detail=0)
        texto_unificado = " ".join(resultados).upper()

        es_long  = "LONG" in texto_unificado or ("ENTRADA" in texto_unificado and "TP" in texto_unificado)
        es_short = "SHORT" in texto_unificado or ("ENTRADA" in texto_unificado and "SL" in texto_unificado)

        if es_long or es_short:
            direccion = "🟢 COMPRA / LONG" if es_long else "🔴 VENTA / SHORT"
            mensaje = (
                f"🚨 *¡SEÑAL DETECTADA EN LA NUBE (1H)*\n\n"
                f"**Dirección:** {direccion}\n"
                f"**Datos detectados:**\n`{texto_unificado[:250]}`\n\n"
                f"⚡ *Revisa tu plataforma para operar.*"
            )
            print("🚨 ¡Orden detectada! Enviando notificación...")
            enviar_alerta_telegram(mensaje)
        else:
            print("ℹ️ No hay nuevas órdenes activas en este momento.")

    except Exception as e:
        print(f"❌ Error en la ejecución: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
