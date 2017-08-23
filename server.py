import shortuuid
import platform
import uuid
import traceback
import shutil
from flask import request, jsonify
from core.handler import Handler
from config import *
from core.utils import randomize_round_id

PORT = 4999

@app.route('/')
def hello_world():
    return 'Hello World!'

def verify_token(data):
    try:
        with open('token.txt') as f:
            TOKEN = f.read().strip()
            if not TOKEN:
                return True
            if data == TOKEN:
                return True
            return False
    except (FileNotFoundError, KeyError):
        return False


@app.route('/reset', methods=['GET'])
def reset_token():
    return 'hello world'


@app.route('/judge', methods=['POST'])
def server_judge():
    round_id = randomize_round_id()
    token = request.headers.get('Token')
    if not verify_token(token):
        return jsonify({'status':-1,message:"illegal token"})
    __data = request.get_json()
    hh=Handler(__data,round_id)
    hh.run()
    return jsonify({"message":"ok"})


@app.route('/info', methods=['GET'])
def server_info():

    result = {'status': 'received', 'error': 'not responding'}
    token = request.headers.get('Token')
    if not verify_token(token):
        return jsonify({'status':-1,message:"illegal token"})

    try:
        # System Information
        result['system'] = ', '.join(platform.uname())

        cpu_info = []
        with open('/proc/cpuinfo') as f:
            for line in f:
                if line.strip():
                    if line.rstrip('\n').startswith('model name'):
                        model_name = line.rstrip('\n').split(':')[1]
                        cpu_info.append(model_name.strip())
        result['cpu'] = ', '.join(cpu_info)

        mem_info = []
        with open('/proc/meminfo') as f:
            for line in f:
                if line.strip():
                    if line.rstrip('\n').startswith('MemTotal'):
                        mem_total = line.rstrip('\n').split(':')[1]
                        mem_info.append(mem_total.strip())
        result['memory'] = ', '.join(mem_info)

        result['cpp'] = os.popen('g++ --version').readline().strip()

        result['java'] = ''
        java_info_path = os.path.join(TMP_DIR, str(uuid.uuid1()))
        if os.system('java -version 2> ' + java_info_path) == 0:
            with open(java_info_path, 'r') as f:
                java_info = []
                for line in f:
                    if line.strip():
                        java_info.append(line.strip())
                result['java'] = ', '.join(java_info)
        os.remove(java_info_path)

        result['python'] = os.popen('python3 --version').readline().strip()

        if len(os.popen('ps aux | grep redis | grep -v grep').readlines()) == 0:
            raise Exception('Redis is not running')
        if len(os.popen('ps aux | grep celery | grep -v grep').readlines()) == 0:
            raise Exception('Celery is not running')

        result['status'] = 'ok'
        result['error'] = ''
    except Exception as e:
        result['status'] = 'failure'
        result['error'] = str(e)
    return jsonify(result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=False)
