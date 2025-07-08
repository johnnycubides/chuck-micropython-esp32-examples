import time
import network
from machine import Pin, ADC, UART
from client import Client

# NETWORK
SSID = "luna"
PASSWORD = "samus.com"
# MQTT DEFINITIONS
OSC_SERVER = "192.168.2.105"
OSC_PORT = 9001
CLIENT_ID = "/piano"
TOPIC_KEYBOARD = CLIENT_ID + "/teclado"
TOPIC_ADC = CLIENT_ID + "/pedal"
TOPIC_UART = CLIENT_ID + "/uart"
# PERIPHERALS DEFINITIONS
LED_PIN = 2
BUTTON_PIN = 0
ADC_PIN = 32
TX_PIN = 17
RX_PIN = 16
BAUDRATE = 57600  # 9600 57600 115200

# Make objects for peripherals
led = Pin(LED_PIN, Pin.OUT)
adc = ADC(ADC_PIN)
user_button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)
uart_fpga = UART(2, baudrate=BAUDRATE, tx=17, rx=16)


def connectSTA(ssid, pwd):
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print("connecting to network...")
        sta_if.active(True)
        sta_if.connect(ssid, pwd)
        while not sta_if.isconnected():
            pass
    print("network config:", sta_if.ifconfig())


def get_osc_format(array):
    if array[0] == "i":  # si formato integer
        return int(array[1])
    elif array[0] == "f":  # si formato flotante
        return float(array[1])
    else:  # "s" es string
        return array[1]


# Función principal
def main():
    # 1. Conectarse a una RED WIFI
    connectSTA(SSID, PASSWORD)
    # 2. Configurar el cliente OSC
    osc_client = Client(OSC_SERVER, OSC_PORT)
    print("Configurando cliente OSC")

    while True:
        print("waiting")
        # 4. Verificar si se ha pulsado el botón
        if user_button.value() == 0:
            adc_value = adc.read()
            print(adc_value)
            osc_client.send(TOPIC_ADC, adc_value)
        # 5. Verificar si se ha recibido datos por UART
        if uart_fpga.any():
            buffer = uart_fpga.read().decode("utf-8")
            #               0       1       2       3           4           5 ...
            # decoder = ["osc", "topic", "format", "value1", "format", "value2", ... ]
            decoder = buffer.split(" ")
            print(decoder)
            if decoder[0] == "osc":
                size = len(decoder)
                if size == 4:  # topic más un valor con formato
                    osc_client.send(decoder[1], get_osc_format(decoder[2:4]))
                if size == 6:  # topic más dos valores con formato
                    osc_client.send(
                        decoder[1],
                        get_osc_format(decoder[2:4]),
                        get_osc_format(decoder[4:6]),
                    )
                if size == 8:  # topic más tres valores con formato
                    osc_client.send(
                        decoder[1],
                        get_osc_format(decoder[2:4]),
                        get_osc_format(decoder[4:6]),
                        get_osc_format(decoder[6:8]),
                    )
                if size == 10:  # topic más cuatro valores con formato
                    osc_client.send(
                        decoder[1],
                        get_osc_format(decoder[2:4]),
                        get_osc_format(decoder[4:6]),
                        get_osc_format(decoder[6:8]),
                        get_osc_format(decoder[8:10]),
                    )
        # 6. Esperar un tiempo antes de hacer el loop
        time.sleep(0.1)


if __name__ == "__main__":
    main()
