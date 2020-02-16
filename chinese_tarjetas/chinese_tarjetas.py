from concurrent.futures.thread import ThreadPoolExecutor
from urllib.request import urlopen
from urllib.parse import quote
from bs4 import BeautifulSoup
from ntpath import basename
from os import path
from hanziconv import HanziConv
from googletrans import Translator
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import bs4
import concurrent.futures
import ebooklib
import traceback
import logging
import os
import ntpath
import sys
import re
import jinja2
import requests


def create_driver(headless=True, binary_location=None, implicit_wait_time=5):
    """
    Creates a Google-based web driver
    :param bool headless: Indicates whether to start the browser in headless mode or not
    :param str binary_location: The location of the chromedriver binary
    :param int implicit_wait_time: In case someone wants to modify it, they could change the time the browser will wait
                                   for results to return.
    :return: Returns a type of selenium.webdriver.chrome.webdriver.WebDriver for use in opening a chrome browser
    """
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--test-type")

    if headless:
        options.add_argument("--headless")

    if binary_location is not None:
        options.binary_location = binary_location

    driver = webdriver.Chrome(chrome_options=options)

    # This means the driver will wait up to 10 seconds to find a designated element.
    driver.implicitly_wait(implicit_wait_time)

    return driver


def create_image_name(organized_entry, image_location=""):
    """
    Used to do the path munging to create the image location entry

    :param dict organized_entry: The organized entry for which you want to create the image location string
    :param str image_location: The location you want to store the image. Nothing by default
    :return: Returns a string with the full path to the image if image_location is defined otherwise it only returns
             the base filename.
    :rtype: str
    """

    file_name = basename(organized_entry["image"].file_name.split('.')[0])
    file_extension = basename(organized_entry["image"].file_name.split('.')[1])

    if image_location:
        return path.join(image_location, file_name + "-" + organized_entry["pinyin_text"] + '.' + file_extension)
    else:
        return file_name + "-" + organized_entry["pinyin_text"] + '.' + file_extension


