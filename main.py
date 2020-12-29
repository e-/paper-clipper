import argparse
import sys
from selenium import webdriver

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import requests
import os
import re


logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
                    )
logger = logging.getLogger('clipper')


def parse():
    parser = argparse.ArgumentParser(description='Paper clipper')
    parser.add_argument('path', metavar='PATH', type=str,
                        help='path to the list of papers')
    parser.add_argument('--driver', default='chrome',
                        help='driver to use (default: chrome).')
    parser.add_argument('--failed', default='failed.txt',
                        help="file to store failed searches")
    # parser.add_argument('--sum', dest='accumulate', action='store_const',
    #                     const=sum, default=max,
    #                     help='sum the integers (default: find the max)')

    args = parser.parse_args()
    return args


def get_driver(args):
    if args.driver == 'chrome':
        return webdriver.Chrome()


def get_href(driver, term):
    driver.get("https://scholar.google.com/")
    elem = driver.find_element_by_name("q")
    elem.clear()
    elem.send_keys(term)
    elem.send_keys(Keys.RETURN)

    a = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "[PDF]"))
    )
    # a = driver.find_element_by_partial_link_text("[PDF]")

    href = a.get_attribute('href')
    return href


def main(args):
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    driver = get_driver(args)
    driver.implicitly_wait(2)

    failed = open(args.failed, 'w', encoding='utf-8')

    with open(args.path, 'r', encoding='utf-8') as fin:
        for term in fin.readlines():
            term = term.strip()

            try:
                m = re.match(r"^(\[.*\]).*“(.*)”.*$", term)
                filename = "{} {}".format(
                    m.group(1), m.group(2))
                filename = re.sub(r'[\-\.:]', '', filename)

                href = get_href(driver, term)
                logger.info(href)

                r = requests.get(href)

                # [Ahlberg and Shneiderman 94] Chris Ahlberg and Ben Shneiderman. “Visual Information Seeking: Tight Coupling of Dynamic Query Filters with Starfield Displays.”
                print(filename)
                with open(os.path.join('downloads', '{}.pdf'.format(filename)), 'wb') as f:
                    f.write(r.content)

            except Exception as e:
                logger.error(e)
                print(term, file=failed)

    failed.close()
    driver.quit()


if __name__ == '__main__':
    args = parse()
    main(args)
