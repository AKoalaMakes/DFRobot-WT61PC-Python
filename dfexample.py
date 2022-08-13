from time import sleep 
from time import perf_counter

from dfrobotWT61PC import DFRobot_WT61PC


gyro = DFRobot_WT61PC('COM6')

while(True):
    t1 = perf_counter()
    if gyro.available():
        print("Accel:", *(f"{x:8.3f}" for x in gyro.accel()),end='  \t')
        print("Gyro:", *(f"{x:8.3f}" for x in gyro.gyro()),end='  \t')
        print("Angle:", *(f"{x:8.3f}" for x in gyro.angle()),end='  \t')
        t2 = perf_counter()        
        print(f' time= {t2-t1}',end='\t')
        print('                 ',end='\r')
    sleep(0.01)