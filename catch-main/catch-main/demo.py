import re
import time
import json
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from datetime import datetime
import pandas as pd
import numpy as np
import os


def get_bgm_url(page_num):
    url_list = []
    vote_num = []
    title_list = []
    base_url = "https://bangumi.tv/anime/browser?sort=rank&page="
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    for i in range(1, page_num + 1):
        url = base_url + str(i)
        response = session.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # 提取动画链接和标题
        anime_links = soup.find_all('a', class_='l')
        for link in anime_links:
            href = link.get('href')
            if '/subject' in href:
                url_list.append(href)
                title_list.append(link.text.strip())

        # 提取评分人数
        rating_spans = soup.find_all('span', class_='tip_j')
        for span in rating_spans:
            number = re.findall(r'\d+', span.text)
            if number:
                vote_num.append(int(number[0]))

    # 使用pandas来处理url、vote和title
    df = pd.DataFrame({
        'url': url_list,
        'vote_num': vote_num,
        'title': title_list
    })

    return df


def data_deal(stars, need_num, times):
    merged_times = np.concatenate(times)
    merged_stars = np.concatenate(stars).astype(int)

    # 将时间和星级转换为DataFrame并按时间排序
    df = pd.DataFrame({
        'time': merged_times,
        'stars': merged_stars
    })
    df['time'] = pd.to_datetime(df['time'], format="%Y-%m-%d %H:%M")
    df.sort_values(by='time', ascending=False, inplace=True)

    # 取前 need_num[0] 个星级值
    first_n_values = df['stars'].head(need_num[0])

    return first_n_values.mean()


def get_points(df):
    result = []

    kind = ['/collections?page=', '/doings?page=', '/on_hold?page=', '/dropped?page=']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    for idx, row in df.iterrows():
        url = row['url']
        vote_num = row['vote_num']
        base_url = "https://bangumi.tv" + url + '/collections'
        response = session.get(base_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        num_temp = soup.find_all('small')
        need_num = []
        stars = [[] for _ in range(len(kind))]
        times = [[] for _ in range(len(kind))]

        for n in num_temp:
            number = re.findall(r'\d+', n.text)
            if number:
                need_num.append(int(number[0]))

        need_num = need_num[1:5]
        need_num = np.array(need_num)
        need_num[0] = vote_num / 10
        comments_and_ratings = []

        for k, kind_content in enumerate(kind):
            page_num = 1
            success_num = 0
            max_page = get_max_page(url, kind_content, page_num, session, headers)
            print(f"max_page: {max_page}")

            # 设置最大爬取页数限制
            max_crawl_page = 100  # 可以根据需要调整这个值

            while page_num <= max_crawl_page:
                base_url = "https://bangumi.tv" + url + kind_content + str(page_num)
                response = session.get(base_url, headers=headers)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')

                user_containers = soup.find_all('div', class_=re.compile('userContainer'))
                for container in user_containers:
                    # 提取评论
                    comment_tag = container.find('p', class_='content')  # 修改这里
                    if comment_tag:
                        comment = comment_tag.text.strip()
                    else:
                        comment = ''

                    # 提取评分
                    star_tag = container.find('span', class_=re.compile(r'\bstarlight\b'))
                    if star_tag:
                        star_class = star_tag.get('class')
                        if star_class and len(star_class) > 1:
                            number = re.findall(r'\d+', star_class[1])
                            if number:
                                rating = int(number[0])
                                comments_and_ratings.append((comment, rating))
                                print(f"提取到评论：{comment}，评分：{rating}")

                print(f"第{page_num}页已获取{len(comments_and_ratings)}条评论和评分")
                page_num += 1
                time.sleep(1)

                # 检查是否还有下一页
                next_page_tag = soup.find('a', text='›')
                if not next_page_tag or not next_page_tag.get('href'):
                    break

        # 数据处理
        result.append(data_deal(stars, need_num, times))
        print(f"{row['title']}的评分人数为{vote_num}，评分为{result[-1]}")

        # 数据清洗并保存
        comments_df = pd.DataFrame(comments_and_ratings, columns=['comment', 'rating'])
        print("原始评论数据框：")
        print(comments_df)

        cleaned_comments_df = data_cleaning(comments_df)
        print("清洗后的评论数据框：")
        print(cleaned_comments_df)

        if not cleaned_comments_df.empty:
            cleaned_comments_df.to_csv('cleaned_comments.csv', index=False, mode='a', header=not os.path.exists('cleaned_comments.csv'))
            print("已保存清洗后的评论到 cleaned_comments.csv")
        else:
            print("清洗后的数据框为空，未保存文件")

    return result


def data_cleaning(df):
    # 去除重复数据
    df = df.drop_duplicates()

    # 去除缺失值
    df = df.dropna()

    # 数据格式标准化
    df['comment'] = df['comment'].apply(lambda x: x.strip().replace('\n', ' '))
    df['rating'] = df['rating'].astype(int)

    # 去除评论为空的行
    df = df[df['comment'] != '']

    return df


def get_max_page(url, kind_content, page_num, session, headers):
    base_url = "https://bangumi.tv" + url + kind_content + str(page_num)
    response = session.get(base_url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')

    max_page_span = soup.find_all('span', class_='p_edge')
    max_page = 10
    if max_page_span:
        max_page_text = max_page_span[0].text
        max_page_number = re.findall(r'\d+', max_page_text)
        if max_page_number:
            max_page = int(max_page_number[-1])
    return max_page


if __name__ == '__main__':
    # 获取排行榜第一页所有动画 URL 的评分
    df = get_bgm_url(1)
    print(df)
    # 保存url_list为txt文件
    df.to_csv('url_list.txt', index=False)
    result = get_points(df)
    # 爬取前480的动画链接和评分人数