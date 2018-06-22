# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

global_seq = 100000
def next_seq( inc=1 ):
    """A thread unsafe sequence generator"""
    global global_seq
    global_seq += inc 
    return str( global_seq )

class BaseItem(scrapy.Item):
    seq = scrapy.Field()
    filename = scrapy.Field()
    def __init__(self,  **kargs):
        global global_seq
        super(scrapy.Item, self).__init__(kargs)
        self['seq'] = unicode(global_seq)

class ErrorItem(BaseItem):
    error_msg = scrapy.Field()

class BlogMetaItem(BaseItem):
    src_url = scrapy.Field()
    title = scrapy.Field()
    publish_date = scrapy.Field()
    tags = scrapy.Field()
    classes = scrapy.Field()

class PrevBlogItem(BaseItem):
    url = scrapy.Field()

class TextItem(BaseItem):
    text = scrapy.Field()

class ImageItem(BaseItem):
    image_urls = scrapy.Field()
    images = scrapy.Field()

