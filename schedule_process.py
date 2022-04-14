import os
import signal
import subprocess
import schedule
import time

def run_bot(pro):
    pro.kill()
    pro = subprocess.Popen("python bot.py")
    pro.wait()

process = subprocess.Popen("python bot.py")

# restart bot every monday
schedule.every().monday.do(run_bot, pro = process)

while True:
    schedule.run_pending()
    time.sleep(1)
