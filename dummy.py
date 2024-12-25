from flask import Flask,request,redirect,Response,abort,jsonify
import json
from datetime import datetime, timedelta

apikey = 'testkey'
instance = {}

app = Flask(__name__)

@app.route('/',methods=['GET'])
def status():
    if 'Authorization' not in request.headers:
        abort(404)
    if request.headers['Authorization'] != f'Token {apikey}':
        abort(404)
    if 'userid' not in request.args or int(request.args['userid']) not in instance:
        abort(404)
    expiredat = datetime.fromisoformat(instance[int(request.args['userid'])]['expiredat'])
    now = datetime.now().astimezone()
    if now > expiredat:
        del instance[int(request.args['userid'])]
        abort(404)
    return jsonify(instance[int(request.args['userid'])])

@app.route('/create',methods=['POST'])
def create():
    if 'Authorization' not in request.headers:
        abort(404)
    if request.headers['Authorization'] != f'Token {apikey}':
        abort(404)
    #url = "http://172.31.0.1:25500"
    url = "nc 172.31.0.1 25500"
    now = datetime.now().astimezone() + timedelta(minutes=5)
    #now = datetime.now().astimezone() + timedelta(seconds=10)
    if 'userid' not in request.json or request.json['userid'] in instance:
        abort(404)
    instance[request.json['userid']] = {
        #"accesspoint": f'<a href="{url}">{url}</a>',
        "accesspoint": f'<code>{url}</code>',
        "expiredat": now.isoformat(timespec='seconds')
    }
    print(instance)
    return jsonify(True)

@app.route('/destroy',methods=['POST'])
def destroy():
    if 'Authorization' not in request.headers:
        abort(404)
    if request.headers['Authorization'] != f'Token {apikey}':
        abort(404)
    if 'userid' not in request.json or request.json['userid'] not in instance:
        abort(404)
    del instance[int(request.json['userid'])]
    return jsonify(True)

@app.route('/flag',methods=['GET'])
def flag():
    if 'Authorization' not in request.headers:
        abort(404)
    if request.headers['Authorization'] != f'Token {apikey}':
        abort(404)
    return "TSC{testinstanceflag}"

#@app.route('/',methods=['GET', 'POST'])
@app.route('/<path:data>',methods=['GET', 'POST'])
def root(data=''):
    print(json.dumps({
        "request_line": f"{request.method} {request.full_path} {request.environ.get('SERVER_PROTOCOL')}",
        "headers": {key: value for key, value in request.headers.items()},
        "body": request.stream.read().decode('utf-8'),
        "environ": {key: str(value) for key, value in request.environ.items()}
    }, indent=4))
    return "com"

if __name__ == "__main__":
    app.run(host="::", port=5000)
