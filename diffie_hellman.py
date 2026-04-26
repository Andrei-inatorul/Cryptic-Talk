import os
import random
import xTEA
import xtea_util
P = 179769313486231590770839156793787453197860296048756011706444423684197180216158519368947833795864925541502180565485980503646440548199239100050792877003355816639229553136239076508735759914822574862575007425302077447712589550957937778424442426617334727629299387668709205606050270810842907692932019128194467627007
g = 2
# https://github.com/cryptosense/diffie-hellman-groups/blob/master/gen/common.json

def power_modulo(m : int, c : int, N : int) -> int:
    s = 1
    while c > 1:
        if c % 2:
            # print(f"c = {c}")
            s = (s*m)%N
        m = (m * m) % N
        c //= 2
    return (m * s)%N

def generate_private_key():
    random_bytes = os.urandom(128)
    return int.from_bytes(random_bytes, 'big')

def generate_public_key(private_key):
    return power_modulo(g, private_key, P)

private_key = generate_private_key()
private_key2 = generate_private_key()

pk = generate_public_key(private_key)
pk2 = generate_public_key(private_key2)

shared_secret = power_modulo(pk, private_key2, P)
shared_secret2 = power_modulo(pk2, private_key, P)

print("public key    : ", private_key)
print("private key   : ", pk)

print("shared secret : ", shared_secret)
print("shared secret2: ", shared_secret2)

mask = (1 << 128) - 1
key = shared_secret & mask
key |= (1 << 127)

print(f"\n{100*"-"}\n")

print(key)
print(key.bit_length())
message = "pneumonoultramicroscopicsilicovolcaniconioza"
key = key.to_bytes(16, 'big')
print("str:", key)
print(len(key))

print(f"\n{100*"-"}\n")
c = xTEA.encrypt_message(message, key)

print("cyphertext:", c)
# -------------------------------------
d = xTEA.decrypt_message(c, key)
print("decrypt:", d)

print(f"\n{100*"-"}\n")
# key = bytes.fromhex(hex(key).replace('0x',''))
# # key = KEY.ljust(16, b'0')  # cheia 128 bits
# print("pre ljust: ", key)
# key = xtea_util.ljust(key, b'\x00', 16)
# print(key)
