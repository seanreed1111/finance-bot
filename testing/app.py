
import os, time
from pathlib import Path
import redis
from flask import Flask
from dotenv import load_dotenv

app = Flask(__name__)
cache = redis.Redis(host='redis', port=6379)
load_dotenv('/run/secrets/MyDeploymentSecret')

def get_hit_count():
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0: raise exc
            retries -= 1
            time.sleep(0.5)

@app.route('/secret')
def secret():
#    return f"{Path.cwd()} \n {os.system('cat /run/secrets/MyDeploymentSecret')}"
    return os.getenv('EMBEDDING_DEPLOYMENT_NAME')

@app.route('/')
def hello():
    count = get_hit_count()
    return 'Hello World! I have been seen {} times.\n'.format(count)
