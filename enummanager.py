# _*_ coding:utf-8 _*_

import os
import re
import enumdb
import enumretrieve
import configfilemanager
import searchfile
from collections import Iterable

"""
Date :   2019/07/12
Author:  Zhou Junjie
Comment:  枚举管理类
          功能：管理枚举数据库类、枚举检索类、管理配置文件（读写配置参数）、读写两个枚举配置文件(hierarchy、list)、 
               给UI层提供功能接口 
            
          enumconfiginfo 是一个枚举字典，由多个 "枚举变量名:枚举相关信息"  键值对构成；
          枚举相关信息 是一个列表；
          第一个元素是 子枚举信息 subenum;是一个列表结构，列表元素是各个子枚举变量名；
          第二个元素是 层次关系信息 hierinfo;是一个字典结构，键值对为"枚举值:下一层枚举变量名"；
          第三个元素是 枚举变量所在头文件的路径Path；
          通过这样的enumconfiginfo将枚举相关信息整合到一起，方便读写配置文件，并且根据该信息提供的策略去检索头文件；
          
接口：
数据库操作：
db_cleanup_enum    清空数据库
db_refresh_enum    更新数据库
db_lookup_enum     查询枚举（返回处理后的查询结果）
pure_lookup_enumdb 查询枚举（直接返回查询结果）


枚举配置文件读取：
read_file_enum_all                 读取enumlist、enumhierarchy两个文件，读到的枚举信息放入 self.enum_config_info 中
read_file_enumhierarchy            读取enumhierarchy这个文件
read_file_enumlist                 读取enumlist这个文件
is_enumname_exist_in_enumlist      检查某个枚举量是否存在于enumlist文件中
is_enumname_exist_in_enumhierarchy 检查某个枚举量是否存在于enumhierarchy文件中
get_enumname_list                  读取enumlist文件，返回读取结果——列表形式
get_enumname_hierachy_list         读取enumhierachy文件，返回读取结果——列表形式
get_enumconfiginfo                 读取两个文件，返回self.enum_config_info


修改枚举配置文件：
modify_enum_hierarchy    修改枚举层析信息
modify_enum_subenum      修改子枚举
modify_enum_path         修改枚举头文件路径
add_enum                 往枚举配置文件中增加枚举
delete_enum              删除配置文件中的枚举量，同时删除数据库中该枚举量


配置文件中配置参数的读写：
lookup_param             查询配置参数  
put_param                添加配置参数
"""


