import btree

""" def createdb(spt, per, mod):
    with open('db','wb') as f:
        db = btree.open(f)

        db[b'setpoint'] = spt.encode()
        db[b'periodo'] = per.encode()
        db[b'modo'] = mod.encode()

        db.close() """

def storedb(spt, per, mod):
    with open('db','wb') as f:
        db = btree.open(f)

        db[b'setpoint'] = str(spt).encode()
        db[b'periodo'] = str(per).encode()
        db[b'modo'] = mod.encode()

        db.close()

def readdb():
    with open('db','rb') as f:
        db = btree.open(f)

        spt = float(db[b'setpoint'].decode())
        per = float(db[b'periodo'].decode())
        mod = db[b'modo'].decode()

    return spt, per, mod