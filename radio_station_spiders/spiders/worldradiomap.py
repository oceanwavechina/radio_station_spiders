import scrapy
from scrapy.http import response
import urllib
from copy import deepcopy
from radio_station_spiders.items import RadioStationSpidersItem
import time
import pickle


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
            href = country_page.xpath("@href").get()
            station_info = {'country_name' : country_name}
            yield scrapy.Request(href, self.parse_city, meta = {'station_info': pickle.dumps(station_info)})

    def parse_city(self, response):
        # from https://worldradiomap.com/us/
        country_iso_code = response.url.split('/')[-2].upper()
        city_pages = response.xpath('//h1[@class="title"]/a[@href]/@href').getall()
        for page in city_pages:
            page_abs_url = urllib.parse.urljoin(response.url, page)
            station_info = pickle.loads(response.meta["station_info"])
            station_info.update({'country_iso_code': country_iso_code})
            yield scrapy.Request(page_abs_url, self.parse_stations, meta={'station_info': pickle.dumps(station_info)})
            
    def parse_stations(self, response):
        # from https://worldradiomap.com/ca/winnipeg
        locations = response.xpath('//ul[@class="linklist"]/li/a/text()').getall()[1:]
        city_name = locations[-1]
        # location_flags = [ urllib.parse.urljoin(response.url, r_rul) for r_rul in response.xpath('//td[@colspan]/img/@src').getall()]
        
        stations = response.xpath('//table[@class="fix"]/tr[starts-with(@class,"rt")]')
        for station in stations:
            station_freq = ''.join([ch for ch in ''.join(station.xpath('td[contains(@class,"freq")]/text()').getall()) if ch.isprintable()]).strip()
            station_detail_page = urllib.parse.urljoin(response.url, station.xpath('td[contains(@class,"fsta")]/a/@href').get())
            station_icon = urllib.parse.urljoin(response.url, station.xpath('td[contains(@class,"fsta")]/a/img/@src').get())
            station_name = "".join( station.xpath('td[contains(@class,"fsta")]/a/text()').getall()).strip(' \n\t')
            station_transmitter = station.xpath('td[contains(@class,"fpre")]/text()').get().strip(', ')
            station_info = pickle.loads(response.meta["station_info"])
            station_info.update({
                "src_url": response.url,
                "locations": locations,
                "city_name": city_name,
                "freq": station_freq,
                "icon": station_icon,
                "name": station_name,
                "transmitter": station_transmitter,
                })
            if station_transmitter is not None:
                yield scrapy.Request(station_detail_page, self.parse_station_stream_url, meta={'station_info': pickle.dumps(station_info)})
        
    def parse_station_stream_url(self, response):
        time.sleep(0.1)
        station_info = pickle.loads(response.meta["station_info"])
        stream_url = response.xpath("//audio[@id='radiomapplayer']/@src").get()
        if stream_url:
            item = RadioStationSpidersItem()
            item['country_name'] = station_info['country_name']
            item['country_iso_code'] = station_info['country_iso_code']
            item['city_name'] = station_info['city_name']
            item['freq'] = station_info['freq']
            item['icon'] = station_info['icon']
            item['name'] = station_info['name']
            item['transmitter'] = station_info['transmitter']
            item['stream_url'] = stream_url 
            item['src_url'] = station_info['src_url']
            yield item
        
        
