# -*- coding: utf-8 -*-
import scrapy
from lg_scraper.items import LgScraperItem
import re

class ScrapyLocalGoverment(scrapy.Spider):
    name = 'scrapy_local_goverment'
    allowed_domains = ['city.chiba.jp']
    start_urls = ['https://www.city.chiba.jp/']
    search_word = '@city.chiba'

    def parse(self, response):
        print("\n>>> Parse " + response.url + " <<<")
        urls = response.css("a::attr('href')").extract()
        self.parse_word(response)
        for url in urls:
            url = response.urljoin(url)
            yield scrapy.Request(url, callback=self.parse)

    def parse_word(self, response):
        main_contents = response.css('body').extract_first()

        if self.search_word in main_contents:
            item = LgScraperItem()
            item['title'] = response.selector.xpath('//title/text()').extract_first()
            item['url'] = response.url
            # item['email'] = response.css('body').xpath(self.search_word).getall()
            yield item
            print('{}という文字列を発見しました。\nURL: {}'.format(self.search_word, response.url))
