#!/usr/bin/env python3
import LCD1602
import time
import requests
from gpiozero import OutputDevice, InputDevice, DigitalInputDevice, Button

# DHT11クラス 
class DHT11():
    MAX_DELAY = 100
    BIT_1_DELAY = 10
    BITS_LEN = 40

    def __init__(self, pin):
        self._pin = pin

    def read_data(self):
        gpio = OutputDevice(self._pin)
        gpio.off()
        time.sleep(0.02)  # Start signal
        gpio.close()
        gpio = InputDevice(self._pin)
        bits = ""
        delay_count = 0
        bit_count = 0

        # Wait for sensor response
        while gpio.value == 1:
            pass

        while bit_count < self.BITS_LEN:
            while gpio.value == 0:
                pass
            while gpio.value == 1:
                delay_count += 1
                if delay_count > self.MAX_DELAY:
                    break
            bits += "1" if delay_count > self.BIT_1_DELAY else "0"
            delay_count = 0
            bit_count += 1

        try:
            h = int(bits[0:8], 2)
            hd = int(bits[8:16], 2)
            t = int(bits[16:24], 2)
            td = int(bits[24:32], 2)
            c = int(bits[32:40], 2)
        except:
            return 0.0, 0.0

        if c != (h + hd + t + td):
            return 0.0, 0.0
        return float(f"{h}.{hd}"), float(f"{t}.{td}")

# 熱中症危険度の評価
def evaluate_heat_risk(temp, hum):
    if temp >= 31 and hum >= 75:
        return "Danger", "危険"
    elif temp >= 28 and hum >= 70:
        return "Warning", "警戒"
    elif temp >= 25 and hum >= 65:
        return "Caution", "注意"
    else:
        return "Safe", "安全"

# LINEメッセージ送信
CHANNEL_ACCESS_TOKEN = ''
USER_ID = ''

def send_line_message(user_id, message):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "to": user_id,
        "messages": [{"type": "text", "text": message}]
    }
    response = requests.post(url, headers=headers, json=payload)
    print("📤 LINE送信:", response.status_code, response.text)

# 初期化 
DHT_PIN = 14
PIR_PIN = 25
BTN_PIN = 17
dht = DHT11(DHT_PIN)
pir = DigitalInputDevice(pin=PIR_PIN, pull_up=False)
button = DigitalInputDevice(BTN_PIN,pull_up=False)

LCD1602.init(0x3f, 1)  # LCD I2Cアドレス (0x27の場合は変更)
LCD1602.write(0, 0, 'System Starting...')
time.sleep(2)
LCD1602.clear()

# 測定関数 
def measure_and_notify(trigger_source):
    LCD1602.clear()
    LCD1602.write(0, 0, f"{trigger_source}測定中...")
    print(f"🔔 {trigger_source}トリガーで測定開始")

    hum, temp = dht.read_data()
    if hum != 0.0 and temp != 0.0:
        lcd_risk, jp_risk = evaluate_heat_risk(temp, hum)

        # LCD表示
        line1 = f"T:{temp:.1f}C H:{int(hum)}%"
        line2 = f"Risk: {lcd_risk}"
        LCD1602.write(0, 0, line1.ljust(16))
        LCD1602.write(0, 1, line2.ljust(16))

        # ターミナル表示
        print(f"🌡 温度:{temp:.1f}°C 💧湿度:{hum:.1f}% 🚨危険度:{jp_risk}")

        # LINE送信
        msg = f"📡 {trigger_source}測定\n🌡 温度:{temp:.1f}°C\n💧湿度:{hum:.1f}%\n🚨危険度:{jp_risk}"
        send_line_message(USER_ID, msg)
    else:
        LCD1602.write(0, 0, 'Sensor Error')
        print("❌ 温湿度測定失敗")

    time.sleep(10)

# メインループ 
try:
    while True:
        if pir.value == 1:
            measure_and_notify("👤 人感")
        elif button.is_pressed:
            measure_and_notify("🔘 ボタン")
        else:
            LCD1602.clear()
            LCD1602.write(0, 0, 'Waiting...')
            print("⏳ 待機中...")
            time.sleep(1)

except KeyboardInterrupt:
    LCD1602.clear()
    LCD1602.write(0, 0, 'Shutting Down...')
    print("🛑 終了しました")
