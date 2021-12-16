import socket
import time
import math

# connects
def connect():
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.connect(('192.168.99.215',23))
    soc.setblocking(0)
    return soc

# converts buffer data to int
def to_int(data):
    val = 0
    iter = 0

    buf = data.decode('utf-8')
    while iter < len(buf) and buf[iter].isdigit():
        val = val*10 + int(buf[iter])
        iter = iter + 1
    
    return val

def read_sensor(soc, cmd):
    # clears any late new lines etc
    try:
        dat = soc.recv(1024)
    except:
        pass

    # sends command to bot
    soc.sendall(cmd)

    # empty buffer of reply
    data = b''

    # tries to get reply
    for i in range(3):
        try:
            dat=soc.recv(1024)

            if dat:
                data=data+dat # adds to buffer
            else:
                time.sleep(0.1) # sleeps if we don't got anything new
        except:
            time.sleep(0.1) # waits if theres an exception
        
    val = to_int(data)
    return val

