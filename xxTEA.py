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

def decrypt(message : str, key : int) -> str:
    raise NotImplementedError("De facut ANDREI")

# test data
message = "ABCDEFG"
KEY = '0123456789012345'
print(encrypt(message, KEY))