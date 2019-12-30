# _*_ coding:utf-8 _*_

import os
import pprint
import re


# pattern 文件名
# directory 路径
# 返回一个列表，包含了搜寻到所有文件的完整路径
def find(pattern, directory):
    found = []
    pattern = pattern.lower()
    for (root, dirs, files) in os.walk(directory):
        for file in files+dirs:
            if pattern in file.lower():
                new_pattern = re.compile('^'+pattern, re.I)
                if new_pattern.findall(file):
                    found.append(os.path.join(root, file))
    return found


if __name__ == '__main__':
    directory = 'E:\\Terminal\\NBSW\\Subscriber\\02_Sourcecode\\branch\\br_NBB_Integration_Wind'
    pattern = 'dmr_appid_define.h'
    found = find(pattern, directory)
    pprint.pprint(found[:])
    print(len(found))
