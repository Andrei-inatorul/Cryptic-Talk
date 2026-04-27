import network
import time
import usocket as socket
import XTEA
from machine import Pin, I2C
import i2c_lcd
from time import sleep_us, ticks_ms, ticks_us, sleep
import diffie_hellman as dh

"""
BUTOANE SI SMECHERII
"""

left_pressed_flag = False
right_pressed_flag = False

ltime_l = 0
ctime_l = 0

ltime_r = 0
ctime_r = 0


def left_pressed(pin):
    global ctime_l, ltime_l, left_pressed_flag
    ctime_l = ticks_ms()
    if (abs(ctime_l - ltime_l) > 40):  # debounce (aveam 3 apasari cand eu apasam doar o data)
        left_pressed_flag = True
        print("L Button Pressed!")
    ltime_l = ctime_l


def right_pressed(pin):
    global ctime_r, ltime_r, right_pressed_flag
    ctime_r = ticks_ms()
    if (abs(ctime_r - ltime_r) > 40):  # debounce (aveam 3 apasari cand eu apasam doar o data)
        right_pressed_flag = True
        print("R Button Pressed!")
    ltime_r = ctime_r


left_button = Pin(18, Pin.IN, Pin.PULL_DOWN)
right_button = Pin(26, Pin.IN, Pin.PULL_DOWN)

left_button.irq(trigger=Pin.IRQ_RISING, handler=left_pressed)
right_button.irq(trigger=Pin.IRQ_RISING, handler=right_pressed)

I2C_ADDR = 0x27
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16

i2c = I2C(sda=Pin(21), scl=Pin(22), freq=400000)

lcd = i2c_lcd.I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)


def wifi_setup(hostname: str = "picosoma", ssid: str = "namnet", password: str = "amuitatparola"):
    wlan = network.WLAN(network.STA_IF)
    #     wlan.disconnect()  # nu stiu daca e necesara asta
    wlan.active(True)
    wlan.config(hostname=hostname)
    wlan.config(pm=network.WLAN.PM_NONE)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        print("Incerc sa ma conectez la wifi...")
        time.sleep(1)
    print("M-am conectat la wifi! =^._.^=")
    myIp = network.WLAN(network.STA_IF).ifconfig()[0]
    print("Ip-ul meu:", myIp)
    return myIp, wlan


def get_addr(hostname: str):
    # ia ip din hostname
    addr_info = socket.getaddrinfo(hostname, 25565)
    return addr_info[0][-1][0]


def socket_setup(ip, port) -> socket.socket:
    """
    Creeaza un socket pe portul ales
    :param port:
    :return: socket-ul creat
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip, port))
    return sock


def socket_listen(sock):
    """
    primim mesaj (sau nu)
    """
    try:
        data = sock.recv(1024)
        return data
    except OSError:
        return None


def socket_send(sock: socket.socket, data: str, addr):
    """
    Trimite un mesaj catre adresa addr
    :param sock: socket
    :param data: mesajul (obligatoriu string/bytes) pe care vrem sa il transmitem
    :param addr: adresa la care trimitem mesajul tuple("ip", port)
    """
    assert type(data) == str or type(data) == bytes
    if type(data) == str:
        data = bytes(data, 'utf-8')
    sock.sendto(data, addr)


def main():
    ip = ""
    myip, wifi = wifi_setup()
    port = 25565
    s = socket_setup(myip, port)
    s.settimeout(
        2)  # asteptam 2 sec daca nu primim nimic apare OSError care isi ia handle in functia de recv adica nu primim nimic
    lcd.clear()
    lcd.putstr("Conectat la wifi! =^._.^=")
    #    ip = get_addr("soma.local")  # asta daca ai hostname sau doar folosesti ip-ul
    """
    START DIFFIE HELLMAN
    """
    hostname = 'minisoma.local'
    try:
        ip = get_addr(hostname)
    except OSError:
        lcd.putstr("Nu am gasit ip-ul destinatarului..")
    print(ip)
    while ip == '':
        lcd.clear()
        try:
            ip = get_addr(hostname)
        except OSError:
            lcd.putstr("Nu am gasit ip-ul destinatarului..")
        print("incerc sa gasesc ip...")
        lcd.putstr("Incerc sa gasesc ip-ul destinatarului..")
    # am ip destinatar deci pot sa incep key exchange
    private_key, public_key = dh.generate_keypair()
    lcd.clear()
    lcd.putstr("Chei generate cu succes")
    lcd.clear()
    lcd.putstr(f"Public ...{public_key % 100000}")
    lcd.move_to(0, 1)
    lcd.putstr(f"Private ...{private_key % 100000}")
    time.sleep(1)
    lcd.clear()
    lcd.putstr(f"Trimit public")
    addr = (ip, port)
    data = None
    while data is None:
        data = socket_listen(s)
    received_str = data.decode('utf-8')
    other_public = int(received_str)
    print(other_public)
    secret = dh.get_shared_secret(other_public, private_key)
    socket_send(s, str(public_key), addr)
    print("am trimis cheia publica")
    key = dh.get_key_from_shared_secret(secret)
    """
    STOP DIFFIE HELLMAN
    """
    global left_pressed_flag, right_pressed_flag
    while True:
        message = None
        if left_pressed_flag == True:
            message = XTEA.encrypt_message("LeftButtonPressed", key)
            lcd.clear()
            lcd.putstr(f"Left        <-")
            left_pressed_flag = False
        elif right_pressed_flag == True:
            message = XTEA.encrypt_message("RightButtonPressed", key)
            lcd.clear()
            lcd.putstr(f"Right       ->")
            right_pressed_flag = False
        if message is not None:
            print(message)
            socket_send(s, message, addr)
            message = None

        data = socket_listen(s)
        if data is not None:
            #             data = data.decode('utf-8')
            decrypted_message = XTEA.decrypt_message(data, key)
            decrypted_message = decrypted_message.strip('\x00')
            lcd.clear()
            lcd.putstr(decrypted_message)


main()



