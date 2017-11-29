# encoding: utf-8
import os
from config import *
from .languages import LANGUAGE_SETTINGS
from config import COMPILER_USER_UID, COMPILER_GROUP_GID
from .utils import emit_to_one
from config import *

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

        self.judge_client_id = data['judge_client_id']
        self.revert = None
        if "revert" in  data:
            self.revert = data["revert"]

        
        # 文件比较器
        self.cmp= 'fcmp2'
        if 'cmp' in data:
            self.cmp =data['cmp']

        self.code = data['code']
        self.time = data['time']
        self.memory = data['memory']
        self.judge_id = data['judge_id']
        self.round_id = round_id
        # 数据目录
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
            max_memory=self.memory
        ).split(' ')

        # 源代码

        # OS init
        if not os.path.exists(self.data_dir):
            emit_to_one(self.judge_client_id,{
                "status":-1,
                "mid":PREPARE_JUDGE,
                "message":'数据文件夹没有找到'
                })
            raise FileNotFoundError
        if not os.path.exists(self.round_dir):
            os.mkdir(self.round_dir)

        os.chown(self.round_dir, COMPILER_USER_UID, COMPILER_GROUP_GID)
