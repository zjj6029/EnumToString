# _*_ coding:utf-8 _*_

import os
import re
import constant
"""
Date :   2019/07/31
Author:  Zhou Junjie
Comment: 该类负责管理配置文件Config.txt,读写配置文件中的参数,该类的接口主要提供给Enummanager调用，

接口说明：
put_param:    增加一个 参数:参数值  的键值对（参数不存在时则自动添加该对，参数存在时则覆盖参数值）；
lookup_param: 查询某参数的参数值，如果参数不存在，返回一个抛出一个异常KeyError；
delete_param: 删除某参数的对应键值对;
"""


class ConfigFileManager:
    def __init__(self):
        self.paramvalue_list = []
        self.paramvalue_dic = {}

    def __read_config_file(self):
        file_full_path = os.path.dirname(__file__) + constant.config_file_path_suffix
        if not os.path.exists(file_full_path):
            open(file_full_path, mode='w')
            return False
        file_r = open(file_full_path, mode='rt')
        self.paramvalue_list = file_r.readlines()
        file_r.close()
        pattern = constant.config_file_kv_pattern
        for item in self.paramvalue_list:
            res = re.search(pattern, item)
            if res:
                self.paramvalue_dic[res.group(1)] = res.group(2)

    # 参数new 表示是否写入新的参数键值对
    def __write_config_file(self, param, value, new=True):
        file_full_path = os.path.dirname(__file__) + constant.config_file_path_suffix
        if new:
            # 直接在文件末尾写入新的键值对
            file_w = open(file_full_path, mode='a+')
            file_w.write("\n"+param+" = "+value)
            file_w.close()
        else:
            # 找到原有的键值对，修改值
            # 记录当前是第几行
            count = 0
            # 记录key所在的行
            keyline = -1
            for line in self.paramvalue_list:
                if re.search(param, line):
                    self.paramvalue_list[count] = param + " = " + value+"\n"
                count = count+1
            file_w = open(file_full_path, mode='w')
            file_w.write("".join(self.paramvalue_list))
            file_w.close()

    def put_param(self, param, value):
        self.__read_config_file()
        if param in self.paramvalue_dic.keys():
            if value != self.paramvalue_dic[param]:
                self.__write_config_file(param, value, False)
        else:
            self.__write_config_file(param, value, True)

    def lookup_param(self, param):
        self.__read_config_file()
        try:
            return self.paramvalue_dic[param]
        except KeyError:
            return None

    # todo
    def delete_param(self, param):
        pass


# 测试代码
if __name__ == '__main__':
    cf = ConfigFileManager()
    """
    初始化当前Config.txt文件中有3个键值对
    EnvPath = D:/testfolder
    Param1 = value1
    Param2 = value2
    """

    # 写入已有的键值对，值不同 EnvPath : D/PycharmProjects
    cf.put_param('EnvPath', 'D/PycharmProjects')
    """
    此时Config.txt文件中会变成如下所示：
    EnvPath = D/PycharmProjects
    Param1 = value1
    Param2 = value2
    """

    # 写入新的键值对
    cf.put_param('Param3', 'value3')
    """
    此时Config.txt文件中会变成如下所示：
    EnvPath = D/PycharmProjects
    Param1 = value1
    Param2 = value2
    Param3 = value3
    """

    print(cf.lookup_param('EnvPath'))
    """
    查询EnvPath
    会打印如下内容：
    D/PycharmProjects
    """

    """s
    输出不存在的参数 Param4
    会打印异常
    """
    try:
        (cf.lookup_param('Param4'))
    except KeyError:
        print("KeyError Happens,Param4 not exists")


