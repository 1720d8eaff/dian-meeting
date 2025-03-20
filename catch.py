from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import json
import time


def get_bilibili_anime_reviews_selenium():
    # 设置Selenium WebDriver
    # 需要提前下载ChromeDriver，并替换为实际的驱动路径
    driver_path = 'path/to/chromedriver'
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service)

    # B站动漫影评的URL（需要替换为实际的动漫影评页面URL）
    url = 'https://www.bilibili.com/read/cv1234567'  # 示例URL，请替换为实际的动漫影评页面URL

    try:
        driver.get(url)
        time.sleep(3)  # 等待页面加载完成

        # 根据实际页面结构提取影评和评分
        reviews = []
        # 假设影评内容在<div class="review-content">标签中，评分在<span class="score">标签中
        review_elements = driver.find_elements(By.CSS_SELECTOR, 'div.review-content')
        score_elements = driver.find_elements(By.CSS_SELECTOR, 'span.score')

        for i in range(len(review_elements)):
            review = review_elements[i].text
            score = score_elements[i].text if i < len(score_elements) else '无评分'
            reviews.append({'review': review, 'score': score})

        return reviews
    except Exception as e:
        print(f"获取数据时出错: {e}")
        return None
    finally:
        driver.quit()


def save_to_json(data, filename='anime_reviews.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"数据已保存到 {filename}")


if __name__ == '__main__':
    anime_reviews = get_bilibili_anime_reviews_selenium()
    if anime_reviews:
        save_to_json(anime_reviews)
    else:
        print("未能获取到影评数据")