import scrapy
from scrapy.http import response
import urllib


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
        station_pages = response.xpath("//a[starts-with(@href,'http://worldradiomap.com/')]/@href").getall()
        # city_name = 
        for page in station_pages:
            yield scrapy.Request(page, self.parse_station_in_country_city)

    def parse_station_in_country_city(self, response):
        url_list = response.url.split('/')
        iso_code = url_list[-2]
        city = url_list[-1]
        print('country:', iso_code, 'city:', city)
        station_detail_page = response.xpath("//a[starts-with(@href,'../') and @onclick]/@href").getall()
        for page in station_detail_page:
            page_abs_url = urllib.parse.urljoin(response.url, page)
            yield scrapy.Request(page_abs_url, self.parse_station_stream_url)
        
    def parse_station_stream_url(self, response):
        stream_url = response.xpath("//audio[@id='radiomapplayer']/@src").get()
        print('stream url:', stream_url)
        if not stream_url or len(stream_url) < 5:
            print("*"*20, response.url)
        
        
