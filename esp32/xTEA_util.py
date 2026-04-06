def rjust(message: str, ch: str, length: int) -> str:
    return message + ch * (length - len(message))

def ljust(message, ch, length) -> str:
    return ch * (length - len(message)) + message

def lstrip(message, ch):
    for i in range (len(message)):
        if message[i] != ch:
            break
    message = message[i:]
    return message

def rstrip(message, ch):
    for i in range (len(message) - 1, 0, -1):
        if message[i] != ch:
            break

    message = message[0:i+1]
    return message

