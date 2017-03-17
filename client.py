import json
import matplotlib.pyplot as plt
import socket

from IPython.display import display_pretty

sock = socket.socket(socket.AF_UNIX)
sock.connect(b'\0/tmp/datademo')

def ser(d):
    return json.dumps(d).encode('utf-8') + b'\n'

def deser(b):
    return json.loads(b.decode('utf-8'))

def request(d):
    sock.sendall(ser(d))
    buf = b''
    while b'\n' not in buf:
        buf += sock.recv(4096)
    return deser(buf.split(b'\n', 1)[0])

def get_recent():
    return request({'recent': True})

def get_range(from_id, to_id):
    return request({'from': from_id, 'to': to_id})

# -------------------------------------------

def plotit(data):
    ids = [d['id'] for d in data]
    a = [d['a'] for d in data]
    b = [d['b'] for d in data]

    plt.plot(ids, a, label='a')
    plt.plot(ids, b, label='b')
    plt.ylim(0, 20)
    plt.legend()
    plt.show()
    plt.close()

def ipy_summary(idrange=None):
    if idrange is None:
        data = get_recent()
    else:
        data = get_range(*idrange)
    
    id_range = data[0]['id'], data[-1]['id']
    display_pretty("Data for range {}-{}".format(*id_range),
                    raw=True, metadata={'data_range': id_range})

    plotit(data)
    
    if idrange is None:
        print("To get this data again later, run:")
        print("    data = ipy_summary(({!r}, {!r}))".format(
                    data[0]['id'], data[-1]['id']))

    return data
