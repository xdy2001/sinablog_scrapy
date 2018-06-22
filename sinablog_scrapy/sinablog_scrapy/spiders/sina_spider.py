# -*- coding: utf-8 -*-
import random, time, datetime, re
import scrapy
from scrapy.loader import ItemLoader
from sinablog_scrapy.items import BlogMetaItem, PrevBlogItem, ErrorItem, TextItem, ImageItem, next_seq
from scrapy.selector import Selector
from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import html2text
import bs4


count = 0

ref_name = u''

class SinaSpider(scrapy.Spider):
    name = "sina"
    urls = ["http://blog.sina.com.cn/s/blog_489e98b90102xd2e.html"]
    def start_requests(self):
        for i, url in enumerate(self.urls):
            self.cur_url = url
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        global ref_name
        next_seq(1)
        bmItem = BlogMetaItem()
        bmItem['src_url'] = response.url

        bs = bs4.BeautifulSoup( response.body, 'html5lib' )
        
        bmItem['title'] = bs.find( 'div', {'class':'articalTitle'} ).h2.string
        bmItem['publish_date'] = bs.find( 'div', {'class':'articalTitle'} ).find( 'span', {'class':['time', 'SG_txtc']} ).string 

        ref_name = bmItem['publish_date'] + u'-' + bmItem['title'] +  unicode(response.url)

        bmItem['tags'] = u''.join( [ i.string + u'　'  for i in bs.find( 'div', id='sina_keyword_ad_area').table.tr.find( 'td', {'class':'blog_tag'}).find_all('a') if i.string != None ] ) 
        bmItem['classes'] = u''.join( [ i.string + u'　'  for i in bs.find( 'div', id='sina_keyword_ad_area').table.tr.find( 'td', {'class':'blog_class'}).find_all('a') if i.string != None ] ) 
        yield bmItem
        
        bs_body = bs.find( 'div', id="sina_keyword_ad_area2" )
        for aitem in self.extract_items( bs_body ):
            yield aitem

        
        next_seq(1)
        pbItem = PrevBlogItem()
        has_prev = [ i for (i, t) in enumerate( bs.find( 'div', {'class':['articalfrontback', 'SG_j_linedot1', 'clearfix']}).find_all( 'span')) if u'前' in t.string ] 
        if len( has_prev ) > 0:
            pbItem['url'] = bs.find( 'div', {'class':['articalfrontback', 'SG_j_linedot1', 'clearfix']}).find_all( 'a')[has_prev[0]]['href'] 
        else:
            pbItem['url'] = None
        yield pbItem

    def extract_items(self, item , indent=0):
        for sub_item in item.children:
            print '    ' * indent + " ======= " + str(sub_item.name)
            if sub_item.name != u'img' and sub_item.string != None and len( sub_item.string.strip() ) > 0:
                if isinstance ( sub_item, bs4.element.NavigableString ):
                    next_seq(self.is_new_paragraph(sub_item))
                    yield TextItem(text=sub_item.string) 
            if sub_item.name == u'img' and sub_item.get('src') != None:
                img_urls = [ sub_item['src'] ]
                if  sub_item.get('real_src') != None:
                    img_urls.append( sub_item['real_src'] )
                src = filter( lambda x: not re.compile( r'(\d+\.\d+\d\.\d+\.\d+)|(sg_trans\.gif)' ).findall( x ) , img_urls )
                if len( src ) > 0 :
                    next_seq(1)
                    yield ImageItem(image_urls=[ src[0] ])
                else:
                    next_seq(1)
                    yield TextItem(text=u'【获取图片失败】')
                    with open( '/var/tmp/sina_err.log', 'a') as f:
                        errMsg = u"[%s] Failed to fetch img in '%s'\n" % ( unicode(datetime.datetime.now()), ref_name ) 
                        f.write( errMsg.encode( 'UTF-8' ) )
                        errMsg = u"src '%s''\n" % ( sub_item.get('src') ) 
                        f.write( errMsg.encode( 'UTF-8') ) 
                        if sub_item.get('real_src'):
                            errMsg = u"real_src '%s''\n" % ( sub_item.get('real_src') ) 
                            f.write( errMsg.encode( 'UTF-8') ) 

            if 'children' in  dir( sub_item ) :
                for aitem in self.extract_items( sub_item, indent + 1 ):
                    yield aitem

    def is_new_paragraph(self, item ):
        if item.parent.name in [ 'span', 'font', 'strong' ]:
            parent = item.parent
            prev = parent.previous_sibling
            while prev != None:
                if isinstance( prev, bs4.element.NavigableString ):
                    if prev.string == None or len( prev.string.strip() ) == 0 :
                        prev = prev.previous_sibling
                        continue
                    else:
                        return 0
                elif prev.name in [ 'span', 'font', 'strong' 'wbr' ]:
                    return 0
                else:
                    return 1
        return 1


