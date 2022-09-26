# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class RadioStationSpidersItem(scrapy.Item):
    # define the fields for your item here like:
    country_name = scrapy.Field()
    country_iso_code = scrapy.Field()
    city_name = scrapy.Field()
    freq = scrapy.Field()
    icon = scrapy.Field()
    name = scrapy.Field()
    transmitter = scrapy.Field()
    stream_url = scrapy.Field()
    src_url = scrapy.Field()
