# coding:utf-8

import os
import re

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


real_path = os.path.abspath( os.path.dirname(__file__))

dirs = os.listdir(real_path)

for _path in dirs:
    if os.path.isdir( os.path.join(real_path,_path)):
        print("dir %s: %s" % (_path,str(import_data(_path))))

