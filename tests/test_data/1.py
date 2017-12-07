import os
import re
import shutil


src = '/home/judgetest/rjudge/tests/test_data/aplusb'


re_num = re.compile('\d+');
re_input = re.compile('input')


datalist = os.listdir(src)

for _file in datalist:
    name = 'aplusb'
    num = re_num.search(_file).group(0)
    if re_input.search(_file):
        name = name+num +'.in'
    else:
        name = name+num +'.out'
    shutil.move(os.path.join(src,_file),os.path.join(src,name))
