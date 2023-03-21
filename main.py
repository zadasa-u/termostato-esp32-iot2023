from mqtt_as import MQTTClient
from mqtt_local import config
from dbm import createdb,readdb, storedb
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

# Constantes y etiquetas:
SPT = 30 # temperatura umbral predeterminada
PER = 20 # periodo de publicacion predeterminado
MOD = 'AUTO' # modo de funcionamiento predeterminado

D = 0.2 # tiempo de destello del led
N = 15 # numero de destellos
destellar = False

ID = '(SDZ)' + config['client_id'].decode()
#ID = '78e36d1852e0'

# defino cadenas para subtopicos:
'''
TT = '{}/temperatura'.format(ID)
TH = '{}/humedad'.format(ID)
TS = '{}/setpoint'.format(ID)
TP = '{}/periodo'.format(ID)
TM = '{}/modo'.format(ID)
TR = '{}/rele'.format(ID)
'''
###########################################################
# funciones para configuracion del cliente:
def sub_cb(topic, msg, retained):
    dtopic = topic.decode()
    dmsg = msg.decode()
    print('Topic = {} -> Valor = {}'.format(dtopic, dmsg))
    
    global spt, per, mod, destellar

    if dtopic == 'setpoint':
        try:
            spt = float(dmsg)
            storedb(s=spt,p=per,m=mod)
            eval_spt() # actualizacion instantanea de ser necesario
        except OSError:
            print('El mensaje no se puede convertir a flotante')
    elif dtopic == 'periodo':
        try:
            per = float(dmsg)
            storedb(s=spt,p=per,m=mod)
        except OSError:
            print('El mensaje no se puede convertir a flotante')
    elif dtopic == 'modo':
        if dmsg in ('AUTO','MAN'):
            mod = dmsg
            storedb(s=spt,p=per,m=mod)
            if dmsg == 'AUTO':
                #pass
                eval_spt() # actualizacion instantanea de ser necesario
    elif dtopic == 'rele':
        if mod == 'MAN':
            if dmsg == 'ON':
                # encender rele:
                rele.value(0)
            elif dmsg == 'OFF':
                # apagar el rele:
                rele.value(1)
    elif dtopic == 'destello':
        if dmsg == 'ON':
            destellar = True
        elif dmsg == 'OFF':
            destellar = False
        
async def wifi_han(state):
    print('Wifi is', 'UP' if state else 'DOWN')
    await asyncio.sleep(1)

async def conn_han(client):
    # topicos que el mismo cliente publica
    #await client.subscribe('temperatura', 1)
    #await client.subscribe('humedad', 1)

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
def eval_spt():
    '''Cuando el modo es AUTO, evalua si la temperatura
    supera el umbral fijado por setpoint para encender el rele.
    (no es asincrona pero es util para asegurar una respuesta rapida
    al recibir una actualizacion de setpoint o modo)'''
    if mod == 'AUTO' and temp > spt:
        rele.value(0) # activa rele (activo en bajo)
    else:
        rele.value(1) # desactiva rele (activo en bajo)

async def dest():
    global destellar
    while True:
        if destellar:
            # destella N veces
            for i in range(N):
                led.value(0)
                await asyncio.sleep(D)
                led.value(1)
                await asyncio.sleep(D)
            destellar = False
        await asyncio.sleep(2)

async def monit():
    global mod, temp, spt
    while True:
        if mod == 'AUTO':
            if temp > spt:
                rele.value(0) # activa rele (activo en bajo)
            else:
                rele.value(1) # desactiva rele
        await asyncio.sleep(5)

async def main(client):
    await client.connect()
    
    global temp, hum, spt, per, mod, destellar

    await asyncio.sleep(2)
    while True:
        # en caso de publicar la informacion como subtopicos:
        '''await client.publish(TT,'{}'.format(temp), qos = 1)
        await client.publish(TH,'{}'.format(hum), qos = 1)
        await client.publish(TS,'{}'.format(spt), qos = 1)
        await client.publish(TP,'{}'.format(per), qos = 1)
        await client.publish(TM,'{}'.format(mod), qos = 1)
        await client.publish(TM,'{}'.format('ON' if rele.value else 'OFF'), qos = 1)'''
        
        try:
            d.measure()
            try:
                temp=d.temperature()
                #await client.publish(TT, '{}'.format(temperatura), qos = 1)
            except OSError as e:
                print("sin sensor temperatura")
            try:
                hum=d.humidity()
                #await client.publish(TH, '{}'.format(humedad), qos = 1)
            except OSError as e:
                print("sin sensor humedad")
        except OSError as e:
            print("sin sensor")
        
        # evalua el setpoint con la ultima lectura de temperatura
        #eval_spt() # reemplazada por su contraparte asincrona: monit()

        # publicacion de datos:
        DAT = {
            'temperatura':'{:.1f}'.format(temp),
            'humedad':'{:.1f}'.format(hum),
            'setpoint':'{:.1f}'.format(spt),
            'periodo':'{:.1f}'.format(per),
            'modo':mod,
            'rele':('OFF' if rele.value() else 'ON')
            }
        JDAT = json.dumps(DAT)
        await client.publish('{}'.format(ID), JDAT, qos = 1)

        await asyncio.sleep(per)

async def master():
    await asyncio.gather(main(client), monit(), dest())

# para pruebas:
temp = 31.4
hum = 68.9
""" spt = SPT
per = PER
mod = MOD """

#storedb(SPT,PER,MOD) # crea la base de datos y almacena los valores por defecto
#spt, per, mod = SPT, PER, MOD

if 'db' not in uos.listdir():
    print('Base de datos no encontrada \n ...creando una nueva')
    createdb(SPT,PER,MOD) # crea la base de datos y almacena los valores por defecto
    spt, per, mod = SPT, PER, MOD
else:
    print('Base de datos encontrada \n ...leyendo datos')
    spt, per, mod = readdb()

try:
    #asyncio.run(main(client))
    asyncio.run(master())
finally:
    client.close()
    asyncio.new_event_loop()