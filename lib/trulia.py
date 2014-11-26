##encoding=utf8

from __future__ import print_function
from .crawler import Crawler
from bs4 import BeautifulSoup as BS4
import re

class Parser(object):
    """Parser is a html analysis object to extract information from html
    """
    def _digital_filter(self, text):
        """摘出文本内所有0-9数字的部分"""
        res = list()
        for char in text:
            if char.isdigit():
                res.append(char)
        return "".join(res)    

    def _address_parser(self, address_fields):
        """解析街道信息, 稳定输出, 不会有异常"""
        
        try:
            address, city, state, zipcode = (address_fields[0],
                                             address_fields[1],
                                             address_fields[2],
                                             address_fields[3])
            return address, city, state, zipcode
        except:
            return "unknown", "unknown", "unknown", "unknown"
        
    def _feature_parser(self, features):
        """解析feature信息, 稳定输出, 不会有异常"""
        price, sqft, lot_size, bedroom, bathroom, status, heating, exterior_walls, build_year = ("unknown", 
                                                                    "unknown", 
                                                                    "unknown", 
                                                                    "unknown", 
                                                                    "unknown", 
                                                                    "unknown", 
                                                                    "unknown",
                                                                    "unknown",
                                                                    "unknown", )
        
        for field in features:
            field = field.lower()
            ## 价格
            if "price" in field:
                price = self._digital_filter(field)
                continue
            ## 面积
            elif ("sqft" in field) and ("lot size" not in field):
                sqft = self._digital_filter(field)
                continue
            ## 院子面积
            elif ("sqft" in field) and ("lot size" in field):
                lot_size = self._digital_filter(field)
                continue
            ## 卧室
            elif "bedroom" in field:
                bedroom = self._digital_filter(field)
                continue
            ## 洗手间
            elif "bathroom" in field:
                bathroom = self._digital_filter(field)
                continue
            ## 市场状态
            elif "status" in field:
                status = field.split(":")[-1].strip()
                continue
            ## 供暖方式
            elif "heating" in field:
                heating = field.split(":")[-1].strip()
                continue
            ## 外墙
            elif "exterior walls" in field:
                exterior_walls = field.split(":")[-1].strip()
                continue
            ## 建造年份
            elif "built in" in field:
                build_year = self._digital_filter(field)
                continue
        return price, sqft, lot_size, bedroom, bathroom, status, heating, exterior_walls, build_year
    
    def _schools_info_parser(self, schools_info):
        try:
            num_highschool = self._digital_filter(schools_info[2])
            num_midschool = self._digital_filter(schools_info[3])
            num_elementaryschool = self._digital_filter(schools_info[4])
            return num_highschool, num_midschool, num_elementaryschool
        except:
            return -1, -1, -1
        
    def property_page(self, html):
        """property info extractor
        extract detail info from HTML
        """
        soup = BS4(html)
        
        ## === address, city, state,
        address_field = list()
        try:
            h1 = soup.find("h1", itemprop = "address")
            for span in h1.find_all("span"):
                if span.string:
                    address_field.append(span.string.strip())
        except:
            pass
        
        ## === features and public record
        features = list()
        try: ## === features
            ul = soup.find("ul", class_ = "listInline pdpFeatureList")
            for li in ul.find_all("li"):
                if len(li.attrs) == 0:
                    features.append(li.text.strip())
        except:
            pass
        
        try: ## === public record
            ul = soup.find("ul", class_ = "listInline mbn pdpFeatureList")
            for li in ul.find_all("li"):
                if len(li.attrs) == 0:
                    features.append(li.text.strip())
        except:
            pass
        
        ## === school
        schools_info = list()
        try:
            div = soup.find("div", class_ = "mediaBody  pls ptm pln")
            for p in div.find_all("p"):
                schools_info.append(p.text.strip())
        except:
            pass
    
        print(address_field)
        print(features)
        print(schools_info)
        
        ## === validate result, if result valid, then return, if not, raise error
        if (len(address_field) > 0) and (len(features) > 0): # 如果都有数据
            
            address, city, state, zipcode = self._address_parser(address_field)
            price, sqft, lot_size, bedroom, bathroom, status, heating, exterior_walls, build_year = self._feature_parser(features)
            num_highschool, num_midschool, num_elementaryschool = self._schools_info_parser(schools_info)
            
            return address, city, state, zipcode, \
                price, sqft, lot_size, bedroom, bathroom, status, heating, exterior_walls, build_year, \
                num_highschool, num_midschool, num_elementaryschool
            
        else: # 抛出异常
            raise Exception("Failed to extract info.")
        
class Query(object):
    """
    """
    def __init__(self, testmode = False):
        self.spider = Crawler()
        if not testmode:
            self.spider.enable_proxy(100)
            try:
                spider.pm.load__pxy()
            except:
                pass

    def _gen_url(self, address, city_or_zipcode, status = "for_sale"):
        if status in {"for_sale", "for_rent", "sold"}:
            if status == "for_sale":
                display1, display2, tst = "for_sale", "for+sale", "h"
            elif status == "for_rent":
                display1, display2, tst = "for_rent", "for+rent", "r"
            elif status == "sold":
                display1, display2, tst = "sold", "sold", "h"
    
            return ("http://www.trulia.com/submit_search/?display=%s&search=%s&locationId="
                    "&locationType=&tst=%s&ac_entered_query=&ac_index=&propertyId=&propertyIndex="
                    "&display=%s" % (display1, 
                                     " ".join([address, city_or_zipcode]).replace(" ", "+"), 
                                     tst,
                                     display2 ) )
        else:
            raise Exception("search type error.")

    def by_address_zipcode(self, address, city_or_zipcode):
        return self.spider.html(self._gen_url(address, city_or_zipcode) )
    
    