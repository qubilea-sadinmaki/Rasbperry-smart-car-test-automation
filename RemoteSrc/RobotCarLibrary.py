#!/usr/bin/env python

from __future__ import print_function

import os
import sys
import time 
import datetime;
import pyautogui
import RPi.GPIO as GPIO

from robotremoteserver import RobotRemoteServer
from Led import Led
from Buzzer import Buzzer
from Line_Tracking import *
from Ultrasonic import *
from servo import *
from Motor import *
from ADC import *
from rpi_ws281x import *
from picamera2 import Picamera2

try:
    basestring
except NameError:   # Python 3
    basestring = str


class RobotCarLibrary(object):
    """Example library to be used with Robot Framework's remote server.

    This documentation is visible in docs generated by `Libdoc`.
    """
    LedIndexes = [0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80]
    White = [255,255,255]
    Red = [255,0,0]
    Green = [0,255,0]
    Blue = [0,0,255]
    Yellow = [255,255,0]
    Cyan = [0,255,255]
    Purple = [255,0,255]
    Black = [0,0,0]
    AllColors = [White,Red,Green,Blue,Yellow,Cyan,Purple,Black]
    picam2 = None
        
 
    def take_picture(self):
        """Takes picture. Names the picture with date & time
        Returns the file name."""
        print("Taking picture")
        if(self.picam2 == None):
           self.picam2 = Picamera2()
        dt = datetime.datetime.now()
        picName = f"{dt}.jpg"
        self.picam2.start_and_capture_file(picName)
        return picName
        
    def remote_screenshot(self,name=""):
        """Takes screenshot of remote machine. Saves it with date/time as it's name."""
        if name == "":
                dt = datetime.datetime.now()
                scrShotName = f'/ScreenShots/{dt}.png'
        else:
                scrShotName = f'/ScreenShots/{name}.png'
                
        scrShot = pyautogui.screenshot(scrShotName)
        return scrShotName
        
    def get_battery_voltage(self):
        adc = Adc()
        return adc.batteryVoltage()
   
    def test_buzzer(self, timeToBuzz):
        """Sets the Buzzer on for given given time."""
        passed = True
        buzzer = Buzzer()
        buzzer.run('1')
        
        state = buzzer.getBuzzerPinState()
        if(state):
            print('Buzzer started buzzing')
        else:
            print("Buzzer should have started buzzing!")
            
        time.sleep(int(timeToBuzz))
        
        state = buzzer.getBuzzerPinState()
        if(state):
            print(f"Buzzer was buzzing for {timeToBuzz} seconds as expected")
        else:
            print("Buzzer should be buzzing!")
            passed = False
            
        buzzer.run('0') 
        
        state = buzzer.getBuzzerPinState()
        if not(state):
            print("Buzzer was closed as expected")
        else:
            print("Buzzer should have been closed!")
            passed = False
            
        return passed
        
    def set_motors(self,leftUpper=0,leftLower=0,rightUpper=0,rightLower=0):
            """Set motors on. Parameters are leftUpper,leftLower,rightUpper,rightLower.
            If no parameters are given, then motors are set to stop."""
            motor = Motor()
            motor.setMotorModel(int(leftUpper),int(leftLower),
            int(rightUpper),int(rightLower))
            print(f"Motors set on speeds : {leftUpper},{leftLower},{rightUpper},{rightLower}")
        
    def test_motor(self, motorIndex, speed=1000):
        """Sets motor with given index to given speed.
        Compares given speed with value read from the corresponding channel of
        Raspi PCA9685 16-Channel PWM Servo Driver
        and returns the result of their match."""
        speed = int(speed)
        motorPassed = True
        motor = Motor()
        print(f"Set motor {motorIndex} to {speed}")
        channel = motor.setMotorIndex(int(motorIndex), speed)
        time.sleep(0.25)
        speedOnMotor =  motor.getMotorValue(channel)
        #Convert speed to 8-bit to compare it to the speed got from the motor.
        speed8Bit = abs(speed) & 0xFF
        
        if(speedOnMotor == speed8Bit):
            print("Speed on motor is as expected")
        else:
            print(f"Speed on motor {channel} is NOT as expected. It is {speedOnMotor}. Should be{speed8Bit}")
            motorPassed = False
        time.sleep(0.25)
        motor.setMotorModel(0,0,0,0)
        return motorPassed
        
    def test_servos(self):
        passed = True
        servo = Servo()
        print("Reset servos to center.")
        self.reset_servos()
        
        for i in [45,20,45,90,135,160,135,90]:
            servoPassed = self.test_servo(0,i, servo)
            if not(servoPassed):
                passed = False
        
        for i in [50,80,130,170,130,80]:
            servoPassed = self.test_servo(1,i, servo)
            if not(servoPassed):
                passed = False     
        
        return passed
        
    def reset_servos(self):
        """Sets camera and ultra sonic sensor to point straight ahead."""
        servo = Servo()
        print("Reset servos to center.")
        servo.setServoPwm('0',90)
        servo.setServoPwm('1',80)
        time.sleep(0.5)
        
    def test_servo(self, channel, angle, servo=None):
        """Tests that given servo rotates to given angle.
        Compares given abgle with value read from the corresponding channel of
        Raspi PCA9685 16-Channel PWM Servo Driver 
        and returns the result of their match."""
        angle = int(angle)
        if(servo == None):
            servo = Servo()
        
        servo.setServoPwm(channel, angle)
        
        angle_8_bit = servo.get8BitValue(channel, angle)
        print(f"Set servo on channel {channel} to {angle}, {angle_8_bit} on 8-bit")
        time.sleep(1)
        servo_angle_8_bit = servo.getServoPwmValue(channel)
        
        print(f"Servo angle on channel {channel} is {servo_angle_8_bit} as 8-bit value")
        return angle_8_bit == servo_angle_8_bit
        
    def get_distance_with_ultrasonic_sensor(self):
        """Tests ultrasonic sensor. Returns distance to nearest obstacle 
        in front of sensor"""
        self.reset_servos()
        print("Start ultrasonic sensor")
        ultrasonic=Ultrasonic() 
        return ultrasonic.get_distance()
        
    def test_infrared_sensor(self):
        """Tests infrared sensor. Returns if black line is under and 
        in the middle of robotcar."""
        infrared = Line_Tracking()
        return GPIO.input(infrared.IR01)!=True and GPIO.input(infrared.IR02)==True and GPIO.input(infrared.IR03)!=True
     
    def get_infrared_sensors_value(self):
        """Returns string that indicates if there is black line under sendors. Possible values are: 
        ALL, NONE, LEFT, LEFTCENTER, LEFTRIGHT, CENTER, RIGHT and RIGHTCENTER"""
        infrared = Line_Tracking()
        if(GPIO.input(infrared.IR01)==True and GPIO.input(infrared.IR02)==True and GPIO.input(infrared.IR03)==True):
                return "ALL"
        if(GPIO.input(infrared.IR01)==False and GPIO.input(infrared.IR02)==False and GPIO.input(infrared.IR03)==False):
                return "NONE"
        if(GPIO.input(infrared.IR01)==True and GPIO.input(infrared.IR02)==False and GPIO.input(infrared.IR03)==False):
                return "LEFT"
        if(GPIO.input(infrared.IR01)==True and GPIO.input(infrared.IR02)==True and GPIO.input(infrared.IR03)==False):
                return "LEFTCENTER"
        if(GPIO.input(infrared.IR01)==True and GPIO.input(infrared.IR02)==False and GPIO.input(infrared.IR03)==True):
                return "LEFTRIGHT"
        if(GPIO.input(infrared.IR01)==False and GPIO.input(infrared.IR02)==True and GPIO.input(infrared.IR03)==False):
                return "CENTER"
        if(GPIO.input(infrared.IR01)==False and GPIO.input(infrared.IR02)==False and GPIO.input(infrared.IR03)==True):
                return "RIGHT"
        if(GPIO.input(infrared.IR01)==False and GPIO.input(infrared.IR02)==True and GPIO.input(infrared.IR03)==True):
                return "RIGHTCENTER"
        
    def set_led_color(self,i,R,G,B):
        """Sets given led the given RGB color."""
        led = Led()
        led.ledIndex(i,R,G,B)
        
    def get_led_color(self,i):
        led = Led()
        return led.ledIndex(i)    
        
    def all_leds_are_white(self):
        """Tests that all leds work on color white(rgb:255,255,255) and returns the result."""
        passed = True
        led = Led()
        
        for ledIndex in self.LedIndexes:
            led.ledIndex(ledIndex,self.White[0],self.White[1],self.White[2])
            time.sleep(0.1)
         
        i = 0
        for ledIndex in self.LedIndexes:
            color = led.getLedColor(ledIndex)
            i += 1
            if(self.colors_match(color, self.White)):
                print(f'Led number {i} was white')
            else:
                print(f'COLOUR OF LED NUMBER {i} WAS {color[0]}, {color[1]}, {color[2]}. Was expecting 255, 255, 255.')
                passed = False
                
        self.close_all_leds()
            
        return passed
        
    def all_leds_have_all_colors(self):
        """Tests that all leds work on all given colors 
        (white,red,green,blue,yellow,cyan and purple)
        and returns the result."""

        passed = True
        led = Led()
        i = 0
        
        for ledIndex in self.LedIndexes:
            for color in self.AllColors:
                led.ledIndex(ledIndex,color[0],color[1],color[2])
                time.sleep(0.1)
                ledColor = led.getLedColor(ledIndex)
                i += 1
                print(f'Led number {i} color was {ledColor[0]},{ledColor[1]},{ledColor[2]}')
                if(self.colors_match(ledColor, color)):
                    print(f'Led number {i} color was {ledColor[0]}, {ledColor[1]}, {ledColor[2]} as expected.')
                else:
                    print(f'Led number {i} color was {ledColor[0]}, {ledColor[1]}, {ledColor[2]}.')
                    print(f'COLOUR SHOULD HAVE BEEN {color[0]},{color[1]},{color[2]}!')
                    passed = False
                time.sleep(0.1)
         
        return passed
    
    def close_all_leds(self):
        """Closes all leds (sets them to black)."""
        led = Led()
        for ledIndex in self.LedIndexes:
            led.ledIndex(ledIndex,0,0,0)
            
    def colors_match(self, colorA, colorB):
        """Returns the result of given colors matching."""
        return (colorA == colorB)

if __name__ == '__main__':
    RobotRemoteServer(RobotCarLibrary(), host='192.168.1.219', port=8270 )
