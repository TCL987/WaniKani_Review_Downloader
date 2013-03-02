import json
import urllib
import time
import codecs
from datetime import datetime

FILENAME = "WaniKani_Lists.csv"
TITLES = ["Radicals", "Kanji", "Vocabulary"]
API_KEY = "b6848ce10af685617dcec5bf67bb42be"
LEVELS = "1,2"

REQUEST_URLS = ["http://www.wanikani.com/api/user/" + API_KEY + "/radicals/",
                "http://www.wanikani.com/api/user/" + API_KEY + "/kanji/",
                "http://www.wanikani.com/api/user/" + API_KEY + "/vocabulary/"]


def get_reading(url, item):
    if url.find("kanji") > 0:
        important_reading = item[u'important_reading']
        return item[important_reading]
    if url.find("vocabulary") > 0:
        return item[u'kana']
    return None


def parse_api_feed(urls, level=""):
    data = []

    for url in urls:
        current = []
        feed = (urllib.urlopen(url + str(level))).read()
        result = json.loads(feed.decode("utf8"))
        items = (result[u'requested_information'])
        failed = 0
        for item in items:
            try:
                stats = item[u'stats']
                if (stats is not None and stats is not u'null'):
                    character = item[u'character']
                    meaning = item[u'meaning']
                    meaning = meaning.replace(',',';')
                    available = (item[u'stats'])[u'available_date']
                    available = datetime.fromtimestamp(int(available))
                    available = available.strftime('%Y-%m-%d %H:%M:%S')
                    reading = get_reading(url, item)
                    if reading is not None:
                        reading = reading.replace(',',';')
                    current.append([character, meaning, reading, available])
            except Exception as inst:
                failed += 1
                print item, failed, inst.message
        data.append(current)
    return data


def output_file(filename, level=""):
    f = codecs.open(filename, 'w', "utf-8")
    f.write(u'\uFEFF')
    try:
        data = parse_api_feed(REQUEST_URLS, level)
        for part in data:
            f.write(TITLES[data.index(part)] + "\n" + "----------\n")
            for entry in part:
                if entry[0] is None:
                    entry[0] = "No unicode"
                if entry[2] is None:
                    entry.pop(2)
                line = ','.join(entry) + '\n'
                f.write(line)
            f.write('----------\n\n')
    finally:
        f.close()

try:
    print "Getting List"
    output_file(FILENAME, LEVELS)
    print "List saved"
except:
    print "Failed, the file is probably open or the API is down."


