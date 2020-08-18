__author__ = "Grant Curell"
__copyright__ = "Do what you want with it"
__license__ = "GPLv3"
__version__ = "2.1"
__maintainer__ = "Grant Curell"

import json
from argparse import ArgumentParser
from pathlib import Path
from concurrent.futures.thread import ThreadPoolExecutor
from urllib.request import urlopen
from urllib.parse import quote, urljoin
from bs4 import BeautifulSoup
from hanziconv import HanziConv
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from jinja2 import Template
from os import path, getenv
import bs4
import concurrent.futures
import traceback
import sys
import platform
import pickle
import logging
import re
import requests
import htmlmin


def create_driver(headless=True, binary_location=None, implicit_wait_time=5) -> webdriver:
    """
    Creates a Google Chrome-based web driver

    :param bool headless: Indicates whether to start the browser in headless mode or not
    :param str binary_location: The location of the chromedriver binary
    :param int implicit_wait_time: In case someone wants to modify it, they could change the time the browser will wait
                                   for results to return.
    :return: Returns a type of selenium.webdriver.chrome.webdriver.WebDriver for use in opening a chrome browser
    """
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--test-type")
    options.add_argument("--disable-web-security")

    if headless:
        options.add_argument("--headless")

    if binary_location is not None:
        options.binary_location = binary_location

    driver = webdriver.Chrome(chrome_options=options)

    # This means the driver will wait up to 10 seconds to find a designated element.
    driver.implicitly_wait(implicit_wait_time)

    return driver


def get_examples_html(word, word_pinyin, example_driver=None, is_server=True, max_page=20, show_chrome=False):
    """
    Reach out to https://dict.naver.com/linedict/zhendict/dict.html#/cnen/example?query=%E4%B8%BA%E7%9D%80
    and get example sentences.

    :param str word: The word_to_process, in traditional character format, for which you want to retrieve examples
    :param str word_pinyin: The pinyin of the word_to_process - to make sure if there are multiple variants you get a matching
                            variant
    :param selenium.webdriver.chrome.webdriver.WebDriver driver: The webdriver we want to use to generate the example
    :param bool is_server: Determines if the function is being called from a server or not.
    :param int max_page: The maximum number of pages in which to search for examples
    :param bool show_chrome: Used to determine whether to show the browser or not
    :return Returns a template string with all of the examples formatted within it.
    :rtype str
    """

    template = None

    logging.info("Creating an example for " + word)

    logging.info("Requested word_to_process is: " + word)
    logging.debug("URL is: https://dict.naver.com/linedict/zhendict/dict.html#/cnen/example?query=" + word)

    url_string = "https://dict.naver.com/linedict/zhendict/dict.html#/cnen/example?query=" \
                 + quote(word)  # type: str

    if not is_server:
        example_driver = create_driver()

    example_driver.get(url_string)

    i = 0

    # This forces Chrome to wait to return until an element with class name autolink appears. Autolink in this case
    # Autolink is the name of the span class in the examples.
    while i < 2:
        try:
            example_driver.find_element_by_class_name("autolink")
            i = 2
        except NoSuchElementException:
            if i < 2:
                i = i + 1
                example_driver.get(url_string)
            else:
                if not is_server:
                    example_driver.quit()
                return "No examples found for that word_to_process or finding an example took longer than 5 seconds."

    examples = []
    examples_found = False

    i = 0
    while not examples_found:

        html = example_driver.page_source

        soup = BeautifulSoup(html, 'html.parser')  # type: bs4.BeautifulSoup

        results = soup.find_all("div", {"class": "example_lst"})  # type: bs4.element.ResultSet

        if len(results) > 1:
            if not is_server:
                example_driver.quit()
            return "The HTML contained more than one div with class \"example_lst\" which shouldn't happen. Has their " \
                   "HTML changed? This error prevents us from continuing to generate an example."

        for example in results[0].find_all("li"):

            # We don't need more than five examples.
            if i > 4:
                examples_found = True
                break

            data = example.find("div", {"class": "exam"})

            chinese_sentence = data.find("p", {"class": "stc"}).text.split(" ")
            del chinese_sentence[-2:]
            chinese_sentence = "".join(chinese_sentence).replace(word, "<em class=\"highlight\">" + word + "</em>")

            # I know the way I did this is gross. Sue me.
            pinyin = str(data.find("p", {"class": "pinyin"})).replace("<p class=\"pinyin\">", "").replace("</p>", "") \
                .replace("hl", "highlight")
            translation = data.find("p", {"class": "trans"}).text

            if word_pinyin in pinyin:
                examples.append((chinese_sentence, pinyin, translation))
                i = i + 1
                logging.debug("Character pinyin did not match example. Skipping this example.")

        template = Template(open('examples.html.j2', encoding="utf-8").read())

        if not examples_found:
            logging.debug("Not all examples found. Moving to next page.")
            try:
                # Example if I ever decide to change this to a click:
                # example_driver.find_element_by_css_selector('a.btn.next').click()  # Click to get the next page

                # Urls are normally formatted like:
                # https://dict.naver.com/linedict/zhendict/dict.html#/cnen/example?query=%E7%9D%80&page=1
                # If we want to get the next page we can just manually change the page via the below.
                split_url = example_driver.current_url.split("page=")
                if len(split_url) == 1:
                    example_driver.get(split_url[0] + "&page=2")
                else:
                    # split_url[1] contains the page number in the URL
                    page = int(split_url[1]) + 1
                    if page < max_page:
                        example_driver.get(split_url[0] + "page=" + str(page))
                    else:
                        logging.info("Checked " + str(page) + " pages looking for " + word + " (" + word_pinyin +
                                     ") and did not reach requested number of examples")
                        break
                example_driver.find_element_by_class_name("autolink")  # Wait for the results to appear
            except NoSuchElementException:
                if i > 0:
                    logging.info("No more example pages to check. Moving on.")
                else:
                    "No examples found for that word_to_process or finding an example took longer than 5 seconds."

    if not is_server:
        example_driver.quit()

    if template is None:
        return None
    else:
        return template.render(examples=examples)


