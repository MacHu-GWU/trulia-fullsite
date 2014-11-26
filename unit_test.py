##encoding=utf8

from __future__ import print_function
from lib import *

address, zipcode = "5908 Sonoma Rd", "20817"
query, parser = Query(testmode = True), Parser()

print(query._gen_url(address, zipcode))

html = query.by_address_zipcode(address, zipcode)

print(parser.property_page(html))

# http://www.trulia.com/submit_search/?display=for_sale&search=5908+Sonoma+Rd+20817&locationId=&locationType=&tst=h&ac_entered_query=&ac_index=&propertyId=&propertyIndex=&display=for+sale
# http://www.trulia.com/submit_search/?display=for_rent&search=5908+Sonoma+Rd+20817&locationId=&locationType=&tst=r&ac_entered_query=&ac_index=&propertyId=&propertyIndex=&display=for+rent
# http://www.trulia.com/submit_search/?display=sold&search=5908+Sonoma+Rd+20817&locationId=&locationType=&tst=h&ac_entered_query=&ac_index=&propertyId=&propertyIndex=&display=sold