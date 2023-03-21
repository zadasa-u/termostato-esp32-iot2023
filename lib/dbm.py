import btree

def storedb(spt, per, mod):
    with open('db','wb') as f:
        db = btree.open(f)

        try:
            db[b'setpoint'] = str(spt).encode()
            db[b'periodo'] = str(per).encode()
            db[b'modo'] = mod.encode()
        except:
            print('Error en los tipos de datos')

        db.flush()
        db.close()

def readdb():
    with open('db','rb') as f:
        db = btree.open(f)

        try:
            str = float(db[b'setpoint'].decode())
            per = float(db[b'periodo'].decode())
            mod = db[b'modo'].decode()
        except:
            print('Clave/s no encontrada/s')

        db.flush()
        db.close()

    return str, per, mod