Demo of live updates with the IPython kernel in Jupyter

* `client2.py` is the kernel piece, reading the data and sending updated plots on a 'comm'.
* `commclient.js` is the frontend part, displaying the plots and adding the snapshot toolbar button.
* `data.py` and `producer.py` create random data, store it in a database, and emit it as JSON.
