# Servidor basico para mantener el bot online

from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return 'Hola, estoy vivo'

def run():
  app.run(host = '0.0.0.0', port = 8080)

def keep_alive():
  t = Thread(target = run)
  t.start()