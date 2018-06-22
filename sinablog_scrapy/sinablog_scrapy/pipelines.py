# -*- coding: utf-8 -*-
from sinablog_scrapy.items import BlogMetaItem, PrevBlogItem, ErrorItem, TextItem, ImageItem
from scrapy.exceptions import DropItem
import time, os
from sinablog_scrapy import settings



# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html



title = None
publish_date = None

def save_text(item, content):
    suffix = ""
    if isinstance( item, BlogMetaItem ):
        suffix = ".meta"
    elif isinstance( item, PrevBlogItem ):
        suffix = ".prev"
    elif isinstance( item, ErrorItem ):
        suffix = ".err"
    elif isinstance( item, TextItem ):
        suffix = ".text"
    elif isinstance( item, ImageItem ):
        suffix = ".img"
    elif isinstance( item, PrevBlogItem ):
        suffix = ".next"

    print "============= ",
    print os.path.join( settings.TXT_STORE, item['seq'] + suffix )
    with open( os.path.join( settings.TXT_STORE, item['seq'] + suffix ), 'ab+' ) as f:
        f.write( content.encode('UTF-8') + u'\n'.encode('UTF-8') )

class ErrorItemPipeline(object):
    def process_item(self, item, spider):
        global title
        global publish_date
        if not isinstance( item, ErrorItem ):
            return item
        try:
            if title != None:
                title = None
                publish_date = None
        finally:
            raise DropItem(item['error_msg'])

class BlogMetaPipeline(object):
    def process_item(self, item, spider):
        global title
        global publish_date 
        if not isinstance( item, BlogMetaItem ):
            return item

        if title == None:
            title = item['title']
            publish_date = item['publish_date'].replace(u')', u'').replace(u'(', u'' ).replace( u'-', u'' ).replace( u':', u'' ).replace( u' ', u'-' )

        save_text(item, publish_date + u'-' + title + u'.docx' )
        save_text(item, item['title'])
        save_text(item, u"博客原文： " + item['src_url'] + u" \n")
        save_text(item, u"发布日期：" + item['publish_date'] + u"\n")
        save_text(item, u"标签： " + item['tags'] + u"\n")
        save_text(item, u"分类： " + item['classes'] + u"\n")


        return item

class PrevBlogPipeline(object):
    def process_item(self, item, spider):
        global title
        global publish_date
        if not isinstance( item, PrevBlogItem ): 
            return item

        title = None
        publish_date = None

        next_url = item['url']
        if next_url != None:
            save_text( item, next_url )

        return item 

class TextItemPipeline(object):
    def process_item(self, item, spider):
        if not isinstance( item, TextItem ):
            return item

        save_text( item, item['text'] )

        return item

class ImageItemPipeline(object):
    def process_item(self, item, spider):
        if not isinstance( item, ImageItem ):
            return item

        if len( item['images'] ) == 0:
            save_text( item, u'【下载图片失败】%s ' % ( unicode( item['imge_urls'][0]) ) )
        else:
            save_text( item, item['images'][0]['path'] )

        return item

