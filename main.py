from mqtt_as import MQTTClient
from mqtt_local import config
import uasyncio as asyncio
import dht, machine


# Configuracion de pines:
DHT = 13
RELE = 12
LED = 27

# sensor
d = dht.DHT22(machine.Pin(DHT))

# rele:
rele = machine.Pin(RELE,machine.Pin.OUT)

# led para destellos:
led = machine.Pin(LED,machine.Pin.OUT)

# Constantes y etiquetas:
SPT = 30 # temperatura umbral predeterminada
PER = 20 # periodo de publicacion predeterminado
MOD = 'AUTO' # modo de funcionamiento predeterminado

D = 1 # tiempo de destello del led

ID = config['client_id']

# defino cadenas para subtopicos:
TT = '{}/temperatura'.format(ID)
TH = '{}/humedad'.format(ID)
TS = '{}/setpoint'.format(ID)
TP = '{}/periodo'.format(ID)
TM = '{}/modo'.format(ID)

###########################################################
# funciones para configuracion del cliente:
def sub_cb(topic, msg, retained):
    print('Topic = {} -> Valor = {}'.format(topic.decode(), msg.decode()))

async def wifi_han(state):
    print('Wifi is ', 'up' if state else 'down')
    await asyncio.sleep(1)

async def conn_han(client):
    # topicos que el mismo cliente publica
    #await client.subscribe(TT, 1)
    #await client.subscribe(TH, 1)

    # topicos para comando remoto del termostato:
    await client.subscribe('setpoint', 1)
    await client.subscribe('periodo', 1)
    await client.subscribe('modo', 1)
    
    await client.subscribe('destello', 1)
    await client.subscribe('rele', 1)

# Define configuracion del cliente
config['subs_cb'] = sub_cb
config['connect_coro'] = conn_han
config['wifi_coro'] = wifi_han
config['ssl'] = True

# Inicia cliente
MQTTClient.DEBUG = True
client = MQTTClient(config)

###########################################################
# funciones generales
async def main(client):
    await client.connect()
    
    global temp, hum, spt, per, mod

    # para pruebas:
    temp = 41
    hum = 61
    spt = SPT
    per = PER
    mod = MOD

    n = 1

    await asyncio.sleep(2)
    while True:
        print(f'    n = {n}')
        n+=1
        #await client.publish(TT,'{}'.format(temp), qos = 1)
        #await client.publish(TH,'{}'.format(hum), qos = 1)
        #await client.publish(TS,'{}'.format(spt), qos = 1)
        #await client.publish(TP,'{}'.format(per), qos = 1)
        #await client.publish(TM,'{}'.format(mod), qos = 1)

        '''try:
            d.measure()
            try:
                temperatura=d.temperature()
                await client.publish(TT, '{}'.format(temperatura), qos = 1)
            except OSError as e:
                print("sin sensor temperatura")
            try:
                humedad=d.humidity()
                await client.publish(TH, '{}'.format(humedad), qos = 1)
            except OSError as e:
                print("sin sensor humedad")
        except OSError as e:
            print("sin sensor")'''
        
        await asyncio.sleep(per)

try:
    asyncio.run(main(client))
finally:
    client.close()
    asyncio.new_event_loop()