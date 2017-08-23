# coding:utf-8

from core.settings import RoundSettings
from core.compile import compile
from core.judge import run_judge,_result_checker
from core.utils import import_data,randomize_round_id
file_object = open('./tests/test_src/a+b_ok.cpp')
__code = file_object.read()

__data = {
        "max_time":1000,
        "max_memory":128*1024*1024,
        "problem_id":1,
        "lang":'cpp',
        "code":__code,
        "r_url":'192.168.0.233/data'
}

print(__data)
m_set=RoundSettings(__data,'123')
# res = compile(__data,m_set.src_path,
        # m_set.compile_cmd,
        # m_set.compile_out_path,
        # m_set.compile_log_path,
        # m_set.round_dir,
        # m_set.language_settings['env']
        # )
#res = compile.delay(m_set)
res = compile.delay(__data,m_set.src_path,
        m_set.compile_cmd,
        m_set.compile_out_path,
        m_set.compile_log_path,
        m_set.round_dir,
        m_set.language_settings['env']
        )

config_data ={
        "max_time":m_set.max_time,
        "max_memory":m_set.max_memory,
        "run_cmd":m_set.run_cmd,
        "env":m_set.language_settings["env"],
        "rule":m_set.language_settings["seccomp_rule"],
        "data_dir":m_set.data_dir,
        "round_dir":m_set.round_dir,
        "judger_indicator":m_set.judger_indicator
        }
print(res)
res2 = run_judge.delay(None,config_data,"ex_input1.in","ex_output1.out",1)
print(res2.get())
