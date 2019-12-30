# _*_ coding:utf-8 _*_

import shelve
import os

"""
Date :   2019/12/16
Author:  Zhou Junjie
Comment: 这个数据库类HrcppDB的接口主要提供给EnumManage调用，然后再由EnumManage提供接口给EnumUI类调用,EnumUI类直接对接用户的操作。
"""


class HrcppDB:

    def __init__(self):
        self.database = None

    def open_hrcppdb(self):
        self.database = shelve.open(os.path.dirname(__file__) + '\\Data\\hrcppdb.dat')

    def close_hrcppdb(self):
        self.database.close()

    def store_element(self, key_opcode, value_str):
        self.database[key_opcode] = value_str

    def lookup_element(self, key_opcode):
        value_str = self.database[key_opcode]
        return value_str

    # 删除枚举
    def delete_element(self, key_opcode):
        database = shelve.open(os.path.dirname(__file__) + '\\Data\\hrcppdb.dat')
        del database[key_opcode]

    # 清空数据库
    def clear_hrcppdb(self):
        try:
            os.remove(os.path.dirname(__file__)+'\\Data\\hrcppdb.dat.bak')
            os.remove(os.path.dirname(__file__) + '\\Data\\hrcppdb.dat.dir')
            os.remove(os.path.dirname(__file__) + '\\Data\\hrcppdb.dat.dat')
        except FileNotFoundError:
            pass

    def check_db_exist(self):
        if os.path.exists(os.path.dirname(__file__)+'\\Data\\hrcppdb.dat.dat'):
            return True
        else:
            return False
