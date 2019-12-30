# _*_ coding:utf-8 _*_

import shelve
import os
import constant

"""
Date :   2019/07/04
Author:  Zhou Junjie
Comment: 枚举数据库类
         该类的接口给EnumManager类调用
         
接口说明：
store_enumdb:       存储枚举，enumvar-枚举变量名，enuminfolist-对应枚举信息列表(同enumretrieve类get_enumlist接口返回的enuminfolist)
lookup_enumdb:      查询枚举(对查询值处理后返回)，pid是"变量名+值" 的形式
pure_lookup_enumdb: 查询枚举(直接返回查询值)，pid是"变量名+值" 的形式
delete_enumdb:      删除数据库中指定枚举变量，enumvar  
clean_enumdb:       清空整个数据库

例：
enumvar       - DV_Event  (DV_Event为枚举变量名，PSEvent为子枚举变量名)，
              - DV_Event包含子枚举 PSEvent 、KeyEvent、HRCPPEvent等；
enuminfolist  - enumdic为元素的列表；
enuminfo      - 字典 {enumvar:PSEvent, enumvalue:1, enumstr:"PS CLEAR DOWN", enumnote:"拆线"}；
"""


class EnumDB:

    def __init__(self):
        pass

    # 存储枚举
    def store_enumdb(self, enumvar, enuminfolist):
        database = shelve.open(os.path.dirname(__file__) + constant.enum_DB_path_suffix)
        length = len(enuminfolist)
        for i in range(0, length):
            pid = enumvar+'_'+str(enuminfolist[i]['enumvalue'])
            database[pid] = enuminfolist[i]
        database.close()

    # 查询枚举
    def lookup_enumdb(self, pid):
        database = shelve.open(os.path.dirname(__file__) + constant.enum_DB_path_suffix)
        retval1 = "对应的枚举变量名为："+database[pid]['enumvar']+'\n'+'\n'
        retval2 = "对应的枚举字符串为："+database[pid]['enumstr']+'\n'+'\n'
        retval3 = "对应的注释："+database[pid]['enumnote']
        database.close()
        return retval1+retval2+retval3

    # 删除枚举
    def delete_enumdb(self, enumvar):
        database = shelve.open(os.path.dirname(__file__) + constant.enum_DB_path_suffix)
        count = 0
        key = enumvar+'_'+str(count)
        while key in database:
            del database[key]
            count = count + 1
            key = enumvar+'_'+str(count)

    # 清空数据库
    def clean_enumdb(self):
        try:
            os.remove(os.path.dirname(__file__) + constant.enum_DB_path_suffix + '.bak')
            os.remove(os.path.dirname(__file__) + constant.enum_DB_path_suffix + '.dir')
            os.remove(os.path.dirname(__file__) + constant.enum_DB_path_suffix + '.dat')
        except FileNotFoundError:
            pass

    def pure_lookup_enumdb(self, pid):
        database = shelve.open(os.path.dirname(__file__) + constant.enum_DB_path_suffix)
        ret = database[pid]['enumstr']
        database.close()
        return ret
