# coding:utf-8

from config import *
import _judger
import os
import shutil
import subprocess
from .utils import random_string


'''
参数:
    not_use  不使用,在task chain的时候会传递过来
    config_data:
        max_time 最大时间,1000毫秒
        max_memroy 最大内存,单位mb
        run_cmd   运行命令,和language_settings 有关
        env       环境变量
        rule      c_cpp
        data_dir  原始数据路径
        round_dir 运行的路径
key:in_file 输入文件
val:out_file 输出文件
count:idx  编号,第几个测试点


config_data:
    time
    memroy
    outputsize
    stack
    in      输入文件
    out     输出文件
    rule
    round_dir 运行目录
    cmp 比较器

'''
@celery.task
def run_judge(not_use,config_data,key,val,count):

    in_path = os.path.join(config_data["data_dir"], key)
    out_path = os.path.join(config_data["round_dir"], random_string(32))
    ans_path = os.path.join(config_data["data_dir"], val)
    log_path = os.path.join(config_data["round_dir"], random_string(32))
    # Prevent input errors
    if not os.path.exists(in_path):
        open(in_path, "w").close()


    result = _judger.run(**_run_args(config_data,in_path, out_path, log_path))
    
    if( (result["result"] == 0  or result["result"] == RUNTIME_ERROR  ) and
            result["memory"] > config_data["max_memory"]*1024*1024):
        result["result"]  = MEMORY_LIMIT_EXCEEDED;
    # A fake time limit / memory limit exceeded
    elif result['cpu_time'] > config_data["max_time"] or result['result'] == CPU_TIME_LIMIT_EXCEEDED \
            or result['result'] == REAL_TIME_LIMIT_EXCEEDED:
                result['cpu_time'] = config_data["max_time"]
                result['result'] = CPU_TIME_LIMIT_EXCEEDED
    elif result['result'] == MEMORY_LIMIT_EXCEEDED:
        result['memory'] = config_data["max_memory"]

    elif result['result'] == 0:
        res_judge = _result_checker(config_data,in_path,out_path,ans_path)
        # print("res_judge %d" % res_judge)
        if(res_judge !=0):
            result['result']= WRONG_ANSWER

    verdict = result['result']
    return dict(
        count=count,
        time=result['cpu_time'],
        memory=result['memory'] // 1024,
        result=verdict
    )

    # print("Running Result of " + self.lang + ": " + str(result))

'''
参数 
    config_data:
        max_time
        max_memroy
        run_cmd
        env
        rule
'''
def _run_args(config_data,in_path,out_path,log_path):
    return dict(
            max_cpu_time=config_data["max_time"],
            max_real_time= config_data["max_time"]* 3,
            max_memory=config_data["max_memory"]* 1048576 + 16*1024*1024,
            max_output_size=128 * 1024 * 1024,
            max_process_number=_judger.UNLIMITED,
            exe_path=config_data["run_cmd"][0],
            input_path=in_path,
            output_path=out_path,
            error_path=log_path,
            args=config_data["run_cmd"][1:],
            env=["PATH=" + os.getenv("PATH")] + config_data["env"],
            log_path=log_path,
            seccomp_rule_name=config_data["rule"],
            uid=RUN_USER_UID,
            gid=RUN_GROUP_GID
            )

def _result_checker(config_data,in_path,out_path,ans_path):
    running_path = os.path.join(config_data["round_dir"], 'spj')
    time_limit = int(config_data["max_time"]/ 1000 * 10)
    # print("out_path: %s" % out_path)
    # print("ans_path: %s" % ans_path)
    return subprocess.call([running_path, in_path, out_path, ans_path],stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=time_limit)