def query_yes_no(question, default="yes"):
    """
    Ask a yes/no question via raw_input() and return the answer.

    :param str question: A string that is presented to the user.
    :param str default: is the presumed answer if the user just hits <Enter>.
    :return The "answer" return value is True for "yes" or False for "no".
    :rtype bool
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def output_combined(output_file_name, word_list, delimiter, thread_count, show_chrome=False):
    """
    Allows you to output flashcards with both the word_to_process and the character embedded in them.

    :param str output_file_name: The name of the file to which we want to write the new flashcards
    :param list word_list: The list of words we want to write to file
    :param str delimiter: The delimiter you want to use for your flashcards
    :param int thread_count: The number of threads that will be used to pull examples
    :param bool show_chrome: Used to control whether the chrome browsers will appear or not
    :return: Returns nothing
    """

    with open(output_file_name, 'w', encoding="utf-8-sig") as output_file:

        examples = {}

        logging.info("Launching threads to get example text.")

        # Here we use threading to launch multiple threads to get the examples at the same time so this doesn't take
        # forever.
        with ThreadPoolExecutor(max_workers=thread_count) as executor:

            future_example = {executor.submit(get_examples_html, word["simplified"], word["pinyin"], is_server=False,
                                              show_chrome=show_chrome): word for word in word_list}

            length = str(len(word_list))
            i = 1

            for future in concurrent.futures.as_completed(future_example):
                word_processed = future_example[future]
                logging.info("We have processed " + str(i) + " of " + length + " examples.")
                try:
                    if word_processed is not None:
                        examples[word_processed["final_traditional"]] = future.result()
                    else:
                        logging.info("No examples found for word_to_process: " + word_processed["final_traditional"])
                except Exception as exc:
                    logging.error('%r generated an exception: %s' % (word_processed["final_traditional"], exc))
                else:
                    logging.info('Finished processing word_to_process %s' % word_processed["final_traditional"])

                i = i + 1

        logging.info("Finished getting all examples.")

        logging.info("Writing words.")
        for word in word_list:

            output_file.write(word["final_traditional"] + delimiter + word["simplified"] + delimiter + word["pinyin"] +
                              delimiter + "<br>".join(word["defs"]).replace(delimiter, "") +
                              delimiter + word["hsk"].replace(" ", "") + delimiter +
                              word["history"].replace(delimiter, "") + delimiter)

            for character in word["characters"]:
                output_file.write(character.replace('\n', "").replace(delimiter, ""))

            try:
                line = examples[word["final_traditional"]].replace('\n', "") + "\n"
            except KeyError:
                logging.debug("No examples found for word_to_process: " + word["final_traditional"])
            i = i + 1

            output_file.write(line.replace(delimiter, ""))


def get_words(words, skip_choices=False, ask_if_match_not_found=True, combine_exact_defs=False, preference_hsk=False):
    """
    Reaches out to www.mdbg.net and grabs the data for each of the words on which you want data

    :param list words: The list of the words you want to add
    :param bool skip_choices: Whether you want to skip selection of the different possible options. The closest match
                              will be selected instead.
    :param bool ask_if_match_not_found: The program will first try to skip all choices, but if it can't find a match
                                         it will ask.
    :param bool combine_exact_defs: Used if you want to just return a definition for everything with an exact match.
    :param bool preference_hsk: Used as a tiebreaker if there are multiple matches. Selects the one which is an HSK word_to_process
    :return: Returns two lists, one with the words found and the other with the characters found
    :rtype: list
    """

    new_words = []  # type: list

    length = str(len(words))
    i = 1

    for word in words:

        logging.info("Processing word_to_process " + str(i) + " of " + length)
        i = i + 1

        try:
            word = word.strip()  # type: str

            for word_entry in process_word(word, skip_choices=skip_choices,
                                           ask_if_match_not_found=ask_if_match_not_found,
                                           combine_exact_defs=combine_exact_defs,
                                           preference_hsk=preference_hsk):
                if word_entry:
                    new_words.append(word_entry)

        except KeyboardInterrupt:
            if query_yes_no("You have pressed ctrl+C. Are you sure you want to exit?"):
                exit(0)
        except AttributeError as e:
            logging.error("It looks like we've caught an attribute error. Maybe there's an invalid character "
                          "in the input? Error is: " + str(e))
            return None
        # Because you could spend a lot of time working on this we want to avoid program termination at all costs
        # Because of this we catch all exceptions and provide the option to continue or not.
        except:
            traceback.print_exc()
            logging.error("Uh oh. We've run into a problem, but we're trying to stop the program from terminating "
                          "on you!")
            if not query_yes_no(
                    "We have caught an unknown exception but prevented the program from terminating. "
                    "Do you want to continue with the next word_to_process?"):
                exit(1)

    if len(new_words) < 1:
        new_words = None

    return new_words


def extract_html_images(site: str, soup: BeautifulSoup, character: str = "") -> BeautifulSoup:
    """
    Grabs all the images from chinse-characters.org or other site

    :param character: The character for which you are grabbing images
    :param site: The site from which you want to extract the characters. Should only be the base URL.
    :param soup: A BS4 object containing all the HTML
    :return: Returns an updated BeautifulSoup object with the image names mangled for Anki.
    """

    for img in soup.find_all('img'):
        url = img['src']
        filename = re.search(r'/([\w_-]+)/([\w_-]+[.](jpg|gif|png))$', url)

        if not filename:
            print("Regex didn't match with the url: {}".format(url))
            continue

        file_prefix = character + "_" + filename.group(1) + "_" + filename.group(2)

        if path.exists(path.join(image_path, file_prefix)):
            logging.warning("WARNING: the file " + character + filename.group(1) + " already exists so we are skipping "
                                                                                   "it!!!")
        else:
            with open(path.join(image_path, file_prefix), 'wb') as f:
                if 'http' not in url:
                    # sometimes an image source can be relative
                    # if it is provide the base url which also happens
                    # to be the site variable atm.
                    url = '{}{}'.format(site, url)
                response = requests.get(url)
                f.write(response.content)

        img['src'] = file_prefix

    return soup


def process_word_entry(entry):
    """
    Processes a single row from www.mbdg.net and returns it in a dictionary

    :param bs4.element.Tag entry: This is equivalent to one row in the results from www.mdbg.net
    :return: Returns a list of dictionary items containing each of the possible results
    :rtype: list of dicts
    """

    organized_entry = {"characters": []}  # type: dict

    organized_entry. \
        update({"traditional": entry.find("td", {"class": "head"}).find("div", {"class": "hanzi"}).text})

    # I didn't investigate why, but for some reason the site was adding u200b so I just manually stripped that
    # whitespace out.
    organized_entry. \
        update({"pinyin": str(entry.find("div", {"class": "pinyin"}).text).lower().strip().replace(u'\u200b', "")})

    # The entries come separated by /'s which is why we have the split here
    # The map function here just gets rid of the extra whitespace on each word_to_process before assignment
    organized_entry. \
        update({"defs": list(map(str.strip, str(entry.find("div", {"class": "defs"}).text).split('/')))})

    tail = entry.find("td", {"class": "tail"})
    simplified = tail.find("div", {"class": "hanzi"})  # type: bs4.element.Tag
    hsk = tail.find("div", {"class": "hsk"})  # type: bs4.element.Tag

    character_string = ""

    if simplified is not None:
        organized_entry.update({"simplified": simplified.text})

        for i, character in enumerate(organized_entry["traditional"], start=0):

            if character == organized_entry["simplified"][i]:
                character_string = character_string + character
            else:
                character_string = character_string + character + organized_entry["simplified"][i]
    else:
        organized_entry.update({"simplified": ""})
        character_string = organized_entry["traditional"]

    organized_entry["history"] = ""

    for i, character in enumerate("".join(dict.fromkeys(organized_entry["traditional"]))):
        r = requests.put("http://127.0.0.1:5000/api/lookup", data=json.dumps({"characters_to_lookup": character}),
                         headers={'Content-Type': 'application/json'})

        if r.status_code != 404:
            if i == 0:
                organized_entry["history"] = organized_entry["history"] + r.json()[0]["explanation"]
            else:
                organized_entry["history"] = organized_entry["history"] + "<br><br>" + r.json()[0]["explanation"]
        else:
            organized_entry["history"] = ""

    # Get the words from chinese-characters
    for character in "".join(dict.fromkeys(organized_entry["traditional"])):

        driver.get("http://chinese-characters.org/cgi-bin/lookup.cgi?characterInput=" + quote(
            character) + "&submitButton1=Go%21")
        soup = BeautifulSoup(driver.page_source, 'html.parser')  # type: bs4.BeautifulSoup

        html = ""

        for i, table in enumerate(soup.find_all("table"), start=0):

            # The first table is stuff we don't care about
            if i < 4:
                continue

            for descendant in table.find_all(recursive=True):
                if "background" in descendant.attrs:
                    descendant.attrs.pop("background")

                # Remove all the random table images they have
                if "img" == descendant.name:
                    if "table" in descendant["src"] or "unavail" in descendant["src"] or "lg-feed" in descendant["src"]:
                        descendant.extract()

            for a in table.findAll('a'):
                if "href" in a.attrs:
                    a["href"] = urljoin("http://chinese-characters.org/", a.get('href'))

            for subtable in soup.find_all("table"):
                subtable.attrs["border"] = "1px solid black;"

            if i == 4:
                html = html + str(extract_html_images("http://chinese-characters.org/", table, character=character))
            elif i == 5:
                html = html + "<table border: \"1px solid black;\">" + str(table.find("tbody")) + "</table>"
                break
            else:
                break

        organized_entry["characters"].append(html + "<hr>")

    # Get words from hanzicraft
    url_string = "https://hanzicraft.com/character/" + quote("".join(dict.fromkeys(character_string)))  # type: str

    driver.get(url_string)  # type: str

    soup = BeautifulSoup(driver.page_source, 'html.parser').find(id="display")  # type: bs4.BeautifulSoup

    for favorite_button in soup.find_all('button', id="addfav"):
        favorite_button.decompose()

    for a in soup.findAll('a'):

        if "href" in a.attrs:
            # If the character reference is actually a word_to_process, send us to mdbg instead
            if "character" in a['href'] and len(a['href'].replace('/character/', "")) > 1:
                a['href'] = "https://www.mdbg.net/chinese/dictionary?page=worddict&wdrst=1&wdqb=" + \
                            a['href'].split('/')[2]
            else:
                # The links start is relative. We want them to be FQDNs so they reach out to Hanzicraft
                a['href'] = "https://hanzicraft.com" + a['href']

            # Remove target because it causes the links to fail.
            if "target" in a.attrs:
                a.attrs.pop("target")

    organized_entry["characters"].append(str(soup))

    for i, character in enumerate(organized_entry["characters"], start=0):
        organized_entry["characters"][i] = htmlmin.minify(character, remove_empty_space=True, remove_comments=True,
                                                          remove_optional_attribute_quotes=True)

    if hsk is not None:
        organized_entry.update({"hsk": hsk.text})
    else:
        organized_entry.update({"hsk": ""})

    if organized_entry["simplified"].strip() == "":
        organized_entry["simplified"] = HanziConv.toSimplified(organized_entry["traditional"])

    return organized_entry


def process_word(word_to_process, skip_choices=False, ask_if_match_not_found=True, skip_if_not_exact=True,
                 combine_exact_defs=False, preference_hsk=False):
    """
    Processes a word in the list of words

    :param str word_to_process: The word from the list
    :param skip_choices: Instead of skipping the choices it will just automatically select the closest
                         match
    :param bool ask_if_match_not_found: The program will first try to skip all choices, but if it can't find a match
                                         it will ask.
    :param bool skip_if_not_exact: Skip if an exact match isn't found.
    :param bool combine_exact_defs: Used if you want to just return a definition for everything with an exact match.
    :param bool preference_hsk: Used as a tiebreaker if there are multiple matches. Selects the one which is an HSK word
    :return: Returns a dictionary containing the word's entry
    :rtype: dict
    """

    logging.info("Requested word_to_process is: " + word_to_process)

    logging.debug("URL is: https://www.mdbg.net/chinese/dictionary?page=worddict&wdrst=1&wdqb=" + word_to_process)

    url_string = "https://www.mdbg.net/chinese/dictionary?page=worddict&wdrst=1&wdqb=" \
                 + quote(word_to_process)  # type: str

    html = urlopen(url_string).read().decode('utf-8')  # type: str

    soup = BeautifulSoup(html, 'html.parser')  # type: bs4.BeautifulSoup

    entry_list = []  # Used to return the entries we found.

    entries = []
    for entry in soup.find_all("tr", {"class": "row"}):
        entries.append(process_word_entry(entry))

    match_not_found = False
    definition = ""
    simplified_word = ""

    if skip_choices:
        # We use the simplified to avoid the one to many problem.
        simplified_word = HanziConv.toSimplified(word_to_process)

        selection = 0
        exact_match = False
        found_second = False

        logging.info(str(len(entries)) + " found from mdbg.net. Finding the closest match for " + word_to_process + ".")
        for index, entry in enumerate(entries):
            logging.debug("\n-------- Option " + str(index + 1) + "---------\n")
            logging.debug(str(entry["traditional"]) + "\n" + str(entry["pinyin"]) + "\n" + str(entry["defs"]))

        # Used in the event that we get to the end and no definitions were found. At this point we can use the useless
        # definitions.
        useless_defs = []

        for index, entry in enumerate(entries):
            if entry["traditional"] == simplified_word or entry["simplified"].strip() == simplified_word:
                logging.debug("Found exact match. Selecting " + entry["traditional"])

                useless_definition = False

                for definition in entry["defs"]:
                    if "surname" in str(definition).lower() or "variant of" in str(definition).lower() \
                            or str(definition).lower().startswith("see "):
                        useless_definition = True
                        useless_defs.append(entry)

                if not useless_definition:

                    # If this is already true then it means we found more than one exact match.
                    if not exact_match:
                        exact_match = True
                    else:
                        found_second = True

                    if combine_exact_defs and not ask_if_match_not_found:
                        entry_list.append(entry)

                    # This is only added because the first definition is typically preferable.
                    if not found_second:
                        selection = index + 1

        # Only used when no good definitions were found.
        if len(entry_list) == 0:
            entry_list = useless_defs
            exact_match = True

            if len(useless_defs) > 1:
                found_second = True
            else:
                selection = 1

        # This logic controls behavior associated with the preference_hsk list. When this is active it will prune
        # all results that don't have an HSK association. If none of the results have an HSK association it will do
        # nothing.
        if preference_hsk:

            an_entry_has_hsk = False

            # Make sure at least one entry has an HSK association
            for entry in entry_list:
                if entry["hsk"].strip() != "":
                    an_entry_has_hsk = True

            temp_list = []

            if an_entry_has_hsk:
                for entry in entry_list:
                    if entry["hsk"].strip() != "":
                        temp_list.append(entry)

                entry_list = temp_list
                entries = temp_list

                if len(entry_list) == 1:
                    exact_match = True
                    found_second = False
                    selection = 1

        if not exact_match:

            if skip_if_not_exact:

                return []
            else:
                selection = 1
                match_not_found = True
                if not ask_if_match_not_found:
                    logging.info("Did not find an exact match. Selecting first entry.")
                    logging.info("Selected " + str(entries[selection]["traditional"]))
                else:
                    logging.info("Could not find an exact match. Prompting user for input.")

        # We found multiple exact matches.
        if exact_match and found_second:
            selection = 1
            match_not_found = True
            logging.info("Found multiple possible matches to " + word_to_process + ", prompting for user input.")

        # We found an exact match and there was on second match so no manual intervention is required.
        if exact_match and not found_second:
            logging.info("Selected " + str(entries[selection - 1]["traditional"]))
            entries[selection - 1]["final_traditional"] = entries[selection - 1]["traditional"]

            # Re-initialize the list, wiping anything that might have been it (prevents duplicate values)
            entry_list = [entries[selection - 1]]

    if (ask_if_match_not_found and match_not_found) or not skip_choices:
        print("It looks like there are multiple definitions for " + word_to_process +
              " available. Which one would you like to use?")

        print("\n\n-------- Option 0 ---------\n")
        print("Type 0 to skip.")

        for index, entry in enumerate(entries):
            if entry["traditional"] == simplified_word or entry["simplified"].strip() == simplified_word and not \
                    ("surname" in str(definition).lower() or "variant of" in str(definition).lower()
                     or str(definition).lower().startswith("see ")):
                print("\n-------- Option " + str(index + 1) + "---------\n")
                if "hsk" in entry:
                    print(str(entry["traditional"]) + "\n" + str(entry["pinyin"]) + "\n" + str(entry["defs"]) +
                          "\r" + str(entry["hsk"]))
                else:
                    print(str(entry["traditional"]) + "\n" + str(entry["pinyin"]) + "\n" + str(entry["defs"]))

        print("\n\n")
        selection = -2  # type: int

        print("You may enter multiple selections. Enter them one after another. Type -1 to end.")
        while selection != -1 and selection != 0:
            selection = int(input("Enter your selection: "))

            if len(entries) >= selection > 0:
                if entries[selection - 1] not in entry_list:
                    entry_list.append(entries[selection - 1])

    if selection != 0:
        if len(entry_list) > 1:
            for index, entry in enumerate(entry_list):
                entry["final_traditional"] = "(" + str(index + 1) + ") " + entry["traditional"]
        else:
            entry_list[0]["final_traditional"] = entry_list[0]["traditional"]
        return entry_list
    else:
        return []


parser = ArgumentParser(description="Used to create Anki flash cards based on data from the website www.mdbg.net")
parser.add_argument('--file', metavar='FILE', dest="input_file_name", type=str, required=False,
                    help='The path to a newline delimited list of Chinese words or characters in Hanji The default'
                         'is new_words.txt', default="input.txt")
parser.add_argument('--words-output-file', metavar='WORDS-OUTPUT-FILE', dest="words_output_file_name", type=str,
                    required=False, default="word_list.txt",
                    help='By default this is word_list.txt. You may change it by providing this argument.')
parser.add_argument('--skip-choices', dest="skip_choices", required=False, action='store_true', default=False,
                    help='This option will tell the program to just select the closest match for the word_to_process.')
parser.add_argument('--ask-if-match-not-found', dest="ask_if_match_not_found", required=False, action='store_true',
                    default=False, help='Will only ask for input if an exact match between the pinyin and a '
                                        'character isn\'t found.')
parser.add_argument('--combine-exact', dest="combine_exact", required=False, action='store_true',
                    default=False, help='Will instruct the program to automatically store all definitions matched'
                                        ' in MDBG.')
parser.add_argument('--preference-hsk', dest="preference_hsk", required=False, action='store_true',
                    default=False,
                    help='Uses whether a word_to_process is from HSK vocab as a tiebreaker between multiple'
                         ' matching words. Discards non-HSK words.')
parser.add_argument('--resume', dest="resume", required=False, action='store_true', default=False,
                    help='After word_to_process creation a file called ~temp will be created. Using the same syntax you did'
                         ' to originally run the program, you can add --resume if for some reason the program'
                         ' failed during example creation.')
parser.add_argument('--log-level', metavar='LOG_LEVEL', dest="log_level", required=False, type=str, default="info",
                    choices=['debug', 'info', 'warning', 'error', 'critical'],
                    help='A path to Chinese Blockbuster in EPUB format. In my case, I bought all of them and merged'
                         ' them into one big book.')
parser.add_argument('--delimiter', metavar='DELIMITER', dest="delimiter", required=False, type=str, default="\\",
                    help='Allows you to optionally select the delimiter you use for the delimiter in your Anki'
                         'cards. By default it is ~ which should avoid colliding with anything.')
parser.add_argument('--anki-username', metavar='ANKI_USERNAME', dest="anki_username", required=False, type=str,
                    default="User 1", help='Your Anki username.')
parser.add_argument('--run-server', dest="run_server", required=False, action='store_true', default=False,
                    help='Instead of writing out flashcards, we will start a flask server where you can query '
                         'for characters. This will supersede all other arguments.')
parser.add_argument('--port', dest="port", required=False, type=int, default=5000,
                    help='Specify the port you want Flask to run on')
parser.add_argument('--thread-count', dest="thread_count", required=False, type=int, default=5,
                    help='Specify the number of worker threads with which you want to grab examples.')
parser.add_argument('--show-chrome', dest="show_chrome", required=False, action='store_true',
                    help='Will disable headless mode on Chromedriver and cause the browser to pop up')
parser.add_argument('--print-usage', dest="print_usage", required=False, action='store_true',
                    help='Show example usage.')
parser.add_argument('--show-usage', dest="print_usage", required=False, action='store_true',
                    help='Show example usage.')

args = parser.parse_args()  # type: argparse.Namespace

if not args.run_server and not args.input_file_name and not args.print_usage:
    parser.print_help()
    exit(0)

if args.print_usage:
    print(
        'python chinese_flashcard_maker.py --anki-username "User 1" --file input.txt --skip-choices --show-chrome --delimiter \  --combine-exact --preference-hsk')
    print('\nVisual Studio Code regex for excluding lines starting with asterisk: ^(?!\*).*\\n')
    print('\nMapping for "Chinese Words Updated" is:')
    print('Traditional\nSimplified\nPinyin\nMeaning\nTags\nCharacters')
    exit(0)

if args.ask_if_match_not_found:
    args.skip_choices = True

if 'Windows' in platform.system():
    image_path = path.join(getenv("APPDATA"), "Anki2", args.anki_username, "collection.media")
else:
    logging.error("Only works on Windows with Anki installed!")
    exit(0)

if args.log_level:
    if args.log_level == "debug":
        logging.basicConfig(level=logging.DEBUG)
    elif args.log_level == "info":
        logging.basicConfig(level=logging.INFO)
    elif args.log_level == "warning":
        logging.basicConfig(level=logging.WARNING)
    elif args.log_level == "error":
        logging.basicConfig(level=logging.ERROR)
    elif args.log_level == "critical":
        logging.basicConfig(level=logging.CRITICAL)
else:
    logging.basicConfig(level=logging.INFO)

if not args.delimiter:
    args.delimiter = "\\"
else:
    args.delimiter = args.delimiter.strip('\'').strip('\"')

driver = create_driver(headless=False)

if args.input_file_name and not args.resume:
    if Path(args.input_file_name).is_file():
        words = []
        with open(args.input_file_name, encoding="utf-8-sig") as input_file:
            for word in input_file.readlines():
                if word.strip() != "":
                    words.append(word)

        words = get_words(words, skip_choices=args.skip_choices,
                          ask_if_match_not_found=args.ask_if_match_not_found,
                          combine_exact_defs=args.combine_exact,
                          preference_hsk=args.preference_hsk)

        # Before creating examples, create a temp file with words data. This allows us to retrieve that data
        # in the event of a problem with the examples.
        with open('~temp', 'wb') as words_temp_file:
            pickle.dump(words, words_temp_file)

        output_combined(args.words_output_file_name, words, args.delimiter,
                        args.thread_count, args.show_chrome)
    else:
        print(args.input_file_name + " is not a file or doesn't exist!")
        exit(0)
elif args.resume:

    with open('~temp', 'rb') as words_temp_file:
        words = pickle.load(words_temp_file)

    output_combined(args.words_output_file_name, words, args.delimiter,
                    args.thread_count, args.show_chrome)
else:
    print("No input file name specified! You must provide a word_to_process list or run a server!")
    exit(0)

driver.close()