def get_examples_html(word, word_pinyin, driver=None, is_server=True, max_page=20, show_chrome=False):
    """
    Reach out to https://dict.naver.com/linedict/zhendict/dict.html#/cnen/example?query=%E4%B8%BA%E7%9D%80
    and get example sentences.

    :param str word: The word, in traditional character format, for which you want to retrieve examples
    :param str word_pinyin: The pinyin of the word - to make sure if there are multiple variants you get a matching
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

    logging.info("Requested word is: " + word)
    logging.debug("URL is: https://dict.naver.com/linedict/zhendict/dict.html#/cnen/example?query=" + word)

    url_string = "https://dict.naver.com/linedict/zhendict/dict.html#/cnen/example?query=" \
                 + quote(word)  # type: str

    if not is_server:
        driver = create_driver()

    driver.get(url_string)

    i = 0

    # This forces Chrome to wait to return until an element with class name autolink appears. Autolink in this case
    # Autolink is the name of the span class in the examples.
    while i < 2:
        try:
            driver.find_element_by_class_name("autolink")
            i = 2
        except NoSuchElementException:
            if i < 2:
                i = i + 1
                driver.get(url_string)
            else:
                return "No examples found for that word or finding an example took longer than 5 seconds."

    examples = []
    examples_found = False

    i = 0
    while not examples_found:

        html = driver.page_source

        soup = BeautifulSoup(html, 'html.parser')  # type: bs4.BeautifulSoup

        results = soup.find_all("div", {"class": "example_lst"})  # type: bs4.element.ResultSet

        if len(results) > 1:
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

        env = jinja2.Environment(loader=jinja2.PackageLoader('app', 'templates'))
        template = env.get_template("examples.html")

        if not examples_found:
            logging.debug("Not all examples found. Moving to next page.")
            try:
                # Example if I ever decide to change this to a click:
                # driver.find_element_by_css_selector('a.btn.next').click()  # Click to get the next page

                # Urls are normally formatted like:
                # https://dict.naver.com/linedict/zhendict/dict.html#/cnen/example?query=%E7%9D%80&page=1
                # If we want to get the next page we can just manually change the page via the below.
                split_url = driver.current_url.split("page=")
                if len(split_url) == 1:
                    driver.get(split_url[0] + "&page=2")
                else:
                    # split_url[1] contains the page number in the URL
                    page = int(split_url[1]) + 1
                    if page < max_page:
                        driver.get(split_url[0] + "page=" + str(page))
                    else:
                        logging.info("Checked " + str(page) + " pages looking for " + word + " (" + word_pinyin +
                                     ") and did not reach requested number of examples")
                        break
                driver.find_element_by_class_name("autolink")  # Wait for the results to appear
            except NoSuchElementException:
                if i > 0:
                    logging.info("No more example pages to check. Moving on.")
                else:
                    "No examples found for that word or finding an example took longer than 5 seconds."

    if template is None:
        return None
    else:
        return template.render(examples=examples)


def get_examples_scholarly_html(word):
    """
    Reach out to http://asbc.iis.sinica.edu.tw/ and get example sentences.

    :param str word: The word, in traditional character format, for which you want to retrieve examples
    :return Returns a template string with all of the examples formatted within it.
    :rtype str
    """
    logging.info("Creating an example for " + word)

    # We use the big5 encoding type because this website specifically uses traditional characters.
    params = {'inputword': word.encode(encoding="big5", errors="strict"), "selectAB": "AAB",
              "inputpos": "", "selectFeature": ""}
    try:
        r = requests.post("http://asbc.iis.sinica.edu.tw/process.asp", data=params)
    except ConnectionError:
        logging.error("It looks like connecting to asbc failed. There's a good chance you're getting throttled.")
        return "Connecting to asbc for an example failed. There's a good chance you're getting throttled."

    bs = BeautifulSoup(r.content.decode('big5', errors="replace"), features="lxml")

    # Remove the click elements that are usually on the sides of the results
    for tag in bs.select('u'):
        tag.decompose()

    # Get the results table specifically
    table = bs.find(lambda t_tag: t_tag.name == 'table' and t_tag.has_attr('width') and t_tag['width'] == "100%")

    if table is None:
        logging.info("No examples found for " + word)
        return "No examples found for " + word

    results = []
    i = 0
    for element in table.findAll(lambda tag: tag.name == 'tr'):

        # This is a magic number. I decided I didn't want to get more than 10 results because it's unlikely to be
        # useful.
        if i > 5:
            break

        element_text = ""
        for text in element.findAll(text=True, recursive=True):
            if text != '\n':
                element_text += text

        if element_text != "":
            logging.debug(element_text)

            # element_text is in Traditional Chinese, we want to get the simplified and display both
            results.append([element_text, HanziConv.toSimplified(element_text)])

            i = i + 1

    translator = Translator()
    i = 0

    translation = None

    # This grabs the first element of every result which in our case is just the original traditional Chinese text
    for text_to_translate in [item[0] for item in results]:
        try:
            translation = translator.translate(text_to_translate, src='zh-TW', dest='en')
        except:
            logging.critical("You got an exception while trying to translate something via Google. "
                             "You probably got banned.")
            exit(1)

        # I'm not sure why but the Python library's pronunciation value doesn't work. Howevere, if you go digging
        # through the translation object you can find there is actually a return for the pinyin. It's just always
        # the last item of the translation key in extra data. The last item is a list and the last element of the
        # list is always the pinyin pronunciation word separated.
        results[i].append(translation.extra_data["translation"][-1][-1])
        results[i].append(translation.text)
        i = i + 1

    env = jinja2.Environment(loader=jinja2.PackageLoader('app', 'templates'))
    template = env.get_template("examples_scholarly.html")

    return template.render(results=results)


def get_chars_html(characters, image_location=path.join("app", "static"), server_mode=False, example=None):
    """
    Grabs the HTML for each of the characters in a list of characters. This is used for generating the web pages.

    :param  list characters: A list of the characters you want to grab
    :param str image_location: Used to optionally control where the image is written to
    :param bool server_mode: Used to determine whether this was called by a running web server or not
    :param str example: The HTML for the example text
    :return: Returns a webpgae with all the character data rendered
    :rtype: str
    """

    webpage = ""

    image_path = ""

    for organized_entry in characters:

        if "image" in organized_entry:
            if image_location == path.join("app", "static"):
                image_path = create_image_name(organized_entry, "static")
            else:
                image_path = image_location

            with open(create_image_name(organized_entry, image_location), "wb") as img_file:
                img_file.write(organized_entry["image_content"])  # Output the image to disk

        env = jinja2.Environment(loader=jinja2.PackageLoader('app', 'templates'))
        if server_mode:
            template = env.get_template("character.html")
        else:
            template = env.get_template("character_no_style.html")

        if server_mode:
            if example is not None:
                organized_entry["examples"] += example
            webpage += template.render(image_path=image_path, results=organized_entry) + "<hr>"
        else:
            if "image" in organized_entry:
                webpage += template.render(image_path=create_image_name(organized_entry), results=organized_entry) + \
                           "<hr>"
            else:
                webpage += template.render(image_path=None, results=organized_entry) + "<hr>"

    # There are a huge number of BR tags and they aren't actually necessary.
    return webpage.replace("<br>", "")


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


def _get_word_line(word, delimiter):
    """
    Gets the string used for outputting words to Anki format

    :param dict word: The word you want to output
    :param str delimiter: The delimiter you want to use in the output
    :return: String used for outputting to an Anki flashcard for words
    :rtype: str
    """

    return word["final_traditional"] + delimiter + word["simplified"] + delimiter + word["pinyin"] + delimiter + \
           "<br>".join(word["defs"]).replace(delimiter, "") + delimiter + word["hsk"].replace(" ", "")


def output_combined(output_file_name, char_images_folder, word_list, delimiter, thread_count, show_chrome):
    """
    Allows you to output flashcards with both the word and the character embedded in them.

    :param str output_file_name: The name of the file to which we want to write the new flashcards
    :param str char_images_folder: The folder which will store the images associated with the character images
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
                                              show_chrome=show_chrome):
                              word for word in word_list}

            length = str(len(word_list))
            i = 1

            for future in concurrent.futures.as_completed(future_example):
                word_processed = future_example[future]
                logging.info("We have processed " + str(i) + " of " + length + " examples.")
                try:
                    if word_processed is not None:
                        examples[word_processed["traditional"]] = future.result()
                    else:
                        logging.info("No examples found for word: " + word_processed["final_traditional"])
                except Exception as exc:
                    logging.error('%r generated an exception: %s' % (word_processed["final_traditional"], exc))
                else:
                    logging.info('Finished processing word %s' % word_processed["final_traditional"])

                i = i + 1

        logging.info("Finished getting all examples.")

        logging.info("Writing words.")
        for word in word_list:

            output_file.write(_get_word_line(word, delimiter) + delimiter)

            line = get_chars_html(word["characters"], image_location=char_images_folder).replace('\n', "")

            output_file.write(line.replace(delimiter, ""))

            try:
                line = examples[word["traditional"]].replace('\n', "") + "\n"
            except KeyError:
                logging.debug("No examples found for word: " + word["final_traditional"])
            i = i + 1

            output_file.write(line.replace(delimiter, ""))


