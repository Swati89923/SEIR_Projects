#  Firstly I am importing some libraries which will be required:
#  sys :- to take command  line arguments 
#  requests :- to download websites from internet
#  bs4 : to parse html , there we need title, Body, Links that's why I used here
#  urljoin : to print each url in proper way(Basicall relative links to absolute url).
# urllib3 :- to avoid local system issue, by disabling it..
# selenium :- to render javascript based website, normal request unable to execute Js
# time :- to provide time delay(to load JS)
#re :- to perform regex operations (text cleaning)

import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import urllib3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import re
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# this funcn will fetch html page by taking url as input
def to_get_page(url):                               
    headrs = {                                                     # I was geting  blocked that's I have used fake browser headres
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }

    responses = requests.get(url, headers=headrs, verify=False) # download website html
    responses.raise_for_status() # if get error like 404,403,500 then stop the program.
    html = responses.text

    # If site is JavaScript based (React etc.)
    if "enable JavaScript" in html or len(html) < 2000:
        options = Options()     # It's a configuration  object    for chrome browser            
        options.add_argument("--headless")   # browser will run in background , will not open chrome on screen
        options.add_argument("--disable-gpu") # sometime headless mode crash with GPU that's why I off GPU for safer side
        options.add_argument("--no-sandbox") # to disable security mode 

        driver = webdriver.Chrome(options=options)   # launching chrome browser 
        driver.get(url)
        time.sleep(5)                      # Salenium will open browser and load website and will wait for 5 sec to render js
        html = driver.page_source
        driver.quit()

    return html


# Now this funcn will fetch the title of the page.
def to_get_title(soup):
    if soup.title:
        return soup.title.string.strip()
    return "No Title Found"


# now this funcn will fetch whole content of the page by passing input as parsed html object in this funcn
def to_get_body_contents(soup):

    # remove script and style elements
    for scrpts in soup(["script", "style"]):
        scrpts.decompose()

    text = soup.get_text(separator="\n") # extract whole text

    lins = []  # it will store body 
    seen = set() # I have initialised it to remove duplicate lines 

    for line in text.splitlines():
        clean__line = line.strip()

        # remove unwanted JS message
        if clean__line == "You need to enable JavaScript to run this app.":
            continue                                                       # to skip unwanted js fallback message

        # keep only unique meaningful lines, like remove empty linees , remove duplicates, very small fragments remove
        if clean__line and clean__line not in seen and len(clean__line) > 2:
            seen.add(clean__line)
            lins.append(clean__line)

    return "\n".join(lins)


# Now this funcn will extract links of that page 
def to_get_links(soup, base_url):
    links = set()   # using set to remove duplicates

    for tag in soup.find_all("a", href=True):       # extrating all anchor tags
        full_url = urljoin(base_url, tag["href"])         # converting relative link to url
        links.add(full_url)

    return sorted(links) # returning links in alphabetic sorted order


# this is the main funcn starting point of my program
def main():
    if len(sys.argv) != 2: # here i am checking url has given proper url or not 
        print("Usage: python scraper.py <URL>")
        return

    url = sys.argv[1] # to fetch url from command line

    # automatically add https if missing
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    html = to_get_page(url)

    if not html:
        return

    soup = BeautifulSoup(html, "html.parser")

    print("Title:")
    print(to_get_title(soup))

    print("Body:")
    print(to_get_body_contents(soup))

    print("Outlinks:")
    for link in to_get_links(soup, url):
        print(link)


if __name__ == "__main__":
    main()
