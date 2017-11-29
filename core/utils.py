import uuid
import os
import re
import random
import string
import chardet
from flask_socketio import emit


def import_data(path):
    infile_re = ['.in$','.input$','.txt$']
    outfile_re  = ['.out$','.output$','.ans$','.answer']

    raw_file_list = os.listdir(path)
    raw_file_set = set(raw_file_list)

    result = []

    # 为空

    real_infile_re=None
    # choose in_file_re
    for in_re in infile_re:
        infile_pattern = re.compile(in_re,re.I)
        for infile in raw_file_list:
            if infile_pattern.search(infile) is not None:
                real_infile_re = infile_pattern
                break;
        if real_infile_re != None :
            break;
    
    if real_infile_re == None :  # 没有找到
        return {
                'status':-1,
                'message':'没有找到in文件',
                'datalist':raw_file_list
                }


    for in_file in raw_file_list:
        if infile_pattern.search(in_file) is not None:
            raw_file_set.remove(in_file)
            out_file=''
            for outfile in raw_file_set:
                if( os.path.splitext(outfile)[0] == os.path.splitext(in_file)[0]):
                    out_file = outfile
                    result.append([in_file,outfile])
                    break
            # print(out_file)
            if out_file != '':
                raw_file_set.remove(outfile)

    # print(result)
    # 按字典 infile序排序
    return {
            'status':0,
            'result': sorted(result,key=lambda x:x[0].lower())
            }


# def import_data(path):
    # import operator
    # from functools import cmp_to_key

    # def compare(a, b):
        # x, y = a[0], b[0]
        # try:
            # cx = list(map(lambda x: int(x) if x.isdigit() else x, re.split(r'([^\d]+)', x)))
            # cy = list(map(lambda x: int(x) if x.isdigit() else x, re.split(r'([^\d]+)', y)))
            # if operator.eq(cx, cy):
                # raise ArithmeticError
            # return -1 if operator.lt(cx, cy) else 1
        # except Exception:
            # if x == y:
                # return 0
            # return -1 if x < y else 1

    # result = []
    # if not os.path.exists(path):
        # return result
    # raw_file_list = os.listdir(path)
    # file_set = set(raw_file_list)
    # patterns = {'.in$': ['.out', '.ans'], '.IN$': ['.OUT', '.ANS'],
                # 'input': ['output', 'answer'], 'INPUT': ['OUTPUT', 'ANSWER']}

    # for file in raw_file_list:
        # for pattern_in, pattern_out in patterns.items():
            # if re.search(pattern_in, file) is not None:
                # for pattern in pattern_out:
                    # try_str = re.sub(pattern_in, pattern, file)
                    # if try_str in file_set:
                        # file_set.remove(try_str)
                        # file_set.remove(file)
                        # result.append((file, try_str))
                        # break

    # return sorted(result, key=cmp_to_key(compare))


def read_partial_data_from_file(filename, length=4096):
    with open(filename, "r") as f:
        result = f.read(length)
    if len(result) >= length - 1:
        result += '\n......'
    return result


def randomize_round_id():
    return str(uuid.uuid1())


def random_string(length):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))


def judge_data_tranform(data):
    return data

def judge_data_checker(data):
    judge_data_set = set(['stack_limit','code', 'lang', 'time', 'memory', 'judge_id', 'cmp', 'judger', 'revert','outut_size'])
    lang_set = set(['c','cpp','pascal','python'])
    defalut_judge_data = {
            'judger':'qjudge',
            'memory':512,
            'stack':512,
            'time':1,
            'output_size':512,
            'judge_id':'',
            'lang':'cpp',
            'code':'',
            'cmp':'fcmp2',
            'revert':{}
    }
    for key in data:
        if key not in judge_data_set:
            return key +' is illegal'
        else:
            defalut_judge_data[key] = data[key]
    if defalut_judge_data['lang'] not in lang_set:
        return 'item lang'+defalut_judge_data[key]+'is illegal'
    if defalut_judge_data['judge_id'] == '':
        return 'item judge_id should not empty'
    if defalut_judge_data['judger'] != 'qjudge' and defalut_judge_data['judger'] != 'ujudge':
        return 'item judger wrong:'+defalut_judge_data['judger']

    if defalut_judge_data['code'] == '':
        return 'item code should not empty'

    # return judge_data_tranform(defalut_judge_data)
    return defalut_judge_data

# 发送soketio
def emit_to_one(sid,data):
    emit('judge_response', data,namespace='/judge',room=sid)
