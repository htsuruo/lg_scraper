from urllib.request import urlopen
from bs4 import BeautifulSoup
import time
import lxml.html
import urllib
import pandas as pd
import numpy as np

url = "https://advance21.sakura.ne.jp/chihoujichitai/hokkaido.html"


def scraping():

    try:
        df = pd.DataFrame(columns=['name', 'url'])
        # dict = {}
        html = urlopen(url)
        soup = BeautifulSoup(html.read(), "lxml")
        links = soup.select("center table tr td a")

        for link in links:
            if str(link).count('☆'):
                continue
            # dict['name'] = link.text
            # dict['url'] = link.get('href')
            # list.append(dict)
            href = link.get('href')
            arr = href.split("//")
            mail_domain = arr[1]

            if str(link).count('www.'):
                mail_domain = mail_domain.replace('www.', '')
                mail_domain = mail_domain[:-1]

            df = df.append({"name": link.text, "url": href, "mail_domain": mail_domain}, ignore_index=True)

            # href_list.append(link.get('href'))
        # href_list.append(link.get('href'))
        # href_unique = set(href_list)
        return df

    except Exception as e:
        print('-----page not found.-----')
        print(e)
    return None


def save_to_csv(df):
    try:
        print(df)
        df.to_csv('./output/zichitai.csv', index=False, encoding="utf_8_sig")
        print('saved completed.')
    except Exception as e:
        print('-----saved error.-----')
        print(e)


def execute():
    df = scraping()
    if df is None:
        print("list is not found.")
        return
    print("success.")

    save_to_csv(df)



if __name__ == '__main__':
    print('start scraping...')
    begin_time = time.time()

    execute()

    end_time = time.time()
    print("total time: {:.2} sec".format(end_time - begin_time))

    # page_exist = True

    # page = 1
    # while True:
    # # for i in range(1,4):
    #     print(page_exist)
    #     if page_exist is False:
    #         break
    #     print("page.{}".format(page))
    #     page_exist = scraping(page)
    #     page += 1
