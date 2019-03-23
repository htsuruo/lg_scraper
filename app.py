# coding: UTF-8
from urllib.request import urlopen
from bs4 import BeautifulSoup
import time
import lxml.html
import urllib
import pandas as pd
import numpy as np
import re
import requests
from googlesearch import search

OUTPUT_PATH = './output/local government.csv'
URL_TOP = 'https://advance21.sakura.ne.jp/chihoujichitai/'


class SummaryScraper:
    # 1800弱の市区町村リストを扱うクラス.

    def __init__(self):
        print('start scraping prefectures...')
        self.pref_list = []
        self.pref_df = None
        pass

    def get_prefectures(self):
        # STEP.1 都道府県ののリストを取得

        try:
            html = urlopen(URL_TOP)
            soup = BeautifulSoup(html.read(), "lxml")
            links = soup.select("table tr td a")

            for link in links:
                exclusion = str(link).count('HOME') or str(link).count('都道府県') or str(link).count('メール送信')
                if exclusion:
                    continue
                href = link.get('href')
                self.pref_list.append({'url': href, 'name': link.text})

        except Exception as e:
            print('-----page not found.-----')
            print(e)
            self.pref_list = None

    def get_cities(self):
        # STEP2. 市区町村のリストを取得
        if self.pref_list is None:
            return

        for pref in self.pref_list:

            target_url = URL_TOP + pref['url']

            try:
                df = pd.DataFrame(columns=['pref', 'name', 'top_url', 'domain', 'target_url', 'email' ])
                html = urlopen(target_url)
                soup = BeautifulSoup(html.read(), "lxml")
                links = soup.select("center table tr td a")

                for link in links:
                    if str(link).count('☆'):
                        continue
                    href = link.get('href')
                    arr = href.split("//")
                    domain = arr[1]
                    domain = domain[:-1]

                    df = df.append({"pref": pref['name'], "name": link.text, "top_url": href, 'domain': domain, 'target_url': get_target_url(domain=domain)}, ignore_index=True)

                self.pref_df = pd.concat([self.pref_df, df])

            except Exception as e:
                print('-----page not found.-----')
                print(e)


class LGScraper:
    # 市区町村の中身を扱うクラス.
    email_list = []
    emails = []

    def _clear_variable(self):
        self.email_list = []
        self.emails = []

    def get_email(self, url, search_word):
        self._clear_variable()
        try:
            html = urlopen(url)
            soup = BeautifulSoup(html.read(), "lxml")
            email = soup.find_all(string=re.compile(search_word))
            self._set_emails(email)
            if len(self.emails) > 0:
                print('{}という文字列を発見しました。\nemails: {}'.format(search_word, self.emails))
            else:
                print('{}を含む文字列は見つかりませんでした。'.format(search_word))

        except Exception as e:
            print(e)

    def _set_emails(self, email):
        emails = []
        for e in email:
            tmp = re.sub(r'\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$', "", e)
            res = re.sub(tmp, "", e)
            if self._is_duplicate(res) is False:
                emails.append(res)
                self.email_list.append(res)
        self.emails = emails

    def _is_duplicate(self, email):
        return email in self.email_list

# Google Search
def get_target_url(domain):
    target_url = ''
    kw = '日常生活用具'
    query = "{} {}".format(domain, kw)
    for url in search(query, lang='ja', stop=1):
        print(url)
        target_url = url
    return target_url

# class GoogleSearch:
    # headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0"}
    # URL_HEAD = 'https://www.google.co.jp/search?num=1&q=site:'
    # target_url =''

    # def __init__(self):
        # self.url = '{}{} "{}"'.format(self.URL_HEAD, self.domain, self.KW)
        # print(self.url)
        # pass

    # def get_page(self):
    #     try:
    #         p = urllib.parse.urlparse(self.url)
    #         query = urllib.parse.quote_plus(p.query, safe='=&')
    #         self.url = '{}://{}{}{}{}{}{}{}{}'.format(
    #             p.scheme, p.netloc, p.path,
    #             ';' if p.params else '', p.params,
    #             '?' if p.query else '', query,
    #             '#' if p.fragment else '', p.fragment
    #         )
    #         print(self.url)
    #         request = urllib.request.Request(self.url, headers=self.headers)
    #         html = urlopen(request)
    #         soup = BeautifulSoup(html.read(), "lxml")
    #         link = soup.select(".r > a")
    #         title = soup.select(".r > a > .LC20lb")
    #         if len(link) < 1:
    #             return
    #         href = link[0].get('href')
    #         print(title)
    #
    #     except Exception as e:
    #         print('-----page not found.-----')
    #         print(e)


def gen_search_word(domain):
    res = ''
    if str(domain).count('www.'):
        res = domain.replace('www.', '')
    res = res.replace('.jp', '')
    res = res.replace('.lg', '')
    res = res[:-1]
    res = "@" + res
    return res


def save_to_csv(df):
    try:
        print(df)
        df.to_csv(OUTPUT_PATH, index=False, encoding="utf_8_sig")
        print('saved completed.')
    except Exception as e:
        print('-----saved error.-----')
        print(e)


def execute():
    s_scraper = SummaryScraper()
    s_scraper.get_prefectures()
    s_scraper.get_cities()
    lg_scraper = LGScraper()
    for index, row in s_scraper.pref_d.iterrows():
        search_word = gen_search_word(domain=row['domain'])
        lg_scraper.get_email(url=row['target_url'], search_word=search_word)
        s_scraper.pref_df.at[index, 'email'] = lg_scraper.emails

    save_to_csv(s_scraper.pref_df)



if __name__ == '__main__':
    print('start scraping...')
    begin_time = time.time()

    execute()

    end_time = time.time()
    print("total time: {} sec".format(end_time - begin_time))
