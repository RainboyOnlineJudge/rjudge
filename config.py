from multiprocessing import cpu_count
from celery import Celery
from flask import Flask

import grp
import os
import pwd

# Judge server directories

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TESTLIB_BUILD_DIR = os.path.join(BASE_DIR, 'testlib/build')
JUDGE_BASE_DIR = '/judge_server'
JUDGE_BASE_DIR_PAST = '/judge_server_past'

ROUND_DIR = os.path.join(JUDGE_BASE_DIR, 'round')
DATA_DIR = os.path.join(JUDGE_BASE_DIR, 'data')
TMP_DIR = os.path.join(JUDGE_BASE_DIR, 'tmp')

RUN_USER_UID = pwd.getpwnam("nobody").pw_uid
RUN_GROUP_GID = grp.getgrnam("nogroup").gr_gid

COMPILER_USER_UID = pwd.getpwnam("compiler").pw_uid
COMPILER_GROUP_GID = grp.getgrnam("compiler").gr_gid

# Important! Code meaning!
# ERROR_CODE < 0: FORGIVEN
WRONG_ANSWER = -1
ACCEPTED = 0
# ERROR_CODE > 0: TERMINATION ERROR
CPU_TIME_LIMIT_EXCEEDED = 1
REAL_TIME_LIMIT_EXCEEDED = 2
MEMORY_LIMIT_EXCEEDED = 3
RUNTIME_ERROR = 4
SYSTEM_ERROR = 5
COMPILE_ERROR = 6
IDLENESS_LIMIT_EXCEEDED = 7
SUM_TIME_LIMIT_EXCEEDED = 8


# MID 值
PREPARE_JUDGE   =0
START_JUDGE     =1
AYANALIYSE_DATA =2
COMPILE_COMLETE =3
JUDGING         =4
END_JUDGE       =5



# socket respone message ID

START_JUDGE=1


app = Flask(__name__)
app.config['broker_url'] = 'redis://localhost:6379/0'
app.config['result_backend'] = 'redis://localhost:6379/0'
# app.config['imports'] = ['core.judge', 'core.post', 'core.compile']
app.config['imports'] = ['core.judge', 'core.post', 'core.compile']
app.config['worker_concurrency'] = max(cpu_count(), 1)

celery = Celery(app.name, broker=app.config['broker_url'])
celery.conf.update(app.config)
