# coding: UTF-8

import requests

URL_APP = "http://homolog.opac.scielo.org/"

LEGACY_URLS = "fixtures/legacy_urls.txt"

if __name__ == "__main__":
    with open(LEGACY_URLS) as leg_url:
        for line in leg_url:
            url = URL_APP + line.strip("\n")

            resp = requests.get(url)

            if resp.status_code != 200:
                print("URL %s, Status Code: %s" % (url, resp.status_code))
