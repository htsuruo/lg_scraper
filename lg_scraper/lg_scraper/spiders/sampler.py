import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from lg_scraper.items import LgScraperItem
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re

class MySpider(CrawlSpider):
    name = 'sampler'
    allowed_domains = ['www.city.yokohama.lg.jp']
    start_urls = ['http://www.city.yokohama.lg.jp']
    search_word = '@city.yokohama'

    list_allow = [r'^(?=.*shogai).*$']  # この条件に合うリンクは巡回
    list_deny = [r'.+\.(txt|pdf)']

    rules = (
        # 巡回ルール
        # Rule(
        #     LinkExtractor(), follow=True,
        # ),
        # データ抽出ルール
        Rule(LinkExtractor(
            allow=list_allow,
            deny=list_deny,
            unique=True  # おなじリンク先ではデータ抽出しない
        ),
            callback='parse_items',  # 条件に合えば、ここで指定したデータ抽出実行関数を実行する。
            follow=True,
        ),
    )


    def parse_items(self, response):
        main_contents = response.css('body').extract_first()

        if self.search_word in main_contents:
            html = urlopen(response.url)
            soup = BeautifulSoup(html.read(), "lxml")
            email = soup.find_all(string=re.compile("@city.yokohama"))

            item = LgScraperItem()
            item['title'] = response.css('title::text').extract_first()
            item['url'] = response.url
            item['email'] = email
            yield item
            print('{}という文字列を発見しました。\nURL: {}'.format(self.search_word, response.url))