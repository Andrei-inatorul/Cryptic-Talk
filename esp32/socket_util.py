import network
import time
import usocket as socket


def wifi_setup(hostname: str = "picosoma", ssid: str = "namnet", password: str = "amuitatparola"):
    wlan = network.WLAN(network.STA_IF)
    wlan.disconnect()  # nu stiu daca e necesara asta
    wlan.active(True)
    wlan.config(hostname=hostname)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        print("Incerc sa ma conectez la wifi...")
        time.sleep(1)
    print("M-am conectat la wifi! =^._.^=")
    myIp = network.WLAN(network.STA_IF).ifconfig()[0]
    print("Ip-ul meu:", myIp)
    return myIp


def get_addr(hostname: str):
    # ia ip din hostname
    addr_info = socket.getaddrinfo(hostname, 25565)
    return addr_info[0][-1][0]


def socket_setup(port) -> socket.socket:
    """
    Creeaza un socket pe portul ales
    :param port:
    :return: socket-ul creat
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("10.240.33.2", port))
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
    wifi_setup()
    port = 25565
    s = socket_setup(port)
    s.settimeout(2) # asteptam 2 sec daca nu primim nimic apare OSError care isi ia handle in functia de recv adica nu primim nimic
    ip = get_addr("soma.local") # asta daca ai hostname sau doar folosesti ip-ul
    print(ip)
    while True:
        try:
            data = socket_listen(s)
            if data is not None:
                print(data)
            socket_send(s, "r", (ip, port))
        except OSError:
            print("n-am gasit")
            s.close()


main()

