import csv
import requests
from bs4 import BeautifulSoup

def convert_to_tenge(text):
    res = ""
    index = 0
    for i in range(len(text)):
        if text[i].isdigit():
            res += text[i]
        else:
            index = i
            break
    salary = int(res)
    if text[index:index+3] == 'руб':
        salary *= 6
    elif text[index:index+3] == 'USD':
        salary *= 450
    return salary

def parse_resumes(search_text):
    url = f"https://hh.kz/search/resume?text={search_text}&area=40&isDefaultArea=true&pos=full_text&logic=normal&exp_period=all_time&currency_code=KZT&ored_clusters=true&order_by=relevance"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    # get the number of pages to parse
    num_pages = int(soup.find('div', attrs={'class': 'pager'}).find_all('span',recursive=False)[-1].find('a').find('span').text)
    num_pages = min(25, num_pages)

    # initialize the csv writer
    with open(f"{search_text}.csv", mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Title", "Specialization", "Salary", "Age", "Employment(Занятость)", "Work schedule", "Experience_years", "Experience_month", "Citizenship", "Sex"])

        # parse each page and write the results to the csv file
        for i in range(0, num_pages):
            url = f"https://hh.kz/search/resume?text={search_text}&area=40&isDefaultArea=true&pos=full_text&logic=normal&exp_period=all_time&currency_code=KZT&ored_clusters=true&order_by=relevance&page={i}"
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')

            resume_blocks = soup.find_all('div', {'class': 'resume-search-item__content'})

            for block in resume_blocks:
                # get the link to the individual page of each CV
                link = 'https://hh.kz' + block.find('a', {'class': 'serp-item__title'})['href']
                print(link)
                response = requests.get(link, headers=headers)
                soup = BeautifulSoup(response.content, 'html.parser')

                # parse the details of each CV
                resume_content = soup.find('div', {'class': 'resume-applicant'})
                title = resume_content.find('span', {'class': 'resume-block__title-text'}).text.strip()
                specialization = resume_content.find('li', {'data-qa': 'resume-block-position-specialization'}).text.strip()
                salary = resume_content.find('div', {'class': 'resume-block-position-salary'})
                if salary == None:
                    salary = 0
                else:
                    salary = resume_content.find('div', {'class': 'resume-block-position-salary'}).find('span').text.replace(' ', '')
                    salary = convert_to_tenge(salary)
                age = resume_content.find('span', {'data-qa': 'resume-personal-age'})
                if age == None:
                    age = 0
                else:
                    age = int(resume_content.find('span', {'data-qa': 'resume-personal-age'}).find('span').text.strip().split()[0])
                employment = (resume_content.find('div', {'data-qa': 'resume-block-position'}).find_all('p')[-2]).text.strip()[10:]
                work_schedule = (resume_content.find('div', {'data-qa': 'resume-block-position'}).find_all('p')[-1]).text.strip()[14:]
                experience_yearsx = resume_content.find('div', {'data-qa': 'resume-block-experience'})
                if experience_yearsx == None:
                    experience_years = 0
                    experience_month = 0
                else:
                    experience_years = int(experience_yearsx.find('span', {'class': 'resume-block__title-text resume-block__title-text_sub'}).find_all('span')[0].text.strip().split()[0])
                    experience_month = int(experience_yearsx.find('span', {'class': 'resume-block__title-text resume-block__title-text_sub'}).find_all('span')[0].text.strip().split()[0])
                citizenship = resume_content.find('div', {'data-qa': 'resume-block-additional'}).find_all('p')[-2].text.strip().split()[-1]
                sex = resume_content.find('span', {'data-qa': 'resume-personal-gender'}).text.strip()

                # write the details to the csv file
                writer.writerow([title, specialization, salary, age, employment, work_schedule, experience_years, experience_month, citizenship, sex])

parse_resumes("java")