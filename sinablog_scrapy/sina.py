from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from sinablog_scrapy.spiders import sina_spider
import sys


process = CrawlerProcess(get_project_settings())

sina_spider.SinaSpider.urls = [ sys.argv[1] ]

process.crawl( sina_spider.SinaSpider)
process.start() # the script will block here until the crawling is finished


