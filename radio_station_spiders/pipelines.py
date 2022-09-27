# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import logging
import sqlite3

conn = sqlite3.connect('test.db')
#VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')''', (item['country_name'], item['country_iso_code'], item['city_name'], item['freq'], item['icon'], item['name'], item['transmitter'], item['stream_url']))
class RadioStationSpidersPipeline:
    def process_item(self, item, spider):
        c = conn.cursor()
        c.execute('''INSERT INTO  "radio_stations" \
("country_name", "country_iso_code", "city_name", "freq", "icon", "name", "transmitter", "stream_url") \
VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (item['country_name'], item['country_iso_code'], item['city_name'], item['freq'], item['icon'], item['name'], item['transmitter'], item['stream_url']))
        conn.commit()        
        logging.log(logging.INFO, item)
        return item
