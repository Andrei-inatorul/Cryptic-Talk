import board
import busio
import adafruit_ssd1306
from time import sleep
# Create the I2C interface using the Pi's hardware I2C pins
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize the display (Address 0x3C is standard)
display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, addr=0x3c)

display.poweron()
# Clear display
display.fill(0)
display.show()

import struct
DELTA = 0x9E3779B9
MASK = 0XFFFFFFFF


def encrypt(message : str, key: str, nr_rounds=32) -> str:
    # Prepare key and message with fixed sizes + padding with '0'
    #padding is made in the front of the text/key!!
    key = KEY.rjust(16, '0').encode() # 128 bits
    message = message.rjust(8, '0') # 64 bits

    # split message to left and right
    right = int.from_bytes(message[0:4].encode('utf-8'), 'little')
    left = int.from_bytes(message[4:8].encode('utf-8'), 'little')


    key = struct.unpack('4I', key) # split the key in 4 mini keys of 32 bit -> 4 int
    sum = 0
    for i in range(nr_rounds):
        right = (right + ((((left << 4) ^ (left >> 5)) + left) ^
                          (sum + int(key[sum & 3])))) & MASK
        sum = (sum + DELTA) & MASK
        left = (left + ((((right << 4) ^ (right >> 5)) + right) ^
                        (sum + int(key[(sum >> 11) & 3])))) & MASK
    # concat of the two halves
    cipher_bytes = right.to_bytes(4, 'little') + left.to_bytes(4, 'little')
    # cipher in hex
    cipher_hex = cipher_bytes.hex()
    return cipher_hex

def decrypt(cypher: str, key : str, nr_rounds:int =32) -> str: # chinul meu existential am pus v0 in loc de v1 undeva si crapa T-T acu e ok
    key = key.rjust(16, '0').encode()
    key = [int.from_bytes(key[0:4], 'little'), int.from_bytes(key[4:8], 'little'),
           int.from_bytes(key[8:12], 'little'), int.from_bytes(key[12:16], 'little')]

    cypher = bytes.fromhex(cypher)
    v0 = int.from_bytes(cypher[0:4], 'little')
    v1 = int.from_bytes(cypher[4:8], 'little')

    sum = (DELTA * nr_rounds) & MASK

    for _ in range(nr_rounds):
        v1 = (v1 - ((((v0 << 4) ^ (v0 >> 5)) + v0) ^ (sum + int(key[(sum >> 11) & 3])))) & MASK
        sum = (sum - DELTA) & MASK
        v0 = (v0 - ((((v1 << 4) ^ (v1 >> 5)) + v1) ^ (sum + int(key[sum & 3])))) & MASK

    message_bytes = v0.to_bytes(4, 'little') + v1.to_bytes(4, 'little')
    message_bytes.rstrip(b'\x00')
    return message_bytes.decode('utf-8')


# test data
message = "CORNELIU" # BUG daca pui mai putin iti da 0 in fata la decodat. Vezi: A
                     # BUG daca pui unicode ? ? iti papa o litera. Vezi: ab?iguit
                     # daca pui emoji crapa la decode (cine ar fi creezut). Vezi: ??
                     # Momentan daca ii dai "pneumonoultramicroscopicsilicovolcaniconioza" iti cripteaza doar pneumono and this is sad

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


while True:
    message = input()
    message = message.strip()
    clear_screen(display)
    display_text(display, message, (0, 0))
    print("text: ", message)
    KEY = '0123456789012345'
    c = encrypt(message, KEY)
    print("cyphertext: ", c)
    display_text(display, c, (0, 16))
    print("decrypred text: ", decrypt(c, KEY))

