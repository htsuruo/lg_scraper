import scrapy


class QuotesSpider(scrapy.Spider):
    name = "quotes_spider"
    allowed_domains = ['chiyell.net']
    start_urls = [
        'https://stg.chiyell.net/',
    ]

    def parse(self, response):
        print("\n>>> Parse " + response.url + " <<<")
        urls = response.css("a::attr('href')").extract()
        for url in urls:
            url = response.urljoin(url)
            yield scrapy.Request(url, callback=self.parse)

    def parse_word(self, response):
        print("\nHOGE " + response.url)