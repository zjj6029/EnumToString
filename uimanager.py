# _*_ coding:utf-8 _*_

import re
import os
import tkinter
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import enummanager
import fuzzyfinder
import time
import traceback
import hrcppmanager
import constant
import searchfile
"""
Date :   2019/07/10
Author:  Zhou Junjie
Comment: 该类负责完成UI的显示功能，直接面向用户，给用户提供各项功能
"""


class UIManager:

    # 创建各类成员对象（窗体、组件、其他）
    def __init__(self):
        # 创建&配置_窗体
        self.window = tkinter.Tk()
        self.window.title('枚举值转字符串查询工具')
        self.window.resizable(1, 1)
        self.window.geometry('1000x800+500+100')

        # 创建_菜单栏
        self.menubar = tkinter.Menu(self.window)
        self.window['menu'] = self.menubar

        # 创建下拉菜单
        self.dropdown_menu1 = tkinter.Menu(self.menubar, tearoff=0)
        self.dropdown_menu2 = tkinter.Menu(self.menubar, tearoff=0)
        self.dropdown_menu3 = tkinter.Menu(self.menubar, tearoff=0)
        self.dropdown_menu4 = tkinter.Menu(self.menubar, tearoff=0)

        # 创建_标签_显示必要文本信息
        self.lb1 = tkinter.Label(self.window, text='枚举层次', font=("Arial,15"))
        self.lb2 = tkinter.Label(self.window, text='枚举量', font=("Arial,15"))
        self.lb3 = tkinter.Label(self.window, text='枚举值', font=("Arial,15"))
        self.lb4 = tkinter.Label(self.window, text='进制', font=("Arial,15"))
        self.lb5 = tkinter.Label(self.window, text='结果', font=("Arial,15"))

        self.level1 = tkinter.Label(self.window, text='Level-1', font=("Arial,15"))
        self.level2 = tkinter.Label(self.window, text='Level-2', font=("Arial,15"))
        self.level3 = tkinter.Label(self.window, text='Level-3', font=('Arial,15'))
        self.level4 = tkinter.Label(self.window, text='Level-4', font=("Arial,15"))

        # 创建_下拉列表，绑定下拉选中的变量
        self.enumvarchosen1 = tkinter.StringVar()
        self.enumvar1 = tkinter.ttk.Combobox(self.window, width=45, textvariable=self.enumvarchosen1)
        self.enumvarchosen2 = tkinter.StringVar()
        self.enumvar2 = tkinter.ttk.Combobox(self.window, width=45, textvariable=self.enumvarchosen2)
        self.enumvarchosen3 = tkinter.StringVar()
        self.enumvar3 = tkinter.ttk.Combobox(self.window, width=45, textvariable=self.enumvarchosen3)
        self.enumvarchosen4 = tkinter.StringVar()
        self.enumvar4 = tkinter.ttk.Combobox(self.window, width=45, textvariable=self.enumvarchosen4)

        # 创建_确认按钮
        self.confirm1 = None
        self.confirm2 = None
        self.confirm3 = None
        self.confirm4 = None

        # 创建_文本框_枚举值输入
        self.inputval1 = tkinter.Text(width=9, height=2)
        self.inputval2 = tkinter.Text(width=9, height=2)
        self.inputval3 = tkinter.Text(width=9, height=2)
        self.inputval4 = tkinter.Text(width=9, height=2)

        # 创建_下拉列表_进制选择输入
        self.radixvalue1 = tkinter.StringVar()
        self.radix1 = tkinter.ttk.Combobox(self.window, width=5, textvariable=self.radixvalue1)
        self.radixvalue2 = tkinter.StringVar()
        self.radix2 = tkinter.ttk.Combobox(self.window, width=5, textvariable=self.radixvalue2)
        self.radixvalue3 = tkinter.StringVar()
        self.radix3 = tkinter.ttk.Combobox(self.window, width=5, textvariable=self.radixvalue3)
        self.radixvalue4 = tkinter.StringVar()
        self.radix4 = tkinter.ttk.Combobox(self.window, width=5, textvariable=self.radixvalue4)

        # 创建_文本框_结果显示
        self.result1 = tkinter.Text(width=45, height=10)
        self.result2 = tkinter.Text(width=45, height=10)
        self.result3 = tkinter.Text(width=45, height=10)
        self.result4 = tkinter.Text(width=45, height=10)

        # 实例化一个enumDB对象
        self.enummanage = enummanager.EnumManager()
        self.enumname_list = self.enummanage.get_enumname_list()

        self.__logpath = "null"

    # 配置_菜单栏
    def config_menu(self):
        self.dropdown_menu1.add_command(label='打开配置文件-层次关系信息', command=lambda: self.dropdown_menu1_open_config_file('EnumHierarchy'))
        self.dropdown_menu1.add_command(label='打开配置文件-路径&子枚举信息', command=lambda: self.dropdown_menu1_open_config_file('EnumList'))
        self.dropdown_menu1.add_command(label='打开配置文件-日志解析策略', command=lambda: self.dropdown_menu1_open_config_file('LogAnalysis'))
        self.dropdown_menu1.add_command(label='关闭程序', command=self.dropdown_menu1_end_program)
        self.menubar.add_cascade(label='文件', menu=self.dropdown_menu1)

        self.dropdown_menu2.add_command(label='更新数据库', command=self.dropdown_menu2_update_db)
        self.dropdown_menu2.add_command(label='清空数据库', command=self.dropdown_menu2_clean_db)
        self.dropdown_menu2.add_command(label='增加枚举量', command=self.dropdown_menu2_add_enum)
        self.dropdown_menu2.add_command(label='删除枚举量', command=self.dropdown_menu2_delete_enum)
        self.dropdown_menu2.add_command(label='修改枚举量', command=self.dropdown_menu2_modify_enum)
        self.menubar.add_cascade(label='数据', menu=self.dropdown_menu2)

        self.dropdown_menu3.add_command(label='项目路径', command=self.dropdown_menu3_env_path)
        self.dropdown_menu3.add_command(label='日志解析', command=self.dropdown_menu3_log_analysis)
        self.menubar.add_cascade(label='编辑', menu=self.dropdown_menu3)

        self.dropdown_menu4.add_command(label='注意事项', command=self.dropdown_menu4_help)
        self.menubar.add_cascade(label='帮助', menu=self.dropdown_menu4)

    # 配置_标签_显示必要文本信息
    def config_label(self):
        self.lb1.place(relx=0.05, rely=0.05, anchor=tkinter.NW)
        self.lb2.place(relx=0.25, rely=0.05, anchor=tkinter.NW)
        self.lb3.place(relx=0.5, rely=0.05, anchor=tkinter.NW)
        self.lb4.place(relx=0.59, rely=0.05, anchor=tkinter.NW)
        self.lb5.place(relx=0.78, rely=0.05, anchor=tkinter.NW)

        self.level1.place(relx=0.05, rely=0.1, anchor=tkinter.NW)
        self.level2.place(relx=0.05, rely=0.3, anchor=tkinter.NW)
        self.level3.place(relx=0.05, rely=0.5, anchor=tkinter.NW)
        self.level4.place(relx=0.05, rely=0.7, anchor=tkinter.NW)

    # 配置_下拉列表_枚举变量输入
    def config_combobox_input_enum(self):
        self.enumvar1.place(relx=0.15, rely=0.1, anchor=tkinter.NW)
        self.enumvar2.place(relx=0.15, rely=0.3, anchor=tkinter.NW)
        self.enumvar3.place(relx=0.15, rely=0.5, anchor=tkinter.NW)
        self.enumvar4.place(relx=0.15, rely=0.7, anchor=tkinter.NW)

        # 设置_Combobox下拉显示的内容
        self.enumvar1['value'] = self.enumname_list
        self.enumvar2['value'] = self.enumname_list
        self.enumvar3['value'] = self.enumname_list
        self.enumvar4['value'] = self.enumname_list

        self.enumvar1.bind('<Button-1>', self.var1chosen_input_fuzzy_match)
        self.enumvar2.bind('<Button-1>', self.var2chosen_input_fuzzy_match)
        self.enumvar3.bind('<Button-1>', self.var3chosen_input_fuzzy_match)
        self.enumvar4.bind('<Button-1>', self.var4chosen_input_fuzzy_match)

        self.window.update()

    # 配置_创建 确认按钮
    def config_button_confirm(self,):
        # 注： 通过给以下4个Button控件中参数command绑定回调函数的方式，程序会报错，暂时不知道什么原因。如果只给一个Button的command参数赋值的话则不会报错
        self.confirm1 = tkinter.Button(self.window, relief='raised', text='Level1确认')
        self.confirm1.bind("<Button-1>", self.confirm1_callback)

        self.confirm2 = tkinter.Button(self.window, text='Level2确认')
        self.confirm2.bind("<Button-1>", self.confirm2_callback)

        self.confirm3 = tkinter.Button(self.window, text='Level3确认')
        self.confirm3.bind("<Button-1>", self.confirm3_callback)

        self.confirm4 = tkinter.Button(self.window, text='Level4确认')
        self.confirm4.bind("<Button-1>", self.confirm4_callback)

        self.confirm1.place(relx=0.5, rely=0.15)
        self.confirm2.place(relx=0.5, rely=0.35)
        self.confirm3.place(relx=0.5, rely=0.55)
        self.confirm4.place(relx=0.5, rely=0.75)

    # 配置_文本框及下拉列表_枚举值输入，进制选择输入
    def config_text_input_value(self):
        self.inputval1.place(relx=0.5, rely=0.1, anchor=tkinter.NW)
        self.inputval2.place(relx=0.5, rely=0.3, anchor=tkinter.NW)
        self.inputval3.place(relx=0.5, rely=0.5, anchor=tkinter.NW)
        self.inputval4.place(relx=0.5, rely=0.7, anchor=tkinter.NW)

        self.radix1.place(relx=0.58, rely=0.1, anchor=tkinter.NW)
        self.radix2.place(relx=0.58, rely=0.3, anchor=tkinter.NW)
        self.radix3.place(relx=0.58, rely=0.5, anchor=tkinter.NW)
        self.radix4.place(relx=0.58, rely=0.7, anchor=tkinter.NW)

        # 设置下拉选项
        radixlist = ['HEX', 'DEC']
        self.radix1['value'] = radixlist
        self.radix2['value'] = radixlist
        self.radix3['value'] = radixlist
        self.radix4['value'] = radixlist

        # 设置默认显示的内容
        self.radix1.current(0)
        self.radix2.current(0)
        self.radix3.current(0)
        self.radix4.current(0)

    # 配置_文本框_结果显示
    def config_text_result(self):
        self.result1.place(relx=0.65, rely=0.1, anchor=tkinter.NW)
        self.result2.place(relx=0.65, rely=0.3, anchor=tkinter.NW)
        self.result3.place(relx=0.65, rely=0.5, anchor=tkinter.NW)
        self.result4.place(relx=0.65, rely=0.7, anchor=tkinter.NW)

    # 用户输入字符串后按下左键产生模糊匹配列表-按下左键
    def var1chosen_input_fuzzy_match(self, sequence=None):
        self.enumvar1['value'] = fuzzyfinder.fuzzyfinder(self.enumvar1.get(), self.enummanage.get_enumname_list())
        return sequence

    def var2chosen_input_fuzzy_match(self, sequence=None):
        self.enumvar2['value'] = fuzzyfinder.fuzzyfinder(self.enumvar2.get(), self.enummanage.get_enumname_list())
        return sequence

    def var3chosen_input_fuzzy_match(self, sequence=None):
        self.enumvar3['value'] = fuzzyfinder.fuzzyfinder(self.enumvar3.get(), self.enummanage.get_enumname_list())
        return sequence

    def var4chosen_input_fuzzy_match(self, sequence=None):
        self.enumvar4['value'] = fuzzyfinder.fuzzyfinder(self.enumvar4.get(), self.enummanage.get_enumname_list())
        return sequence

    def combo1_input_fuzzy_match(self, combobox, enumname, sequence=None):
        combobox['value'] = fuzzyfinder.fuzzyfinder(enumname.get(), self.enummanage.get_enumname_list())
        return sequence

    """
    确认按钮的回调函数
    """
    # 确认按钮1的回调函数
    def confirm1_callback(self, sequence=None):
        # 查询数据库，并显示结果
        selectedenumvar = self.enumvarchosen1.get()
        # 由于Combobox可写，需要检查用户输入的正确性
        if selectedenumvar not in self.enummanage.get_enumname_list():
            self.result1.delete(0.0, "end")
            self.result1.insert(0.0, "枚举变量名输入有误，请检查并重新输入！")
            return sequence
        inputenumval = self.inputval1.get(0.0, "end")
        if self.radixvalue1.get() == 'HEX':
            radix = 16
        elif self.radixvalue1.get() == 'DEC':
            radix = 10
        else:
            radix = 16
        try:
            decval = int(inputenumval, radix)
        except ValueError:
            messagebox.showerror("错误", "当前进制与输入值不匹配或是没有输入值，请检查输入和进制。")
            return sequence

        self.result1.delete(0.0, "end")
        self.result1.insert(0.0, self.enummanage.db_lookup_enum(selectedenumvar, decval))

        # 还可以根据此处输入的值，来决定下一层combobox显示的默认值
        if self.enummanage.is_enumname_exist_in_enumhierarchy(selectedenumvar):
            # 字典结构
            enumhierarchy=self.enummanage.read_file_enumhierarchy(selectedenumvar)[1]
            for k in enumhierarchy:
                if(int(k,16) == int(inputenumval,16)):
                    val = enumhierarchy[k]
                    enumname_list = self.enummanage.get_enumname_list()
                    count = 0
                    for element in enumname_list:
                        if val == element:
                            self.enumvar2.current(count)
                            return sequence
                        count = count+1

    # 确认按钮2的回调函数
    def confirm2_callback(self, sequence=None):
        # 查询数据库，并显示结果
        selectedenumvar = self.enumvarchosen2.get()
        # 由于Combobox可写，需要检查用户输入的正确性
        if selectedenumvar not in self.enummanage.get_enumname_list():
            self.result2.delete(0.0, "end")
            self.result2.insert(0.0, "枚举变量名输入有误，请检查并重新输入！")
            return sequence
        inputenumval = self.inputval2.get(0.0, "end")
        if self.radixvalue2.get() == 'HEX':
            radix = 16
        elif self.radixvalue2.get() == 'DEC':
            radix = 10
        else:
            radix = 16
        try:
            decval = int(inputenumval, radix)
        except ValueError:
            messagebox.showerror("错误", "当前进制与输入值不匹配或是没有输入值，请检查输入和进制。")
            return sequence

        self.result2.delete(0.0, "end")
        self.result2.insert(0.0, self.enummanage.db_lookup_enum(selectedenumvar, decval))

        # 还可以根据此处输入的值，来决定下一层combobox显示的默认值
        if self.enummanage.is_enumname_exist_in_enumhierarchy(selectedenumvar):
            # 字典结构
            enumhierarchy=self.enummanage.read_file_enumhierarchy(selectedenumvar)[1]
            for k in enumhierarchy:
                if(int(k,16) == int(inputenumval,16)):
                    val = enumhierarchy[k]
                    enumname_list = self.enummanage.get_enumname_list()
                    count = 0
                    for element in enumname_list:
                        if val == element:
                            self.enumvar3.current(count)
                            return sequence
                        count = count+1

    # 确认按钮3的回调函数
    def confirm3_callback(self, sequence=None):
        # 查询数据库，并显示结果
        selectedenumvar = self.enumvarchosen3.get()
        # 由于Combobox可写，需要检查用户输入的正确性
        if selectedenumvar not in self.enummanage.get_enumname_list():
            self.result3.delete(0.0, "end")
            self.result3.insert(0.0, "枚举变量名输入有误，请检查并重新输入！")
            return sequence
        inputenumval = self.inputval3.get(0.0, "end")
        if self.radixvalue3.get() == 'HEX':
            radix = 16
        elif self.radixvalue3.get() == 'DEC':
            radix = 10
        else:
            radix = 16
        try:
            decval = int(inputenumval, radix)
        except ValueError:
            messagebox.showerror("错误", "当前进制与输入值不匹配或是没有输入值，请检查输入和进制。")
            return sequence

        self.result3.delete(0.0, "end")
        self.result3.insert(0.0, self.enummanage.db_lookup_enum(selectedenumvar, decval))

        # 还可以根据此处输入的值，来决定下一层combobox显示的默认值
        if self.enummanage.is_enumname_exist_in_enumhierarchy(selectedenumvar):
            # 字典结构
            enumhierarchy=self.enummanage.read_file_enumhierarchy(selectedenumvar)[1]
            for k in enumhierarchy:
                if(int(k,16) == int(inputenumval,16)):
                    val = enumhierarchy[k]
                    enumname_list = self.enummanage.get_enumname_list()
                    count = 0
                    for element in enumname_list:
                        if val == element:
                            self.enumvar4.current(count)
                            return sequence
                        count = count+1

    # 确认按钮4的回调函数
    def confirm4_callback(self, sequence=None):
        # 查询数据库，并显示结果
        selectedenumvar = self.enumvarchosen4.get()
        # 由于Combobox可写，需要检查用户输入的正确性
        if selectedenumvar not in self.enummanage.get_enumname_list():
            self.result3.delete(0.0, "end")
            self.result3.insert(0.0, "枚举变量名输入有误，请检查并重新输入！")
            return sequence
        inputenumval = self.inputval4.get(0.0, "end")
        if self.radixvalue4.get() == 'HEX':
            radix = 16
        elif self.radixvalue4.get() == 'DEC':
            radix = 10
        else:
            radix = 16
        try:
            decval = int(inputenumval, radix)
        except ValueError:
            messagebox.showerror("错误", "当前进制与输入值不匹配或是没有输入值，请检查输入和进制。")
            return sequence

        self.result4.delete(0.0, "end")
        self.result4.insert(0.0, self.enummanage.db_lookup_enum(selectedenumvar, decval))
        return sequence

    """
    “文件”菜单栏下拉列表中的各个回调函数
    """
    def dropdown_menu1_end_program(self):
        self.window.quit()
        return

    def dropdown_menu1_open_config_file(self, filename):
        file_full_path = os.path.dirname(__file__) + '\\Config\\' + filename + '.txt'
        os.popen(file_full_path)
        return

    """
    “数据”菜单栏下拉列表中的各个回调函数
    """
    # 更新数据库 回调函数
    def dropdown_menu2_update_db(self):
        # res非空的话，说明有个枚举变量配置出错，res就是出错的变量，会提示用户
        try:
            res = self.enummanage.db_refresh_enum()
            if not res:
                messagebox.showinfo(title="完成", message="数据库更新完毕。")
            else:
                # 提示用户枚举变量的路径出错，找不到该文件
                messagebox.showerror(title="路径配置出错", message="枚举变量" + res + "的路径配置错误，找不到其所在头文件，请检查该路径配置！")
        except Exception as result:
            messagebox.showerror(title="更新数据库时发生异常，详情如下：", message=result)
            return

    # 清空数据库 回调函数
    def dropdown_menu2_clean_db(self):
        self.enummanage.db_cleanup_enum()
        messagebox.showinfo(title="完成", message="数据库清空完毕。")
        return

    # 增加枚举 回调函数
    def dropdown_menu2_add_enum(self):
        enumname = tkinter.StringVar()
        enumpath = tkinter.StringVar()
        subenum = tkinter.StringVar()
        tpl = tkinter.Toplevel()
        tpl.title('增加枚举')
        tpl.resizable(1, 1)
        tpl.geometry('700x200+500+100')
        label1 = tkinter.Label(tpl, text='请输入新增的枚举变量名：', font=("Arial,15"))
        label1.place(relx=0.05, rely=0.05, anchor=tkinter.NW)

        entry1 = tkinter.Entry(tpl, textvariable=enumname, width=55)
        entry1.place(relx=0.34, rely=0.05, anchor=tkinter.NW)

        label2 = tkinter.Label(tpl, text='输入变量所在的头文件的完整路径（已知项目路径情况下，可只填写头文件名）：', font=("Arial,15"))
        label2.place(relx=0.05, rely=0.20, anchor=tkinter.NW)

        entry2 = tkinter.Entry(tpl, textvariable=enumpath, width=84)
        entry2.place(relx=0.05, rely=0.32, anchor=tkinter.NW)

        label3 = tkinter.Label(tpl, text='请输入该变量在头文件中的各子枚举变量名（有多个的话用逗号隔开）：', font=("Arial,15"))
        label3.place(relx=0.05, rely=0.47, anchor=tkinter.NW)

        entry3 = tkinter.Entry(tpl, textvariable=subenum, width=84)
        entry3.place(relx=0.05, rely=0.59, anchor=tkinter.NW)

        button1 = tkinter.Button(tpl, text='Ok', command=lambda: self.dropdown_menu2_add_enum_sub_callback(tpl, enumname, enumpath, subenum))
        button1.place(relx=0.05, rely=0.80, anchor=tkinter.NW, width=80, height=30)

        button2 = tkinter.Button(tpl, text='Cancel', command=tpl.destroy)
        button2.place(relx=0.55, rely=0.80, anchor=tkinter.NW, width=80, height=30)

    def dropdown_menu2_add_enum_sub_callback(self, tpl, enumname, enumpath=None, subenum=None):
        if not enumname.get():
            messagebox.showinfo("错误", "您没有选择枚举来进行修改！")
            return

        subenumlist = []
        if subenum.get():
            subenumlist = re.findall("[A-Za-z_0-9]+", subenum.get())
        enumname = enumname.get()
        enumpath = enumpath.get()
        if not self.enummanage.add_enum(enumname, subenumlist, enumpath):
            messagebox.showinfo("失败", "添加失败，已经有该枚举量了！")
        else:
        # 刷新一下枚举变量
            self.enumname_list = self.enummanage.get_enumname_list()
            messagebox.showinfo("完成", "新的枚举量添加完毕！")
        tpl.destroy()

    # 删除枚举 回调函数
    def dropdown_menu2_delete_enum(self):
        enumname = tkinter.StringVar()

        tpl = tkinter.Toplevel()
        tpl.title('增加枚举')
        tpl.resizable(1, 1)
        tpl.geometry('500x150+500+100')

        label1 = tkinter.Label(tpl, text='请选择要删除的变量名：', font=("Arial,15"))
        label1.place(relx=0.05, rely=0.05, anchor=tkinter.NW)

        # Combobox只读，防止用户删除不存在的枚举变量，删除枚举变量本身就是一件很谨慎的事情
        combo1 = tkinter.ttk.Combobox(tpl, state='readonly', width=50, textvariable=enumname)
        combo1.place(relx=0.05, rely=0.25, anchor=tkinter.NW)
        combo1['value'] = self.enumname_list

        button1 = tkinter.Button(tpl, text='Ok', command=lambda: self.dropdown_menu2_delete_enum_sub_callback(tpl, enumname))
        button1.place(relx=0.05, rely=0.55, anchor=tkinter.NW, width=80, height=30)

        button2 = tkinter.Button(tpl, text='Cancel', command=tpl.destroy)
        button2.place(relx=0.55, rely=0.55, anchor=tkinter.NW, width=80, height=30)

    def dropdown_menu2_delete_enum_sub_callback(self, tpl, enumname):
        if not enumname.get():
            messagebox.showinfo("失败", "您没有选择要删除的枚举变量!")
        else:
            self.enummanage.delete_enum(enumname.get())
            self.enumname_list = self.enummanage.get_enumname_list()
            messagebox.showinfo("完成", "枚举量删除完毕！")
        tpl.destroy()

    # 修改枚举 回调函数
    def dropdown_menu2_modify_enum(self):
        enumname = tkinter.StringVar()
        enumpath = tkinter.StringVar()
        subenum = tkinter.StringVar()

        tpl = tkinter.Toplevel()
        tpl.title('增加枚举')
        tpl.resizable(1, 1)
        tpl.geometry('600x300+500+100')

        label1 = tkinter.Label(tpl, text='请选择要修改的变量名：', font=("Arial,15"))
        label1.place(relx=0.05, rely=0.05, anchor=tkinter.NW)

        # Combobox只读，防止用户修改不存在的枚举变量，修改枚举变量本身就是一件很谨慎的事情
        combo1 = tkinter.ttk.Combobox(tpl, state='readonly', width=35, textvariable=enumname)
        combo1.place(relx=0.05, rely=0.14, anchor=tkinter.NW)
        combo1['value'] = self.enumname_list

        label2 = tkinter.Label(tpl, text='请输入修改后的头文件路径：（不修改则为空）', font=("Arial,15"))
        label2.place(relx=0.05, rely=0.28, anchor=tkinter.NW)

        entry2 = tkinter.Entry(tpl, textvariable=enumpath, width=80)
        entry2.place(relx=0.05, rely=0.37, anchor=tkinter.NW)

        label3 = tkinter.Label(tpl, text='请输入修改后的各子枚举变量名,用逗号隔开（不修改则为空）：', font=("Arial,15"))
        label3.place(relx=0.05, rely=0.54, anchor=tkinter.NW)

        entry3 = tkinter.Entry(tpl, textvariable=subenum, width=80)
        entry3.place(relx=0.05, rely=0.63, anchor=tkinter.NW)

        button1 = tkinter.Button(tpl, text='Ok', command=lambda: self.dropdown_menu2_modify_enum_sub_callback(tpl, enumname, enumpath, subenum))
        button1.place(relx=0.05, rely=0.80, anchor=tkinter.NW, width=80, height=30)

        button2 = tkinter.Button(tpl, text='Cancel', command=tpl.destroy)
        button2.place(relx=0.55, rely=0.80, anchor=tkinter.NW, width=80, height=30)

    def dropdown_menu2_modify_enum_sub_callback(self, tpl, enumname, enumpath, subenum):
        if not enumname.get():
            messagebox.showinfo("错误", "您没有选择枚举来进行修改！")
            return
        if enumpath.get():
            self.enummanage.modify_enum_path(enumname.get(), enumpath.get())
        if subenum.get():
            subenumlist = []
            subenumlist = re.findall("[A-Za-z_0-9]+", subenum.get())
            self.enummanage.modify_enum_subenum(enumname.get(), subenumlist)
        messagebox.showinfo("完成", "枚举量"+enumname.get()+"修改完毕！")
        # 最好还可以显示一下修改的结果
        tpl.destroy()

    """
    “编辑”菜单栏下拉列表中的各个回调函数
    """
    def dropdown_menu3_env_path(self):
        path = self.enummanage.lookup_param(constant.param_key_envpath)
        if not path:
            path = "Null"
        e = tkinter.StringVar()
        # new一个toplevel的提示框
        # 完成向提示框中加入Entry、Button、Label的布局
        tpl = tkinter.Toplevel()
        tpl.title('项目路径')
        tpl.resizable(1, 1)
        tpl.geometry('460x200+500+100')
        label1 = tkinter.Label(tpl, text='当前项目路径为:', font=("Arial,15"))
        label2 = tkinter.Label(tpl, text=path, font=("Arial,15"))
        label3 = tkinter.Label(tpl, text='请输入新的项目路径:', font=("Arial,15"))
        label1.place(relx=0.05, rely=0.05, anchor=tkinter.NW)
        label2.place(relx=0.05, rely=0.15, anchor=tkinter.NW)
        label3.place(relx=0.05, rely=0.33, anchor=tkinter.NW)
        entry = tkinter.Entry(tpl, textvariable=e, width=55)
        entry.place(relx=0.05, rely=0.45, anchor=tkinter.NW)
        button2 = tkinter.Button(tpl, text='Ok', command=lambda: self.dropdown_menu3_env_path_sub_callback(tpl, e))
        button2.place(relx=0.05, rely=0.68, anchor=tkinter.NW, width=80, height=30)

    def dropdown_menu3_env_path_sub_callback(self, tpl, e):
        self.enummanage.put_param(constant.param_key_envpath, e.get())
        messagebox.showinfo("完成", "项目路径修改完毕，程序会在该路径下自动搜寻配置文件中指定的头文件！")
        tpl.destroy()

    def dropdown_menu3_log_analysis(self):
        tpl = tkinter.Toplevel()
        tpl.title('日志解析')
        tpl.resizable(1, 1)
        tpl.geometry('460x200+500+100')
        label1 = tkinter.Label(tpl, text='选择日志文件:', font=("Arial,15"))
        label1.place(relx=0.05, rely=0.05, anchor=tkinter.NW)
        button1 = tkinter.Button(tpl, text='选择文件', width=55, command=lambda: self.dropdown_menu3_log_analysis_sub_callback_filechoose(tpl, label2))
        button1.place(relx=0.05, rely=0.20, anchor=tkinter.NW)
        label2 = tkinter.Label(tpl, text="日志未选择", width=55)
        label2.place(relx=0.05, rely=0.40, anchor=tkinter.NW)

        button2 = tkinter.Button(tpl, text='开始解析', command=self.dropdown_menu3_log_analysis_sub_callback_beginanalysis)
        button2.place(relx=0.37, rely=0.60, anchor=tkinter.NW, width=80, height=30)

    def dropdown_menu3_log_analysis_sub_callback_filechoose(self, tpl, label):
        fd = filedialog.LoadFileDialog(tpl)
        label["text"] = fd.go()
        self.__logpath = label["text"]

    def dropdown_menu3_log_analysis_sub_callback_beginanalysis(self):
        isanalysishrcpp = False   # 是否解析HRCPP的标记变量
        try:
            # 0、解析HRCPP的准备工作
            if messagebox.askyesno("选择", "请问是否额外解析HRCPP opcode"):
                isanalysishrcpp = True
                head_file_name_list = constant.hrcpp_opcode_headfile_list
                head_file_path_list = []
                param_value_envpath = self.enummanage.lookup_param(constant.param_key_envpath)
                if param_value_envpath == None:
                    messagebox.showerror("错误", "没有配置项目路径，导致找不到HRCPP opcode头文件，请配置项目路径后再尝试。")
                    return
                for item in head_file_name_list:
                    found = searchfile.find(item, param_value_envpath)
                    if len(found) == 0:
                        messagebox.showerror("错误", "在项目路径下找不到HRCPP opcode头文件。请检查项目路径是否正确，或是头文件名的正确性。")
                        return
                    head_file_path_list.append(found[0])
                hm = hrcppmanager.HrcppManager(head_file_path_list)
                if not hm.check_DB_exists():
                    hm.retrieveandstore()

            if not messagebox.askokcancel("温馨提示", "日志解析时首先根据日志解析策略文件配置的进制进行数字解读，没有配置的话默认对数字采用16进制解读，请悉知！"):
                return

            # 1、检查路径下是否存在该文件
            if not os.path.exists(self.__logpath):
                messagebox.showerror("错误", "指定路径下找不到该日志文件")
                return

            # 2、读取待解析日志文件的所有内容
            try:
                logfile = open(self.__logpath, mode='r', encoding='utf-8')
                filelines = logfile.readlines()
                logfile.close()
            except UnicodeDecodeError:
                logfile = open(self.__logpath, mode='r', encoding='gbk')
                filelines = logfile.readlines()
                logfile.close()

            except Exception as result:
                messagebox.showerror(title="异常", message="读取文件时发生异常，请尝试将编码格式改为utf-8。异常详情如下："+str(result))
                return

            # 3、读取日志解析策略
            path = os.path.dirname(__file__) + constant.log_analysis_file_path_suffix
            strategyfile = open(path, mode='r', encoding='utf-8')
            content = strategyfile.read()
            strategyfile.close()
            strategymap = {}  # 解析策略存放到map中，key是用户指定要解析的flag， value枚举变量名
            pattern = "\s*\[\s*([\._a-zA-Z0-9]*)\s*\]\s*=\s*([\._a-zA-Z0-9]*)\s*=\s*([0-9]*)"
            for item in re.findall(pattern, content):
                key = item[1]     #要解析的字符串
                value = item[0]   #对应枚举
                radix = item[2]   #进制

                # 检测读取到的进制值是否有误,如果没有配置，默认16进制
                try:
                    if radix == None:
                        radix = 16
                    else:
                        if int(radix, 10) != 10 and int(radix, 10) != 16:
                            raise ValueError
                except ValueError:
                    messagebox.showerror("错误", key + "的进制配置错误，请检查日志解析策略文件，请输入16或者10")
                    return

                lst = [value, int(radix, 10)]
                strategymap[key] = lst

            # 4、解析日志各行，进行枚举数值的释义添加
            count = 0
            for line in filelines:

                # 5、解析HRPP opcode
                hrcpp_reg_str_1 = "Rev App Data\s*:\s*0A\s0B\s([0-9a-zA-Z\s]{11})"  # 依赖日志打印内容，以后考虑提取出来
                if isanalysishrcpp:
                    hrcpp_match = re.search(hrcpp_reg_str_1, line)
                    if hrcpp_match:
                        raw_opcode = hrcpp_match.group(1)
                        opcode = "0x" + str.lower(raw_opcode.replace(" ", ''))  # 去掉空格，字母最小化
                        try:
                            hrcpp_str = hm.lookupDB(opcode)
                            str_list = list(line)
                            nPos = str_list.index('\n')
                            str_list.insert(nPos, " // " + hrcpp_str)
                            str2 = "".join(str_list)
                            filelines[count] = str2
                        except KeyError:
                            pass

                # 6、解析枚举值
                for key in strategymap:
                    # 获取枚举变量名,进制
                    enumname = strategymap[key][0]
                    enumradix = strategymap[key][1]

                    # 根据进制选择正则匹配字符串
                    if enumradix == 10:
                        reg_str = "[\s\(\[=]*([0-9a-zA-Z]*)[\s\]\)]*"
                    elif enumradix == 16:
                        reg_str = "[\s\(\[=]*[0xX]*([0-9a-zA-Z]*)[\s\]\)]*"
                    else:
                        messagebox.showerror("错误", traceback.print_exc())
                        return

                    match = re.search(key+reg_str, line)
                    if match:
                        # 根据匹配结果查询 枚举字符串
                        enumval = match.group(1)

                        # 16进制时，对于0的情况会出现ValueError，这里特殊处理一下
                        try:
                            decval = int(enumval, enumradix)
                        except ValueError:
                            deval = 0

                        # 获取枚举值的释义字符串
                        try:
                            enumstr = self.enummanage.pure_lookup_enumdb(enumname, decval)
                        except KeyError:
                            messagebox.showerror("错误", "数据库中无法检索到"+key+":("+match.group(1)+")相应枚举字符串，请检查配置文件并更新数据库")
                            return

                        # 将枚举字符串 作为注释插入该行
                        str_list = list(line)
                        nPos = str_list.index('\n')
                        str_list.insert(nPos, " // "+enumstr)
                        str2 = "".join(str_list)
                        filelines[count] = str2
                        break
                count = count + 1

            # 7、解析后结果写入一份新的日志文件，与之前日志文件用后缀加以区分，在同一路径下，这里就指定固定路径下，固定带时间戳后缀名的log
            ts = time.strftime('%y%m%d%H%M%S')
            outputpath = "D:\\LogParsed"+str(ts)+".txt"
            fd = open(outputpath, mode='w+', encoding='utf-8')
            fd.write("".join(filelines))

            # 8、弹框提示用户解析完成
            messagebox.showinfo("完成", "解析完成，请在路径"+outputpath+"下查看")

        except Exception as result:
            messagebox.showerror(title="异常", message="解析日志发生异常，异常详情如下：" + str(result)+line)
            traceback.print_exc()
            return
        return

    def dropdown_menu4_help(self):
        file_full_path = os.path.dirname(__file__) + constant.notation_file_path_suffix
        fd = open(file_full_path, mode='r', encoding='utf-8')
        context = fd.read()
        fd.close()
        messagebox.showinfo("注意事项", context)

    # 将所有组件的配置和设置封装一下
    def config_window(self):
        self.config_menu()
        self.config_label()
        self.config_combobox_input_enum()
        self.config_text_input_value()
        self.config_text_result()
        self.config_button_confirm()

    # 调用该方法_运行窗体
    def run(self):
        self.config_window()
        self.window.mainloop()


if __name__ == '__main__':
    window = UIManager()
    window.run()
