##encoding=utf8

from __future__ import print_function
from lib import *
import pandas as pd, numpy as np

def batch():
    parser = Parser()
    spider = Crawler()
    spider.enable_proxy(100)
    try:
        spider.pm.load__pxy()
    except:
        pass
    
    
    df = pd.read_csv("address.txt", sep = "\t", header = 0, index_col = False, dtype = {"PostalCode" : np.str})
    
    def gen_url(address, city_or_zipcode, status):
        return "http://www.trulia.com/submit_search/?display=%s&search=%s&locationId=&locationType=&tst=h&ac_entered_query=&ac_index=&propertyId=&propertyIndex=&display=%s" % (status, 
                                                                                                                                                                                " ".join([address, zipcode]).replace(" ", "+"), 
                                                                                                                                                                                status.replace("_", "+") )
    
    for address, zipcode in df.loc[:, ["Address", "PostalCode"]].values:
        url = gen_url(address, zipcode, "for_sale")
        print(url, address, zipcode)
        html = spider.html(url)
        print(parser.property_page(html))
        break
# address, zipcode, status, display = "2330 S Ode St", "22202", "for_sale", "for+sale"
# address, zipcode, status, display = "412 crestview dr", "21532", "for_sale", "for+sale"

def query_one(address, zipcode):
    query = Query(testmode=True)
    parser = Parser()
    html = query.by_address_zipcode(address, zipcode)
    print(parser.property_page(html))
    
query_one("2330 S Ode St", "22202")