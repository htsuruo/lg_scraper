import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from lg_scraper.items import LgScraperItem
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re

class MySpider(CrawlSpider):
    name = 'sampler'
    allowed_domains = ['www.city.ichikawa.lg.jp']
    start_urls = ['http://www.city.ichikawa.lg.jp/']
    search_word = '@city.ichikawa'

    title = ''
    url = ''
    emails = ''

    # list_allow = [r'^(?=.*kenkotofukushi).*$']  # この条件に合うリンクは巡回
    list_allow = []
    list_deny = [r'.+\.(txt|pdf)']

    kw_list = ['日常', '生活', '用具', '福祉', '障害', '障がい']

    email_list = ['']

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
            title = response.css('title::text').extract_first()
            if title is None:
                return

            if '日常生活用具' in title is False:
                return

            # for kw in self.kw_list:
            #     if kw in self.title is False:
            #         return

            html = urlopen(response.url)
            soup = BeautifulSoup(html.read(), "lxml")
            email = soup.find_all(string=re.compile(self.search_word))

            self.title = title
            self.set_emails(email)
            if len(self.emails) < 1:
                return
            self.url = response.url
            self.set_item()
            print('{}という文字列を発見しました。\nURL: {}'.format(self.search_word, response.url))

    def set_item(self):
        item = LgScraperItem()
        item['title'] = self.title
        item['url'] = self.url
        item['email'] = self.emails
        yield item

    def set_emails(self, email):
        emails = []
        for e in email:
            tmp = re.sub(r'\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$', "", e)
            res = re.sub(tmp, "", e)
            if self.is_duplicate(res) is False:
                emails.append(res)
                self.email_list.append(res)
        self.emails = emails

    def is_duplicate(self, email):
        return email in self.email_list


