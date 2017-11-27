# encoding: utf-8
import os
from config import *
from .languages import LANGUAGE_SETTINGS
from config import COMPILER_USER_UID, COMPILER_GROUP_GID


class RoundSettings:

    def __init__(self, data, round_id):
        """
        :param data: should include:
        max_time, max_sum_time, max_memory, problem_id
        lang
        code
        r_url
        :param round_id: round id
        """




        self.revert = None
        if "revert" in  data:
            self.revert = data["revert"]

        
        # 文件比较器
        self.cmp= ''
        if 'cmp' in data:
            self.cmp =data['cmp']

        self.code = data['code']
        self.time = data['time']
        self.memory = data['memory']
        self.judge_id = data['judge_id']
        self.round_id = round_id
        self.data_dir = os.path.join(DATA_DIR, str(self.judge_id))
        # 执行代码的目录
        self.round_dir = os.path.join(ROUND_DIR, str(self.round_id))

        self.language_settings = LANGUAGE_SETTINGS[data['lang']]
        # self.run_dir = self.settings.round_dir

        # Ready to make some files
        self.src_name = self.language_settings['src_name']
        self.exe_name = self.language_settings['exe_name']
        self.src_path = os.path.join(self.round_dir, self.src_name)
        self.exe_path = os.path.join(self.round_dir, self.exe_name)

        # Compilation related
        self.compile_out_path = os.path.join(self.round_dir, 'compile.out')
        self.compile_log_path = os.path.join(self.round_dir, 'compile.log')
        self.compile_cmd = self.language_settings['compile_cmd'].format(
            src_path=self.src_path,
            exe_path=self.exe_path,
        ).split(' ')

        # Running related
        self.seccomp_rule_name = self.language_settings['seccomp_rule']
        self.run_cmd = self.language_settings['exe_cmd'].format(
            exe_path=self.exe_path,
            # The following is for Java
            exe_dir=self.round_dir,
            exe_name=self.exe_name,
            max_memory=self.max_memory
        ).split(' ')

        # 生成传递给 不同judge的 参数
        # self.judge_args
        self.judge_args = {}
        if data['judger'] == 'qjudge' :
            slef.judge_args['max_cpu_time'] = ''
            slef.judge_args['max_real_time'] = ''
        elif data['judger'] == 'ujudge' :
            pass

        # 源代码

        # OS init
        if not os.path.exists(self.data_dir):
            raise FileNotFoundError
        if not os.path.exists(self.round_dir):
            os.mkdir(self.round_dir)

        os.chown(self.round_dir, COMPILER_USER_UID, COMPILER_GROUP_GID)
