import os
import signal
import subprocess
import schedule
import time
from datetime import datetime

process = subprocess.Popen("python bot.py")

def run_bot():
    global process
    process.kill()
    process = subprocess.Popen("python bot.py")
    print("RESTART: ", datetime.now())

# restart bot every monday
schedule.every().monday.do(run_bot)

while True:
    schedule.run_pending()
    time.sleep(1)