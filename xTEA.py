import secrets
import struct
from typing import Tuple

DELTA = 0x9E3779B9
MASK = 0XFFFFFFFF


def encrypt_64b(message: int, key: str, nr_rounds = 32) -> str:
    # pregatire cheie si mesaj -> daca nu au lungimea destul de mare => padding la final
    key = KEY.ljust(16, '0').encode() # cheia 128 bits
    # print(key)
    message_bytes = message.to_bytes(8, 'little')

    right = int.from_bytes(message_bytes[0:4], 'little')
    left = int.from_bytes(message_bytes[4:8], 'little')

    key = struct.unpack('4I', key) # split the key in 4 mini keys of 32 bit -> 4 int
    sum = 0
    for i in range(nr_rounds):
        right = (right + ((((left << 4) ^ (left >> 5)) + left) ^
                          (sum + int(key[sum & 3])))) & MASK # v0
        sum = (sum + DELTA) & MASK
        left = (left + ((((right << 4) ^ (right >> 5)) + right) ^
                        (sum + int(key[(sum >> 11) & 3])))) & MASK # v1
    # concatenarea celor doua parti
    cipher_bytes = right.to_bytes(4, 'little') + left.to_bytes(4, 'little')
    # cipher in hex
    cipher_hex = cipher_bytes.hex()
    return cipher_hex

def encrypt(message: str, key: str, nr_rounds = 32) -> str: # cu CBC

    # if(len(message) <= 8): # daca avem doar 8 caractere
    #     # message = message.encode('utf-8'), 'little'
    #     return encrypt_64b(message,key,nr_rounds) # mesajul poate fi criptat direct

    IV = secrets.token_bytes(8) # 8 biti random :D
    last_encrypted_chunk = hex(int.from_bytes(IV, 'little')) # intializam cu IV
    encrypted_message = "" + IV.hex()  # in prima bucata avem initialization vector
    print("IV:",IV)

    message_chuncks = [message[i : i + 8]for i in range(0, len(message), 8)] # despartim mesajul in bucati de cate 64 biti
    for i in message_chuncks:
        msg_chunk_padded = i.ljust(8, '0')  # daca chunck-ul nu e complet este completat cu 0
        msg_chunk_int = int.from_bytes((msg_chunk_padded.encode('utf-8')), 'little') # si il transformam in bytes

        xored = msg_chunk_int ^ int(last_encrypted_chunk,16)
        print("XORED", xored)
        encrypted_chunk = encrypt_64b(xored, key, nr_rounds) # criptam bucata curenta
        encrypted_message += encrypted_chunk # adaugam rezultatul la cel final
        last_encrypted_chunk = "0x" + encrypted_chunk


    return encrypted_message


def decrypt(cypher: str, key : str, nr_rounds:int = 32) -> str: # chinul meu existential am pus v0 in loc de v1 undeva si crapa T-T acu e ok
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
    return message_bytes.decode('latin-1')


# test data
message = "CORNELI" # BUG daca pui mai putin iti da 0 in fata la decodat. Vezi: A
                     # BUG daca pui unicode ț ș iti papa o litera. Vezi: abțiguit
                     # daca pui emoji crapa la decode (cine ar fi creezut). Vezi: 🥰
                     # Momentan daca ii dai "pneumonoultramicroscopicsilicovolcaniconioza" iti cripteaza doar pneumono and this is sad
print("text: ", message)
KEY = '0123456789012345'
c = encrypt(message, KEY)
print("cyphertext: ", c)
#----------------------------------------------------------------------------
# iv = bytes.fromhex(c[:16])
# c1 = c[16:]
# decrypted = decrypt(c1, KEY)
#
# print(decrypted)