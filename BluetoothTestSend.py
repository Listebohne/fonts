import bluetooth

def send_data():
    target_address = "B8:27:EB:E8:B0:A9"  # Bluetooth-Adresse des Raspberry Pi
    port = 1

    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.connect((target_address, port))

    message = "Hello from Android"
    sock.send(message)
    sock.close()

if __name__ == "__main__":
    send_data()