class EnumManager:

    def __init__(self):
        self.enum_config_info = {}                                        # 关于枚举相关信息的字典 { 枚举变量：info }键值对；
        self.config_param_namelist = ['EnvPath']                          # 当前配置参数的列表
        self.config_param_dic = {}.fromkeys(self.config_param_namelist)   # 关于当前参数的字典，初始化字典的各个键值为None

        self.config_file_manager = configfilemanager.ConfigFileManager()
        self.enum_db = enumdb.EnumDB()
        self.enum_retrieve = enumretrieve.EnumRetrieve()

        # 初始化 config_param_dic
        for param in self.config_param_namelist:
            try:
                self.config_param_dic[param] = self.config_file_manager.lookup_param(param)
            except KeyError:
                pass

    """
    以只读方式打开文件，如果文件不存在则创建文件
    """
    def __open_file_with_read(self, filename):
        file_full_path = os.path.dirname(__file__)+'\\Config\\'+filename+'.txt'
        if not os.path.exists(file_full_path):
            open(file_full_path, mode='w')
        return self.__open_file_with_mode(filename, 'rt')

    """
    r   只读，如果文件没有会报错 FileNotFoundError；
    r+  可读可写，如果文件没有会报错 FileNotFoundError；写的话会覆盖原有内容；
    rt  默认只读模式，如果文件没有回报错 FileNotFoundError ；
    w   只读方式打开文件，如果没有文件会创建，已有的文件内容会被覆盖；
    w+  可读可写，如果文件没有会创建，已有的文件内容会被覆盖，也就是直接读的话就是个空文件；
    a+  可读可写，如果文件没有会创建，写入的话会在末尾写入，不会影响原有文件内容；
    """
    def __open_file_with_mode(self, filename, mode):
        file_full_path = os.path.dirname(__file__) + '\\Config\\' + filename + '.txt'
        return open(file_full_path, mode=mode, encoding='utf-8')

    """
    该函数会将enumconfiginfo的内容写进配置文件
    然后对相应内容替换更改；
    如果replace为真，则先完全清空源文件，按照enumconfiginfo内容写入；
    否则是增量式，修改式地写入；
    """
    def __write_file_enumlist(self, enumconfiginfo, replace=False):
        if replace:
            file_w = self.__open_file_with_mode('EnumList', 'w')
            filelines = []
            for key in enumconfiginfo:
                firstline = "["+key+"]"+"\n"
                secondline = "Path:"+enumconfiginfo[key][2]+"\n"
                thirdline = "Enum:{"
                for subenum in enumconfiginfo[key][0]:
                    if subenum == enumconfiginfo[key][0][-1]:
                        thirdline = thirdline + subenum
                    else:
                        thirdline = thirdline + subenum+","
                thirdline = thirdline +"}\n"
                filelines.append("\n"+firstline+secondline+thirdline)
            file_w.write("".join(filelines))
            file_w.close()
            return
        # 遍历dic的每个键值对
        for key in enumconfiginfo:
            # 判断键是否已经存在
            if self.is_enumname_exist_in_enumlist(key):
                # 存在-修改相应内容
                file_r = self.__open_file_with_mode('EnumList', 'r+')
                filelines = file_r.readlines()
                file_r.close()
                # 记录当前是第几行
                count = 0
                # 记录key所在的行
                keyline = -1
                # key正则匹配表达式
                reg_ex = '\[\s*' + key + '\s*\]'
                for line in filelines:
                    result = re.search(reg_ex, line)
                    # 如果匹配到key
                    if result:
                        # 记录 key所在的行
                        keyline = count
                    # 替换key对应path行的内容
                    if keyline != -1:
                        filelines[keyline+1] = "Path:"+enumconfiginfo[key][2]+"\n"
                    # 替换key对应enum行的内容
                    if keyline != -1:
                        filelines[keyline+2] = "Enum:"+"{"+",".join(enumconfiginfo[key][0])+"}"+"\n"
                        break
                    # if keyline != -1 and count == keyline+1:
                    #     filelines[count] = "Path:"+enumconfiginfo[key][2]+"\n"

                    #if keyline != -1 and count == keyline+2:
                    #    filelines[count] = "Enum:"+"{"+",".join(enumconfiginfo[key][0])+"}"+"\n"
                    #
                    count = count + 1
                file_rw = self.__open_file_with_mode('EnumList', 'w+')
                file_rw.write("".join(filelines))
                file_rw.close()
            else:
                # 不存在-直接在文件末尾写入
                file_w = self.__open_file_with_mode('EnumList', 'a+')
                file_w.write("\n\n")
                file_w.write("["+key+"]")
                file_w.write("\n")
                file_w.write("Path:"+enumconfiginfo[key][2])
                file_w.write("\n")
                file_w.write("Enum:"+"{"+",".join(enumconfiginfo[key][0])+"}")
                file_w.close()

    """
    该函数会将enumconfiginfo的内容写进配置文件
    然后对相应内容替换更改
    如果replace为真，则先完全清空源文件，按照enumconfiginfo内容写入；
    否则是增量式，修改式地写入；
    """
    def __write_file_enumhierarchy(self, enumconfiginfo, replace=False):
        if replace:
            file_w = self.__open_file_with_mode('EnumHierarchy', 'w')
            filelines = []
            for key in enumconfiginfo:
                if not isinstance(enumconfiginfo[key][1], Iterable):
                    continue
                titleline = "["+key+"]"+"\n"
                subenumlines = []
                for subenum in enumconfiginfo[key][1]:
                    subenumlines.append(subenum+":"+enumconfiginfo[key][1][subenum]+"\n")
                filelines.append("\n"+titleline+"".join(subenumlines))
            file_w.write("".join(filelines))
            file_w.close()
            return
        # 遍历dic的每个键值对
        for key in enumconfiginfo:
            if not isinstance(enumconfiginfo[key][1], Iterable):
                continue
            # 判断键是否已经存在
            if self.is_enumname_exist_in_enumhierarchy(key):
                # 存在-修改相应内容
                file_r = self.__open_file_with_mode('EnumHierarchy', 'r+')
                filelines = file_r.readlines()
                file_r.close()
                # 记录当前是第几行
                count = 0
                # 记录key所在的行
                keyline = -1
                nextkeyline = -1
                # key正则匹配表达式
                reg_ex = '\[\s*' + key + '\s*\]'
                reg_next = '\['
                for line in filelines:
                    result = re.search(reg_ex, line)
                    if keyline != -1:
                        subresult= re.search(reg_next, line)
                        if subresult:
                            nextkeyline = count
                            del filelines[keyline+1:nextkeyline-1]
                            # 遍历该key的hierarchy字典中的各个键值对
                            subcount = keyline+1
                            for hierarchy_key in enumconfiginfo[key][1]:
                                insert_content = hierarchy_key+":"+enumconfiginfo[key][1][hierarchy_key]+"\n"
                                filelines.insert(subcount, insert_content)
                                subcount = subcount+1
                            break
                    # 如果匹配到key
                    if result:
                        # 记录 key所在的行
                        keyline = count

                    count = count + 1
                file_rw = self.__open_file_with_mode('EnumHierarchy', 'w+')
                file_rw.write("".join(filelines))
                file_rw.close()
            else:
                # 不存在-直接在文件末尾写入
                file_w = self.__open_file_with_mode('EnumHierarchy', 'a+')
                file_w.write("\n\n")
                file_w.write("[" + key + "]")
                file_w.write("\n")
                for subkey in enumconfiginfo[key][1]:
                   file_w.write(subkey+":"+enumconfiginfo[key][1][subkey]+"\n")
                file_w.close()

    """
    根据配置文件读取到和路径信息，结合EnvPath 生成绝对路径，并赋值到enumconfiginfo中；
    如果生成路径有误，无法搜到相应头文件，则会返回路径第一个出错的枚举变量的key；
    如果路径没有错，就返回None；
    """
    def __handlepath(self):
        value_env_path = self.config_file_manager.lookup_param('EnvPath')
        # 如果没有找到预先配置的相对路径,直接使用读取到的rawpath不做加工
        if not value_env_path:
            return

        # pattern是绝对路径的开头形式
        pattern = '^[a-zA-Z]\s*:'

        # 遍历所有rawpath，将对于仅文件名的rawpath 转换成绝对路径赋回去给self.enumconfiginfo[key][2]
        # rawpath可能的形式：完整绝对路径、仅头文件名；  这里暂不处理不完整路径（相对路径的形式）
        for key in self.enum_config_info:
            # 取出配置文件中读到的路径 rawpath
            rawpath = self.enum_config_info[key][2]
            if not re.search(pattern, rawpath):
                # 没匹配到 说明这是仅文件名的情况，需要转换成绝对路径
                found = searchfile.find(rawpath, value_env_path)
                if len(found) == 0:
                    # 返回路径有误的枚举变量名
                    return key
                else:
                    self.enum_config_info[key][2] = found[0]
        return

    # 以下两个程序参数处理相关函数，目前只用到环境变量EnvPath
    def put_param(self, param, value):
        self.config_file_manager.put_param(param, value)
        self.config_param_dic[param] = value

    def lookup_param(self, param):
        return self.config_param_dic[param]

    def get_enumconfiginfo(self):
        self.read_file_enum_all()
        return self.enum_config_info

    def get_enumname_list(self):
        file = self.__open_file_with_read('EnumList')
        content = file.read()
        file.close()
        reg_enumname = '\s*\[\s*([A-Za-z0-9_]*)\s*\][\r\t\n\s]*'
        return re.findall(reg_enumname, content)

    def get_enumname_hierachy_list(self):
        file = self.__open_file_with_read('EnumHierarchy')
        content = file.read()
        file.close()
        reg_enumname = '\s*\[\s*([A-Za-z0-9_]*)\s*\][\r\t\n\s]*'
        return re.findall(reg_enumname, content)

    # 同时读取两个文件，并进行相对路径的处理，生成enumconfiginfo
    def read_file_enum_all(self, enum_name=None):
        self.enum_config_info = {}  # 先将当前属性清空
        self.read_file_enumlist(enum_name)
        self.read_file_enumhierarchy(enum_name)
        # 这里加上对读取到的enumlist中的路径的处理，生成最终的绝对路径返回给self.enumconfiginfo，
        return self.__handlepath()

    """
    enunname      枚举变量名
    enumname 为空， 对配置文件中描述的所有枚举进行全量读取
    enumname 不为空，对特定枚举进行读取
    """
    # 读取文件_枚举
    def read_file_enumlist(self, enum_name=None):
        file_el = self.__open_file_with_read('EnumList')
        content = file_el.read()
        file_el.close()
        # 读取所有
        if enum_name == None:
            reg_ex = '\s*\[\s*[A-Za-z0-9_]*\s*\][\r\t\n\s]*'+'[\\\\_,/\{\}:a-zA-Z0-9\r\t\n\s\.]*'
            reg_enumname = '\s*\[\s*([A-Za-z0-9_]*)\s*\][\r\t\n\s]*'
            reg_path = 'Path\s*:\s*([\\\\/_0-9a-zA-Z:\.]*)[\r\n]*Enum'
            reg_enum = '([_a-zA-Z0-9]*)[,\}]+'
            raw_result = re.findall(reg_ex, content)
            for item in raw_result:
                enumname = re.search(reg_enumname, item).group(1)
                temp_result = re.search(reg_path, item)
                path_result =temp_result.group(1)
                enum_result = re.findall(reg_enum, item)
                if enumname not in self.enum_config_info:
                    self.enum_config_info[enumname] = [0, 1, 2]
                self.enum_config_info[enumname][0] = enum_result
                self.enum_config_info[enumname][2] = path_result
            return self.enum_config_info
        # 读取指定一个枚举
        else:
            reg_ex = '(\[\s*' + enum_name + '\s*\][\\\\/:a-zA-Z0-9_\r\n\s,\{\}\.]*)\[*'
            raw_result = re.search(reg_ex, content).group(1)
            if raw_result:
                reg_path = 'Path\s*:\s*([\\\\/0-9a-zA-Z:\._]*)[\r\n]*'
                reg_enum = '([_a-zA-Z0-9]*)[,\}]+'
                path_result = re.search(reg_path, raw_result).group(1)
                enum_result = re.findall(reg_enum, raw_result)
                if enum_name not in self.enum_config_info:
                    self.enum_config_info[enum_name] = [0, 1, 2]
                self.enum_config_info[enum_name][0] = enum_result
                self.enum_config_info[enum_name][2] = path_result
            return self.enum_config_info[enum_name]

    """
    enunname      枚举变量名
    enumname 为空， 对配置文件中描述的所有枚举进行全量读取
    enumname 不为空，对特定枚举进行读取
    """
    # 读取文件_枚举层次关系
    def read_file_enumhierarchy(self, enum_name=None):
        file_eh = self.__open_file_with_read('EnumHierarchy')
        content = file_eh.read()
        file_eh.close()
        # 读取所有
        if enum_name == None:
            reg_ex = '\s*\[\s*[A-Za-z0-9_]*\s*\][\r\t\n\s]*'+'[\\\\,/\{\}:a-zA-Z0-9_\r\t\n\s]*'
            reg_enumname = '\s*\[\s*([A-Za-z0-9_]*)\s*\][\r\t\n\s]*'
            reg_hierarchy = '(\d*):([a-zA-Z0-9_]*)'
            raw_result = re.findall(reg_ex, content)
            for item in raw_result:
                enumname = re.search(reg_enumname, item).group(1)
                hierarchy = {}
                for subitem in re.findall(reg_hierarchy, item):
                    hierarchy[subitem[0]] = subitem[1]
                if enumname not in self.enum_config_info:
                    self.enum_config_info[enumname] = [0, 1, 2]
                self.enum_config_info[enumname][1] = hierarchy
            return self.enum_config_info
        # 读取指定一个枚举
        else:
            reg_ex = '(\['+enum_name+'\][:a-zA-Z0-9_\r\n]*)\[*'
            raw_result = re.search(reg_ex, content).group(1)
            reg_hierarchy = '(\d*):([a-zA-Z0-9_]*)'
            hierarchy_result = re.findall(reg_hierarchy, raw_result)
            hierarchy = {}
            for item in hierarchy_result:
                hierarchy[item[0]] = item[1]
            if enum_name not in self.enum_config_info:
                self.enum_config_info[enum_name] = [0, 1, 2]
            self.enum_config_info[enum_name][1] = hierarchy
            return self.enum_config_info[enum_name]

    """
    搜寻枚举变量是否在enumhierarchy文件中
    返回值：布尔值
    """
    def is_enumname_exist_in_enumhierarchy(self, enum_name):
        file_eh = self.__open_file_with_read('EnumHierarchy')
        reg_ex = '\[\s*'+enum_name+'\s*\]'
        result = re.search(reg_ex, file_eh.read())
        file_eh.close()
        if result:
            return True
        else:
            return False

    """
    搜寻枚举变量是否在enumlist文件中
    返回值：布尔值
    """
    def is_enumname_exist_in_enumlist(self, enum_name):
        file_el = self.__open_file_with_read('EnumList')
        reg_ex = '\['+enum_name+'\]'
        result = re.search(reg_ex, file_el.read())
        file_el.close()
        if result:
            return True
        else:
            return False

    # 以下这些都是直接提供给外部的使用的接口
    """
        新增一个枚举，需要提供完整的信息，
        参数如下：
        enumname   枚举变量名
        hierarchy  枚举层次关系
        subenums   子枚举信息
        path       枚举变量所在路径

        返回值：True 添加成功；
               False 添加失败，当前枚举已存在；
    """
    # 新增一个枚举量
    def add_enum(self, enumname, subenums, path, hierarchy=None):
        # 判断是否是已有枚举
        if self.is_enumname_exist_in_enumlist(enumname):
            return False

        # 写入配置文件中
        enumconfiginfo = {}
        enumconfiginfo[enumname] = [subenums, hierarchy, path]
        if not hierarchy:
            self.__write_file_enumhierarchy(enumconfiginfo)
        self.__write_file_enumlist(enumconfiginfo)

        # 写入数据库中
        # 不写入数据库中
        return True

    """
    enunname 枚举变量名
    """
    # 删除某个枚举
    def delete_enum(self, enumname):
        # 从数据库中删除
        self.enum_db.delete_enumdb(enumname)

        # 从配置文件中删除
        self.enum_config_info = {}  # 先将当前属性清空
        self.read_file_enumlist()
        self.read_file_enumhierarchy()

        del self.enum_config_info[enumname]

        self.__write_file_enumhierarchy(self.enum_config_info, True)
        self.__write_file_enumlist(self.enum_config_info, True)

    """
    enunname 枚举变量名
    new_path 新的路径
    修改配置文件，并根据配置文件重新更新数据库
    """
    # 修改枚举量的路径
    def modify_enum_path(self, enumname, new_path):
        # 判断是否不存在枚举
        if not self.is_enumname_exist_in_enumlist(enumname):
            return False

        enumconfiginfo={}
        enumconfiginfo[enumname] = self.read_file_enumlist(enumname)
        enumconfiginfo[enumname][2] = new_path
        self.__write_file_enumlist(enumconfiginfo)
        return True

    """
    enunname    枚举变量名
    new_subenum 新的子枚举
    修改配置文件，并根据配置文件重新更新数据库
    """
    # 修改枚举的子枚举
    def modify_enum_subenum(self, enumname, new_subenum):
        # 判断是否不存在枚举
        if not self.is_enumname_exist_in_enumlist(enumname):
            return False

        enumconfiginfo = {}
        enumconfiginfo[enumname] = self.read_file_enumlist(enumname)
        enumconfiginfo[enumname][0] = new_subenum
        self.__write_file_enumlist(enumconfiginfo)
        return True

    """
    enunname      枚举变量名
    new_hierarchy 新的层次关系
    修改配置文件，并根据配置文件重新更新数据库
    """
    # 修改枚举的层次关系
    def modify_enum_hierarchy(self, enumname, new_hierarchy):
        # 判断是否不存在枚举
        if not self.is_enumname_exist_in_enumhierarchy:
            return False

        enumconfiginfo = {}
        enumconfiginfo[enumname] = self.read_file_enumhierarchy(enumname)
        enumconfiginfo[enumname][1] = new_hierarchy
        self.__write_file_enumlist(enumconfiginfo)
        return True

    """
    enunname  枚举变量名
        为空:  对配置文件中的所有枚举在数据库进行更新
        不为空: 对配置文件中的特定枚举在数据库进行更新
    """
    def db_refresh_enum(self, enumname=None):
        if enumname == None:
            self.enum_db.clean_enumdb()
        # 读取配置文件，将读取到的内容存放到实例属性enumconfiginfo中
        wrong_key = self.read_file_enum_all(enumname)
        if wrong_key:
            return wrong_key
        for key in self.enum_config_info:
            path = self.enum_config_info[key][2]
            if isinstance(self.enum_config_info[key][0], list):
                try:
                    self.enum_retrieve.build_enuminfolist(self.enum_config_info[key][0], path)
                except FileNotFoundError:
                    ex = Exception("找不到枚举变量"+key+"所对应头文件，路径错误。请检查配置文件。")
                    raise ex
                except AttributeError:
                    ex = Exception("出现了AttributeError，应该是"+key+"的Enum中的某个子枚举变量的注释中出现中文特殊符号，导致正则无法匹配，检索失败，例如‘、【】等。请检查相应头文件，尽量不在注释中的使用特殊符号。")
                    raise ex
                self.enum_db.store_enumdb(key, self.enum_retrieve.enuminfolist)

    # 清空数据库
    def db_cleanup_enum(self):
        self.enum_db.clean_enumdb()

    # 查询枚举量
    def db_lookup_enum(self, name, val):
        input_key = name + '_' + str(val)
        return self.enum_db.lookup_enumdb(input_key)

    # 读取数据库，纯粹返回键值
    def pure_lookup_enumdb(self, name, val):
        input_key = name + '_' + str(val)
        return self.enum_db.pure_lookup_enumdb(input_key)




