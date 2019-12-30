# _*_ coding:utf-8 _*_

import re
"""
Date :   2019/07/05
Author:  Zhou Junjie
Comment: 枚举检索类
         从指定头文件中检索枚举量，将检索到的枚举量信息存储在一个列表中，即enuminfolist，该列表中的元素是字典，
         字典enuminfo包含的内容有四项：枚举的变量名enumvar，字符串enumstr，值enumvalue，说明enumnote；
         这样的复合结构enuminfolist将作为数据载体来传递给enumdb类，以达到将枚举量信息存入数据库中的目的。
         
接口说明：
build_enuminfolist     构建枚举列表
get_enuminfolist       获取枚举列表，第一次获取前要调用build_enumlist
clean_up_enuminfolist  清空枚举列表      

例：
enuminfo  {enumvar:PSEvent, enumvalue:1, enumstr:"PS CLEAR DOWN", enumnote:"拆线"} 
"""
# note: 对于define宏定义 常量  这个检索起来比较麻烦，暂时不做；


class EnumRetrieve:
    name = ''   # 枚举量名称

    def __init__(self):
        self.enuminfo = {}
        self.enuminfolist = []
        self.enumlistNextIndex = 0

    # 创建enuminfolist
    def build_enuminfolist(self, subenums, path):
        self.enuminfo = {}
        self.enuminfolist = []
        self.enumlistNextIndex = 0

        for subenum in subenums:
            self.__build_subenuminfolist(subenum, path)
        return True

    # 在头文件中检索子枚举变量的信息，每个枚举字符串信息组合成字典，并作为元素插入到enumlist列表中
    def __build_subenuminfolist(self, subenum, path):
        self.enuminfo['enumvar'] = subenum
        # 这里可能会有 FileNotFoundError异常
        filecontent = open(path, 'r').read()

        filecontent.encode("UTF-8")


        # 两种枚举量书写方式
        regex_str1 = "typedef\s*enum[\r\n]*\{[\r\n]*([=_\s,.;:!?<>\t/\u201c-\uFFFFA-Za-z0-9\r\n]*)\}\s*"+subenum
        regex_str2 = "enum\s*"+subenum+"[\r\n]*\{[\r\n]*([=_\s,.;:!?<>\t/\u201c-\uFFFFA-Za-z0-9\r\n]*)\}"
        result = re.search(regex_str1, filecontent)

        if result == None:
            # 如果第一种书写方式不匹配，使用第二种书写方式匹配
            result = re.search(regex_str2, filecontent)
        # 这里可能会抛出 AttributeError异常
        # 将匹配到的各行枚举转换成一个列表，各行枚举是列表中的元素
        splitresult = re.split('\n', result.group(1))
        # 该正则表达式有三个子表达式 用于匹配一行枚举中的：枚举字符串、枚举值、注释，
        regex_str3 = '[\n\t\s]*([0-9A-Za-z_]*)\s*=?\s*([0-9a-zA-Z_]*),?[\t\s/]*([\u201c-\uFFFFA-Za-z0-9,.;:!?\s]*)[\r\n]*'
        # 记录行数用
        count = 0
        # 遍历该列表各行枚举
        for i in splitresult:
            result = re.search(regex_str3, i)
            # 如果匹配的行是空行，就不执行下列语句
            if result.group(1).strip() != '':
                self.enuminfo['enumstr'] = result.group(1)
                self.enuminfo['enumnote'] = result.group(3)
                try:
                    a = eval(result.group(2))
                except SyntaxError:   # 如果子表达式2匹配到的是空
                    self.enuminfo['enumvalue'] = count
                    count += 1
                except NameError:    # 如果子表达式2匹配到的是字符串，则该字符串是紧接着的上一个枚举量的最后一个枚举字符串
                    a = self.enuminfolist[self.enumlistNextIndex - 1]['enumvalue']
                    self.enuminfo['enumvalue'] = a
                    count = a+1
                else:
                    self.enuminfo['enumvalue'] = a
                    count = a+1
                self.enuminfolist.append(self.enuminfo.copy())
                self.enumlistNextIndex += 1   # 一旦往列表中加入一个元素，NextIndex指向下一个未插入元素的位置
        return True

    # 获取枚举列表
    def get_enuminfolist(self):
        return self.enuminfolist

    # 清空枚举列表
    def clean_up_enuminfolist(self):
        self.enuminfolist = []








