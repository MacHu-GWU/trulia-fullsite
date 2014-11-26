##encoding=utf8

from __future__ import print_function
from lib import *
from bs4 import BeautifulSoup as BS4
import sqlite3
import math
import re

dbpath = "trulia.db"
conn = sqlite3.connect(dbpath)
c = conn.cursor()
        
class TruliaFullsite(object):
    def __init__(self):
        self.spider = Crawler()
        self.base_url = "http://www.trulia.com"
        self.entrance = "http://www.trulia.com/sitemap/"
        self.pathtree = dict()
        self.log = Log()        
        self.spider.enable_proxy()
        
    def ld(self):
        self.pathtree = load_js("pathtree.json")
        
    def dp(self):
        dump_js(self.pathtree, "pathtree.json", fastmode = False, replace = True)

    def _digital_filter(self, text):
        """摘出文本内所有0-9数字的部分"""
        res = list()
        for char in text:
            if char.isdigit():
                res.append(char)
        return "".join(res)
    
    def _pathfinder_state(self):
        html = self.spider.html(self.entrance)
        if html:
            soup = BS4(html)
            div = soup.find("div", style = "float:left;width:480px;")
            for a in div.find_all("a"):
                self.pathtree.setdefault(self.base_url + a["href"], 
                                         {"ref": {"state_name" : a.text.strip()} } )
    
    def _pathfinder_city(self):
        for state_url in self.pathtree:
            for url in ["%s%s/" % (state_url, char) for char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"]:
                print(url)
                if len(self.pathtree[state_url]) <= 300:
                    try:
                        html = self.spider.html(url)
                        if html:
                            soup = BS4(html)
                            div = soup.find("div", style = "float:left;width:480px;")
                            
                            a_list = div.find_all("a")
                            span_list = div.find_all("span", class_ = "tiny")
                            
                            for a, span in zip(a_list, span_list):
                                self.pathtree[state_url].setdefault(
                                                                    self.base_url + a["href"], 
                                                                    {
                                                                     "ref": {
                                                                             "city_name" : a.text.strip(),
                                                                             "results_num" : int(self._digital_filter(span.text.strip()))
                                                                             } 
                                                                     } 
                                                                    )
                    except Exception as e:
                        self.log.write("%s" % e, "%s" % url)
            self.dp()
    
    
    def _report(self):
        city_num, property_num = 0, 0
        for state_url in self.pathtree:
            city_num_in_state = len(self.pathtree[state_url]) - 1
            state_name = self.pathtree[state_url]["ref"]["state_name"]
            city_num += city_num_in_state
            
            print("%s %s" % (state_name, city_num_in_state))
            
            for city_url in ignore_iterkeys(self.pathtree[state_url]):
                property_num_in_city = self.pathtree[state_url][city_url]["ref"]["results_num"]
                property_num += property_num_in_city
                
        print("city number = %s" % city_num)
        print("property number = %s" % property_num)
        


if __name__ == "__main__":
    def taskplan_crawl():
        tru = TruliaFullsite()
        tru.ld()
        
        ## === 开始爬
        tru._pathfinder_state()     # 爬下所有state_url
        tru._pathfinder_city()      # 爬下所有city_url
        
        tru._report()
        
#     taskplan_crawl()

    def task_to_db():
        """得到所有51个州和19982个城市的排列组合，并存入数据库
        """
        
        try:
            c.execute("""CREATE table city_and_state (state TEXT, city TEXT, 
            for_sale INTEGER, for_rent INTEGER, sold INTEGER, PRIMARY KEY (state, city) );""")
        except:
            pass
        
        try:
            c.execute("CREATE table property_url (url TEXT, state TEXT, city TEXT, PRIMARY KEY (url));")
        except:
            pass
        
        pathtree = load_js("pathtree.json")
        for state_url in pathtree:
            for city_url in ignore_iterkeys(pathtree[state_url]):
                state, city = city_url.split("/")[-3:-1]
                try:
                    c.execute("INSERT INTO city_and_state VALUES (?,?,?,?,?)", (state, city, 0, 0, 0))
                except:
                    pass
        conn.commit()
        
#     task_to_db()

    def reset_tast():
        c.execute("UPDATE city_and_state SET for_sale = 0 WHERE for_sale = 1;")
        c.execute("UPDATE city_and_state SET for_rent = 0 WHERE for_rent = 1;")
        c.execute("UPDATE city_and_state SET sold = 0 WHERE sold = 1;")
        conn.commit()
        
    reset_tast()
    
    def get_property_url():
        log = Log()
        spider = Crawler()
        spider.enable_proxy()
        for keyword in ["for_rent", "sold","for_sale"]:
            print("{:=^100}".format(keyword))
            c.execute("""SELECT state, city FROM city_and_state WHERE {0} = 0 AND (state = 'CA' OR state = 'TX');
            """.format(keyword))
            
            for state, city in c.fetchall():
                query_url = "http://www.trulia.com/%s/%s,%s" % (keyword, city, state)
                print(query_url)
#                 sleep(2)
                
                html = spider.html(query_url)
                
                try: # 试试看第一个页面http请求是否返回了html
                    
                    soup = BS4(html)
                
                    try: # 既然返回了html，再试试看是不是一个有效包含了很多pages的页面
                        div = soup.find("div", class_ = "srpPagination")
                        sub_div = div.find("div", class_ = "col cols16 mts txtC srpPagination_list")
                        pages = list()
                        pages.append(int(sub_div.span.text))
                        for a in sub_div.find_all("a"):
                            pages.append(int(a.text))
                        num_of_pages = max(pages)
                        
                        try: # 试着解析每一页上的房产url地址
                            for url in ["%s/%s_p" % (query_url, i+1) for i in range(num_of_pages)]:
                                print("\t", url)
                                html = spider.html(url, lock_proxy = True)
                                soup = BS4(html)
                                for li in soup.find_all("li", id = "propertyAnchor_"):
                                    a = li.find("a", class_ = re.compile(r"primaryLink[\s\S]*"))
                                    property_url = "http://www.trulia.com" + a["href"]
                                    try:
                                        c.execute("INSERT INTO property_url VALUES (?,?,?)", (property_url, state, city))
                                    except:
                                        pass
                                    
                            c.execute("""UPDATE city_and_state SET {0} = 1 
                            WHERE state = '{1}' AND city ='{2}';""".format(keyword, state, city))
                            print("\tSUCCESS, all records have been downloaded.")
                            spider.pm.update_health(1)
                            
                        except:
                            log.write("Failed at downloading pages", query_url)
                            spider.pm.update_health(0)
                        
                    except: # 好像不是包含了很多pages的页面，试试看是不是搜索结果为空的页面；如果是，则算成功了。则更新状态，直接跳出循环
                        res = soup.find_all("div", class_ = "boxBody txtC pvl")
                        if len(res) == 2: # 结果为空
                            c.execute("""UPDATE city_and_state SET {0} = 1 
                            WHERE state = '{1}' AND city ='{2}';""".format(keyword, state, city))
                            print("\tSUCCESS, it is an empty results page.")
                            spider.pm.update_health(1) # 代理好评
                        else: # 错误页面，算失败
                            log.write("Failed at blocked page.", query_url)
                            spider.pm.update_health(0) # 说明被block了，代理差评
                            
                except: # 没有正常返回html
                    log.write("Failed at first http request.", query_url)
                    spider.pm.update_health(0) # 说明被block了，代理差评
                    
                conn.commit()
                
#                 with open("%s_%s.html" % (city, state), "w") as f:
#                     f.write(str(html))
                    
                with open("proxy.txt", "w") as f:
                    f.write(str(spider.pm.proxy))
                    
    get_property_url()