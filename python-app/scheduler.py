import schedule
import time
import subprocess

def update_protest_data():
    print("🔄 시위 데이터 업데이트 중...")
    subprocess.run(["python3", "update_protest_data.py"])

# 매일 오후 6시에 실행
schedule.every().day.at("12:00").do(update_protest_data)

while True:
    schedule.run_pending()
    time.sleep(1)
