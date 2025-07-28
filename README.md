# Heat Risk Monitor with DHT11, PIR, LCD & LINE Notification

Raspberry Piを用いた、温湿度センサ（DHT11）・人感センサ（PIR）・LCDディスプレイ・LINE通知機能を組み合わせた熱中症リスク監視システムです。

---

## 機能概要

- DHT11で温度・湿度を計測  
- 人感センサまたはボタンで測定をトリガー  
- LCD1602（I2C）に計測値とリスクを表示  
- 熱中症危険度を判定し、日本語で表示  
- LINE BOTで指定ユーザーに通知

---

## システム構成

- Raspberry Pi（GPIO使用）  
- DHT11 温湿度センサ  
- PIR 人感センサ  
- ボタン（GPIO）  
- LCD1602（I2C）  
- LINE Messaging API  

---

## 回路図

![回路図](images/circuit_diagram.png)

## セットアップ手順

1. LCD1602用ドライバをインストール  
2. LINE DevelopersでMessaging APIチャネルを作成  
3. スクリプト内にアクセストークンとユーザーIDを設定  
