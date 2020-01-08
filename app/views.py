import logging
from flask import render_template, request
from app import app
from concurrent.futures.thread import ThreadPoolExecutor
from app.forms import CharacterForm, GenerateFlashcardsForm
from os import path, system
from hanziconv import HanziConv
from chinese_tarjetas.chinese_tarjetas import get_words, get_chars_html, get_examples_html, output_combined_online, \
    output_characters, get_examples_scholarly_html


@app.route('/_lookup_character')
def _lookup_character():
    # This is used to store multiple templates. This is only used when we find multiple character entries.
    webpage = ""

    input_text = request.args.get('character_to_lookup').strip()
    if request.args.get('save_character') == "true":
        save_character_checked = True
    else:
        save_character_checked = False

    input_word = input_text.split(' ')[0]
    input_word_traditional = HanziConv.toTraditional(input_word)
    input_word_simplified = HanziConv.toSimplified(input_word)

    executor = ThreadPoolExecutor(max_workers=4)

    get_words_future = executor.submit(get_words, [input_word], app.config["ebook"], select_closest_match=True)
    if app.config['SCHOLARLY']:
        example_future = executor.submit(get_examples_scholarly_html, input_word_traditional)
    else:
        example = get_examples_html(input_word_simplified, driver=app.config['DRIVER'])

    if get_words_future.result() is not None:
        word, chars = get_words_future.result()
    else:
        return 'Uh oh. The server went and pooped itself. Investigate the logs for more info.'

    if word is None and chars is None:
        return 'No results were found for that word.'
    else:

        if chars is not None:

            if app.config['SCHOLARLY']:
                # Make sure that heuristics succeeded and we don't fail to convert for a one to many. This should happen
                # relatively infrequently so we should still get a net time save.
                if input_word_traditional != chars[0]["traditional"]:
                    logging.warning(
                        "We used some heuristics to convert from Simplified to Traditional Chinese. It looks like "
                        "on further evaluation they failed. This is not fatal and will be automatically fixed, but "
                        "we must make a new web request which will take a few seconds.")
                    logging.warning("The original search was for " + input_word + " which was converted to " +
                                    input_word_traditional + " but mdbg.net returned " + chars[0]["traditional"])
                    example_future = executor.submit(get_examples_scholarly_html, chars[0]["traditional"])

            if save_character_checked:
                if app.config['SCHOLARLY']:
                    example = example_future.result()
                output_characters("character_searches.txt", app.config['IMAGE_FOLDER'], [chars[0]],
                                  app.config['DELIMITER'], example, online=True)
            return get_chars_html(chars, server_mode=True, example=example)

        elif word is not None:

            if len(word[0]["traditional"]) == 1 and len(input_word) > 1:
                return 'No results were found for that word.'

            # Make sure that heuristics succeeded and we don't fail to convert for a one to many. This should happen
            # relatively infrequently so we should still get a net time save.
            if input_word_traditional != word[0]["traditional"]:
                logging.warning(
                    "We used some heuristics to convert from Simplified to Traditional Chinese. It looks like "
                    "on further evaluation they failed. This is not fatal and will be automatically fixed, but "
                    "we must make a new web request which will take a few seconds.")
                logging.warning("The original search was for " + input_word + " which was converted to " +
                                input_word_traditional + " but mdbg.net returned " + word[0]["traditional"])
                example_future = executor.submit(get_examples_scholarly_html, word[0]["traditional"])

            logging.info("Performing character lookup for " + word[0]["traditional"])

            char_future_server = executor.submit(get_chars_html, word[0]["characters"], server_mode=True)
            char_future = executor.submit(get_chars_html, word[0]["characters"],
                                          image_location=app.config['IMAGE_FOLDER'], server_mode=False)

            webpage += render_template("word.html", word=word[0]) + "<hr>"
            webpage += char_future_server.result()

            logging.info("Waiting on example to return.")
            if app.config['SCHOLARLY']:
                example = example_future.result()
            webpage += example

            if app.config["CREATE_COMBINED"]:
                output_combined_online(word[0], app.config['OUTPUT_FILE'], app.config['DELIMITER'],
                                       char_future.result(), example)
            else:
                if not path.exists('word_searches.txt'):
                    with open('word_searches.txt', 'w'):
                        pass

                with open("word_searches.txt", "r", encoding="utf-8-sig") as file:
                    word_file_contents = file.read()

                    if (not word[0]["simplified"] and word[0]["traditional"] not in word_file_contents) or \
                            (word[0]["traditional"] not in word_file_contents and word[0]["simplified"]
                             not in word_file_contents):

                        with open("word_searches.txt", "a+", encoding="utf-8-sig") as word_file:
                            word_file.write(word[0]["traditional"] + "\n")

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