from machine import Pin, I2C
import ssd1306
from util import do_connect
from config import AP_PASSWORD, AP_SSID, PORT_SEND, PORT_RCV
import socket

# oled -> addr = 0x3C
i2c = I2C(sda=Pin(21), scl=Pin(22))
display = ssd1306.SSD1306_I2C(128, 32, i2c)

# display on display :DDDD
# display.text('Hello, World!', 0, 0, 1)
# display.show()

ip, mask = do_connect(AP_SSID, AP_PASSWORD)  # connect through wifi + addr1 -> my ip + mask :D

addr_send = (ip, PORT_SEND)  # adrr trimitere
addr_rcv = (ip, PORT_RCV)  # adrr primire

# socket trimitere
# socket_send = socket.socket()
# socket_send.connect(addr_rcv)

# socket primire neblocant
socket_rcv = socket.socket()
socket_rcv.bind(addr_rcv)

# socket_send.send(b'ceva')

# while True:
#      data = socket_rcv.recv(4)
#      print(str(data, 'utf8'), end='')



