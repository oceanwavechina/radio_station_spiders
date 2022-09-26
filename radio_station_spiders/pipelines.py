# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import logging
import sqlite3

conn = sqlite3.connect('test.db')

class RadioStationSpidersPipeline:
    def process_item(self, item, spider):
        logging.log(logging.INFO, item)
        return item
