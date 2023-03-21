import btree

def createdb(s, p, m):
    with open('db','wb') as f:
        db = btree.open(f)

        db[b'setpoint'] = b'{:.1f}'.format(s)
        db[b'periodo'] = str(p).encode()
        db[b'modo'] = str(m).encode()

        db.flush()
        db.close()

def storedb(s=None, p=None, m=None):
    with open('db','wb') as f:
        db = btree.open(f)

        if s != None:
            db[b'setpoint'] = str(s).encode()
            print('Setpoint guardado')
        if p != None:
            db[b'periodo'] = str(p).encode()
            print('Periodo guardado')
        if m != None:
            db[b'modo'] = m.encode()
            print('Modo guardado')

        db.flush()
        db.close()

def readdb():
    with open('db','rb') as f:
        db = btree.open(f)

        s = float(db[b'setpoint'].decode())
        p = float(db[b'periodo'].decode())
        m = db[b'modo'].decode()

        db.flush()
        db.close()

    return s, p, m