import asyncio
import requests
from bs4 import BeautifulSoup
import sqlite3


url = 'https://jobs.dou.ua/vacancies/?category=Python'
con = sqlite3.connect('work_file.db')
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS vacancy(id , date, title, sh_info)")


async def get_html_by_url(url):

    headers = {
        'user-agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                       + 'AppleWebKit/537.36 (KHTML, like Gecko) '
                       + 'Chrome/108.0.0.0 Safari/537.36')
    }
    response = requests.get(url, headers=headers)
    assert response.ok
    return response.text


def get_information_from_html(html):
    res = []
    soup = BeautifulSoup(html, 'html.parser')
    vacancies = soup.find_all('div', class_='vacancy')
    for vacancy in vacancies:
        date = vacancy.find('div', class_='date')
        link = vacancy.find('div', class_='title').a
        description = vacancy.find('div', class_='sh-info')
        title = link.text
        if date:
            date = date.text
        else:
            date = None
        sh_info = description.text.strip()
        vacancy_info = (date, title, sh_info)
        res.append(vacancy_info)
    return res


async def save_information_to_db(information):
    sql = ''' INSERT INTO vacancy(date, title, sh_info)
                  VALUES(?,?,?) '''

    cur.execute(sql, information)
    con.commit()


async def main():
    html = await get_html_by_url(url)
    res = get_information_from_html(html)
    for information in res:
        await save_information_to_db(information)


if __name__ == '__main__':
    asyncio.run(main())
