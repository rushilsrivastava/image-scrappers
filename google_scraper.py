import requests
import time
import urllib
import argparse
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from pathlib import Path
from lxml.html import fromstring
import os
import sys
from fake_useragent import UserAgent
if sys.version_info[0] > 2:
    import urllib.parse as urlparse
else:
    import urlparse
    reload(sys)
    sys.setdefaultencoding('utf8')

'''
Commandline based Google Image scraping. Gets up to 800 images.
Author: Rushil Srivastava (rushu0922@gmail.com)
'''


def search(url):
    # Create a browser and resize for exact pinpoints
    browser = webdriver.Chrome()
    browser.set_window_size(1024, 768)
    print("\n===============================================\n")
    print("==> Chrome Driver Launched")

    # Open the link
    browser.get(url)
    time.sleep(1)
    print("==> Link Loaded")

    element = browser.find_element_by_tag_name("body")

    print("==> Scrolling page...")
    # Scroll down
    for i in range(30):
        element.send_keys(Keys.PAGE_DOWN)
        time.sleep(0.3)  # bot id protection

    try:
        browser.find_element_by_id("smb").click()
        print("==> Generated 'Show More' event")
        for i in range(50):
            element.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.3)  # bot id protection
    except:
        for i in range(10):
            element.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.3)  # bot id protection

    print("==> Reached end of page")

    time.sleep(1)
    # Get page source and close the browser
    print("==> Saving page source...")
    source = browser.page_source
    with open('dataset/logs/google/source.html', 'w+', encoding='utf-8', errors='replace') as f:
        f.write(source)

    print("==> Page source saved")
	
    browser.close()
    print("==> Closed browser window")
    print("\n===============================================\n")

    return source


def error(link):
    print("==> Skipped. Can't download or no metadata.\n")
    file = Path("dataset/logs/google/errors.log".format(query))
    if file.is_file():
        with open("dataset/logs/google/errors.log".format(query), "a") as myfile:
            myfile.write(link + "\n")
    else:
        with open("dataset/logs/google/errors.log".format(query), "w+") as myfile:
            myfile.write(link + "\n")


def download_image(link, image_data):
    download_image.delta += 1
    # Use a random user agent header for bot id
    ua = UserAgent()
    headers = {"User-Agent": ua.random}

    # Get the image link
    try:
        # Get the file name and type
        file_name = link.split("/")[-1]
        type = file_name.split(".")[-1]
        type = (type[:3]) if len(type) > 3 else type
        if type.lower() == "jpe":
            type = "jpeg"
        if type.lower() not in ["jpeg", "jfif", "exif", "tiff", "gif", "bmp", "png", "webp", "jpg"]:
            type = "jpg"

        # Download the image
        print("==> Downloading Image #{} from {}".format(
            download_image.delta, link))
        try:
            if sys.version_info[0] > 2:
                urllib.request.urlretrieve(link, "dataset/google/{}/".format(query) + "Scrapper_{}.{}".format(str(download_image.delta), type))
            else:
                urllib.urlopen(link, "dataset/google/{}/".format(query) + "Scrapper_{}.{}".format(str(download_image.delta), type))
            print("[%] Downloaded File")
            with open("dataset/google/{}/Scrapper_{}.json".format(query, str(download_image.delta)), "w") as outfile:
                json.dump(image_data, outfile, indent=4)
        except Exception as e:
            download_image.delta -= 1
            download_image.errors += 1
            print("==> Error: {}".format(e))
            error(link)
    except Exception as e:
        download_image.delta -= 1
        download_image.errors += 1
        print("==> Error: {}".format(e))
        error(link)


if __name__ == "__main__":
    # parse command line options
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="Give the url that I should parse.")
    args = parser.parse_args()

    # set local vars from user input
    query = urlparse.parse_qs(urlparse.urlparse(args.url).query)['q'][0]
    url = args.url

    # check directory and create if necessary
    if not os.path.isdir("dataset/"):
        os.makedirs("dataset/")
    if not os.path.isdir("dataset/google/{}".format(query)):
        os.makedirs("dataset/google/{}".format(query))
    if not os.path.isdir("dataset/logs/google/".format(query)):
        os.makedirs("dataset/logs/google/".format(query))

    source = search(url)

    # set stack limit
    sys.setrecursionlimit(1000000)

    # Parse the page source and download pics
    soup = BeautifulSoup(str(source), "html.parser")
    ua = UserAgent()
    headers = {"User-Agent": ua.random}

    try:
        os.remove("dataset/logs/google/errors.log")
    except OSError:
        pass

    # Get the links and image data
    links = [json.loads(i.text)["ou"]
             for i in soup.find_all("div", class_="rg_meta")]
    print("[%] Indexed {} Images.".format(len(links)))

    print("\n===============================================\n")
    print("[%] Getting image metadata\n")
    images = {}
    linkcounter = 0
    errorcounter = 0
    for a in soup.find_all("div", class_="rg_meta"):
        rg_meta = json.loads(a.text)
        if 'st' in rg_meta:
            title = rg_meta['st']
        else:
            title = ""
        link = rg_meta["ou"]
        print("==> Getting info on: {}".format(link))
        try:
            image_data = "google", query, rg_meta["pt"], rg_meta["s"], title, link, rg_meta["ru"]
            images[link] = image_data
        except Exception as e:
            images[link] = image_data
            print("==> Issue getting data: {}\n[!] Error: {}".format(rg_meta, e))
            errorcounter += 1

        print("==> Information received for: {}".format(link))
        linkcounter += 1

    # Open i processes to download
    print ("\n Done fetching metadata.  {} succeeded | {} failed".format(linkcounter,errorcounter))
    print("\n===============================================\n")
    download_image.delta = 0
    download_image.errors = 0
    for i, (link) in enumerate(links):
        try:
            download_image(link, images[link])
        except Exception as e:
            error(link)

    print("\n\n[%] Done. Downloaded images.   {} succeeded | {} failed".format(download_image.delta,download_image.errors))
    print("\n===============================================\n")
