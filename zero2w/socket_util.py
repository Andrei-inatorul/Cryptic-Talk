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

# ip = get_addr("picosoma.local")#"10.240.33.112"#get_addr("picosoma.local") #
# print(ip)
# s = socket_setup(25565)
# socket_send(s, "179769313486231590770839156793787453197860296048756011706444423684197180216158519368947833795864925541502180565485980503646440548199239100050792877003355816639229553136239076508735759914822574862575007425302077447712589550957937778424442426617334727629299387668709205606050270810842907692932019128194467627007", (ip, 25565))
# print("trimis")
# while(1):
#     data = socket_listen(s)
#     print(data) if data is not None else print(".", end="")