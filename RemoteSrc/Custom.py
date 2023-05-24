import time
from picamera2 import Picamera2
from Led import *
from Motor import *
from Buzzer import *
from RobotCarLibrary import *
from robotremoteserver import RobotRemoteServer

class Custom:
    def __init__(self):
        self.led=Led()
        self.motor=Motor()
        self.buzzer=Buzzer()
    
    def spin(self, speed=2000, mod=1, spinTime=4):
        self.motor.setMotorModel(mod*speed,mod*speed,mod*-speed,mod*-speed)
        time.sleep(spinTime)
        self.motor.setMotorModel(0,0,0,0)
    
    def startSignal(self):
        for x in range(3):
            self.beep(0.0625)
            time.sleep(0.0625)
        
        time.sleep(0.125)
        
        for x in range(3):
            self.beep(0.0625)
            time.sleep(0.0625)
            
    def beep(self, beepTime=4):
        self.buzzer.run('1')
        time.sleep(beepTime)
        self.buzzer.run('0')
        
    def spinRun(self):
        self.startSignal()
        self.spin(2000)
        self.startSignal()
        self.spin(2000, -1)
        
    def takePicture(self):
        picam2 = Picamera2()
        picam2.start_and_capture_file("test.jpg")
        
# Main program logic follows:
if __name__ == '__main__':
    rcLib = RobotRemoteServer(RobotCarLibrary(), host='192.168.1.219', port=8270 )
    keywordNames = rcLib.get_keyword_names()
    print(keywordNames)
    
