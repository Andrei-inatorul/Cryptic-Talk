import socket
import xTEA


def get_addr(hostname):
    """
    Preia ip-ul folosind hostname
    :param hostname: string reprezentand hostname-ul pt care vrem ip-ul
    :return: ip
    """
    return socket.gethostbyname(hostname)

def socket_setup(port) -> socket.socket:
    """
    Creeaza un socket pe portul ales
    :param port:
    :return: socket-ul creat
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", port))
    return sock

def socket_listen(sock: socket.socket) -> bytes:
    """
        Asteapta un mesaj si il returneaza.
        Dimensiunea mesajului este de 1024 octeti.
        Mesajul returnat e de tip bytes.
    """
    return sock.recv(1024)

def socket_send(sock: socket.socket, data: str, addr):
    """
    Trimite un mesaj catre adresa addr
    :param sock: socket
    :param data: mesajul (obligatoriu string) pe care vrem sa il transmitem
    :param addr: adresa la care trimitem mesajul tuple("ip", port)
    """
    assert type(data) == str
    data = bytes(data, 'utf-8')
    sock.sendto(data, addr)

ip = get_addr("picosoma.local")#"10.240.33.112"#get_addr("picosoma.local") #

s = socket_setup(25565)
msg = xTEA.encrypt_message("AAAA", xTEA.KEY)
socket_send(s, msg, (ip, 25565))
print("am trimis")
print(socket_listen(s))