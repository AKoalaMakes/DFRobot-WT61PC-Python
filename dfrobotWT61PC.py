#   Adapted from https://github.com/DFRobotdl/DFRobot_WT61PC

#   Packet format looks like this in hex:
#   55,51,ae,ff,0c,00,12,08,78,08,f9
#   55,52,00,00,00,00,00,00,78,08,27
#   55,53,43,00,87,01,6d,01,6a,42,8d
#   55,54,00,00,00,00,00,00,00,00,00

#   where each byte represents
#   0       1       2       3       4       5       6       7       8       9       10 
#   start   header  X-Low  X-High   Y-Low  Y-High   Z-Low  Z-High   ??      ??      checksum

#   Start is always 55
#   header is 1 of 4 possibilities 
#       81 = accelleration
#       82 = Gyro
#       83 = Angle
#       84 = Unknown
#   X-Y-Z data is 16-bit signed little endian
#   Unknown what the 4th byte pairs are for, the origonal code does not specify

#   ---------------------------------------------------------------------------
#   Note windows has a legacy serial mouse detection that operates on every serial port
#   when it is enumerated by default.  Strange feature that shouldn't exist yet it means 
#   any serial mouse from 25+ years ago will work on both Windows 3.0 and Windows 11

#   This is CORRECTLY disabled in Device Manager->COMx Porperties->Port Serrings->Advanced Settings
#       Look for 'Serial Enumerator' and uncheck it
#   ---------------------------------------------------------------------------

import serial

HEADERACC = 81          #packet header for accelleration data, 0x51 in hex
HEADERGYRO =  82        #packet header for gyro, 0x52 in hex
HEADERANGLE = 83        #packet data for angle, 0x53 in hex
HEADER55 = 85           #main packet header, 0x55 in hex or 85 in dec

#   Contructor needs target port passed, EG DFRobot_WT61PC('COM5') or DFRobot_WT61PC('/dev/AMA1')
class DFRobot_WT61PC:
    def __init__(self, serialPort):
        self._port = None
        try:
            self._port = serial.Serial(serialPort, 9600, timeout = 1, write_timeout = 1)
        except BaseException as ex:
            print(f"Failed to open {serialPort}: {str(ex)}")     
            self._port = None
        self._accel = [0,0,0]
        self._gyro = [0,0,0]
        self._angle = [0,0,0]


    def accel(self):
        return self._accel
        
        
    def gyro(self):
        return self._gyro
    
    
    def angle(self):
        return self._angle


    def getPacket(self):
        if self._port.in_waiting > 0:
            c = bytearray(b'')
            for i in range(11):
                c += port.read()
        return count

    
    #read and decode data from sensor
    def recieveData(self):   
        buff = bytearray(b'')
        while(True):        
            buff = self._port.read(1)
            if int.from_bytes(buff, "little") == 0: return buff     #got nothing so exit 
            if int.from_bytes(buff, "little") == HEADER55:          #got packet header, next bytes will be data
                break
        buff += self._port.read(10)
        if len(buff) == 11:                                         #helps deal with edge cases like unplugging the sensor
            if self.getCS(buff[:10]) == int.from_bytes(buff[10:11],"little"):
                return buff
            else: return b''
        return b'' 


    #Find Checksum, checksum is sum of al 11 bytes truncated to 8-bit integer
    def getCS(self, data):
        cs = 0
        for i in data:
            cs = cs + i
        cs = cs % 256
        return cs


    #check if there is data to update from
    def available(self):
        if self._port is not None:
            if self._port.in_waiting >= 44: #wait for at least 4 packets worth, incleases latency but significantly decreases blocking time
                for i in range(4):
                    data = self.recieveData()
                    if int.from_bytes(data[1:2], "little") == HEADERACC:
                        self._accel = self.getAcc(data)
                    elif int.from_bytes(data[1:2], "little") == HEADERGYRO:
                        self._gyro = self.getGyro(data)
                    elif int.from_bytes(data[1:2], "little") == HEADERANGLE:
                        self._angle = self.getAngle(data)
                    else:
                        pass
                    return True
        return False    


    #decode data to meaningful numbers, data packets are little Endian, Accel and Gyro are signed, Angle is not
    def getAcc(self, data):
        accX = int.from_bytes(data[2:4], "little", signed=True) / 32768 * 16 * 9.8
        accY = int.from_bytes(data[4:6], "little", signed=True) / 32768 * 16 * 9.8
        accZ = int.from_bytes(data[6:8], "little", signed=True) / 32768 * 16 * 9.8
        return list([accX, accY, accZ])


    def getGyro(self, data):
        gyroX = int.from_bytes(data[2:4], "little", signed=True) / 32768 * 2000
        gyroY = int.from_bytes(data[4:6], "little", signed=True) / 32768 * 2000
        gyroZ = int.from_bytes(data[6:8], "little", signed=True) / 32768 * 2000
        return list([gyroX, gyroY, gyroZ])


    def getAngle(self, data):
        angleX = int.from_bytes(data[2:4], "little", signed=False) / 32768 * 180 
        angleY = int.from_bytes(data[4:6], "little", signed=False) / 32768 * 180 
        angleZ = int.from_bytes(data[6:8], "little", signed=False) / 32768 * 180 
        return list([angleX, angleY, angleZ])


    #send command to update frequency of device
    #Freqnuency range has 11 settings set as a byte from 0 to 11, this 
    def selectFreq(self,freq):
        if freq < 0 or freq > 11:
            return False
        msg = b'\xff\xaa\x03'                   #raw frequence change message
        msg += freq.to_bytes(1, "little")       #append new freqnency
        msg += b'x00'                           #append terminator
        port.write(msg)
        return True
        
        