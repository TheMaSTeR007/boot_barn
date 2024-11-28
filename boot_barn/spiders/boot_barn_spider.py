from boot_barn.items import BootBarnItem
from scrapy.cmdline import execute
from boot_barn import db_config
from typing import Iterable
from scrapy import Request
import lxml.html
import pymysql
import scrapy


def get_store_state(store_info_selector) -> str:
    state_name = ' '.join(store_info_selector.xpath('.//span[@class="store-address-state"]//text()'))
    return state_name if state_name not in ['', ' '] else 'N/A'


def get_store_url(store_selector) -> str:
    url_slug = ' '.join(store_selector.xpath('.//div[@class="city"]/a/@href'))
    store_url = 'https://www.bootbarn.com' + url_slug
    return store_url if url_slug not in ['', ' '] else 'N/A'


def get_store_no(store_selector) -> str:
    store_no = ' '.join(store_selector.xpath('.//@store-id'))
    return store_no if store_no not in ['', ' '] else 'N/A'


def get_store_name(parsed_hmtl) -> str:
    store_name = ' '.join(parsed_hmtl.xpath('//h1[@class="section-title"]/text()'))
    return store_name if store_name not in ['', ' '] else 'N/A'


def get_store_street(store_info_selector) -> str:
    address1 = ' '.join(store_info_selector.xpath('.//span[@class="store-address1"]//text()'))
    address2 = ' '.join(store_info_selector.xpath('.//span[@class="store-address2"]//text()'))
    store_street = address1 + address2
    return store_street if store_street not in [' ', ''] else 'N/A'


def get_store_city(store_info_selector) -> str:
    store_city = ' '.join(store_info_selector.xpath('.//span[@class="store-address-city"]//text()')).replace(',', '')
    return store_city if store_city not in [' ', ''] else 'N/A'


def get_store_zipcode(store_info_selector) -> str:
    store_zipcode = ' '.join(store_info_selector.xpath('.//span[@class="store-address-postal-code"]//text()'))
    return store_zipcode if store_zipcode not in [' ', ''] else 'N/A'


def get_store_phone(store_info_selector) -> str:
    store_phone = ' '.join(store_info_selector.xpath('.//div[@class="store-phone-container"]/a/span[@class="store-phone"]/text()'))
    return store_phone if store_phone not in ['', ' '] else 'N/A'


def get_store_direction_url(store_info_selector) -> str:
    store_direction_url = ' '.join(store_info_selector.xpath('.//a[@title="Get Directions"]/@href'))
    return store_direction_url if store_direction_url not in ['', ' '] else 'N/A'


def get_store_open_hours(store_info_selector) -> str:
    store_hours_selector = store_info_selector.xpath('.//div[contains(@class, "store-hours-container")]//div[@class="store-hours-days"]')[0]
    open_days = store_hours_selector.xpath('./span[contains(@class, "stores-day")]/text()')
    open_hours = store_hours_selector.xpath('./span[not (contains(@class, "stores-day"))]/text()')
    store_open_hours = ' | '.join([day + hours for day, hours in zip(open_days, open_hours)]).replace('*', '')
    return store_open_hours if store_open_hours not in ['', ' '] else 'N/A'


