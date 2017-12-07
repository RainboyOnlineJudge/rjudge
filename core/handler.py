# coding:utf-8

from celery import group
from .settings import RoundSettings
from .judge import run_judge
from .post import post_data
from .compile import compile
from config import *
from .utils import import_data,randomize_round_id,emit_to_one



class Handler(object):

    def __init__(self,data,round_id):
        '''
        param data  包括:
            r_url:数据返回的地址,http-post 方法,具体看doc中设计
            language: c,cpp,pas
            code:评测代码
            setting:评测的相关设定
        '''
        # 初始化设定
        self.settings  = RoundSettings(data,round_id)
        pass

    #评测
    def run(self):
        # 测试数据是否正确
        data = import_data(self.settings.data_dir)
        # print(data)
        

        if data['status']!= 0:
            data['mid'] = PREPARE_JUDGE
            data['revert'] = self.settings.revert
            emit_to_one(self.settings.judge_client_id,data)
            return 

        # 返回数据长度
        emit_to_one(self.settings.judge_client_id,{
            'status':0,
            'message':'评测数据正常',
            'data':data['result'],
            'mid':PREPARE_JUDGE,
            'revert':self.settings.revert
            })
        
        # for debug 输出 round dir
        print(self.settings.round_dir)

        for_compile_data = {
                "code":self.settings.code,
                "data_dir":self.settings.data_dir,
                "round_dir":self.settings.round_dir,
                "judge_client_id":self.settings.judge_client_id,
                "cmp":self.settings.cmp,
                "revert":self.settings.revert
        }
        for_judge_data = {
                "time":self.settings.time,
                "memory":self.settings.memory,
                "output_size":self.settings.output_size,
                "judger":self.settings.judger,
                "run_cmd":self.settings.run_cmd,
                "env":self.settings.language_settings["env"],
                "rule":self.settings.language_settings["seccomp_rule"],
                "data_dir":self.settings.data_dir,
                "round_dir":self.settings.round_dir,
                "cmp":self.settings.cmp,
                "judge_client_id":self.settings.judge_client_id,
                "revert":self.settings.revert
        }

        groups = [run_judge.s(for_judge_data,key,val,idx)
                          for idx, (key, val) in enumerate(data, start=1)]
        # task_series = compile.s(
                # for_compile_data,
                # self.settings.src_path,
                # self.settings.compile_cmd,
                # self.settings.compile_out_path,
                # self.settings.compile_log_path,
                # self.settings.round_dir,
                # self.settings.language_settings['env'])
                # |group(ss)|post_data.s(self.settings.r_url,self.settings.revert)
        task_series = compile.s(
                self.settings.code, #code
                self.settings.data_dir,#data_dir
                self.settings.round_dir,#round_dir
                self.settings.judge_client_id,
                self.settings.cmp,
                self.settings.revert,
                self.settings.src_path,
                self.settings.compile_cmd,
                self.settings.compile_out_path,
                self.settings.compile_log_path,
                self.settings.language_settings['env']
                ) | group(groups) |post_data(self.settings.judge_client_id,self.settings.revert)
        task_series()
