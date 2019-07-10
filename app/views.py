from flask import render_template, request
from app import app
from app.forms import CharacterForm
from os import path
from chinese_tarjetas.chinese_tarjetas import get_words,get_chars_html


@app.route('/_lookup_character')
def _lookup_character():
    # This is used to store multiple templates. This is only used when we find multiple character entries.
    webpage = ""

    input_text = request.args.get('character_to_lookup').strip()

    word, chars = get_words([input_text], app.config["ebook"], skip_choices=True)

    if chars is not None:

        return get_chars_html(chars)

    elif word is not None:

        webpage += render_template('word.html', word=word[0]) + "<hr>"
        webpage += get_chars_html(word[0]["characters"])

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
                            word[0]["traditional"] + " / " + word[0]["simplified"] + " / " + ",".join(word[0]["defs"]) +
                            "\n")
                    else:
                        word_file.write(word[0]["traditional"] + " / " + ",".join(word[0]["defs"]) + "\n")

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