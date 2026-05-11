import board
import busio
import adafruit_ssd1306
from time import sleep
import XTEA
from socket_util import *
from diffie_hellman import *
import RPi.GPIO as GPIO
import sys

GPIO.setmode(GPIO.BCM)  # Use Broadcom pin numbering
servo_pin = 14          # Your specific pin
GPIO.setup(servo_pin, GPIO.OUT)
i2c = busio.I2C(board.SCL, board.SDA)
display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, addr=0x3c)
display.poweron()
# Clear display
display.fill(0)
display.show()

MIN_DUTY = 2.5
MAX_DUTY = 12.5
STEP = 0.5

#servo = GPIO.PWM(8, 50)
servo = GPIO.PWM(servo_pin, 50)
servo.start(7.5)

def display_text(display, text, pos):
    x = pos[0]
    y = pos[1]
    display.text(f"{text}", x, y, 1)
    display.show()
    sleep(0.01)


def main():
    duty = 7.5
    servo.ChangeDutyCycle(duty)
    s = socket_setup(25565)
    """
    START DIFFIE HELLMAN
    """
    ip = ''
    port = 25565
    try:
        ip = get_addr("picosoma.local")
    except OSError:
        print("Nu am gasit ip-ul destinatarului..")
    while ip == '':
        try:
            ip = get_addr("soma.local")
        except OSError:
            print("Nu am gasit ip-ul destinatarului..")
        print("incerc sa gasesc ip...")
    #am ip destinatar deci pot sa incep key exchange
    private_key, public_key = generate_keypair()
    print("Chei generate cu succes")
    print(f"Public ...{public_key%100000}")
    print(f"Private ...{private_key%100000}")
    print(f"Trimit public")
    print(ip)
    addr = (ip, port)
    socket_send(s, str(public_key), addr)
    print("am trimis cheia publica")

    data = None
    while data is None:
        data = socket_listen(s)
    received_str = data.decode('utf-8')
    other_public = int(received_str)
    print(other_public)
    secret = get_shared_secret(other_public, private_key)
    key = get_key_from_shared_secret(secret)
    """
    STOP DIFFIE HELLMAN
    """
    while True:
        display.fill(0)
        data = None
        while data is None:
            data = socket_listen(s)
        msg = data.decode('utf-8')
        decrypt = XTEA.decrypt_message(msg, key)
        decrypt = decrypt.strip('\x00')
        print(decrypt)
        IV = os.urandom(6)
        if decrypt == 'LeftButtonPressed':
            print("l")
            duty = min(MAX_DUTY, duty + STEP)
        elif decrypt == 'RightButtonPressed':
            print("r")
            duty = max(MIN_DUTY, duty - STEP)
        duty = round(duty, 2)
        servo.ChangeDutyCycle(duty)
        angle = (duty - MIN_DUTY) * (180 / (MAX_DUTY - MIN_DUTY))
        angle = round(angle, 1)
        print(duty)
        display_text(display, str(angle), (0, 0))
        display.show()
        reply = XTEA.encrypt_message(str(angle), key, IV)
        IV = bytes.fromhex(reply[16:32])
        socket_send(s, reply, addr)


try:
    main()
except KeyboardInterrupt:
    servo.stop()
    GPIO.cleanup()
    try:
        sys.exit(130)
    except SystemExit:
        os._exit(130)
