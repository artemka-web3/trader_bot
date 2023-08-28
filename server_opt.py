import os
import time
import schedule

def job():
    os.system('sudo systemctl restart collect_big.service')
    time.sleep(2)
    os.system('sudo apt clean')
    time.sleep(2)
    os.system('sudo apt autoremove')
    time.sleep(2)
    os.system('sudo rm -rf /tmp/*')

schedule.every(3).minutes.at(':00').do(job)

while True:
    schedule.run_pending()
    time.sleep(1)