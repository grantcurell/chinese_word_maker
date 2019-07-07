from flask import render_template, request
from app import app
from app.forms import CharacterForm
from chinese_tarjetas.chinese_tarjetas import process_char_entry
from os import path
from ntpath import basename

@app.route('/_lookup_character')
def _lookup_character():

    # This is used to store multiple templates. This is only used when we find multiple character entries.
    webpage = ""

    character = request.args.get('character_to_lookup').strip()

    character_results = process_char_entry(app.config["ebook"], character)

    # Used to print out multiple characters in the event there are duplicates
    has_duplicates = False

    if character_results:

        for organized_entry in character_results:
            image_path = "static/" + basename(organized_entry["image"].file_name)

            with open(path.join("app", "static", basename(organized_entry["image"].file_name)), "wb") as img_file:
                img_file.write(organized_entry["image_content"])  # Output the image to disk

            # TODO: The addition of the definition here is just acting as a poor man's recent searches. I should include
            # TODO: this in the website.
            if character not in open("character_searches.txt", "r", encoding="utf-8-sig").read() or has_duplicates:
                with open("character_searches.txt", "a+", encoding="utf-8-sig") as character_searches:
                    if "has_duplicates" in organized_entry:
                        has_duplicates = True
                    character_searches.write(
                        character + " \\ " + organized_entry["soundword_text"] + " \\ " +
                        organized_entry["pinyin_text"] + " \\ " + organized_entry["defs_text"] + "\n")

            webpage += render_template('character.html', title='Configure Inventory', image_path=image_path,
                                       results=organized_entry) + "<hr>" \
                                                                  "" \

        return webpage

    else:
        return 'We could not find that character in the book!'


@app.route('/', methods=['GET', 'POST'])
@app.route('/index.html', methods=['GET', 'POST'])
def index():
    form = CharacterForm()
    return render_template('index.html', title='Configure Inventory', form=form)


@app.route('/help')
def help():
    character_form = CharacterForm()
    return render_template("help.html", form=character_form)