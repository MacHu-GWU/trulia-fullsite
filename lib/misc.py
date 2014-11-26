##################################
#encoding=utf8                   #
#version =py27, py33             #
#author  =sanhe                  #
#date    =2014-10-29             #
#                                #
#    (\ (\                       #
#    ( -.-)o    I am a Rabbit!   #
#    o_(")(")                    #
#                                #
##################################

from __future__ import print_function
import time
import sys

def sleep(n):
    time.sleep(n)
    
def tryit(howmany, func, *argv, **kwarg):
    """这个函数使用了一个重要的技巧将原函数的参数原封不动的封装成tryit这个函数的参数了
    用户只要跟使用func原函数一样使用tryit函数就好了，只不过在前面多了两个howmany和func的参数
        howmany 是尝试次数
        func 是你所要尝试的函数
        *argv, **kwarg 是func中的参数
        
    func函数一定要有如下特点：
        如果能正常运行，说明一定其中没有异常。
        如果有异常，一定要抛出异常，打断函数
    """
    flag = 1
    while flag <= howmany:
        try:
            return func(*argv, **kwarg)
        except Exception as e:
            current_error = e
            flag += 1            
    raise current_error