from flask import render_template, request
from app import app
from app.forms import CharacterForm
from chinese_tarjetas.chinese_tarjetas import get_words
from os import path
from ntpath import basename


def _get_chars_html(characters):
    """
    Grabs the HTML for each of the characters in a list of characters

    :param characters: A list ofg the characters you want to grab
    :return: Returns a webpgae with all the character data rendered
    :rtype: str
    """

    webpage = ""

    # Used to print out multiple characters in the event there are duplicates
    has_duplicates = False

    for organized_entry in characters:

        if "image" in organized_entry:
            image_path = "static/" + basename(organized_entry["image"].file_name)

            with open(path.join("app", "static", basename(organized_entry["image"].file_name)), "wb") as img_file:
                img_file.write(organized_entry["image_content"])  # Output the image to disk

        if not path.exists('character_searches.txt'):
            with open('character_searches.txt', 'w'): pass

        with open("character_searches.txt", "r", encoding="utf-8-sig") as file:
            characters_file_contents = file.read()

            print(characters_file_contents)

            if (organized_entry["traditional"] not in characters_file_contents and
                    ("simplified" in organized_entry and organized_entry["simplified"] not in characters_file_contents))\
                    or ("simplified" not in organized_entry and organized_entry["traditional"] not in characters_file_contents)\
                    or has_duplicates:

                with open("character_searches.txt", "a+", encoding="utf-8-sig") as character_searches:
                    if "has_duplicates" in organized_entry:
                        has_duplicates = True

                    if "simplified" in organized_entry:
                        character_searches.write(
                            organized_entry["traditional"] + "/" + organized_entry["simplified"] + " \\ " +
                            organized_entry["pinyin_text"] + " \\ " + organized_entry["soundword_text"] +
                            " \\ " + organized_entry["defs_text"] + "\n")
                    else:
                        character_searches.write(
                            organized_entry["traditional"] + " \\ " + organized_entry["pinyin_text"] + " \\ " +
                            organized_entry["soundword_text"] + " \\ " + organized_entry["defs_text"] + "\n")

            webpage += render_template('character.html', image_path=image_path, results=organized_entry) + "<hr>"

    return webpage


@app.route('/_lookup_character')
def _lookup_character():
    # This is used to store multiple templates. This is only used when we find multiple character entries.
    webpage = ""

    input_text = request.args.get('character_to_lookup').strip()

    word, chars = get_words([input_text], app.config["ebook"], skip_choices=True)

    if chars is not None:

        return _get_chars_html(chars)

    elif word is not None:

        webpage += render_template('word.html', word=word[0]) + "<hr>"
        webpage += _get_chars_html(word[0]["characters"])

        if not path.exists('word_searches.txt'):
            with open('word_searches.txt', 'w'): pass

        with open("word_searches.txt", "r", encoding="utf-8-sig") as file:
            word_file_contents = file.read()

            if word[0]["traditional"] not in word_file_contents and (
                    "simplified" in word[0] and word[0]["simplified"] not in word_file_contents) or \
                    ("simplified" not in word[0] and word[0]["traditional"] not in word_file_contents):

                with open("word_searches.txt", "a+", encoding="utf-8-sig") as word_file:
                    if "simplified" in word[0]:
                        word_file.write(
                            word[0]["traditional"] + " / " + word[0]["simplified"] + " / " + ",".join(word[0]["defs"]))
                    else:
                        word_file.write(word[0]["traditional"] + " / " + ",".join(word[0]["defs"]))

        return webpage

    else:
        return 'We could not find that character in the book!'


@app.route('/', methods=['GET', 'POST'])
@app.route('/character', methods=['GET', 'POST'])
@app.route('/index.html', methods=['GET', 'POST'])
def index():
    form = CharacterForm()
    return render_template('index.html', title='Configure Inventory', form=form)


@app.route('/help')
def help():
    character_form = CharacterForm()
    return render_template("help.html", form=character_form)