import scrapy
from scrapy.http import response
import urllib
from copy import deepcopy
from radio_station_spiders.items import RadioStationSpidersItem
import json


'''
XPath 教程
https://www.w3school.com.cn/xpath/xpath_syntax.asp

玩法：
    先用 scrapy shell "https://xxx.com//daaf" 把xpath中的元素解析好，然后在弄到代码里边
    
    https://www.nationsonline.org/index.html
    
    https://www.nationsonline.org/oneworld/country_code_list.htm
    
    国家，国旗
    https://flaglog.com/country-codes
    https://flaglog.com/codes/standardized-rectangle-120px/CN.png
'''

stations = []

class WorldRadiomapSpider(scrapy.Spider):
    name = 'worldradiomap'
    allowed_domains = ['worldradiomap.com']
    start_urls = ['https://worldradiomap.com/list/']

    def parse(self, response):
        # from https://worldradiomap.com/list/
        country_pages = response.xpath("//a[starts-with(@href,'http://worldradiomap.com/') and starts-with(@title,'Radio')]")
        for country_page in country_pages:
            country_name = country_page.xpath("@title").get().split('in ')[1].strip('the ')
            country_iso_code = response.url.split('/')[-2].upper()
            href = country_page.xpath("@href").get()
            station_info = {'country_name' : country_name, 'country_iso_code': country_iso_code}
            meta = deepcopy({'station_info': station_info})
            yield scrapy.Request(href, self.parse_city, meta = meta)

    def parse_city(self, response):
        # from https://worldradiomap.com/us/
        city_pages = response.xpath('//h1[@class="title"]/a[@href]/@href').getall()
        for page in city_pages:
            page_abs_url = urllib.parse.urljoin(response.url, page)
            yield scrapy.Request(page_abs_url, self.parse_stations, meta=response.meta)
            
    def parse_stations(self, response):
        # from https://worldradiomap.com/ca/winnipeg
        locations = response.xpath('//ul[@class="linklist"]/li/a/text()').getall()[1:]
        city_name = locations[-1]
        location_flags = [ urllib.parse.urljoin(response.url, r_rul) for r_rul in response.xpath('//td[@colspan]/img/@src').getall()]
        
        stations = response.xpath('//tr[@class]')
        for station in stations:
            station_freq = ''.join([ch for ch in ''.join(station.xpath('td[@class="freq"]/text()').getall()) if ch.isprintable()]).strip()
            station_detail_page = urllib.parse.urljoin(response.url, station.xpath('td[@class="fsta"]/a/@href').get())
            station_icon = urllib.parse.urljoin(response.url, station.xpath('td[@class="fsta"]/a/img/@src').get())
            station_name = "".join( station.xpath('td[@class="fsta"]/a/text()').getall()).strip(' \n\t')
            station_transmitter = station.xpath('td[@class="fpre"]/text()').get()
            station_info = {
                "locations": locations,
                "city_name": city_name,
                "station_freq": station_freq,
                "station_icon": station_icon,
                "station_name": station_name,
                "station_transmitter": station_transmitter,
                }
            response.meta["station_info"].update(deepcopy(station_info))
            yield scrapy.Request(station_detail_page, self.parse_station_stream_url, meta=response.meta)
        
    def parse_station_stream_url(self, response):
        # print(response.meta)
        stream_url = response.xpath("//audio[@id='radiomapplayer']/@src").get()
        if not stream_url or len(stream_url) < 5:
            print("*" * 50, response.url)
        else:
            response.meta['station_info']['stream_url'] = stream_url

        item = RadioStationSpidersItem()
        item['station'] = json.dumps(response.meta['station_info']) 
        yield item
        
        
