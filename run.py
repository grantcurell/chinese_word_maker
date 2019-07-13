__author__ = "Grant Curell"
__copyright__ = "Do what you want with it"

__license__ = "GPLv3"
__version__ = "1.3.0"
__maintainer__ = "Grant Curell"

from ebooklib import epub
from chinese_tarjetas.chinese_tarjetas import *
from argparse import ArgumentParser
from pathlib import Path
from app import app


def main():

    parser = ArgumentParser(description="Used to create Anki flash cards based on data from the website www.mdbg.net")
    parser.add_argument('--file', metavar='FILE', dest="input_file_name", type=str, required=False,
                        help='The path to a newline delimited list of Chinese words or characters in Hanji The default'
                             'is new_words.txt')
    parser.add_argument('--words-output-file', metavar='WORDS-OUTPUT-FILE', dest="words_output_file_name", type=str,
                        required=False, default="word_list.txt",
                        help='By default this is word_list.txt. You may change it by providing this argument.')
    parser.add_argument('--chars-output-file', metavar='CHARS-OUTPUT-FILE', dest="chars_output_file_name", type=str,
                        required=False, default="chars_list.txt",
                        help='By default this is chars_list.txt. You may change it by providing this argument.')
    parser.add_argument('--chars-image-folder', metavar='CHARS-IMAGE-FOLDER', dest="chars_image_folder", type=str,
                        required=False, default="char_images",
                        help='By default creates a folder called char_images in the current directory to store the '
                             'images associated with character images.')
    parser.add_argument('--skip-choices', dest="skip_choices", required=False, action='store_true', default=False,
                        help='This option will skip all choices and ignore the words for which a choice would have '
                             'been made.')
    parser.add_argument('--ebook-path', metavar='EBOOK_PATH', dest="ebook_path", required=False, type=str, default=None,
                        help='A path to Chinese Blockbuster in EPUB format. In my case, I bought all of them and merged'
                             ' them into one big book.')
    parser.add_argument('--log-level', metavar='LOG_LEVEL', dest="log_level", required=False, type=str, default="info",
                        choices=['debug', 'info', 'warning', 'error', 'critical'],
                        help='A path to Chinese Blockbuster in EPUB format. In my case, I bought all of them and merged'
                             ' them into one big book.')
    parser.add_argument('--delimiter', metavar='DELIMITER', dest="delimiter", required=False, type=str, default="~",
                        help='Allows you to optionally select the delimiter you use for the delimiter in your Anki'
                             'cards. By default it is ~ which should avoid colliding with anything.')
    parser.add_argument('--use-media-folder', dest="use_media_folder", required=False, action='store_true',
                        help='If this option is passed the program will try to write to Anki\'s media folder directly.'
                             ' If you pass this argument, you must also pass your Anki username.')
    parser.add_argument('--anki-username', metavar='ANKI_USERNAME', dest="anki_username", required=False, type=str,
                        help='Your Anki username.')
    parser.add_argument('--run-server', dest="run_server", required=False, action='store_true', default=False,
                        help='Instead of writing out flashcards, we will start a flask server where you can query '
                             'for characters. This will supersede all other arguments.')
    parser.add_argument('--port', dest="port", required=False, type=int, default=5000,
                        help='Specify the port you want Flask to run on')
    parser.add_argument('--create-combined', dest="combined_output", required=False, action='store_true',
                        help='Set this option if you want to create flashcards with combined character mnemonics and'
                             ' words in a single output.')
    args = parser.parse_args()  # type: argparse.Namespace

    if args.use_media_folder:
        if args.anki_username:
            args.chars_image_folder = os.path.join(os.getenv("APPDATA"), "Anki2", args.anki_username,
                                                   "collection.media")
        else:
            logging.critical("If you want to write directly to Anki's media folder you must provide your username!")
            exit(0)

    if args.log_level:
        if args.log_level == "debug":
            logging.basicConfig(level=logging.DEBUG)
            app.config['DEBUG'] = True
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

    if args.ebook_path and Path(args.ebook_path).is_file():
        app.config["ebook"] = epub.read_epub(args.ebook_path)
    elif args.ebook_path:
        print(args.ebook_path + " is not a file or that path doesn't exist!")
        exit(0)

    if args.run_server:
        if args.ebook_path:
            app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
            app.run(host='0.0.0.0', port=args.port)
        else:
            print("You cannot start a server without providing a path of a character ebook!")
            exit(0)
    else:
        if args.input_file_name:
            if not args.delimiter:
                args.delimiter = "~"
            else:
                args.delimiter = args.delimiter.strip('\'').strip('\"')

            if Path(args.input_file_name).is_file():
                words = []
                with open(args.input_file_name, encoding="utf-8-sig") as input_file:
                    for word in input_file.readlines():
                        words.append(word)

                words, characters = get_words(words, app.config["ebook"], args.skip_choices)

                if args.combined_output:
                    output_combined(args.words_output_file_name, args.chars_image_folder, words, args.delimiter)
                else:
                    output_words(args.words_output_file_name, words, args.delimiter)
                    output_characters(args.chars_output_file_name, args.chars_image_folder, characters, args.delimiter)
            else:
                print(args.input_file_name + " is not a file or doesn't exist!")
                exit(0)
        else:
            print("No input file name specified! You must provide a word list or run a server!")
            exit(0)


if __name__ == '__main__':
    main()
