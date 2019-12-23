from flask import render_template, request
from app import app
from app.forms import CharacterForm, GenerateFlashcardsForm
from os import path, system
from chinese_tarjetas.chinese_tarjetas import get_words, get_chars_html, get_examples_html


@app.route('/_lookup_character')
def _lookup_character():
    # This is used to store multiple templates. This is only used when we find multiple character entries.
    webpage = ""

    input_text = request.args.get('character_to_lookup').strip()
    if request.args.get('save_character') == "true":
        save_character_checked = True
    else:
        save_character_checked = False

    word, chars = get_words([input_text], app.config["ebook"], select_first=True)

    if chars is not None:

        return get_chars_html(chars, write_character=save_character_checked, server_mode=True)

    elif word is not None:

        webpage += render_template('word.html', word=word[0]) + "<hr>"
        webpage += get_chars_html(word[0]["characters"], write_character=save_character_checked, server_mode=True)
        webpage += get_examples_html(word[0]["traditional"])

        if not path.exists('word_searches.txt'):
            with open('word_searches.txt', 'w'):
                pass

        with open("word_searches.txt", "r", encoding="utf-8-sig") as file:
            word_file_contents = file.read()

            if (not word[0]["simplified"] and word[0]["traditional"] not in word_file_contents) or \
                    (word[0]["traditional"] not in word_file_contents and word[0]["simplified"]
                     not in word_file_contents):

                with open("word_searches.txt", "a+", encoding="utf-8-sig") as word_file:
                    if "simplified" in word[0]:
                        word_file.write(
                            word[0]["traditional"] + " / " + word[0]["simplified"] + " / " + word[0]["pinyin"] + " / "
                            + ",".join(word[0]["defs"]) + "\n")
                    else:
                        word_file.write(word[0]["traditional"] + " / " + ",".join(word[0]["defs"]) + "\n")

        return webpage

    else:
        return 'We could not find that character in the book!'


@app.route('/_generate')
def _generate():
    type = request.args.get('type').strip()

    if type == "characters":
        system('make character')

    return "True"


@app.route('/generate_flashcards')
def generate_flashcards():
    form = GenerateFlashcardsForm()
    return render_template('generate_flashcards.html', title='Generate Flashcards', form=form)


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