import json
from pathlib import Path
import sqlite3
from subprocess import Popen, PIPE
import sys
from tornado.ioloop import IOLoop

from IPython.display import display, Javascript

mydir = Path(__file__).parent

class DataReceiver:
    def __init__(self, pipe, loop=None):
        self.pipe = pipe
        self.loop = loop or IOLoop.current()
        self.callbacks = []
        self.buffer = b''
        self.dbconn = sqlite3.connect('example.sqlite')
        self.dbconn.execute('''CREATE TABLE IF NOT EXISTS thedata
                (id integer primary key autoincrement, a integer, b integer)''')
        self.loop.add_handler(pipe, self.read_data, IOLoop.READ)
    
    def add_to_db(self, j):
        with self.dbconn:
            cursor = self.dbconn.execute('INSERT INTO thedata VALUES (NULL, ?, ?)',
                                    (j['a'], j['b']))
            j['id'] = cursor.lastrowid

    def read_data(self, fd=None, events=None):
        self.buffer += self.pipe.read1(1024)
        lines = self.buffer.splitlines(keepends=True)
        if lines[-1].endswith(b'\n'):
            self.buffer = b''
        else:
            self.buffer = lines.pop()
        
        for line in lines:
            d = json.loads(line.decode('utf-8'))
            self.add_to_db(d)
            for cb in self.callbacks:
                cb(d)

def init_notebook():
    with (mydir / 'commclient.js').open() as f:
        js_code = f.read()

    producer = Popen([sys.executable, 'producer.py'], stdout=PIPE)
    receiver = DataReceiver(producer.stdout)

    def comm_opened(comm, msg):
        
        def data_recvd(datum):
            comm.send(datum)

        receiver.callbacks.append(data_recvd)

    get_ipython().kernel.comm_manager.register_target('elogexpt', comm_opened)

    display(Javascript(js_code))
