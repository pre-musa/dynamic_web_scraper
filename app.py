from playwright.sync_api import sync_playwright
import time 
from bs4 import BeautifulSoup
import csv

class Dynamic_Scraper:
    
    # keywords 리스트를 받아와서 각 키워드마다 잡 목록을 csv 파일로 만들어준다.
    def __init__(self, keywords):

        # init playwright
        self.p = sync_playwright().start()
        self.browser = self.p.chromium.launch(headless=False)

        # self.page = browser.new_page()
        self.keywords = keywords
        self.jobs_db = []

    def stop_playwright_instance(self):
        self.p.stop()

    def scroll_to_bottom(self, page):
        previous_height = page.evaluate("document.body.scrollHeight")

        while(True):
            page.keyboard.down("End")
            time.sleep(2)

            current_height = page.evaluate("document.body.scrollHeight")
            if(current_height == previous_height):
                break

            previous_height = current_height

    def do_the_thing(self):
        content_keyword_fullContent = {}
        
        for keyword in self.keywords:
            url = f"https://www.wanted.co.kr/search?query={keyword}&tab=position"
            page = self.browser.new_page()
            page.goto(url)

            # scroll
            self.scroll_to_bottom(page)
            
            # cache content with keyword
            content_keyword_fullContent[keyword] = page.content()
            page.close()
        
        # stop instances.
        self.stop_playwright_instance()

        # make soup
        for keyword, content in content_keyword_fullContent.items():
            soup = BeautifulSoup(content, "html.parser")
            jobs = soup.find_all("div", class_="JobCard_container__REty8")

            keyword_job_list = []
            seen_link = set()
            for job in jobs:
                link = f"https://www.wanted.co.kr{job.find('a')['href']}"
                if link in seen_link:
                    continue
                seen_link.add(link)
                title = job.find("strong", class_="JobCard_title__HBpZf").text
                company_name = job.find("span", class_="JobCard_companyName__N1YrF").text
                reward = job.find("span", class_="JobCard_reward__cNlG5").text

                job_data = {
                    "Title" : title,
                    "Company_Name" : company_name,
                    "Reward" : reward,
                    "Link" : link,
                }

                keyword_job_list.append(job_data)
            
            # export content into csv file which named with each keyword
            file = open(f"{keyword}.csv", "w")
            csv_writer = csv.writer(file)
            csv_writer.writerow(job_data.keys())
            for job_data in keyword_job_list:
                csv_writer.writerow(job_data.values())
                
            file.close()

keywords = ["python", "flutter", "ios", "android"]
scraper = Dynamic_Scraper(keywords)
scraper.do_the_thing()