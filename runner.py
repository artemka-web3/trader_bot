# here i will restart collecting big volumes every minutes
# and i will run collecting avg volumes every night

import os
import time
import schedule

def restart_tracking_big_volumes():
    os.system('sudo systemctl restart track_volumes.service')
    time.sleep(2)
    os.system('sudo apt clean')
    time.sleep(2)
    os.system('sudo apt autoremove')
    time.sleep(2)
    os.system('sudo rm -rf /tmp/*')

def tracking_subs():
    os.system('sudo systemctl restart track_subs.service')
    time.sleep(2)
    os.system('sudo apt clean')
    time.sleep(2)
    os.system('sudo apt autoremove')
    time.sleep(2)
    os.system('sudo rm -rf /tmp/*')

def send_checks():
    os.system('sudo systemctl restart send_checks.service')
    time.sleep(2)
    os.system('sudo apt clean')
    time.sleep(2)
    os.system('sudo apt autoremove')
    time.sleep(2)
    os.system('sudo rm -rf /tmp/*')


def collect_avg():
    os.system('sudo systemctl restart collect_avg_volumes.service')
    time.sleep(2)
    os.system('sudo apt clean')
    time.sleep(2)
    os.system('sudo apt autoremove')
    time.sleep(2)
    os.system('sudo rm -rf /tmp/*')


schedule.every(3).minutes.at(':00').do(restart_tracking_big_volumes)
schedule.every().day.at('01:00').do(collect_avg)
schedule.every().day.at('23:50').do(send_checks)
schedule.every().hour.do(tracking_subs)





while True:
    schedule.run_pending()
    time.sleep(1)