import RPi.GPIO as GPIO
from time import sleep
import sys
import os
import board
import busio
import adafruit_ssd1306
from time import sleep

#display
i2c = busio.I2C(board.SCL, board.SDA)
display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, addr=0x3c)

def clear_screen(display):
    display.fill(0)
    display.show()
    sleep(0.01)

def display_text(display, text, pos):
    x = pos[0]
    y = pos[1]
    display.text(f"{text}", x, y, 1)
    display.show()
    sleep(0.01)


#GPIO.setmode(GPIO.BOARD)
GPIO.setup(board, GPIO.OUT)
servo = GPIO.PWM(8, 50)

servo.start(7.5)
sleep(1)
def main():
    while True:
        duty = 5.0
        while(duty <= 10):
            servo.ChangeDutyCycle(duty)
            display.fill_rect(3, 3, 3+round(((duty-5)/5)*32), 6, 1)
            display.show()
            sleep(1)
            duty+=0.5


try:
    main()
except KeyboardInterrupt:
    servo.stop()
    GPIO.cleanup()
    try:
        sys.exit(130)
    except SystemExit:
        os._exit(130)