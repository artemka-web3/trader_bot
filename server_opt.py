import os
import time
import schedule

def job():
    os.system('sudo systemctl stop collect_bit.service')
    time.sleep(2)
    os.system('sudo apt clean')
    time.sleep(2)
    os.system('sudo apt autoremove')
    time.sleep(5)
    os.system('sudo rm -rf /tmp/*')
    time.sleep(5)
    os.system('sudo systemctl start collect_bit.service')

schedule.every(10).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)