# coding:utf-8

from celery import group
from .settings import RoundSettings
from .judge import run_judge
from .post import post_data
from .compile import compile
from .utils import import_data,randomize_round_id


class Handler(object):

    def __init__(self,data,round_id):
        '''
        param data  包括:
            r_url:数据返回的地址,http-post 方法,具体看doc中设计
            language: c,cpp,pas
            code:评测代码
            setting:评测的相关设定
                max_time:
                max_memory:
        '''
        self.settings  = RoundSettings(data,round_id)
        pass

    #评测
    def run(self):
        data_set = import_data(self.settings.data_dir)

        __data = {
                "code":self.settings.code,
                "r_url":self.settings.r_url,
                "data_dir":self.settings.data_dir,
                "round_dir":self.settings.round_dir,
                "judger_indicator":self.settings.judger_indicator,
                "revert":self.settings.revert
        }
        __data2 = {
                "max_time":self.settings.max_time,
                "max_memory":self.settings.max_memory,
                "run_cmd":self.settings.run_cmd,
                "env":self.settings.language_settings["env"],
                "rule":self.settings.language_settings["seccomp_rule"],
                "data_dir":self.settings.data_dir,
                "round_dir":self.settings.round_dir,
                "judger_indicator":self.settings.judger_indicator,
                "revert":self.settings.revert
                }

        ss = [run_judge.s(__data2,key,val,idx)
                          for idx, (key, val) in enumerate(data_set, start=1)]
        cc = compile.s(
                __data,
                self.settings.src_path,
                self.settings.compile_cmd,
                self.settings.compile_out_path,
                self.settings.compile_log_path,
                self.settings.round_dir,
                self.settings.language_settings['env'])|group(ss)|post_data.s(self.settings.r_url,self.settings.revert)
        cc()
