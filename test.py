import xTEA_esp32 as xtea
import os

mesaj = 'mesajsecret'
iv = os.urandom(8)
key = b'0123456789012345'
print("iv rand:", iv)
cr = xtea.encrypt_message(mesaj, key, iv)
print("cr", cr)
iv = bytes.fromhex(cr[:16])
print("iv from cr:", iv)
print("cr:", cr)
dc = xtea.decrypt_message(cr, key)
print("dc :", dc)
for i in range(20):
    print(f"============Tura {i}============")
    cr = xtea.encrypt_message(mesaj, key, iv)
    iv = bytes.fromhex(cr[16:32])
    print("iv:", iv)
    print("cr:", cr)
    dc = xtea.decrypt_message(cr, key)
    print("dc :", dc)