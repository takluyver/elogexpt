"""Receives data, stores it in a database, and handles requests for it.
"""

import asyncio
from collections import deque
import json
import sqlite3
import sys

dbconn = sqlite3.connect('example.sqlite')
dbconn.execute('''CREATE TABLE IF NOT EXISTS thedata
        (id integer primary key autoincrement, a integer, b integer)''')
recent = deque(maxlen=20)

async def pull_data():
    """Start producer.py and read the data coming from it.
    """
    proc = await asyncio.create_subprocess_exec(sys.executable, 'producer.py',
                        stdout=asyncio.subprocess.PIPE)
    while True:
        line = await proc.stdout.readline()
        j = json.loads(line.decode('utf-8'))
        with dbconn:
            cursor = dbconn.execute('INSERT INTO thedata VALUES (NULL, ?, ?)',
                                    (j['a'], j['b']))
            j['id'] = cursor.lastrowid
        print('got', j)
        recent.append(j)

async def serve_client(reader, writer):
    """Handle requests for the data."""
    while True:
        line = await reader.readline()
        j = json.loads(line.decode('utf-8'))
        print('Handle request:', j)
        if j.get('recent'):
            data = list(recent)
        else:
            cur = dbconn.execute('''SELECT * FROM thedata WHERE (id BETWEEN ? AND ?)
                            ORDER BY id''', (j['from'], j['to']))
            data = [{'id': r[0], 'a': r[1], 'b': r[2]}
                    for r in cur]
        writer.write(json.dumps(data).encode('utf-8') + b'\n')
        await writer.drain()

loop = asyncio.get_event_loop()

server = asyncio.start_unix_server(serve_client, b'\0/tmp/datademo')
loop.create_task(server)
loop.create_task(pull_data())
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
loop.close()
