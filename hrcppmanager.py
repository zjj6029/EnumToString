# _*_ coding:utf-8 _*_

import re
import hrcppdb

"""
Date :   2019/12/16
Author:  Zhou Junjie
Comment: HrcppManager类
         从指定文件中读取Hrcpp的opcode，同时管理HRCPP数据库。
         HrcppManager 封装所有对数据库hrcppdb的操作，外界不直接使用hrcppdb。
Params:         
         headfilelist - 列表，头文件路径的列表
         
接口：
retrieveandstore  从头文件中提取hrcpp字符串及对应opcode并存入数据库中
lookupDB          查询hrcpp数据库  key-例：0x10110011 格式
clearDB           清空数据库
check_DB_exists   检查数据库是否存在      
"""


class HrcppManager:

    reg_str = "#define[\t\s]*([_a-zA-Z]*)[\t\s]*0[xX]*([0-9A-Za-z]*)"

    def __init__(self, headfilelist):
        self.headfilelist = headfilelist
        self.db = hrcppdb.HrcppDB()

    # 从头文件中提取HRCPP字符串及对应opcode，并存入数据库中
    def retrieveandstore(self):
        self.db.open_hrcppdb()
        for headfile in self.headfilelist:
            fd = open(headfile, "r")
            content = fd.read()
            content.encode("UTF-8")
            fd.close()
            reslist = re.findall(self.reg_str, content)
            for line in reslist:
                self.db.store_element("0x"+str.lower(line[1]), line[0])
        self.db.close_hrcppdb()

    # 查询DB
    def lookupDB(self, key):
        self.db.open_hrcppdb()
        try:
            res = self.db.lookup_element(key.lower())
            print(res)
            return res

        except KeyError:
            print("输入的key有误，请重新输入")
        self.db.close_hrcppdb()

    # 清空DB
    def clearDB(self):
        self.db.clear_hrcppdb()

    # 检查数据库是否存在
    def check_DB_exists(self):
        return self.db.check_db_exist()


# 调试程序
if __name__ == '__main__':
    headfile1 = "D:\\hrcpp_dmr_opcode.h"
    headfile2 = "D:\\hrcpp_common_opcode.h"
    headfile3 = "D:\\hrcpp_nb_common_opcode.h"
    headfilelist = [headfile1, headfile2, headfile3]
    # 初始化
    HR = HrcppManager(headfilelist)

    # 如果数据库不存在
    if not HR.check_DB_exists():
        # 检索并存入数据库
        HR.retrieveandstore()

    while 1:
        inputs = str.lower(input("是否更新数据库，输入yes 或 no: "))
        if inputs == "yes":
            # 清空数据库
            HR.clearDB()
            HR.retrieveandstore()
            print("数据库更新完毕")
            print("")
            break
        elif inputs == 'no':
            break
        else:
            print("输入有误，请重新输入:")
            print("")

    # 查阅
    while 1:
        opcode = input("请输入HRCPP的Opcode:")
        HR.lookupDB(opcode)
        print("")
