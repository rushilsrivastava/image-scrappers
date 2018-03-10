# image-scrapers
Image Scrapers built for scraping Bing and Google images + metadata. Bing works with Python 3 and Google works with Python 2 and 3.

Both the scrapers will save to their own folders under a global folder called `dataset`.

The method used here can grab large numbers of images by automatically generating 'Show more' click events!  No more 100 limit!

## How to Use

### Google:

[![Build Status](https://travis-ci.org/rushilsrivastava/image-scrapers.svg?branch=master)](https://travis-ci.org/rushilsrivastava/image-scrapers)

Make sure you install the requirements by doing:

    pip install -r requirements.txt

Ensure you have the [appropriate version](https://sites.google.com/a/chromium.org/chromedriver/downloads) of ChromeDriver on your machine.

Then:

    python3.5 google_scraper.py --url "https://www.google.com/search?q=cats&source=lnms&tbm=isch&sa=X&ved=0ahUKEwiwoLXK1qLVAhWqwFQKHYMwBs8Q_AUICigB"

Other command line options:

    --hash {yes|no} - default:  no (if unspecified)
        choose to rename each file based on its sha256 hash equivelent.  This is a proven way to detect duplicate downloads
        which may have different filenames.
    --unique {yes|no} - default:  yes (if unspecified)
        choose to place the search run into its own unique folder.  if set to "no", all subsequent runs of the tool will place
        the results in the dataset/google folder, and not into their own unique folders based on search terminology.

### Bing:

Bing Scraping requires a [Bing Image Search API Key](https://azure.microsoft.com/en-us/services/cognitive-services/bing-image-search-api/).

Make sure you install the requirements by doing:

    pip install -r requirements.txt

Then:

    python3.5 bing_scraper.py cats -key YOUR_API_KEY_HERE


## FAQs

*Why do I ask for the url parameter?*
 - I am using the URL parameter so the user can specify tag searches as well (the rectangular suggestions on the top for Google)

*Is this legal?*
 - I do not condone or advise copyright infringement or plagiarism.  It is your responsibility to use this tool appropriately.