def output_combined_online(word, output_file_name, delimiter, char_line, example_line):
    with open(output_file_name, 'a+', encoding="utf-8-sig") as output_file:
        output_file.write(_get_word_line(word, delimiter) + delimiter)
        output_file.write(char_line.replace('\n', "").replace(delimiter, ""))
        output_file.write((example_line.replace('\n', "") + "\n").replace(delimiter, ""))


def get_words(words, ebook=None, skip_choices=False, ask_if_match_not_found=True, combine_exact_defs=False,
              preference_hsk=False):
    """
    Reaches out to www.mdbg.net and grabs the data for each of the words on which you want data or searches an
    instance of Chinese Blockbust eBook for characters.

    :param list words: The list of the words you want to add
    :param ebook ebook: An eBook file object
    :param bool skip_choices: Whether you want to skip selection of the different possible options. The closest match
                              will be selected instead.
    :param bool ask_if_match_not_found: The program will first try to skip all choices, but if it can't find a match
                                         it will ask.
    :param bool combine_exact_defs: Used if you want to just return a definition for everything with an exact match.
    :param bool preference_hsk: Used as a tiebreaker if there are multiple matches. Selects the one which is an HSK word
    :return: Returns two lists, one with the words found and the other with the characters found
    :rtype: list
    """

    new_words = []  # type: list

    if ebook:

        length = str(len(words))
        i = 1

        for word in words:

            logging.info("Processing word " + str(i) + " of " + length)
            i = i + 1

            try:
                word = word.strip()  # type: str

                for word_entry in process_word(word, skip_choices=skip_choices, ebook=ebook,
                                               ask_if_match_not_found=ask_if_match_not_found,
                                               combine_exact_defs=combine_exact_defs,
                                               preference_hsk=preference_hsk):
                    if word_entry:
                        new_words.append(word_entry)

            except KeyboardInterrupt:
                if not query_yes_no("You have pressed ctrl+C. Are you sure you want to exit?"):
                    exit(0)
            except AttributeError:
                logging.error("It looks like we've caught an attribute error. Maybe there's an invalid character "
                              "in the input?")
                return None
            # Because you could spend a lot of time working on this we want to avoid program termination at all costs
            # Because of this we catch all exceptions and provide the option to continue or not.
            except:
                traceback.print_exc()
                logging.error("Uh oh. We've run into a problem, but we're trying to stop the program from terminating "
                              "on you!")
                if not query_yes_no(
                        "We have caught an unknown exception but prevented the program from terminating. "
                        "Do you want to continue with the next word?"):
                    exit(1)

    if len(new_words) < 1:
        new_words = None

    return new_words


