from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def construct_url(keywords: list, start: int):
    """
    :param keywords: list containing search terms. There can be spaces
    :param start: Controls page to display. 0 means first page, 10 means second, 20 means third etc.
    :return: url
    """
    # Reformat input keywords for url. Replace spaces with %20, add double quotes with %22
    search_term = ""
    for keyword in keywords:
        split_keyword = keyword.split(" ")
        len_keyword = len(split_keyword)

        if len_keyword != 1:  # has a space in it
            modified_keyword = ""
            for index, value in enumerate(split_keyword):
                if index != len_keyword - 1:
                    modified_keyword = modified_keyword + value + "%20"
                else:
                    modified_keyword = modified_keyword + value
            keyword = modified_keyword
        search_term = search_term + "+%22" + keyword + "%22"

    url = f"https://scholar.google.com/scholar?start={start}&q={search_term}&hl=en&as_sdt=0,43"
    print(url)
    return url


def get_google_scholar_articles(url):
    s = Service(ChromeDriverManager().install())
    op = webdriver.ChromeOptions()
    # op.add_argument('--headless')
    op.add_argument('--disable-gpu')
    op.add_argument('--headless')
    driver = webdriver.Chrome(service=s, options=op)
    driver.get(url)

    # Wait for the search results to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "gs_res_ccl")))

    # Get article titles and descriptions
    articles = driver.find_elements(By.XPATH, "//div[@class='gs_ri']")

    # Extract titles and descriptions
    article_data = []
    for article in articles:
        title = article.find_element(By.XPATH, ".//h3/a").text
        description = article.find_element(By.XPATH, ".//div[@class='gs_rs']").text

        # Extracting the citation count if available
        try:
            citation_count_element = article.find_element(By.XPATH, ".//a[contains(@href, 'cites')]")
            citation_count = citation_count_element.text
        except:
            citation_count = "N/A"

        # Extracting the year published if available
        try:
            year_element = article.find_element(By.XPATH, ".//div[@class='gs_a']")
            year_published = year_element.text.split(" - ")[1].split(",")[0]
        except:
            year_published = "N/A"

        # Extracting the journal if available
        try:
            journal_element = article.find_element(By.XPATH, ".//div[@class='gs_a']")
            journal = journal_element.text.split(" - ")[1].split(",")[1]
        except:
            journal = "N/A"

        # Extracting the authors if available
        try:
            authors_element = article.find_element(By.XPATH, ".//div[@class='gs_a']")
            authors = authors_element.text.split(" - ")[0]
        except:
            authors = "N/A"

        article_data.append({
            "title": title,
            "description": description,
            "citations": citation_count,
            "year_published": year_published,
            "journal": journal,
            "authors": authors
        })

    driver.quit()
    return article_data


if __name__ == "__main__":
    all_articles = []
    for page in range(0, 100, 10):
        url = construct_url(['astrocyte', 'inner plexiform layer', 'GFAP', 's100'], page)
        articles = get_google_scholar_articles(url)
        all_articles.extend(articles)

    with open('Page Data.txt', "w+", encoding='utf-8') as file:
        for idx, article in enumerate(all_articles, start=1):
            file.write(f"{idx}. {article['title']}\n")
            file.write(f"   {article['description']}\n")
            file.write(f"   Citations: {article['citations']}\n")
            file.write(f"   Year Published: {article['year_published']}\n")
            file.write(f"   Journal: {article['journal']}\n")
            file.write(f"   Authors: {article['authors']}\n")
            file.write("=" * 80)
            file.write("\n")


