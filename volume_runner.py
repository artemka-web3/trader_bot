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


schedule.every(3).minutes.at(':00').do(restart_tracking_big_volumes)


while True:
    schedule.run_pending()
    time.sleep(1)