def _get_word_info(organized_entry, entry):
    """
    This is just a helper function so that I can reuse this code within this method. Notice it does not return
    anything. It is expected that a dictonary

    :param dictonary organized_entry: This is a dictionary we are passing by reference which will hold our
                                            character data
    :param entry: This is the same as entry from process_word_entry. This is one line of data from MDBG
    :return: Returns an organized entry with defs, simplified, and traditional
    """

    organized_entry. \
        update({"traditional": entry.find("td", {"class": "head"}).find("div", {"class": "hanzi"}).text})

    # I didn't investigate why, but for some reason the site was adding u200b so I just manually stripped that
    # whitespace out.
    organized_entry. \
        update({"pinyin": str(entry.find("div", {"class": "pinyin"}).text).strip().replace(u'\u200b', "")})

    # The entries come separated by /'s which is why we have the split here
    # The map function here just gets rid of the extra whitespace on each word before assignment
    organized_entry. \
        update({"defs": list(map(str.strip, str(entry.find("div", {"class": "defs"}).text).split('/')))})

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


def process_word_entry(entry, skip_choices, ask_if_match_not_found, skip_if_not_exact, combine_exact_defs, ebook=None,
                       preference_hsk=False):
    """
    Processes a single row from www.mbdg.net and returns it in a dictionary

    :param bs4.element.Tag entry: This is equivalent to one row in the results from www.mdbg.net
    :param skip_choices: Instead of skipping the choices it will just automatically select the closest match
    :param bool ask_if_match_not_found: See docstrings for process word
    :param bool skip_if_not_exact: See docstrings for process word
    :param bool combine_exact_defs: See docstrings for process word
    :param ebook ebook: An eBook file object
    :param bool preference_hsk: Used as a tiebreaker if there are multiple matches. Selects the one which is an HSK word
    :return: Returns a list of dictionary items containing each of the possible results
    :rtype: list of dicts
    """

    organized_entry = {}  # type: dict

    organized_entry = _get_word_info(organized_entry, entry)

    if ebook:
        organized_entry["characters"] = []  # type: list

        # Loop over every character which is part of the word
        for character in organized_entry["traditional"]:

            logging.debug("Searching for " + organized_entry["traditional"] + "'s character components.")

            individual_characters = process_char_entry(ebook, character)

            # This is to cover words like 這個. The problem is that when the word comes across it is a neutral tone
            # so an exact match is never found. Instead we just default to using the first match in these cases.
            exact_match_found = False

            # Remember some characters might look the same, but have multiple meanings depending on pronunciation. That
            # means we need to loop over all the possible characters with that appearance and find the one whose pinyin
            # matches that of our word
            if individual_characters:
                for individual_character in individual_characters:
                    if individual_character["pinyin_text"] in organized_entry["pinyin"]:
                        logging.debug("Found a match to a character with that exact pronunciation!")
                        organized_entry["characters"].append(individual_character)
                        exact_match_found = True

            if not exact_match_found:

                # Reach out to MDBG, get data on the unknown character
                unknown_character_entry_lookup = get_mdbg(character)

                # Make sure there was a return and if there was perform the lookup
                if unknown_character_entry_lookup:

                    entry_list = []

                    for entry in unknown_character_entry_lookup:
                        entry_list.append(_get_word_info({}, entry))

                    unknown_character_result = process_word(character,
                                                            skip_choices=skip_choices,
                                                            ask_if_match_not_found=ask_if_match_not_found,
                                                            skip_if_not_exact=skip_if_not_exact,
                                                            combine_exact_defs=combine_exact_defs,
                                                            called_from_process_word_entry=True,
                                                            entries=entry_list,
                                                            preference_hsk=preference_hsk)

                    # This converts unknown_character_results from a list of one element to a regular dictionary item.
                    # This happens because process_word returns a list
                    unknown_character_result = unknown_character_result[0]

                    unknown_character_result["defs"] = ', '.join(unknown_character_result["defs"])
                    unknown_character_result["defs_text"] = unknown_character_result["defs"]
                    unknown_character_result["pinyin_text"] = unknown_character_result["pinyin"]
                    unknown_character_result["additionalinfo"] = unknown_character_result["hsk"]

                    if unknown_character_result["pinyin"] != organized_entry["pinyin"]:
                        unknown_character_result["additionalinfo"] += " / " + unknown_character_result["pinyin"] + \
                                                                      " is likely an alternate pronunciation of part" \
                                                                      " of " + organized_entry["pinyin"]

                    organized_entry["characters"].append(unknown_character_result)
                elif individual_characters:
                    organized_entry["characters"].append(individual_characters[0])

    if organized_entry["simplified"].strip() == "":
        organized_entry["simplified"] = HanziConv.toSimplified(organized_entry["traditional"])

    return organized_entry


