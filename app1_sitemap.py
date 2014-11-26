##encoding=utf8

from __future__ import print_function
from lib import *

parser = Parser()
spider = Crawler()
spider.enable_proxy(100)
try:
    spider.pm.load__pxy()
except:
    pass