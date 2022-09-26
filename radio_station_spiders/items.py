# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


'''
{'station': '{"locations": ["North America", "United States", "Ohio"], '
            '"location_flags": '
            '["https://worldradiomap.com/2013/flags/46/us.png", '
            '"https://worldradiomap.com/2013/flags/46/us_oh.png", '
            '"https://worldradiomap.com/us-oh/seal.youngstown.png"], '
            '"station_freq": "1440", "station_icon": '
            '"https://worldradiomap.com/us/images/relevant.gif", '
            '"station_name": "WHKZ Relevant Radio", "station_transmitter": '
            '"Lordstown", "stream_url": '
            '"https://playerservices.streamtheworld.com/api/livestream-redirect/RR_MAIN.mp3"}'}
'''
class RadioStationSpidersItem(scrapy.Item):
    # define the fields for your item here like:
    station = scrapy.Field()
    country_name = scrapy.Field()
    country_iso_code = scrapy.Field()
    stream_url = scrapy.Field()
    pass