def get_mdbg(word):
    """
    Used for looking up a word in the MDBG database

    :param str word: The word to lookup
    :return: Return a type of bs4.element.ResultSet with the results of your lookup.
    """

    logging.debug("URL is: https://www.mdbg.net/chinese/dictionary?page=worddict&wdrst=1&wdqb=" + word)

    url_string = "https://www.mdbg.net/chinese/dictionary?page=worddict&wdrst=1&wdqb=" \
                 + quote(word)  # type: str

    html = urlopen(url_string).read().decode('utf-8')  # type: str

    soup = BeautifulSoup(html, 'html.parser')  # type: bs4.BeautifulSoup

    return soup.find_all("tr", {"class": "row"})  # type: bs4.element.ResultSet


def process_word(word, skip_choices=False, ebook=None, ask_if_match_not_found=True, skip_if_not_exact=True,
                 combine_exact_defs=False, called_from_process_word_entry=False, entries=None, preference_hsk=False):
    """
    Processes a word in the list of words

    :param str word: The word from the list
    :param skip_choices: Instead of skipping the choices it will just automatically select the closest
                         match
    :param ebook ebook: An eBook file object
    :param bool ask_if_match_not_found: The program will first try to skip all choices, but if it can't find a match
                                         it will ask.
    :param bool skip_if_not_exact: Skip if an exact match isn't found.
    :param bool combine_exact_defs: Used if you want to just return a definition for everything with an exact match.
    :param bool called_from_process_word_entry: Used when there is a recursive call from process_word_entry. This
                                                happens when there was a character that had no match in the ebook. In
                                                this case we want to get data from the web, but we need to use the
                                                selection logic of this function to get that data. When this is true,
                                                entries will come from process_word_entry instead of being a blank list.
                                                process_word_entry fills out the fields simplified, tradtional, and
                                                defs. We need that data here because we are going to skip the call from
                                                process_word_entry. This variable is how we pass it.
    :param list entries: A list of character entries for each character in the word.
    :param bool preference_hsk: Used as a tiebreaker if there are multiple matches. Selects the one which is an HSK word
    :return: Returns a dictionary containing the word's entry
    :rtype: dict
    """

    if entries is None:
        entries = []

    logging_level = None

    # Suppress output unless we are in debug mode because this is super confusing with the recursive calls.
    if called_from_process_word_entry:
        if logging.DEBUG != logging.root.level:
            logging_level = logging.root.level
            logging.basicConfig(level=logging.WARNING)

    logging.info("Requested word is: " + word)

    results = get_mdbg(word)

    entry_list = []  # Used to return the entries we found.

    if not called_from_process_word_entry:
        entries = []
        for entry in results:
            entries.append(process_word_entry(entry, skip_choices, ask_if_match_not_found, skip_if_not_exact,
                                              combine_exact_defs, ebook, preference_hsk))

    match_not_found = False
    definition = ""
    simplified_word = ""

    if skip_choices:
        # We use the simplified to avoid the one to many problem.
        simplified_word = HanziConv.toSimplified(word)

        selection = 0
        exact_match = False
        found_second = False

        logging.info(str(len(entries)) + " found from mdbg.net. Finding the closest match for " + word + ".")
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

                # Return the logging level to normal
                if called_from_process_word_entry:
                    logging.basicConfig(level=logging_level)

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
            logging.info("Found multiple possible matches to " + word + ", prompting for user input.")

        # We found an exact match and there was on second match so no manual intervention is required.
        if exact_match and not found_second:
            logging.info("Selected " + str(entries[selection - 1]["traditional"]))
            entries[selection - 1]["final_traditional"] = entries[selection - 1]["traditional"]

            # Re-initialize the list, wiping anything that might have been it (prevents duplicate values)
            entry_list = [entries[selection - 1]]

    if (ask_if_match_not_found and match_not_found) or not skip_choices:
        print("It looks like there are multiple definitions for " + word +
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

    # Return the logging level to normal
    if called_from_process_word_entry:
        logging.basicConfig(level=logging_level)

    if selection != 0:
        if len(entry_list) > 1:
            for index, entry in enumerate(entry_list):
                entry["final_traditional"] = "(" + str(index + 1) + ") " + entry["traditional"]
        else:
            entry_list[0]["final_traditional"] = entry_list[0]["traditional"]
        return entry_list
    else:
        return []


def resolve_href(href, book):
    """
    Resolves an HREF from the text

    :param href: The HREF you want to resolve
    :param book: A pointer to an ebook
    :return: Returns the HTML for the resolved HREF
    """

    potential_hrefs = []

    href = href.split("#")

    url = href[0]
    anchor = href[1]

    for item in book.get_items():
        if url in item.get_name():
            potential_hrefs.append(item)

    for href in potential_hrefs:

        href_content = BeautifulSoup(href.content, 'lxml')

        results = href_content.find(id=anchor)

        if results:
            for element in results.next_elements:
                if element.name == "td":
                    for child in element.contents[0].children:
                        if child.string:
                            child.string = child.string.replace('/', '').replace("\n", "").strip()
                    return element.contents[0]
            return None


def process_char_entry(book, char):
    """
    Reads from an EPUB formatted version of the Chinese Blockbuster series

    :param EpubBook book: An open handle to the EPUB formatted book to use
    :param str char: The Character we want to process
    :return: Returns a list of organized entries dictionaries. Most of the time there will be only one, but sometimes
             the book has multiple entries for a single character.
    :rtype: list of dict - Returns a list of dictionaries containing all the attributes of a character
    """

    logging.debug("-------------------------------------")
    logging.debug("Processing character: " + char)

    # Used to track whether we found the character
    found_char = False

    # In some cases there are multiple variants of a single word. This variable is used to control searching for those.
    continued = False  # type: bool

    # This is a list of organized entries. It is only used if the program finds more than one instance of a symbol match
    organized_entries_list = []

    loop_counter = 0

    for doc in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):

        loop_counter += 1

        content = doc.content.decode('utf-8')

        # You can uncomment this if you want to see a dump of each page's XML
        # logging.debug(content)

        organized_entry = {}  # type: dict

        # This may seem redundant with the following conditional statement, but I figured it would be faster to do
        # a quick character search in place of parsing everything into Beautiful Soup for every run of the loop
        if char in content:
            soup = BeautifulSoup(content, 'lxml')  # type: bs4.BeautifulSoup
            character_header = soup.select_one(
                '.p_chinese_char:contains("' + char + '")')  # type: bs4.element.Tag

            # The ID of the image is stored as the top level directory name inside the document. This next portion
            # grabs that number in an OS safe way. We will need this for both images and uniquely identifying the
            # calibre classes.
            top_level_dir = doc.file_name

            # Get the top level directory from the file path
            while os.path.split(top_level_dir)[0] != "":
                top_level_dir = os.path.split(top_level_dir)[0]

            # Calibre uses a different style sheet for each combined book. Since in my case I combined several
            # volumes together they each have different style sheets. This is expressed in different calibreXXX
            # classes. The solution is to prepend the identifier to the class and update the style sheet.
            for calibre_element in soup.find_all(class_=re.compile("^calibre[0-9]{1,3}")):
                calibre_element.attrs["class"][0] = "id_" + top_level_dir + "_" + calibre_element.attrs["class"][0]

            if character_header is not None:

                # If this results to true, it means that we found the character once, are continuing the loop, but
                # now have found it a second time. This means that there were two pages in the book with the same
                # character.
                if continued:
                    continued = False

                # Remove all the HREFs which will clutter the card.
                for atag in soup.findAll("a"):
                    # if "href" in atag.attrs:
                    #     reference = resolve_href(atag.attrs["href"], book)
                    #     if reference:
                    #         atag.replace_with(reference)
                    #     else:
                    atag.extract()

                logging.debug("Found character " + char + " in the book!")

                character_header = character_header.text.split('[')

                # Get the character from the text
                if len(character_header) == 2:
                    organized_entry["simplified"] = "/" + character_header[0]
                    organized_entry["traditional"] = character_header[1].strip("]")
                elif len(character_header) == 1:
                    organized_entry["traditional"] = character_header[0]
                elif len(character_header) > 2:
                    logging.warning("Anomalous behavior detected. This array should never have more than two "
                                    "characters. This is a non-fatal error, but it is strange.")
                    if not query_yes_no("Anomalous behavior detected. Do you want to continue?"):
                        exit(0)
                    for line in traceback.format_stack():
                        logging.debug(line.strip())

                # Search through the EPUB's images and find the one that is used on our page.
                image_name = ntpath.basename(soup.find("img").attrs['src'])  # Grab the image name

                organized_entry["image"] = book.get_item_with_href(top_level_dir + "/images/" + image_name)
                organized_entry["image_content"] = organized_entry["image"].content

                # Now that we have saved out the image data, remove all remaining image links in the page.
                for image in soup.findAll("img"):
                    image.extract()

                # Get the rest of the data
                for heading in soup.findAll("p", {"class": "p_cat_heading"}):

                    content = ""  # type: str
                    content_text = ""  # type: str

                    for temp_heading in heading.find_next_siblings():
                        # The below stops as soon as we reach the next instance of p_cat_heading or we reach an element
                        # with an image as a child which we also don't want to capture
                        if "p_cat_heading" in temp_heading.attrs["class"][0] \
                                or "img" in str(list(temp_heading.descendants)):
                            break
                        else:
                            logging.debug(str(temp_heading))
                            content += str(temp_heading)
                            content_text = temp_heading.text

                    text = heading.text.strip()  # type: str

                    if text == "DEFINITION":
                        organized_entry["defs"] = content
                        organized_entry["defs_text"] = content_text.replace('\n', '   ')
                    elif text == "PRONUNCIATION":
                        organized_entry["pinyin"] = content
                        organized_entry["pinyin_text"] = content_text.replace('\n', '   ')
                    elif text == "MNEMONICS":
                        organized_entry["mnemonics"] = content
                    elif text == "SOUND WORD":
                        organized_entry["soundword"] = content
                        organized_entry["soundword_text"] = content_text.replace('\n', '   ')
                    elif text == "STORY":
                        organized_entry["story"] = content
                    elif text == "EXAMPLES":
                        organized_entry["examples"] = content
                    elif text == "WANT A LITTLE MORE?":
                        organized_entry["additionalinfo"] = content

                # This means we already found the character previously, but have found another instance. In this case
                # we note this in the dictionary by adding the key has_duplicates.
                if found_char:
                    organized_entries_list[-1]["has_duplicates"] = True
                    organized_entry["has_duplicates"] = True

                # Get the text for simplified components
                content = soup.select_one(
                    '.p_cat_heading__and__centre_alignment:contains("SIMPLIFIED COMPONENTS")')  # type: bs4.element.Tag

                if content is not None:
                    organized_entry["simplifiedcomponents"] = str(content.find_next())

                # Get the headings for traditional components
                content = soup.select_one(
                    '.p_cat_heading__and__centre_alignment:contains("TRADITIONAL COMPONENTS")')  # type: bs4.element.Tag

                if content is not None:
                    organized_entry["traditionalcomponents"] = str(content.find_next())

                # If both of the above are none that means that there are no particular components
                if "traditionalcomponents" not in organized_entry and "simplifiedcomponents" not in organized_entry:
                    content = soup.select_one(
                        '.p_cat_heading__and__centre_alignment:contains("COMPONENTS")')  # type: bs4.element.Tag

                    if content is not None:
                        organized_entry["traditionalcomponents"] = str(content.find_next())
                    else:
                        logging.debug("No components found for character " + char + ".")

                # I noticed some elements didn't strictly adhere to having header information. This is an exception
                # I wrote specifically for definitions.
                if "defs" not in organized_entry:
                    paragraghs = soup.find_all('p')

                    for p in paragraghs:
                        if p.find(text="DEFINITION"):

                            organized_entry["defs"] = ""
                            organized_entry["defs_text"] = ""

                            for temp_heading in p.find_next_siblings():
                                # The below stops as soon as we reach the next instance of p_cat_heading or we reach an
                                # element with an image as a child which we also don't want to capture
                                if "p_cat_heading" in temp_heading.attrs["class"][0] \
                                        or "img" in str(list(temp_heading.descendants)):
                                    break
                                else:
                                    logging.debug(str(temp_heading))
                                    organized_entry["defs"] += str(temp_heading)
                                    organized_entry["defs_text"] += temp_heading.text.replace('\n', '   ') + " "

                            break

                    if "defs" not in organized_entry:
                        logging.warning("We were unable to find a definition for this word. That's pretty weird.")

                logging.debug("MATCH FOUND")

                found_char = True

                if continued:
                    break
                else:
                    continued = True
                    organized_entries_list.append(organized_entry)
                    continue

        # This means that the loop ran again because we found a duplicate character, but this time around the page
        # didn't have a duplicate so we can break.
        elif continued:
            break

    logging.debug("Took " + str(loop_counter) + " loops to find the character.")

    if not found_char:
        logging.warning("Did not find character " + char + " in the book!")
        return None

    logging.debug("Found all of character " + char + "'s information")
    return organized_entries_list
