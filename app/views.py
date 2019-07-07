from flask import render_template, request
from app import app
from app.forms import CharacterForm
from chinese_tarjetas.chinese_tarjetas import process_char_entry
from os import path
from ntpath import basename

@app.route('/_lookup_character')
def _lookup_character():

    character_results = process_char_entry(app.config["ebook"], request.args.get('character_to_lookup'))

    if character_results:
        image_path = "static/" + basename(character_results["image"].file_name)

        with open(path.join("app", "static", basename(character_results["image"].file_name)), "wb") as img_file:
            img_file.write(character_results["image_content"])  # Output the image to disk

        return render_template('character.html', title='Configure Inventory', image_path=image_path,
                               results=character_results)
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