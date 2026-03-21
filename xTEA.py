import secrets
import struct
from pydoc import plaintext
from typing import Tuple

DELTA = 0x9E3779B9
MASK = 0XFFFFFFFF

#----------------------------------------------------------ENCRYPT----------------------------------------------------------------------

def encrypt_64b(message: int, key: str, nr_rounds = 32) -> str:
    # pregatire cheie si mesaj -> daca nu au lungimea destul de mare => padding la final
    key = key.ljust(16, '0').encode() # cheia 128 bits

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

def encrypt_message(message: str, key: str, nr_rounds = 32) -> str: # cu CBC
    IV = secrets.token_bytes(8) # 64 biti random :D
    last_chunk_int = int.from_bytes(IV, 'little') # intializam cu IV in int

    encrypted_message = IV.hex()  # initialization vector necriptat in fata la rezultatul final

    if len(message) % 8 != 0:
        message = message.ljust((len(message) // 8 + 1) * 8, '\0') #adaugam zero-uri la sfarsit data e necesar
    message_chuncks = [message[i : i + 8]for i in range(0, len(message), 8)] # despartim mesajul in bucati de cate 64 biti

    for i in message_chuncks:
        msg_chunk_int = int.from_bytes((i.encode('utf-8')), 'little') # si il transformam in bytes
        xored = msg_chunk_int ^ last_chunk_int
        # print("XORED", xored)
        encrypted_hex = encrypt_64b(xored, key, nr_rounds) # criptam bucata curenta
        encrypted_message += encrypted_hex # adaugam rezultatul la cel final
        last_chunk_int = int.from_bytes(bytes.fromhex(encrypted_hex), 'little')
    return encrypted_message


#----------------------------------------------------------DECRYPT----------------------------------------------------------------------

def decrypt_64b(cypher: str, key : str, nr_rounds:int = 32) -> int: # chinul meu existential am pus v0 in loc de v1 undeva si crapa T-T acu e ok
    key = key.ljust(16, '0').encode()
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

    return (v1 << 32) | v0 # concatenam si returnam ca int :D

def decrypt_message(encryted_message: str, key: str):
    iv = encryted_message[0:16]
    iv_int = int.from_bytes(bytes.fromhex(iv), 'little')
    plaintext = ""
    last_chunk_int = iv_int

    message_chuncks = [encryted_message[i: i + 16] for i in
                       range(16, len(encryted_message), 16)]  # despartim mesajul in bucati de cate 64 biti(hex = 4 biti caracterul -> 64 / 4 = 16 T-T)
    # print(message_chuncks)
    for i in message_chuncks:
        decrypted_chunk = decrypt_64b(i,key)
        plain_chunk = decrypted_chunk ^ last_chunk_int
        plaintext += plain_chunk.to_bytes(8, 'little').decode('utf-8').rstrip('\0')
        last_chunk_int = int.from_bytes(bytes.fromhex(i), 'little')

    return plaintext

#-----------------------------------------------------------TEST------------------------------------------------------------------------
# test data
message = "pneumonoultramicroscopicsilicovolcaniconioza"   # BUG daca pui unicode ț ș iti papa o litera. Vezi: abțiguit
                 # daca pui emoji crapa la decode (cine ar fi creezut). Vezi: 🥰
#
# f = open("shrek.txt")
# message=f.read()

#09ca6f9ed30dca69
print("text: ", message)
KEY = '0123456789012345'
#------------------------------------
c = encrypt_message(message, KEY)
print("cyphertext:",c)
#-------------------------------------
d = decrypt_message(c,KEY)
print("decrypt:", d)