from base64 import encodebytes
from collections import deque
import json
import matplotlib.pyplot as plt
from pathlib import Path
import sqlite3
from subprocess import Popen, PIPE
import sys
from tornado.ioloop import IOLoop
import traceback

from IPython.display import display, Javascript

mydir = Path(__file__).parent

dbconn = sqlite3.connect('example.sqlite')
dbconn.execute('''CREATE TABLE IF NOT EXISTS thedata
        (id integer primary key autoincrement, a integer, b integer)''')

class DataReceiver:
    """Recives data from the producer process.
    
    This uses the kernels event loop to call it when there's data ready to read
    from the pipe, so it can update things without blocking the kernel from
    handling messages.
    
    To make it do things, add functions to self.callbacks .
    """
    def __init__(self, pipe, loop=None):
        self.pipe = pipe
        self.loop = loop or IOLoop.current()
        self.callbacks = []
        self.buffer = b''
        self.loop.add_handler(pipe, self.read_data, IOLoop.READ)
    
    def add_to_db(self, j):
        with dbconn:
            cursor = dbconn.execute('INSERT INTO thedata VALUES (NULL, ?, ?)',
                                    (j['a'], j['b']))
            j['id'] = cursor.lastrowid

    def read_data(self, fd=None, events=None):
        """Called when there's data ready to read from self.pipe"""
        # We might get multiple lines at once, or a read might stop in the
        # middle of a line. This ensures we handle complete lines:
        self.buffer += self.pipe.read1(1024)
        lines = self.buffer.splitlines(keepends=True)
        if lines[-1].endswith(b'\n'):
            self.buffer = b''
        else:
            self.buffer = lines.pop()
        
        # Parse JSON from each line, add the data to the database and call
        # callbacks.
        for line in lines:
            d = json.loads(line.decode('utf-8'))
            self.add_to_db(d)
            for cb in self.callbacks:
                cb(d)

def plotit(data):
    """Make a simple line plot of data"""
    ids = [d['id'] for d in data]
    a = [d['a'] for d in data]
    b = [d['b'] for d in data]

    plt.plot(ids, a, label='a')
    plt.plot(ids, b, label='b')
    plt.ylim(0, 20)
    plt.xlim(ids[0], ids[-1])
    plt.legend()

def get_range(from_id, to_id):
    cur = dbconn.execute('''SELECT * FROM thedata WHERE (id BETWEEN ? AND ?)
                    ORDER BY id''', (from_id, to_id))
    return [{'id': r[0], 'a': r[1], 'b': r[2]} for r in cur]

def show_range(from_id, to_id):
    data = get_range(from_id, to_id)
    plotit(data)
    plt.show()
    plt.close()
    return data

class LivePlotter:
    """Draw plots of recent data and send them over a comm to the Javascript.
    """
    def __init__(self):
        # self.comm = comm
        self.format = get_ipython().display_formatter.format
        self.recent = deque(maxlen=20)
    
    def update(self, datum):
        # self.comm.send(datum)
        try:
            self.recent.append(datum)
            plotit(self.recent)
            data, metadata = self.format(plt.gcf())
            self.comm.send({'png': data['image/png'],
                            'last_id': datum['id']})
            plt.close()
        except Exception as e:
            self.comm.send(str(e))
            traceback.print_exc(file=sys.__stderr__)

def init_notebook():
    """Starts the data producer, hooks up the machinery to receive and plot
    data, and sends the Javascript to connect it to the notebook.
    """
    with (mydir / 'commclient.js').open() as f:
        js_code = f.read()

    producer = Popen([sys.executable, 'producer.py'], stdout=PIPE)
    receiver = DataReceiver(producer.stdout)

    plotter = LivePlotter()
    def comm_opened(comm, msg):
        # This is called when the frontend opens a comm, a channel for us
        # to communicate with it.
        plotter.comm = comm
        receiver.callbacks.append(plotter.update)

    # Register the callback above with the kernel's comm machinery
    get_ipython().kernel.comm_manager.register_target('elogexpt', comm_opened)

    display(Javascript(js_code))
