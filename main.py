from mqtt_as import MQTTClient
from mqtt_local import config
from dbm import readdb, storedb
import uasyncio as asyncio
import ujson as json
import dht, machine, uos

# Configuracion de pines:
DHT = 13
RELE = 12
LED = 27

# sensor
d = dht.DHT22(machine.Pin(DHT))

# rele:
rele = machine.Pin(RELE,machine.Pin.OUT)
rele.value(1) # apagado (activo en bajo)

# led para destellos:
led = machine.Pin(LED,machine.Pin.OUT)
led.value(1) # apagado (activo en bajo)
D = 0.2 # tiempo de destello del led
N = 15 # numero de destellos

ID = '(SDZ)' + config['client_id'].decode()
TR = 1 # periodo de lectura de sensor

# variables globales:
DAT = {
    'temperatura':0,
    'humedad':0,
    'setpoint':26,
    'periodo':20,
    'modo':'AUTO',
    'rele':('OFF' if rele.value() else 'ON')
    }
destellar = False

###########################################################
# funciones para configuracion del cliente:
def sub_cb(topic, msg, retained):
    dtopic = topic.decode()
    dmsg = msg.decode()

    print('Topic = {} -> Valor = {}'.format(dtopic, dmsg))

    global destellar
    mod = False

    if dtopic == 'setpoint':
        try:
            DAT['setpoint'] = float(dmsg)    
            mod = True
        except OSError:
            print('El mensaje no se puede convertir a flotante')
    elif dtopic == 'periodo':
        try:
            DAT['periodo'] = float(dmsg)
            mod = True
        except OSError:
            print('El mensaje no se puede convertir a flotante')
    elif dtopic == 'modo':
        if dmsg in ('AUTO','MAN'):
            DAT['modo'] = dmsg
            mod = True
    elif dtopic == 'rele':
        if DAT['modo'] == 'MAN':
            if dmsg == 'ON':
                releOn()
            elif dmsg == 'OFF':
                releOff()
    elif dtopic == 'destello':
        destellar = (dmsg == 'ON')
    
    if mod: storedb(DAT['setpoint'],DAT['periodo'],DAT['modo'])
        
async def wifi_han(state):
    print('Wifi is', 'UP' if state else 'DOWN')
    await asyncio.sleep(1)

async def conn_han(client):
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
def releOn():
    rele.value(0)

def releOff():
    rele.value(1)

def read_sensor():
    try:
        d.measure()
        try:
            DAT['temperatura'] = d.temperature()
        except:
            print("sin sensor temperatura")
        try:
            DAT['humedad'] = d.humidity()
        except:
            print("sin sensor humedad")
    except:
        print("sin sensor")

async def dest():
    global destellar
    while True:
        if destellar:
            for i in range(N):
                led.value(0)
                await asyncio.sleep(D)
                led.value(1)
                await asyncio.sleep(D)
            destellar = False
        await asyncio.sleep(2)

async def monit():
    while True:
        read_sensor()

        if DAT['modo'] == 'AUTO':
            if DAT['temperatura'] > DAT['setpoint']:
                releOn()
            else:
                releOff()
        
        await asyncio.sleep(TR)

async def main(client):

    await client.connect()
    await asyncio.sleep(2)
    
    while True: 
        await client.publish('{}'.format(ID), json.dumps(DAT), qos = 1)

        await asyncio.sleep(DAT['periodo'])

async def master():
    await asyncio.gather(main(client), monit(), dest())


if 'db' not in uos.listdir():
    print('Base de datos NO encontrada ...creando una nueva')
    storedb(DAT['setpoint'], DAT['periodo'], DAT['modo'])
else:
    print('Base de datos encontrada ...leyendo datos')
    DAT['setpoint'], DAT['periodo'], DAT['modo'] = readdb()

try:
    asyncio.run(master())
finally:
    client.close()
    asyncio.new_event_loop()