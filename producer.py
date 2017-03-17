"""Generates random data for the demo."""

import json
import random
import sys
import time

while True:
    j = {'a': random.randint(0, 10), 'b': random.randint(5, 20)}
    print(json.dumps(j))
    sys.stdout.flush()
    time.sleep(0.5)
