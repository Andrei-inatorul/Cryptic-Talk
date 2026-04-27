import board
import busio
import adafruit_ssd1306
from time import sleep
import XTEA
from socket_util import *
from diffie_hellman import *
from zero2w.program import decrypt

GPIO.setup(board, GPIO.OUT)
i2c = busio.I2C(board.SCL, board.SDA)
display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, addr=0x3c)
display.poweron()
# Clear display
display.fill(0)
display.show()

MIN_DUTY = 1638
MAX_DUTY = 8192
STEP = 36

servo = GPIO.PWM(8, 50)

def display_text(display, text, pos):
    x = pos[0]
    y = pos[1]
    display.text(f"{text}", x, y, 1)
    display.show()
    sleep(0.01)


def main():
    servo.freq(50)
    duty = 4915

    servo.duty_u16(duty)

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
        msg = str(data)
        decrypt = XTEA.decrypt_message(msg, key)
        if decrypt == 'LeftButtonPressed':
            duty = min(MAX_DUTY, duty + STEP)
        elif decrypt == 'RightButtonPressed':
            duty = max(MIN_DUTY, duty - STEP)
        servo.duty_u16(duty)
        angle = (duty - MIN_DUTY) / STEP
        print(angle)
        display_text(display, str(angle), (0, 0))
        display.show()
        reply = XTEA.encrypt_message(str(angle), key)



try:
    main()
except KeyboardInterrupt:
    servo.stop()
    GPIO.cleanup()
    try:
        sys.exit(130)
    except SystemExit:
        os._exit(130)