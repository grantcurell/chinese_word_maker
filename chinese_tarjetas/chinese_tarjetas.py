from urllib.request import urlopen
from urllib.parse import quote
from bs4 import BeautifulSoup
import ebooklib
from ebooklib import epub
import traceback
import logging
import pprint
import os
import ntpath
import sys
import re
from datetime import datetime


def query_yes_no(question, default="yes"):
    """
    Ask a yes/no question via raw_input() and return the answer.

    :param question str A string that is presented to the user.
    :param default is the presumed answer if the user just hits <Enter>.
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


def output_words(words_output_file_name, word_list):
    """
    Outputs the new words to a file for import into Anki

    :param str words_output_file_name: The name of the file to which we want to write the new words
    :param list word_list: The list of words we want to write to file
    :return: Returns nothing
    """

    logging.info("Outputting words.")

    with open(words_output_file_name, 'w', encoding="utf-8-sig") as output_file:

        for word in word_list:

            # You need the <br/>s in anki for newlines. The strip makes sure there isn't one randomly trailing
            output_file.write(word["traditional"] + "," + word["simplified"] + "," + word["pinyin"] + "," +
                              "<br>".join(word["defs"]).replace(",", "") + "," + word["hsk"].replace(" ", "") + "\n")

            logging.info("Writing: " + word["traditional"] + "," + word["simplified"] + "," + word["pinyin"] + "," +
                         "<br>".join(word["defs"]) + "," + word["hsk"])


def output_characters(chars_output_file_name, char_images_folder, char_list):
    """
    Outputs the new characters to a file for import into Anki

    :param str chars_output_file_name: The name of the file to which we want to write the new characters
    :param str char_images_folder: The folder which will store the images associated with the character images
    :param list char_list: The list of characters we want to write to file
    :return: Returns nothing
    """

    logging.info("Outputting characters.")

    # Create target directory if don't exist
    if not os.path.exists(char_images_folder):
        os.mkdir(char_images_folder)
        logging.info("Directory " + char_images_folder + " Created ")

    with open(chars_output_file_name, 'w', encoding="utf-8-sig") as output_file:

        for character in char_list:

            # Write the image for the character out to disk. The module ntpath ensures this is portable to Linux
            # or Windows. The line directly below is necessary to ensure the filename is unique
            filename = str(int(datetime.now().timestamp())) + "-" + ntpath.basename(
                character["image"].file_name).replace("jpeg", "jpg")  # type: str
            with open(os.path.join(char_images_folder, filename), "wb") as img_file:
                img_file.write(character["image_content"])  # Output the image to disk

            if "simplified" not in character:
                character["simplified"] = ""
            if "defs" not in character:
                character["defs"] = ""
            if "mnemonics" not in character:
                character["mnemonics"] = ""
            if "story" not in character:
                character["story"] = ""
            if "examples" not in character:
                character["examples"] = ""
            if "additionalinfo" not in character:
                character["additionalinfo"] = ""
            if "simplifiedcomponents" not in character:
                character["simplifiedcomponents"] = ""
            if "traditionalcomponents" not in character:
                character["traditionalcomponents"] = ""

            character_cleaned = {}

            # Replace any newlines in the text with HTML line breaks
            for key, value in character.items():
                if key != "image":  # The image value has no replace capability so we have to skip it
                    character_cleaned[key] = value.replace("\n", "<br>")

            delimiter = '\\'

            # The only if conditions ensure that if a field is missing because it isn't part of a page that an error
            # isn't thrown.
            output_file.write(
                character_cleaned["traditional"] + delimiter +
                character_cleaned["simplified"] + delimiter +
                character_cleaned["defs"] + delimiter +
                character_cleaned["pinyin"] + delimiter +
                character_cleaned["soundword"] + delimiter +
                "<img src=\"" + filename + "\" />" + delimiter +
                character_cleaned["mnemonics"] + delimiter +
                character_cleaned["story"] + delimiter +
                character_cleaned["examples"] + delimiter +
                character_cleaned["additionalinfo"] + delimiter +
                character_cleaned["simplifiedcomponents"] + delimiter +
                character_cleaned["traditionalcomponents"] +
                "\n"
            )

            if logging.getLogger().level == logging.DEBUG:
                logging.debug("\n-------------------------------------------\n")
                logging.debug("Writing: " +
                              character_cleaned["simplified"] + delimiter +
                              character_cleaned["traditional"] + delimiter +
                              character_cleaned["defs"] + delimiter +
                              character_cleaned["pinyin"] + delimiter +
                              character_cleaned["soundword"] + delimiter +
                              "<img src=" + filename + "/>" + delimiter +
                              character_cleaned["mnemonics"] + delimiter +
                              character_cleaned["story"] + delimiter +
                              character_cleaned["examples"] + delimiter +
                              character_cleaned["additionalinfo"] + delimiter +
                              character_cleaned["simplifiedcomponents"] + delimiter +
                              character_cleaned["traditionalcomponents"] +
                              "\n"
                              )
                logging.debug("\n-------------------------------------------\n")
            else:
                logging.info("Writing the character: " + character["traditional"])


def get_words(input_file_name, ebook_path=None, skip_choices=False):
    """
    Reaches out to www.mdbg.net and grabs the data for each of the words on which you want data

    :param str input_file_name: The name of the file which contains the words we want to grab
    :param str ebook_path: Path to the ebook you want to read from
    :param bool skip_choices: Whether you want to skip selection of the different characters
    :return: Returns a list of the words you want added to Anki with their corresponding data
    :rtype: list
    """

    with open(input_file_name, encoding="utf-8-sig") as input_file:

        new_words = []  # type: list
        new_chars = []  # type: list
        pp = pprint.PrettyPrinter(indent=4)
        book = None

        if ebook_path:
            book = epub.read_epub(ebook_path)  # type: ebooklib.epub.EpubBook

        for word in input_file.readlines():

            try:
                word = word.strip()  # type: str

                # Handle words and characters differently. For individual characters, there is a special feature for
                # looking them up in the book Chinese Blockbuster and making flashcards. This will only be active if
                # the ebook_path is provided on the command line.
                if len(word) <= 2 and book is not None:
                    new_char = process_char_entry(book, word)
                    if new_char is not None:
                        new_chars.append(new_char)
                else:

                    logging.info("Requested word is: " + word)
                    logging.info("URL is: https://www.mdbg.net/chinese/dictionary?page=worddict&wdrst=1&wdqb=" + word)

                    url_string = "https://www.mdbg.net/chinese/dictionary?page=worddict&wdrst=1&wdqb=" \
                                 + quote(word)  # type: str

                    html = urlopen(url_string).read().decode('utf-8')  # type: str

                    soup = BeautifulSoup(html, 'html.parser')  # type: bs4.BeautifulSoup

                    results = soup.find_all("tr", {"class": "row"})  # type: bs4.element.ResultSet

                    entries = []  # type: list

                    for entry in results:

                        entries.append(process_word_entry(entry))

                    if len(entries) > 1 and skip_choices is not True:
                        print( "It looks like there are multiple definitions for this word available. "
                               "Which one would you like to use?")

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

                    elif len(entries) == 1:
                        new_words.append(entries[0])
            except KeyboardInterrupt:
                if not query_yes_no("You have pressed ctrl+C. Are you sure you want to exit?"):
                    exit(0)
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

    return new_words, new_chars


def process_char_entry(book, char):
    """
    Reads from an EPUB formatted version of the Chinese Blockbuster series

    :param EpubBook book: An open handle to the EPUB formatted book to use
    :param str char: The Character we want to process
    :return: Returns a tuple. One with a list of the characters you looked for and the other with words
    :rtype: dict - Returns a dictionary containing all the attributes of a character
    """

    logging.info("-------------------------------------")
    logging.info("Processing character: " + char)

    # Used to track whether we found the character
    found_char = False

    organized_entry = {}  # type: dict

    # continued = False  # type: bool

    for doc in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):

        content = doc.content.decode('utf-8')
        logging.debug(content)

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

                found_char = True
                logging.info("Found character " + char + " in the book!")

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
                    elif text == "STORY":
                        organized_entry["story"] = content
                    elif text == "EXAMPLES":
                        organized_entry["examples"] = content
                    elif text == "WANT A LITTLE MORE?":
                        organized_entry["additionalinfo"] = content

                # Search through the EPUB's images and find the one that is used on our page.
                image_name = ntpath.basename(soup.find("img").attrs['src'])  # Grab the image name

                organized_entry["image"] = book.get_item_with_href(top_level_dir + "/images/" + image_name)
                organized_entry["image_content"] = organized_entry["image"].content

                # Get the text for simplified components
                content = soup.select_one(
                    '.p_cat_heading__and__centre_alignment:contains("SIMPLIFIED COMPONENTS")')   # type: bs4.element.Tag

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
                        logging.info("No components found for character " + char + ".")

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

            # TODO Need to extend this to handle the situation that there are multiple duplicate characters
            """
            if continued:
                break
            else:
                continued = True
                continue
            """

    if not found_char:
        logging.warning("Did not find character " + char + " in the book!")
        return None

    logging.info("Found all of character " + char + "'s information")
    return organized_entry


def process_word_entry(entry):
    """
    Processes a single row from www.mbdg.net and returns it in a dictionary

    :param bs4.element.Tag entry: This is equivalent to one row in the results from www.mdbg.net
    :return: Returns a list of dictionary items containing each of the possible results
    :rtype: list of dicts
    """

    organized_entry = {}  # type: dict

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
