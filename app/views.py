import logging
from flask import render_template, request
from app import app
from concurrent.futures.thread import ThreadPoolExecutor
from app.forms import CharacterForm, GenerateFlashcardsForm
from os import path, system
from hanziconv import HanziConv
from chinese_tarjetas.chinese_tarjetas import get_words, get_chars_html, get_examples_html, output_combined_online, \
    get_examples_scholarly_html


@app.route('/_lookup_character')
def _lookup_character():
    # This is used to store multiple templates. This is only used when we find multiple character entries.
    webpage = ""

    input_text = request.args.get('character_to_lookup').strip()
    if request.args.get('save_character') == "true":
        do_not_save_word_is_checked = True
    else:
        do_not_save_word_is_checked = False

    input_word = input_text.split(' ')[0]
    input_word_traditional = HanziConv.toTraditional(input_word)
    input_word_simplified = HanziConv.toSimplified(input_word)

    executor = ThreadPoolExecutor(max_workers=4)

    get_words_future = executor.submit(get_words, [input_word], app.config["ebook"],
                                       skip_choices=not (app.config['ONLINE_CHOICES']),
                                       ask_if_match_not_found=app.config['ONLINE_CHOICES'],
                                       combine_exact_defs=not (app.config['ONLINE_CHOICES']))

    if app.config['SCHOLARLY']:
        example_future = executor.submit(get_examples_scholarly_html, input_word_traditional)
    else:
        example_future = None

    if get_words_future.result() is not None:
        words = get_words_future.result()
    else:
        return 'Could not find that word.'

    if words is None:
        return 'No results were found for that word.'
    else:

        for word in words:

            if word is not None:

                if len(word["traditional"]) == 1 and len(input_word) > 1:
                    return 'No results were found for that word.'

                # Make sure that heuristics succeeded and we don't fail to convert for a one to many. This should happen
                # relatively infrequently so we should still get a net time save.
                if input_word_traditional != word["traditional"]:
                    logging.warning(
                        "We used some heuristics to convert from Simplified to Traditional Chinese. It looks like "
                        "on further evaluation they failed. This is not fatal and will be automatically fixed, but "
                        "we must make a new web request which will take a few seconds.")
                    logging.warning("The original search was for " + input_word + " which was converted to " +
                                    input_word_traditional + " but mdbg.net returned " + word["traditional"])
                    example_future = executor.submit(get_examples_scholarly_html, word["traditional"])

                logging.info("Performing character lookup for " + word["traditional"])

                char_future_server = executor.submit(get_chars_html, word["characters"], server_mode=True)
                char_future = executor.submit(get_chars_html, word["characters"],
                                              image_location=app.config['IMAGE_FOLDER'], server_mode=False)

                webpage += render_template("word.html", word=word) + "<hr>"
                webpage += char_future_server.result()

                logging.info("Waiting on example to return.")
                if app.config['SCHOLARLY']:
                    example = example_future.result()
                else:
                    example = get_examples_html(input_word_simplified, word["pinyin"], driver=app.config['DRIVER'])

                webpage += example

                if not do_not_save_word_is_checked:
                    output_combined_online(word, app.config['OUTPUT_FILE'], app.config['DELIMITER'],
                                           char_future.result(), example)

                if not path.exists('word_searches.txt'):
                    with open('word_searches.txt', 'w'):
                        pass

                with open("word_searches.txt", "r", encoding="utf-8-sig") as file:
                    word_file_contents = file.read()

                    if (not word["simplified"] and word["traditional"] not in word_file_contents) or \
                            (word["traditional"] not in word_file_contents and word["simplified"]
                             not in word_file_contents):
                        with open("word_searches.txt", "a+", encoding="utf-8-sig") as word_file:
                            word_file.write(word["traditional"] + "\n")

            webpage += '<hr style="height:3px;border:none;color:#333;background-color:#333;" />'

        return webpage


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
