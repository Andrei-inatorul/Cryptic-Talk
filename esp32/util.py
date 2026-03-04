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



