# coding:utf-8

from config import *
import _judger  # 导入 qjudge
import judge   # 导入 ujudge
import os
import shutil
import subprocess
from .utils import random_string,mq_emit


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
infile:in_file 输入文件
outfile:out_file 输出文件
count:idx  编号,第几个测试点


config_data:
    time
    memroy
    output_size
    judger  评测机
    in      输入文件
    out     输出文件
    rule
    judger
    round_dir 运行目录
    data_dir
    cmp 比较器
    revert
'''

@celery.task
def run_judge(not_use,config_data,infile,ansfile,count):

    in_path = os.path.join(config_data["data_dir"], infile)
    out_path = os.path.join(config_data["round_dir"], random_string(32))
    ans_path = os.path.join(config_data["data_dir"], ansfile)
    log_path = os.path.join(config_data["round_dir"], random_string(32))
    spj_path = os.path.join(config_data["round_dir"],"spj")
    ans_checker = { "details":"","exit_code":0}

    # Prevent input errors
    if not os.path.exists(in_path):
        open(in_path, "w").close()

    ## 得到
    run_args = _run_args(config_data,in_path,out_path,log_path);
    # 选择使用的评测机
    result = {}
    if config_data['judger'] == 'ujudge':
        result = judge.run_program(**run_args)
    else :  # 默认使用 qjudge
        result = _judger.run(**run_args)

    # 结果码转换
    if config_data['judger'] == 'ujudge':
        trans = [0,-1,3,1,5,5,5]
        result["result"] = trans[ result["result"] ]
        result["cpu_time"] = result["time"]
        result["real_time"] = result["time"]

    if config_data['judger'] == 'qjudge':
        result["memory"] =result["memory"] // 1024 #转成kb

    
    if( (result["result"] == 0  or result["result"] == RUNTIME_ERROR  ) and
            result["memory"] > config_data["memory"]*1024):
        result["result"]  = MEMORY_LIMIT_EXCEEDED;
    # A fake time limit / memory limit exceeded
    elif result['cpu_time'] > config_data["time"]*1000 or result['result'] == CPU_TIME_LIMIT_EXCEEDED \
            or result['result'] == REAL_TIME_LIMIT_EXCEEDED:
                # result['cpu_time'] = config_data["time"]*1000 ?
                result['result'] = CPU_TIME_LIMIT_EXCEEDED
    # elif result['result'] == MEMORY_LIMIT_EXCEEDED:
        # result['memory'] = config_data["max_memory"]

    elif result['result'] == 0:
        ans_checker  = _result_checker(spj_path,in_path,out_path,ans_path)
        # print("res_judge %d" % res_judge)
        if(ans_checker["exit_code"] !=0):
            result['result']= WRONG_ANSWER

    verdict = result['result']

    judge_ans = dict(
        status=0,
        count=count,
        mid=JUDGING,
        time=result['cpu_time'],
        memory=result['memory'],
        result=verdict,
        details=ans_checker['details'],      # 答案错误细节
        revert=config_data['revert']
    )

    mq_emit(config_data["judge_client_id"],judge_ans)
    del judge_ans["revert"]
    return judge_ans

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
    if config_data['judger'] == 'ujudge':
        arg = 'main'
        mtype = 'defalut'
        if config_data['lang'] == 'python3':
            arg = 'main.py'
            mtype = 'python3.5'
        return dict(
                tl=config_data['time'],         # second
                ml=config_data['memory']+32,    # 默认有32 mb
                ol=config_data['output_size'],
                sl=DEFAULT_STACK_LIMIT,         # 默认的stack limit
                _in=in_path,
                out=os.path.basename(out_path),
                err="/dev/null",
                work_path=config_data['round_dir'],
                _type=mtype,
                argv=[arg]
                )
    else:   # 默认使用 qjudge
        return dict(
            max_cpu_time=config_data["time"]*1000,
            max_real_time= config_data["time"]*1000+3*1000,
            max_memory=(config_data["memory"]+ 32)*1048576, # 默认有32 mb
            # max_output_size=1024 * 1024 * 1024,           # 默认输出大小
            max_output_size = config_data['output_size'] * 1048576,
            max_process_number=_judger.UNLIMITED,
            max_stack=DEFAULT_STACK_LIMIT * 1048576,
            exe_path=config_data["run_cmd"][0],
            input_path=in_path,
            output_path=out_path,
            error_path="/dev/null", # 不接收
            args=config_data["run_cmd"][1:],
            env=["PATH=" + os.getenv("PATH")] + config_data["env"],
            log_path=log_path,
            seccomp_rule_name=config_data["rule"],
            uid=RUN_USER_UID,
            gid=RUN_GROUP_GID
            )

def _result_checker(running_path,in_path,out_path,ans_path):
    # proc = subprocess.call([running_path, in_path, out_path, ans_path],stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=time_limit)
    proc = subprocess.Popen([running_path, in_path, out_path, ans_path],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        outs,errs = proc.communicate(timeout=10)
        exit_code = proc.returncode
        details = errs.decode('utf-8')
        if details == "":
            details = outs.decode('utf-8')
        return {
                'exit_code':exit_code,
                'details':details
                }
    except subprocess.TimeoutExpired:
        proc.kill()
        return {
                'exit_code':-1,
                'details':'TimeOut'
                }
    except Exception as e:
        proc.kill()
        return {
                'exit_code':-1,
                'details':e
                }

    # 这里使用 subprocess.Popen()
