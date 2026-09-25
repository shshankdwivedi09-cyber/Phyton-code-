import json
import time
import requests
import websocket

# -------------------------------------------------------------
# 1. TELEGRAM CONFIGURATION
# -------------------------------------------------------------
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_TELEGRAM_CHAT_ID"

# Minimum Dump Value Filter (Kitne INR se bade SELL order par alert chahiye)
MIN_DUMP_VALUE_INR = 50000 

# -------------------------------------------------------------
# 2. HELPER FUNCTIONS
# -------------------------------------------------------------
def send_telegram_alert(message):
    if TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
        return
        
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID, 
            "text": message, 
            "parse_mode": "Markdown"
        }
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"[Telegram Error]: {e}")

# -------------------------------------------------------------
# 3. WEBSOCKET EVENTS (CoinDCX Live Feed)
# -------------------------------------------------------------
def on_message(ws, message):
    try:
        data = json.loads(message)
        
        if isinstance(data, dict) and "p" in data and "q" in data:
            price = float(data.get("p", 0))
            quantity = float(data.get("q", 0))
            symbol = data.get("s", "UNKNOWN")
            is_sell = data.get("m", False)  # True = Market Sell / Dump
            
            total_value = price * quantity
            
            # SIRF Large SELL orders capture karein
            if is_sell and total_value >= MIN_DUMP_VALUE_INR:
                alert_text = (
                    f"🔴 *COINDCX WHALE DUMP DETECTED!* 🔴\n\n"
                    f"🪙 *Pair:* `{symbol}`\n"
                    f"💥 *Dump Amount:* ₹{total_value:,.2f}\n"
                    f"🏷️ *Price:* {price}\n"
                    f"📦 *Volume:* {quantity:,}\n"
                    f"⏰ *Time:* {time.strftime('%H:%M:%S')}"
                )
                print(f"\n{alert_text}\n" + "-"*40)
                send_telegram_alert(alert_text)

    except Exception as e:
        pass

def on_open(ws):
    print("⚡ Connected to CoinDCX Stream! Monitoring ALL 500+ coins in real-time...")
    send_telegram_alert("🚀 *CoinDCX 500+ Coins Dump Tracker Online!*")
    
    subscribe_msg = {
        "eventName": "subscribe",
        "channelName": "B-all@trades"
    }
    ws.send(json.dumps(subscribe_msg))

def on_error(ws, error):
    print(f"⚠️ [Socket Error]: {error}")

def on_close(ws, close_status_code, close_msg):
    print("🔌 Connection closed. Reconnecting in 3 seconds...")
    time.sleep(3)
    start_scanner()

def start_scanner():
    socket_url = "wss://stream.coindcx.com"
    ws = websocket.WebSocketApp(
        socket_url,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever(ping_interval=20, ping_timeout=10)

if __name__ == "__main__":
    start_scanner()
  
