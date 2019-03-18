import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from lg_scraper.items import LgScraperItem

class MySpider(CrawlSpider):
    name = 'sampler'
    allowed_domains = ['city.chiba.jp']
    start_urls = ['https://www.city.chiba.jp/']
    search_word = '@city.chiba'

    rules = (
        Rule(LinkExtractor(), callback='parse_item'),
    )

    def parse_item(self, response):
        self.logger.info('Hi, this is an item page! %s', response.url)

        main_contents = response.css('body').extract_first()

        if self.search_word in main_contents:
            item = LgScraperItem()
            item['title'] = response.css('title::text').extract_first()
            item['url'] = response.url
            # item['email'] = response.xpath('body[contains(text(), {})]'.format(self.search_word)).get()
            yield item
            print('{}という文字列を発見しました。\nURL: {}'.format(self.search_word, response.url))