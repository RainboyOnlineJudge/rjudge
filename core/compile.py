# coding:utf-8

from config import *
import shutil
import _judger
import os
from .post import post_data
from .utils import read_partial_data_from_file

'''
编译code,
编译/复制spj
参数:
    config_data:
        code 代码
        r_url post的地址
    src_path 生成的代码路径
    compile_cmd 编译命令数组
    compile_out_path  std输出的路径
    compile_log_path  judgelog路径
    run_dir  代码运行的路径
    env 环境变量
    revert 返回的数据
'''
@celery.task
def compile(config_data,src_path,c_cmd,c_out_path,c_log_path,run_dir,env):
    code = config_data["code"]
    r_url = config_data["r_url"]
    compile_cmd = c_cmd
    compile_out_path = c_out_path
    compile_log_path = c_log_path
    
    # 写入代码
    with open(src_path, 'w', encoding='utf-8') as f:
        f.write(code)

    res = _judger.run(
            max_cpu_time=5000,
            max_real_time=10000,
            max_memory=-1,
            max_output_size=128 * 1024 * 1024,
            max_process_number=_judger.UNLIMITED,
            exe_path=compile_cmd[0],
            # /dev/null is best, but in some system, this will call ioctl system call
            input_path=src_path,
            output_path=compile_out_path,
            error_path=compile_out_path,
            args=compile_cmd[1:],
            env=["PATH=" + os.getenv("PATH")] + env,
            log_path=compile_log_path,
            seccomp_rule_name=None,
            uid=COMPILER_USER_UID,  # not safe?
            gid=COMPILER_GROUP_GID
            )

    if res['result']!= 0 :
        payload = { 'verdict':COMPILE_ERROR, 'message':'N/A' }
        if os.path.exists(compile_out_path):
            payload['message'] = read_partial_data_from_file(compile_out_path)
            if payload['message'] == '' and os.path.exists(compile_log_path):
                payload['message'] = read_partial_data_from_file(compile_log_path)
            payload['message'] = payload['message'].replace(run_dir, '~')
        post_data(payload,r_url,config_data["revert"])
        raise Exception('compile error!')
    # _file_checher 这里只运行一遍
    _file_checher(config_data,run_dir)

#设置spj,file checher 

def _file_checher(config_data,round_dir):
    running_path = os.path.join(round_dir, 'spj')

    indicator = config_data["judger_indicator"]
    if indicator == '':
        indicator = 'fcmp'
    search_path = [TESTLIB_BUILD_DIR, config_data["data_dir"]]

    # 复制 
    for path in search_path:
        if indicator in os.listdir(path):
            shutil.copyfile(os.path.join(path, indicator), running_path)
            break
    # 如果上面没有复制,默认就复制 fcmp
    if not os.path.exists(running_path):
        try:
            shutil.copyfile(os.path.join(TESTLIB_BUILD_DIR, 'fcmp'), running_path)
        except OSError:
            print('Judge seems to be not installed?')
            raise OSError

    os.chmod(running_path, 0o755)
