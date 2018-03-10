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
import config
import hashlib
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
Improvements by:  LupineDream (loopyd at lupinedream dot com)
'''


def search(url):
    # Create a browser and resize for exact pinpoints
    browser = webdriver.Chrome()
    browser.set_window_size(1024, 768)
    print("\n===============================================\n")
    print("[%] Chromedriver Launched")

    # Open the link
    browser.get(url)
    time.sleep(1)
    print("[%] Loaded Link")

    element = browser.find_element_by_tag_name("body")

    print("[%] Scrolling Page")
    # Scroll down
    for i in range(30):
        element.send_keys(Keys.PAGE_DOWN)
        time.sleep(0.3)  # bot id protection

    try:
        browser.find_element_by_id("smb").click()
        print("[%] Loaded Show More Element")
        for i in range(50):
            element.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.3)  # bot id protection
    except:
        for i in range(10):
            element.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.3)  # bot id protection

    print("[%] Reached the end of the Page")

    time.sleep(1)
    # Get page source and close the browser
    source = browser.page_source
	
	# fix for travis cli build error with python 2.7
    if sys.version_info[0] > 2:
        with open('dataset/logs/google/source.html', 'w+', encoding='utf-8', errors='replace') as f:
            f.write(source)
    else:
        with open('dataset/logs/google/source.html', 'w') as f:
            f.write(source)
	
    browser.close()
    print("[%] Closed chromedriver")
    print("\n===============================================\n")

    return source


def error(link):
    print("[%] Skipped. Can't download or no metadata.")
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
	
    # set the current directory (fix for python 2.7)
    if sys.version_info[0] > 2:
	    curdir = ""
    else:
        curdir = os.path.dirname(__file__) + os.sep
    
    # ----- BEGIN main download_image try/catch
    try:
        # Get the file name and type
        file_name = link.split("/")[-1]
        type = file_name.split(".")[-1]
        type = (type[:3]) if len(type) > 3 else type
        if type.lower() == "jpe":
            type = "jpeg"
        if type.lower() not in ["jpeg", "jfif", "exif", "tiff", "gif", "bmp", "png", "webp", "jpg"]:
            type = "jpg"

	    # set the working paths depending on the 'unique' argument and the operating system (fix for python 2.7 and linux/windows)
        if config.unique == True:
            imagep = (curdir + "dataset" + os.sep + "google" + os.sep + "{}".format(query) + os.sep + "Scrapper_{}.{}".format(str(download_image.delta), type))
            jsonp = (curdir + "dataset" + os.sep + "/google" + os.sep + "{}".formatr(query) + os.sep + "Scrapper_{}.json".format(str(download_image.delta)))
        else:
            imagep = (curdir + "dataset" + os.sep + "google" + os.sep + "Scrapper_{}.{}".format(str(download_image.delta), type))
            jsonp = (curdir + "dataset" + os.sep + "google" + os.sep + "Scrapper_{}.json".format(str(download_image.delta)))

        # Download the image
        print("\n==> Downloading Image #{} from {}".format(
            download_image.delta, link))
        try:
            
			# open the URL and retrieve the image
            if sys.version_info[0] > 2:
                urllib.request.urlretrieve(link, imagep)
            else:
                urllib.urlopen(link, imagep)
            print("[%] Downloaded image")
            
            # dump the json metadata from the URL to the json file
            with open(jsonp, "w") as outfile:
                json.dump(image_data, outfile, indent=4)
            
            # if the 'hash' argument has been specified, perform the action to rename the files
            if config.hash == True:
                with open(imagep,"rb") as f:
                    contents = f.read()
                    shahash = hashlib.sha256(contents).hexdigest()
                os.rename(imagep,imagep.replace(("Scrapper_{}".format(str(download_image.delta))),shahash))
                os.rename(jsonp,jsonp.replace(("Scrapper_{}".format(str(download_image.delta))),shahash))
                print("[%] Generated sha256 hash: {}".format(str(shahash)))
				
        except Exception as e:
            download_image.delta -= 1
            download_image.errors += 1
            print("[!] Issue Downloading: {}\n[!] Error: {}".format(link, e))
            error(link)
    except Exception as e:
        download_image.delta -= 1
        download_image.errors += 1
        print("[!] Issue Downloading: {}\n[!] Error: {}".format(link, e))
        error(link)
	# ----- END main download_image try/catch


if __name__ == "__main__":
    # parse command line options
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", help="Give the url that the download tool should parse.")
    parser.add_argument("--hash", help="yes/no - Rename the files and json metadata to their sha256 equivalent.  Useful for mutated searches potentially involving duplicate downloads.", nargs="?", default="no")
    parser.add_argument("--unique", help="yes/no - Place all of the resulting downloads in their own unique sub-folder", nargs="?", default="no")
    args = parser.parse_args()

    # set local vars from user input
    query = urlparse.parse_qs(urlparse.urlparse(args.url).query)['q'][0]
    url = args.url

    # if the dataset root doesn't exist, create it.
    if not os.path.isdir("dataset/"):
        os.makedirs("dataset/")
    # if the log directory doesn't exist, create it.
    if not os.path.isdir("dataset/logs/google/".format(query)):
        os.makedirs("dataset/logs/google/".format(query))

    # set global vars for hash from user input
    if (args.hash).lower() == "yes":
        config.hash = True
    else:
        config.hash = False

    # set global vars and construct tree if nonexistent from user input.
    if (args.unique).lower() == "yes":
        config.unique = True
        config.imagepath = ("dataset/google/{}".format(query))
        if not os.path.isdir("dataset/google/{}".format(query)):
            os.makedirs("dataset/google/{}".format(query))
    else:
        config.unique = False
        config.imagepath = ("dataset/google/")
        if not os.path.isdir("dataset/google/"):
            os.makedirs("dataset/google/")

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
        print("[%] Getting info on: {}".format(link))
        try:
            image_data = "google", query, rg_meta["pt"], rg_meta["s"], title, link, rg_meta["ru"]
            images[link] = image_data
        except Exception as e:
            images[link] = image_data
            print("==> Issue getting data: {}\n[!] Error: {}".format(rg_meta, e))
            errorcounter += 1

        print("[%] Downloaded information for: {}".format(link))
        linkcounter += 1

    # Open i processes to download
    print ("\n Done fetching links from page.  {} succeeded | {} failed".format(linkcounter,errorcounter))
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
