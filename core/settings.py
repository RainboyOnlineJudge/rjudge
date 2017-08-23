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

        self.r_url = data["r_url"]

        self.judger_indicator = ''
        if 'judger_indicator' in data:
            self.judger_indicator =data['judger_indicator']

        self.code = data['code']
        self.max_time = data['max_time']
        # self.max_sum_time = data['max_sum_time']
        self.max_memory = data['max_memory']
        self.problem_id = data['problem_id']
        self.round_id = round_id
        self.data_dir = os.path.join(DATA_DIR, str(self.problem_id))
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


        # 源代码

        # OS init
        if not os.path.exists(self.data_dir):
            raise FileNotFoundError
        if not os.path.exists(self.round_dir):
            os.mkdir(self.round_dir)

        os.chown(self.round_dir, COMPILER_USER_UID, COMPILER_GROUP_GID)
