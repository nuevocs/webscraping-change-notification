import httpx
from selectolax.parser import HTMLParser
import pandas as pd
import random
import time
import os
from apprise_func import telegram_notify

url = "https://www.tojitsu-kenpo.or.jp/asp/news_all/newstitle.asp"


def create_dataframe(tree) -> pd.DataFrame:
    date = "body > div > table > tbody > tr > td:nth-child(1)"
    dates = [node.text().strip().replace("[", "").replace("]", "") for node in tree.css(date)]

    title = "body > div > table > tbody > tr > td:nth-child(2)"
    titles = [node.text().strip() for node in tree.css(title)]

    link = "body > div > table > tbody > tr > td:nth-child(2) > span > a"
    links = [node.attributes['href'].replace("../../", "https://www.tojitsu-kenpo.or.jp/") for node in tree.css(link)]

    df = pd.DataFrame({'date': dates, 'title': titles, 'link': links})
    df['href'] = "<a href='" + df['link'] + "'>" + df['title'] + "</a>"
    return df


def scraping_data(url):
    r = httpx.get(url)
    if r.status_code == 200:
        tree = HTMLParser(r.text)
        return tree
        # return create_dataframe(tree)
    else:
        print("URL is something wrong.")


# print(scraping_data(url))

def get_body(url) -> str:
    time.sleep(random.randint(2, 6))
    character_limit: int = 300
    tree = scraping_data(url)
    body = "#newsArticleBody > p"
    bodies = [node.text().strip().replace(" ", "").replace("\u3000", "").replace("\xa0", "") for node in tree.css(body)]
    result = "".join(bodies)
    summary = result[:character_limit]
    return summary


def check_data(df1, df2):
    df_bool = df1.eq(df2)
    if df_bool.eq(False).any().any():
        print("At least one False value exists in the dataframe.")
        false_rows = df2[~df_bool.all(axis=1)]
        for index, row in false_rows.iterrows():
            title = row['href']
            body = f" <strong>{row['date']}</strong> <br /> {get_body(row['link'])}"
            telegram_notify(title, body)
    else:
        print("No False values exist in the dataframe.")
        # return print(df_bool)


def _test_wrong(df, col_name):
    df.at[2, col_name] = "wrong value"
    df.at[7, col_name] = "wrong value dayo"
    return df


if __name__ == "__main__":

    def main_func():
        match os.environ.get("APP_MODE"):
            case "DEV":
                saved_df = create_dataframe(scraping_data(url))
                saved_df.to_csv("current.csv", index=False)
                new_df = create_dataframe(scraping_data(url))
                new_df = _test_wrong(new_df, "title")
                check_data(saved_df, new_df)
            case "PROD":
                saved_df = pd.read_csv("current.csv")
                new_df = create_dataframe(scraping_data(url))
                check_data(saved_df, new_df)
                new_df.to_csv("current.csv", index=False)


    main_func()
