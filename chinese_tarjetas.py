__author__ = "Grant Curell"
__copyright__ = "Do what you want with it"

__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Grant Curell"

from argparse import ArgumentParser
from urllib.request import urlopen
from urllib.parse import quote
from bs4 import BeautifulSoup
import pprint


def output_words(output_file_name, word_list):
    """
    Outputs the new words to a file for import into Anki

    :param str output_file_name: The name of the file to which we want to write the new words
    :param list word_list: The list of words we want to write to file
    :return: Returns nothing
    """

    with open(output_file_name, 'a+', encoding="utf-8") as output_file:

        for word in word_list:

            # You need the <br/>s in anki for newlines. The strip makes sure there isn't one randomly trailing
            output_file.write(word["traditional"] + "," + word["simplified"] + "," + word["pinyin"] + "," +
                              "<br>".join(word["defs"]).replace(",", "") + "," + word["hsk"].replace(" ", "") + "\n")

            print("Writing: " + word["traditional"] + "," + word["simplified"] + "," + word["pinyin"] + "," +
                  "<br>".join(word["defs"]) + "," + word["hsk"])


def get_words(input_file_name):
    """
    Reaches out to www.mdbg.net and grabs the data for each of the words on which you want data

    :param str input_file_name: The name of the file which contains the words we want to grab
    :return: Returns a list of the words you want added to Anki with their corresponding data
    :rtype: list
    """

    with open(input_file_name, encoding="utf-8") as input_file:

        new_words = []  # type: list
        pp = pprint.PrettyPrinter(indent=4)

        for word in input_file.readlines():

            word = word.strip()  # type: str

            print("Requested word is: " + word)
            print("URL is: https://www.mdbg.net/chinese/dictionary?page=worddict&wdrst=1&wdqb=" + word)

            url_string = "https://www.mdbg.net/chinese/dictionary?page=worddict&wdrst=1&wdqb=" \
                         + quote(word)  # type: str

            html = urlopen(url_string).read().decode('utf-8')  # type: str

            soup = BeautifulSoup(html, 'html.parser')  # type: bs4.BeautifulSoup

            results = soup.find_all("tr", {"class": "row"})  # type: bs4.element.ResultSet

            entries = []  # type: list

            for entry in results:

                entries.append(process_entry(entry))

            if len(entries) > 1:
                print("It looks like there are multiple definitions for this word available. Which one would you like"
                      " to use?")

                print("\n\n-------- Option 0 ---------\n\n")
                print("Type 0 to skip.")

                for index, entry in enumerate(entries):
                    print("\n\n-------- Option " + str(index+1) + "---------\n\n")
                    pp.pprint(entry)

                print("\n\n")
                selection = -1  # type: int

                while (selection > len(entries) or selection < 1) and selection != 0:
                    selection = int(input("Enter your selection: "))

                if selection != 0:
                    new_words.append(entries[selection-1])

            else:
                new_words.append(entries[0])

    return new_words


def process_entry(entry):
    """
    Processes a single row from www.mbdg.net and returns it in a dictionary

    :param bs4.element.Tag entry: This is equivalent to one row in the results from www.mdbg.net
    :return: Returns a list of dictionary items containing each of the possible results
    :rtype: list of dicts
    """

    organized_entry = {}

    organized_entry.update({"traditional": entry.find("td", {"class": "head"}).find("div", {"class": "hanzi"}).text})

    # I didn't investigate why, but for some reason the site was adding u200b so I just manually stripped that
    # whitespace out.
    organized_entry.update({"pinyin": str(entry.find("div", {"class": "pinyin"}).text).strip().replace(u'\u200b', "")})

    # The entries come separated by /'s which is why we have the split here
    # The map function here just gets rid of the extra whitespace on each word before assignment
    organized_entry.update({"defs": list(map(str.strip, str(entry.find("div", {"class": "defs"}).text).split('/')))})

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

    pp = pprint.PrettyPrinter(indent=4)

    parser = ArgumentParser(description="Used to create Anki flash cards based on data from the website www.mdbg.net")
    parser.add_argument('--file', metavar='FILE', dest="input_file_name", type=str, required=True,
                        help='The path to a newline delimited list of Chinese words in Hanji')
    parser.add_argument('--output-file', metavar='OUTPUT-FILE', dest="output_file_name", type=str, required=False,
                        default="word_list.txt",
                        help='by default this is word_list.txt. You may change it by providing this argument.')
    args = parser.parse_args()  # type: argparse.Namespace

    output_words(args.output_file_name, get_words(args.input_file_name))


if __name__ == '__main__':
    main()