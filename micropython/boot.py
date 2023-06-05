from machine import Pin, PWM, ADC
from machine import Timer
from time import sleep_ms, sleep
import ubluetooth
import gc

# Mac address: a0:b7:65:4b:16:58
pot=ADC(Pin(25))
pot.atten(ADC.ATTN_11DB)
led=Pin(18, Pin.IN)
led.value(1)
servo=PWM(Pin(5))
servo.freq(50)
ble_msg = ""
speaker=PWM(Pin(14))
speaker.freq(700)
speaker.duty_u16(0)

class ESP32_BLE():
    def __init__(self, name):
        # Create internal objects for the onboard LED
        # blinking when no BLE device is connected
        # stable ON when connected
        self.led = Pin(2, Pin.OUT)
        self.timer1 = Timer(0)
        
        self.name = name
        self.ble = ubluetooth.BLE()
        self.ble.active(True)
        self.disconnected()
        self.ble.irq(self.ble_irq)
        self.register()
        self.advertiser()

    def connected(self):
        global speaker
        self.led.value(1)
        self.timer1.deinit()
        speaker.freq(800)
        speaker.duty_u16(60000)
        sleep(0.2)
        speaker.freq(900)
        sleep(0.3)
        speaker.freq(700)
        speaker.duty_u16(0)
        print("Connected")

    def disconnected(self):        
        self.timer1.init(period=100, mode=Timer.PERIODIC, callback=lambda t: self.led.value(not self.led.value()))
        speaker.freq(900)
        speaker.duty_u16(60000)
        sleep(0.2)
        speaker.freq(800)
        sleep(0.3)
        speaker.freq(700)
        speaker.duty_u16(0)
        print("Disconnected")

    def ble_irq(self, event, data):
        global ble_msg
        
        if event == 1: #_IRQ_CENTRAL_CONNECT:
                       # A central has connected to this peripheral
            self.connected()

        elif event == 2: #_IRQ_CENTRAL_DISCONNECT:
                         # A central has disconnected from this peripheral.
            self.advertiser()
            self.disconnected()
        
        elif event == 3: #_IRQ_GATTS_WRITE:
                         # A client has written to this characteristic or descriptor.          
            buffer = self.ble.gatts_read(self.rx)
            ble_msg = buffer.decode('UTF-8').strip()
            
    def register(self):        
        # Nordic UART Service (NUS)
        NUS_UUID = '6E400001-B5A3-F393-E0A9-E50E24DCCA9E'
        RX_UUID = '6E400002-B5A3-F393-E0A9-E50E24DCCA9E'
        TX_UUID = '6E400003-B5A3-F393-E0A9-E50E24DCCA9E'
            
        BLE_NUS = ubluetooth.UUID(NUS_UUID)
        BLE_RX = (ubluetooth.UUID(RX_UUID), ubluetooth.FLAG_WRITE)
        BLE_TX = (ubluetooth.UUID(TX_UUID), ubluetooth.FLAG_NOTIFY)
            
        BLE_UART = (BLE_NUS, (BLE_TX, BLE_RX,))
        SERVICES = (BLE_UART, )
        ((self.tx, self.rx,), ) = self.ble.gatts_register_services(SERVICES)

    def send(self, data):
        self.ble.gatts_notify(0, self.tx, data + '
')

    def advertiser(self):
        name = bytes(self.name, 'UTF-8')
        adv_data = bytes([0x02, 0x01, 0x02]) + bytes([len(name) + 1, 0x09]) + name
        self.ble.gap_advertise(100, adv_data)
        print(adv_data)
        print("rn")


ble=ESP32_BLE("Rocket base")
measure=False
while True:
    sleep_ms(100)
    if measure:
        val=pot.read()-2235
        valcent=(val*100)/310
        ble.send("Measure: "+str(round(valcent*100)/100)+"%")
        with open("measures", "a") as f:
            f.write(str(round(valcent*100)/100)+"|")
    if ble_msg:
        print(ble_msg)
        if "launch" in ble_msg:
            timer=int(ble_msg.replace("launch", ""))
            ble_msg = ""
            if timer > 0:
                for i in range(timer):
                    if not ble_msg == "cancel":
                        ble.send("-"+str(timer-i))
                        print(timer-i)
                        l=True
                        speaker.duty_u16(60000)
                        sleep(0.3)
                        speaker.duty_u16(0)
                        sleep(0.7)
                        
                    else:
                        ble.send("Launch cancelled by operator")
                        l=False
                        break
                if l:
                    ble.send("Ignition")
                    led=Pin(18, Pin.OUT)
                    speaker.freq(1000)
                    speaker.duty_u16(60000)
                    sleep(0.3)
                    speaker.freq(700)
                    speaker.duty_u16(0)
                    sleep(0.7)
                    for i in range(10):
                        ble.send("+"+str(i+1))
                        sleep(1)
                    led=Pin(18, Pin.IN)
                    for i in range(11):
                        ble.send("+"+str(i+11))
                        sleep(1)
            else:
                ble.send("Error: cannot recognize countdown with time "+str(timer))
        elif ble_msg == "mem":
            memoria_restante = gc.mem_free()
            ble.send(str(memoria_restante))
        elif ble_msg == "on":
            led=Pin(18, Pin.OUT)
            ble.send("Turned on relay on pin 18")
            speaker.duty_u16(60000)
            sleep(0.3)
            speaker.duty_u16(0)
        elif ble_msg == "off":
            led=Pin(18, Pin.IN)
            ble.send("Turned off relay off pin 18")
            speaker.duty_u16(60000)
            sleep(0.3)
            speaker.duty_u16(0)
        elif ble_msg == "startMeasure":
            measure=True
            with open("measures", "a") as f:
                f.write("")
        elif ble_msg == "stopMeasure":
            measure=False
        else:
            ble.send("Error: unknown command: "+ble_msg)
        ble_msg = ""
