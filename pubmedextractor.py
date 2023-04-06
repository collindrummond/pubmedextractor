__author__ = 'Collin Drummond, cdev@email.unc.edu, Onyen = cdev'

import requests
import shutil
import lxml
import tldextract
import re
from bs4 import BeautifulSoup
from dataclasses import dataclass, asdict
from pprint import pprint

MAIN_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=36932988"

@dataclass
class Article:
    pmid: int
    title: str
    date: str
    journal: str
    url: str
    doi: str
    authors: tuple
    type: str
    grants: tuple


def print_metadata(article):
    pprint(asdict(article), sort_dicts=False)


# Simple wrapper around requests.get() to print http status code
def get_url(*args, **kwargs) -> requests.Response:
    response = requests.get(*args, **kwargs)

    print(response.request.method, response.request.url)
    print(response.status_code, response.reason)

    return response


# Finds the PubDate field and parses it into text as YYYY Mon DD.
def get_date(soup):
    date = soup.find("PubDate").get_text(separator=' ')
    return date


def get_title(soup):
    title = soup.find("ArticleTitle").get_text(separator=' ')
    return title


def get_journal(soup):
    journal = soup.find("Title").get_text(separator=' ')
    return journal


def get_pmid_url(pmid):
    url = 'https://pubmed.ncbi.nlm.nih.gov/' + str(pmid)
    return url


def get_doi(soup):
    doi = soup.find("ELocationID").get_text(separator=' ')
    return doi


def get_authors(soup):
    author = soup.find_all("Author",)
    author_list = []
    for name in author:
        author_regex = re.compile(r'\D\d\d\D\D\d\d\d\d\d\d').search(name.get_text()).group()
        author_list.append(author_regex)

    return author_list


def get_type(soup):
    type = soup.find("PublicationType").get_text(separator=' ')
    return type


def get_grants(soup):
    grants = soup.find_all("Grant")
    grant_list = []
    for grant in grants:
        grant_regex = re.compile(r'\D\d\d\D\D\d\d\d\d\d\d').search(grant.get_text()).group()
        grant_list.append(grant_regex)
    return grant_list


def get_metadata(pmid):
    # Make remote request. Can also be POST with parameters
    main_response = get_url(MAIN_URL)

    # Parse content of request response (page)
    main_soup = BeautifulSoup(main_response.content, "lxml-xml")

    date = get_date(main_soup)
    title = get_title(main_soup)
    journal = get_journal(main_soup)
    url = get_pmid_url(pmid)
    doi = get_doi(main_soup)
    author_list = get_authors(main_soup)
    type = get_type(main_soup)
    grant_list = get_grants(main_soup)

    article = Article(pmid, title, date, journal, url, doi, author_list, type, grant_list)

    print_metadata(article)


def main():
    pmids = 36932988

    get_metadata(pmids)

main()