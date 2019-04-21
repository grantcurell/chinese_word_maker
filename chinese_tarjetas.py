import os

from urllib.request import urlopen
from urllib.parse import quote
from html.parser import HTMLParser
from unidecode import unidecode # You can install this library with pip install unidecode
from bs4 import BeautifulSoup


def _write_word():
    with open('new_cards', 'a+', encoding="utf-8") as f:
        # You need the <br/>s in anki for newlines. The strip makes sure there isn't one randomly trailing
        f.write(self.text_edit_card_front.toPlainText().replace("\n", "<br/>").strip('<br/>').replace(";",
                                                                                                      ":") + ";" + self.text_edit_card_back.toPlainText().replace(
            "\n", "<br/>").strip('<br/>').replace(";", ":") + ";" + ";" + "" + "\n")
        # This begins the section which handles adding cards if examples are included
        self.list.pop()
        f.close()
        self._create_card()

def process_entry(entry):
    """
    Processes a single row from www.mbdg.net and returns it in a dictionary

    :param entry: This is equivalent to one row in the results from www.mdbg.net
    :type entry: bs4.element.Tag
    :return: Returns a list of dictionary items containing each of the possible results
    :type: list of dicts
    """

    organized_entry = {}

    organized_entry.update({"traditional": entry.find("td", {"class": "head"}).find("div", {"class": "hanzi"}).text})
    organized_entry.update({"pinyin": entry.find("div", {"class": "pinyin"}).text})

    # The entries come separated by /'s which is why we have the split here
    organized_entry.update({"defs": str(entry.find("div", {"class": "defs"}).text).split('/')})

    tail = entry.find("td", {"class": "tail"})
    simplified = tail.find("div", {"class": "hanzi"})  # type: bs4.element.Tag
    hsk = tail.find("div", {"class": "hsk"})  # type: bs4.element.Tag

    if simplified is not None:
        organized_entry.update({"simplified": simplified.text})
    else:
        organized_entry.update({"simplified": ""})

    if hsk is not None:
        organized_entry.update({"hsk": hsk.text})
    else:
        organized_entry.update({"hsk": ""})

    return organized_entry


def main():

    print("https://www.mdbg.net/chinese/dictionary?page=worddict&wdrst=1&wdqb=" + "人士")

    url_string = "https://www.mdbg.net/chinese/dictionary?page=worddict&wdrst=1&wdqb=" + quote("人")  # type: str

    html = urlopen(url_string).read().decode('utf-8')  # type: str

    soup = BeautifulSoup(html, 'html.parser')

    results = soup.find_all("tr", {"class": "row"})  # type: bs4.element.ResultSet

    entries = []  # type: list

    for entry in results:

        entries.append(process_entry(entry))

    if len(results) > 1:


    for entry in entries:
        print(entry)


if __name__ == '__main__':
    main()