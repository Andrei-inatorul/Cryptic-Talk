import network

def do_connect(ssid, password):
    import machine, network
    wlan = network.WLAN()
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            machine.idle()
    print('connected')
    return wlan.ipconfig('addr4')

def print_this(display, text, poz_x, line, color):
    poz_y = 0
    if (line == 1):
        poz_y = 16
    display.fill(0)
    display.show()
    display.text(text, poz_x, poz_y, color)
    display.show()