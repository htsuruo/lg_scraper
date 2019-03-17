# coding: UTF-8
from urllib.request import urlopen
from bs4 import BeautifulSoup
import time
import lxml.html
import urllib
import pandas as pd
import numpy as np
import re

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
                df = pd.DataFrame(columns=['pref', 'name', 'url'])
                html = urlopen(target_url)
                soup = BeautifulSoup(html.read(), "lxml")
                links = soup.select("center table tr td a")

                for link in links:
                    if str(link).count('☆'):
                        continue
                    href = link.get('href')
                    arr = href.split("//")
                    mail_domain = arr[1]

                    if str(link).count('www.'):
                        mail_domain = mail_domain.replace('www.', '')
                        mail_domain = mail_domain[:-1]

                    df = df.append({"pref": pref['name'], "name": link.text, "url": href}, ignore_index=True)

                self.pref_df = pd.concat([self.pref_df, df])

            except Exception as e:
                print('-----page not found.-----')
                print(e)


class LGScraper:
    # 市区町村の中身を扱うクラス.
    sample_url = 'http://www.city.yokohama.lg.jp/kenko/shogai/yougu/yougu.html'

    def __init__(self):
        pass

    def get_text(self):
        try:
            html = urlopen(self.sample_url)
            soup = BeautifulSoup(html.read(), "lxml")
            text = soup.find_all(string=re.compile("@city.yokohama"))
            print(text)

        except Exception as e:
            print(e)



def save_to_csv(df):
    try:
        print(df)
        df.to_csv(OUTPUT_PATH, index=False, encoding="utf_8_sig")
        print('saved completed.')
    except Exception as e:
        print('-----saved error.-----')
        print(e)


def execute():
    # s_scraper = SummaryScraper()
    # s_scraper.get_prefectures()
    # s_scraper.pref_list.append({'url': 'hokkaido.html', 'name': '北海道'})
    # s_scraper.get_cities()
    lg_scraper = LGScraper()
    lg_scraper.get_text()


    # save_to_csv(s_scraper.pref_df)


if __name__ == '__main__':
    print('start scraping...')
    begin_time = time.time()

    execute()

    end_time = time.time()
    print("total time: {} sec".format(end_time - begin_time))
