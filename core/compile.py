# coding:utf-8

from config import *
import shutil
import _judger
import os
from .post import post_data
from .utils import read_partial_data_from_file,mq_emit


@celery.task
def compile(
        code,        # 代码
        data_dir,    # 数据的目录
        round_dir,   # 运行的目录
        judge_client_id, # 返回的socket client id
        _cmp,       # 文本比较器
        revert,          # 返回的数据
        src_path,        # 源代码路径
        compile_cmd,     # 编译的 args
        compile_out_path, # 输出路径
        compile_log_path, # log 路径
        language_settings          # 针对各个语言的env
        ):
    
    # 编译 代码

    # 写入代码
    with open(src_path, 'w', encoding='utf-8') as f:
        f.write(code)

    compile_code_res={}
    if compile_cmd[0] == '/usr/bin/fpc':
        compile_code_res["status"] = os.system(" ".join(compile_cmd))
    else:
        compile_code_res = __compile__(
                compile_cmd = compile_cmd,
                round_dir = round_dir,
                src_path = src_path,
                compile_out_path=compile_out_path,
                compile_log_path=compile_log_path,
                language_settings = language_settings,
                revert= revert
            )
    if compile_code_res['status'] != 0: # 错误
        compile_code_res['message'] = '代码编译失败';
        compile_code_res['err_code'] = 1
        mq_emit(judge_client_id,compile_code_res)
        raise Exception('code compile error')

    # 统计 spj
    running_path = os.path.join(round_dir, 'spj')
    spj_path = ''
    round_spj_src_path = ''
    extname = os.path.splitext(_cmp)[1]  #cpp
    if extname == '.cpp':  #cpp
        spj_path=os.path.join(data_dir,_cmp)
        round_spj_src_path= running_path+extname
    elif extname == '':  #无后缀
        spj_path =os.path.join(TESTLIB_BUILD_DIR,_cmp)
    else :
        mq_emit(judge_client_id,{
            'status':-1,
            'mid':COMPILING,
            'err_code':2,
            'message':'还不支持这种文件比较器:'+_cmp,
            'revert':revert
            })
        raise Exception('do not support this cmp:'+_cmp +' yet!');

    # 复制 spj
    if os.path.exists(spj_path):
        if extname == '':
            shutil.copyfile(spj_path,running_path)
        else:
            shutil.copyfile(spj_path,round_spj_src_path)
    else :
        mq_emit(judge_client_id,{
            'status':-1,
            'mid':COMPILING,
            'err_code':3,
            'message':'文件比较器不存在:'+_cmp,
            'revert':revert
            })
        raise Exception('cmp not exists');

    # 判断是否要编译
    compile_spj_res = {'status':0,'mid':COMPILING,'revert':revert}
    if extname == '.cpp':
        compile_spj_res = __compile__(
            compile_cmd=['/usr/bin/g++','-o',running_path,round_spj_src_path],
            round_dir=round_dir,
            compile_out_path=os.path.join(round_dir,'spj.out'),
            compile_log_path=os.path.join(round_dir,'spj.log'),
            src_path=round_spj_src_path,
            language_settings=[],
            revert = revert
            )

    if compile_spj_res['status'] != 0:
        compile_spj_res['message'] = '编译spj失败'
        compile_spj_res['err_code'] = 4
        mq_emit(judge_client_id,compile_spj_res)
        raise Exception('spj compile error!');
    #  编译结束

    os.chmod(running_path, 0o755)

    # 发送编译成功的信息
    mq_emit(judge_client_id,{
        'status':0,
        'message':'编译代码成功',
        'mid':COMPILING,
        'revert':revert
        })
    return

# 编译的包装
def __compile__(
        compile_cmd=[],
        round_dir='',
        compile_out_path='',
        compile_log_path='',
        src_path='',
        language_settings='',
        revert={}
        ):
    # print(compile_cmd)
    # print(["PATH=" + os.getenv("PATH")] + language_settings)
    res = {}
    if compile_cmd[0] == '/usr/bin/fpc':
        res = judge.run_program(
                tl=10,   # time_limit 单位s 
                ml=512, # memory_limit 单位 mb
                ol=128, # output_limit 单位 mb
                sl=512, # stack limit 单位 mb
                _in="/dev/null",  # 输入文件
                out=compile_out_path, # 输出文件
                err=compile_out_path, # 错误输出
                work_path=round_dir, # 工作目录
                _type="default", # type default or python3.5
                show_trace_details=False, # 显示详细的信息
                allow_proc=False,         #  允许 fork exec
                unsafe=True,             #  不安全模式
                argv=compile_cmd,        # 运行的程序名
                add_readable_raw=""
                )
    else:
        res = _judger.run(
            max_cpu_time=5000,
            max_real_time=10000,
            max_memory=_judger.UNLIMITED,
            max_output_size=128 * 1024 * 1024,
            max_process_number=_judger.UNLIMITED,
            exe_path=compile_cmd[0],
            # /dev/null is best, but in some system, this will call ioctl system call
            input_path=src_path,
            output_path=compile_out_path,
            error_path=compile_out_path,
            args=compile_cmd[1:],
            env=["PATH=" + os.getenv("PATH")] + language_settings,
            log_path=compile_log_path,
            seccomp_rule_name=None,
            uid=COMPILER_USER_UID,  # not safe?
            gid=COMPILER_GROUP_GID
            )

    if res['result']!= 0 :
        payload = { 'status':-1,'mid':COMPILING,'verdict':COMPILE_ERROR, 'details':'N/A' ,'revert':revert}
        if os.path.exists(compile_out_path):
            payload['details'] = read_partial_data_from_file(compile_out_path)
            if payload['details'] == '' and os.path.exists(compile_log_path):
                payload['details'] = read_partial_data_from_file(compile_log_path)
            payload['details'] = payload['details'].replace(round_dir, '~')
        return payload
    else:
        return {'status':0,'revert':revert}
