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
from googlesearch import search, get_random_user_agent
import os
import platform

OUTPUT_PATH = './output/local_government.csv'
SCRAPED_PATH = './output/local_government_scraped.csv'
URL_TOP = 'https://advance21.sakura.ne.jp/chihoujichitai/'
df_columns = ['pref', 'name', 'top_url', 'domain', 'target_url', 'email']


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
                exclusion = str(link).count('HOME') or str(
                    link).count('都道府県') or str(link).count('メール送信')
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
                df = pd.DataFrame(columns=df_columns)
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

                    data = {"pref": pref['name'], "name": link.text,
                            "top_url": href, 'domain': domain}
                    df = df.append(data, ignore_index=True)
                    print(data)

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
                print('{}という文字列を発見しました。\nemails: {}'.format(
                    search_word, self.emails))
            else:
                print('{}を含む文字列は見つかりませんでした。'.format(search_word))

        except Exception as e:
            print(e)

    def _set_emails(self, email):
        emails = []
        for e in email:
            tmp = re.sub(
                r'\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$', "", e)
            res = re.sub(tmp, "", e)
            if self._is_duplicate(res) is False:
                emails.append(res)
                self.email_list.append(res)

        if len(emails) > 0:
            self.emails = self.emails[0]
        else:
            self.emails = ''

    def _is_duplicate(self, email):
        return email in self.email_list

# Google Search


def google_search(domain):
    target_url = ''
    kw = '日常生活用具'
    query = "{} {}".format(domain, kw)
    print('domain: ' + domain)
    try:
        for url in search(query, lang='ja', stop=1, pause=6.0, user_agent=get_random_user_agent()):
            print(url)
            target_url = url
    except Exception as e:
        print(e)
        target_url = None
    return target_url


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
    # lg_scraper = LGScraper()
    # for index, row in s_scraper.pref_df.iterrows():
    #     print("{} -> {}".format(row['pref'], row['name']))
    #     target_url = google_search(domain=str(row['domain']))
    #     search_word = gen_search_word(domain=str(row['domain']))
    #     lg_scraper.get_email(url=target_url, search_word=search_word)
    #     s_scraper.pref_df.at[index, 'target_url'] = target_url
    # s_scraper.pref_df.at[index, 'email'] = lg_scraper.emails

    save_to_csv(s_scraper.pref_df)

'''
Google Searchを使ってターゲットのURLを拾ってくる.
同一IPだと規制されるためEC2で動かす.
処理が完了したら再起動する.
'''
def scrape_target_url():
    df = pd.read_csv(OUTPUT_PATH)
    pf = platform.system()
    if pf == 'Linux':
        if df.count() < 1:
            shutdown_os()

    if os.path.exists(SCRAPED_PATH):
        df_scraped = pd.read_csv(SCRAPED_PATH)
    else:
        df_scraped = pd.DataFrame(columns=df_columns)

    for index, row in df.iterrows():
        target_url = google_search(domain=str(row['domain']))
        if target_url is None:
            break
        data = {"pref": str(row['pref']), "name": str(row['name']), "top_url": str(
            row['top_url']), 'domain': str(row['domain']), 'target_url': target_url}
        df_scraped = df_scraped.append(data, ignore_index=True)
        df = df.drop(index)

    df.to_csv(OUTPUT_PATH, index=False, encoding="utf_8_sig")
    df_scraped.to_csv(SCRAPED_PATH, index=False, encoding="utf_8_sig")

    if pf == 'Linux':
        reboot_os()


def reboot_os():
    reboot_cmd = 'sudo sh -c "reboot"'
    os.system(reboot_cmd)


def shutdown_os():
    cmd = 'sudo sh -c "halt"'
    os.system(cmd)


if __name__ == '__main__':
    print('start scraping...')
    begin_time = time.time()

    # execute()

    # get target_url using by google search in ec2.
    scrape_target_url()

    end_time = time.time()
    print("total time: {} sec".format(end_time - begin_time))
