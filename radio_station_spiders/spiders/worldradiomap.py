import scrapy
from scrapy.http import response
import urllib
from copy import deepcopy


'''
XPath 教程
https://www.w3school.com.cn/xpath/xpath_syntax.asp

玩法：
    先用 scrapy shell "https://xxx.com//daaf" 把xpath中的元素解析好，然后在弄到代码里边
'''

class WorldRadiomapSpider(scrapy.Spider):
    name = 'worldradiomap'
    allowed_domains = ['worldradiomap.com']
    start_urls = ['https://worldradiomap.com/list/']

    def parse(self, response):
        # 选取所有 /a 标签， 并且有 href属性，并且改属性的值以 http://radiomap.eu/ 开头
        print(response.url)
        country_pages = response.xpath("//a[starts-with(@href,'http://worldradiomap.com/') and starts-with(@title,'Radio')]")
        for country_page in country_pages:
            country_name = country_page.xpath("@title").get().split('in ')[1].strip('the ')
            href = country_page.xpath("@href").get()
            meta = {'country_name' : country_name}
            # print(cb_kwargs)
            yield scrapy.Request(href, self.parse_city, meta=meta)

    def parse_city(self, response):
        city_pages = response.xpath('//h1[@class="title"]/a[@href]/@href').getall()
        for page in city_pages:
            page_abs_url = urllib.parse.urljoin(response.url, page)
            yield scrapy.Request(page_abs_url, self.parse_stations, meta=response.meta)
            
    def parse_stations(self, response):
        # parse location
        print(response.url, '('*30)
        locations = response.xpath('//ul[@class="linklist"]/li/a/text()').getall()[1:]
        location_flags = [ urllib.parse.urljoin(response.url, r_rul) for r_rul in response.xpath('//td[@colspan]/img/@src').getall()]
        
        stations = response.xpath('//tr[@class]')
        for station in stations:
            station_freq = station.xpath('td[@class="freq"]/text()').get()
            station_detail_page = urllib.parse.urljoin(response.url, station.xpath('td[@class="fsta"]/a/@href').get())
            station_icon = urllib.parse.urljoin(response.url, station.xpath('td[@class="fsta"]/a/img/@src').get())
            station_name = "".join( station.xpath('td[@class="fsta"]/a/text()').getall()).strip(' \n\t')
            station_transmitter = station.xpath('td[@class="fpre"]/text()').get()
            station_info = {
                "locations": locations,
                "location_flags": location_flags,
                "station_freq": station_freq,
                "station_icon": station_icon,
                "station_name": station_name,
                "station_transmitter": station_transmitter,
                }
            response.meta["station_info"] = deepcopy(station_info)
            yield scrapy.Request(station_detail_page, self.parse_station_stream_url, meta=response.meta)
        
    def parse_station_stream_url(self, response):
        print(response.meta)
        stream_url = response.xpath("//audio[@id='radiomapplayer']/@src").get()
        print('stream url:', stream_url)
        if not stream_url or len(stream_url) < 5:
            print("*"*20, response.url)
        
        