class BootBarnStorelocatorSpider(scrapy.Spider):
    name = "boot_barn"

    def __init__(self, ):
        """Initialize database connection and set file paths."""
        super().__init__()
        self.client = pymysql.connect(host=db_config.db_host, user=db_config.db_user, password=db_config.db_password, database=db_config.db_name, autocommit=True)
        self.cursor = self.client.cursor()  # Create a cursor object to interact with the database

        # self.page_save_path = rf'C:\Project Files Live (using Scrapy)\storeLocator\{self.today_date_time}\{self.name}'
        # self.input_table = 'states_store_locator'

        """Generates initial requests with cookies and headers."""
        self.cookies = {
            'sid': 'EEsk2hI569K8cLFMxGa9mDI2rs4p4mi23mA',
            'dwanonymous_3aa735181a13aa73b9e06b7d6162b1d5': 'acpfuHpo5agwmNP8hi4r1tkP6o',
            'dwac_30d03f8f7e0d83428425462287': 'EEsk2hI569K8cLFMxGa9mDI2rs4p4mi23mA%3D|dw-only|||USD|false|US%2FPacific|true',
            'cquid': '||',
            '__cq_dnt': '0',
            'dw_dnt': '0',
            'dwsid': 'LNc-ybwCHF9oMxvVinQfLA6qtN2H2Z87CiNnbfJ7NDXB7MSLkgOyCxKnQBhKs_q87L4dvV4SCew4jPLhae_Cow==',
            'cqcid': 'acpfuHpo5agwmNP8hi4r1tkP6o',
            '_vwo_uuid_v2': 'DF36F8ECE3DC97A87FA2DBDB6A88BA93D|daa642e0941fadbc6ba32b2fbc27efda',
            'dw': '1',
            'dw_cookies_accepted': '1',
            '_vwo_uuid': 'DF36F8ECE3DC97A87FA2DBDB6A88BA93D',
            '_vwo_ds': '3%241732605568%3A88.72270505%3A%3A',
            '_vis_opt_s': '1%7C',
            '_vis_opt_test_cookie': '1',
            '_gcl_au': '1.1.1451654194.1732605476',
            '_ga': 'GA1.1.1337061062.1732605477',
            'GlobalE_Full_Redirect': 'false',
            'GlobalE_CT_Data': '%7B%22CUID%22%3A%7B%22id%22%3A%22597558304.612440926.703%22%2C%22expirationDate%22%3A%22Tue%2C%2026%20Nov%202024%2007%3A47%3A57%20GMT%22%7D%2C%22CHKCUID%22%3Anull%2C%22GA4SID%22%3A933180480%2C%22GA4TS%22%3A1732605477830%2C%22Domain%22%3A%22www.bootbarn.com%22%7D',
            'GlobalE_Welcome_Data': '%7B%22showWelcome%22%3Afalse%7D',
            '__cq_uuid': 'acpfuHpo5agwmNP8hi4r1tkP6o',
            '__cq_seg': '0~0.00!1~0.00!2~0.00!3~0.00!4~0.00!5~0.00!6~0.00!7~0.00!8~0.00!9~0.00',
            '_li_dcdm_c': '.bootbarn.com',
            '_lc2_fpi': '9aa8f41704f2--01jdknb1zmc0r8g0jfmhf97x6w',
            '_geuid': 'f9a7541d-4a23-4ee6-b445-ce6b08b96e7c',
            '_geps': 'true',
            'GlobalE_Data': '%7B%22countryISO%22%3A%22US%22%2C%22cultureCode%22%3A%22en-US%22%2C%22currencyCode%22%3A%22USD%22%2C%22apiVersion%22%3A%222.1.4%22%7D',
            'cc-at_bootbarn_us': 'eyJ2ZXIiOiIxLjAiLCJqa3UiOiJzbGFzL3Byb2QvYmNjZl9wcmQiLCJraWQiOiI4YzMyZTExNy1jNjFjLTQzMGItYWFlMS00ODc1NWMzYmIyN2IiLCJ0eXAiOiJqd3QiLCJjbHYiOiJKMi4zLjQiLCJhbGciOiJFUzI1NiJ9.eyJhdXQiOiJHVUlEIiwic2NwIjoic2ZjYy5zaG9wcGVyLW15YWNjb3VudC5iYXNrZXRzIHNmY2Muc2hvcHBlci1kaXNjb3Zlcnktc2VhcmNoIHNmY2Muc2hvcHBlci1teWFjY291bnQucGF5bWVudGluc3RydW1lbnRzIHNmY2Muc2hvcHBlci1jdXN0b21lcnMubG9naW4gc2ZjYy5zaG9wcGVyLW15YWNjb3VudC5vcmRlcnMgc2ZjYy5zaG9wcGVyLXByb2R1Y3RsaXN0cyBzZmNjLnNob3BwZXItcHJvbW90aW9ucyBzZmNjLnNlc3Npb25fYnJpZGdlIGNfcGFzc3dvcmRsZXNzTG9naW5fciBzZmNjLnNob3BwZXItbXlhY2NvdW50LnBheW1lbnRpbnN0cnVtZW50cy5ydyBzZmNjLnNob3BwZXItbXlhY2NvdW50LnByb2R1Y3RsaXN0cyBzZmNjLnNob3BwZXItY2F0ZWdvcmllcyBzZmNjLnNob3BwZXItbXlhY2NvdW50IHNmY2Muc2hvcHBlci1teWFjY291bnQuYWRkcmVzc2VzIHNmY2Muc2hvcHBlci1wcm9kdWN0cyBzZmNjLnNob3BwZXItbXlhY2NvdW50LnJ3IHNmY2Muc2hvcHBlci1zdG9yZXMgc2ZjYy5wd2RsZXNzX2xvZ2luIHNmY2Muc2hvcHBlci1iYXNrZXRzLW9yZGVycyBzZmNjLnNob3BwZXItY3VzdG9tZXJzLnJlZ2lzdGVyIHNmY2Muc2hvcHBlci1teWFjY291bnQuYWRkcmVzc2VzLnJ3IHNmY2Muc2hvcHBlci1teWFjY291bnQucHJvZHVjdGxpc3RzLnJ3IHNmY2Muc2hvcHBlci1iYXNrZXRzLW9yZGVycy5ydyBzZmNjLnNob3BwZXItZ2lmdC1jZXJ0aWZpY2F0ZXMgc2ZjYy5zaG9wcGVyLXByb2R1Y3Qtc2VhcmNoIiwic3ViIjoiY2Mtc2xhczo6YmNjZl9wcm',
            'cc-sg_bootbarn_us': '1',
            'usid_bootbarn_us': 'ff6abacb-0de8-41f3-b4f1-f22e74d48523',
            'cc-at_bootbarn_us_2': 'Q6OnNjaWQ6ZGQxMzVlNmItNGZmNC00Y2Q0LWFhZWYtN2ZjNGExMjkzODY4Ojp1c2lkOmZmNmFiYWNiLTBkZTgtNDFmMy1iNGYxLWYyMmU3NGQ0ODUyMyIsImN0eCI6InNsYXMiLCJpc3MiOiJzbGFzL3Byb2QvYmNjZl9wcmQiLCJpc3QiOjEsImRudCI6IjAiLCJhdWQiOiJjb21tZXJjZWNsb3VkL3Byb2QvYmNjZl9wcmQiLCJuYmYiOjE3MzI2MTIwMjksInN0eSI6IlVzZXIiLCJpc2IiOiJ1aWRvOnNsYXM6OnVwbjpHdWVzdDo6dWlkbjpHdWVzdCBVc2VyOjpnY2lkOmFjcGZ1SHBvNWFnd21OUDhoaTRyMXRrUDZvOjpzZXNiOnNlc3Npb25fYnJpZGdlOjpjaGlkOmJvb3RiYXJuX3VzIiwiZXhwIjoxNzMyNjEzODU5LCJpYXQiOjE3MzI2MTIwNTksImp0aSI6IkMyQy0yMDU0MjQ0MDM3MC0xMzU1NzU4MzAxMTI4NjgzNjYwNjk0ODE3NiJ9.UjILf5D0psDIRHzky97uhdJ4OaDLExnijBTJFz0ziZft3MeljHYgNNzkG0Kxk-BT9XpkTiCqzi0bkseDhb3nGA',
            'cc-nx-g_bootbarn_us': 'aa06HBhtoydtwbRYFYvNe1v6D66mo8biAkpgE1iQQ0I',
            '_vwo_sn': '6511%3A1%3A%3A%3A1',
            '_ga_5S2DVSN1BJ': 'GS1.1.1732611999.2.1.1732612003.56.0.0',
            '_uetsid': '900700d0abc611ef803bfbf3dd72cdd3',
            '_uetvid': '90072f60abc611efa8b9cd7b5384ffb6',
            '_pin_unauth': 'dWlkPVpUbGhNRFF4WVRVdE1tRTNZUzAwTVdNM0xXSXlZakl0TlRJd09UUTRZMkkyTXprMw',
        }

        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'max-age=0',
            'priority': 'u=0, i',
            'referer': 'https://www.bootbarn.com/stores-all',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        }

    def start_requests(self) -> Iterable[Request]:
        # Sending request on store-locator page
        yield scrapy.Request(url='https://www.bootbarn.com/stores-all', cookies=self.cookies, headers=self.headers, dont_filter=True, callback=self.parse)

    def parse(self, response, **kwargs):
        # Page save

        # XPath for the top-level group divs
        parsed_html = lxml.html.fromstring(html=response.text)
        states_selector = parsed_html.xpath('//div[@class="store-group"]')

        # Iterate through each state group
        for state_selector in states_selector:

            # Use relative XPath to find the stores within the current state group
            stores_selectors = state_selector.xpath('.//div[@class="store"]')  # Relative XPath for stores div containers

            # Iterate through each store
            for store_selector in stores_selectors:
                store_url = get_store_url(store_selector)  # Get Store Url
                print('Store url:', store_url)
                store_no = get_store_no(store_selector)

                item = BootBarnItem()
                item['store_no'] = store_no
                item['url'] = store_url

                # Sending request on store page to scrape more information
                yield scrapy.Request(url=store_url, cookies=self.cookies, headers=self.headers,
                                     dont_filter=True, callback=self.parse_store_page, cb_kwargs={'item': item})

            print('*' * 100)

    def parse_store_page(self, response, **kwargs):
        # Page Save

        item = kwargs['item']

        parsed_hmtl = lxml.html.fromstring(html=response.text)
        store_name = get_store_name(parsed_hmtl)
        print("Store:", store_name)

        # Store Details
        store_info_selector = parsed_hmtl.xpath('//div[@class="store-details-container"]')[0]

        # Address
        store_street = get_store_street(store_info_selector)
        store_city = get_store_city(store_info_selector)
        store_state = get_store_state(store_info_selector)  # Get State Name

        # store_address_selector = store_info_selector.xpath('.//div[@class="store-address-container"]')[0]
        store_zip_code = get_store_zipcode(store_info_selector)
        store_phone = get_store_phone(store_info_selector)
        store_direction_url = get_store_direction_url(store_info_selector)

        item['name'] = store_name
        item['direction_url'] = store_direction_url
        item['street'] = store_street
        item['city'] = store_city
        item['state'] = store_state
        item['zip_code'] = store_zip_code
        item['phone'] = store_phone
        item['country'] = 'USA'

        item['latitude'] = 'N/A'
        item['longitude'] = 'N/A'
        item['county'] = 'N/A'
        item['open_hours'] = get_store_open_hours(store_info_selector)
        item['status'] = 'N/A'
        item['provider'] = 'Boot Barn'
        item['category'] = 'Apparel'
        item['updated_date'] = db_config.delivery_date

        print(item)
        print('-' * 50)
        # Send the item data dictionary in pipeline to insert into Database
        yield item


if __name__ == '__main__':
    execute(f'scrapy crawl {BootBarnStorelocatorSpider.name}'.split())

#     name = scrapy.Field()
#     latitude = scrapy.Field()
#     longitude = scrapy.Field()
#     street = scrapy.Field()
#     city = scrapy.Field()
#     state = scrapy.Field()
#     zip_code = scrapy.Field()
#     county = scrapy.Field()
#     phone = scrapy.Field()
#     open_hours = scrapy.Field()
#     url = scrapy.Field()
#     provider = scrapy.Field()
#     category = scrapy.Field()
#     updated_date = scrapy.Field()
#     country = scrapy.Field()
#     status = scrapy.Field()
#     direction_url = scrapy.Field()
