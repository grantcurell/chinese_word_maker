__author__ = "Grant Curell"
__copyright__ = "Do what you want with it"
__license__ = "GPLv3"
__version__ = "1.5.2"
__maintainer__ = "Grant Curell"

from ebooklib import epub
from chinese_tarjetas.chinese_tarjetas import *
from argparse import ArgumentParser
from pathlib import Path
from app import app
import platform
import pickle


def main():

    parser = ArgumentParser(description="Used to create Anki flash cards based on data from the website www.mdbg.net")
    parser.add_argument('--file', metavar='FILE', dest="input_file_name", type=str, required=False,
                        help='The path to a newline delimited list of Chinese words or characters in Hanji The default'
                             'is new_words.txt')
    parser.add_argument('--words-output-file', metavar='WORDS-OUTPUT-FILE', dest="words_output_file_name", type=str,
                        required=False, default="word_list.txt",
                        help='By default this is word_list.txt. You may change it by providing this argument.')
    parser.add_argument('--use-scholarly-examples', dest="scholarly_examples", type=bool,
                        required=False, default=False,
                        help='Controls whether you will use the old style scholarly articles to generate examples or '
                             'not.')
    parser.add_argument('--chars-image-folder', metavar='CHARS-IMAGE-FOLDER', dest="chars_image_folder", type=str,
                        required=False, default=None,
                        help='By default creates a folder called char_images in the current directory to store the '
                             'images associated with character images.')
    parser.add_argument('--skip-choices', dest="skip_choices", required=False, action='store_true', default=False,
                        help='This option will tell the program to just select the closest match for the word.')
    parser.add_argument('--ask-if-match-not-found', dest="ask_if_match_not_found", required=False, action='store_true',
                        default=False, help='Will only ask for input if an exact match between the pinyin and a '
                                            'character isn\'t found.')
    parser.add_argument('--combine-exact', dest="combine_exact", required=False, action='store_true',
                        default=False, help='Will instruct the program to automatically store all definitions matched'
                                            ' in MDBG.')
    parser.add_argument('--preference-hsk', dest="preference_hsk", required=False, action='store_true',
                        default=False, help='Uses whether a word is from HSK vocab as a tiebreaker between multiple'
                                            ' matching words. Discards non-HSK words.')
    parser.add_argument('--resume', dest="resume", required=False, action='store_true', default=False,
                        help='After word creation a file called ~temp will be created. Using the same syntax you did'
                             ' to originally run the program, you can add --resume if for some reason the program'
                             ' failed during example creation.')
    parser.add_argument('--allow-online-choices', dest="allow_online_choices", required=False, action='store_true',
                        default=False, help='Enables command line choices with the server running.')
    parser.add_argument('--ebook-path', metavar='EBOOK_PATH', dest="ebook_path", required=False, type=str,
                        default="combined.epub", help='A path to Chinese Blockbuster in EPUB format. In my case, I '
                                                      'bought all of them and merged them into one big book.')
    parser.add_argument('--log-level', metavar='LOG_LEVEL', dest="log_level", required=False, type=str, default="info",
                        choices=['debug', 'info', 'warning', 'error', 'critical'],
                        help='A path to Chinese Blockbuster in EPUB format. In my case, I bought all of them and merged'
                             ' them into one big book.')
    parser.add_argument('--delimiter', metavar='DELIMITER', dest="delimiter", required=False, type=str, default="\\",
                        help='Allows you to optionally select the delimiter you use for the delimiter in your Anki'
                             'cards. By default it is ~ which should avoid colliding with anything.')
    parser.add_argument('--use-media-folder', dest="use_media_folder", required=False, action='store_true',
                        help='If this option is passed the program will try to write to Anki\'s media folder directly.'
                             ' If you pass this argument, you must also pass your Anki username.')
    parser.add_argument('--anki-username', metavar='ANKI_USERNAME', dest="anki_username", required=False, type=str,
                        default="User 1", help='Your Anki username.')
    parser.add_argument('--run-server', dest="run_server", required=False, action='store_true', default=False,
                        help='Instead of writing out flashcards, we will start a flask server where you can query '
                             'for characters. This will supersede all other arguments.')
    parser.add_argument('--port', dest="port", required=False, type=int, default=5000,
                        help='Specify the port you want Flask to run on')
    parser.add_argument('--thread-count', dest="thread_count", required=False, type=int, default=5,
                        help='Specify the number of worker threads with which you want to grab examples.')
    parser.add_argument('--show-chrome', dest="show_chrome", required=False, action='store_true',
                        help='Will disable headless mode on Chromedriver and cause the browser to pop up')
    parser.add_argument('--single-word', metavar='SINGLE-WORD', dest="single_word", type=str, required=False,
                        help='Use if you only want to create a card for a single word.')
    parser.add_argument('--print-usage', dest="print_usage", required=False, action='store_true',
                        help='Show example usage.')
    
    args = parser.parse_args()  # type: argparse.Namespace

    if not args.run_server and not args.input_file_name and not args.print_usage and not args.single_word:
        parser.print_help()
        exit(0)

    if args.print_usage:
        print('Run a server:')
        print("--run-server --use-media-folder --anki-username \"User 1\"")
        print('\nCreate combined cards:')
        print('python run.py --use-media-folder --anki-username "User 1" --file test_words_2.txt --skip-choices --delimiter \ ')
        print('\nVisual Studio Code regex for excluding lines starting with asterisk: ^(?!\*).*\\n')
        print('\nMapping for "Chinse Words Updated" is:')
        print('Traditional\nSimplified\nPinyin\nMeaning\nTags\nCharacters')
        exit(0)

    if args.ask_if_match_not_found:
        args.skip_choices = True

    # Change path depending on whether we are on Windows or Linux
    if args.use_media_folder or args.chars_image_folder is None:
        if args.anki_username:
            if 'Windows' in platform.system():
                args.chars_image_folder = os.path.join(os.getenv("APPDATA"), "Anki2", args.anki_username,
                                                       "collection.media")
            else:
                args.chars_image_folder = os.path.expanduser("~") + '/.local/share/Anki2/' + args.anki_username + \
                                          '/collection.media'
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

    if not args.delimiter:
        args.delimiter = "\\"
    else:
        args.delimiter = args.delimiter.strip('\'').strip('\"')

    if args.run_server:
        # This means the user would like to create the cards as the words are found.
        app.config['OUTPUT_FILE'] = "word_searches_combined.txt"
        app.config['IMAGE_FOLDER'] = args.chars_image_folder
        app.config['DELIMITER'] = args.delimiter
        if args.show_chrome:
            driver = create_driver(headless=False)
        else:
            driver = create_driver()
        app.config['DRIVER'] = driver

        if args.scholarly_examples:
            app.config['SCHOLARLY'] = True
        else:
            app.config['SCHOLARLY'] = False

        if args.allow_online_choices:
            app.config['ONLINE_CHOICES'] = True
        else:
            app.config['ONLINE_CHOICES'] = False

        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
        app.run(host='0.0.0.0', port=args.port)
        driver.close()
    elif args.single_word:

        words = get_words(args.single_word, ebook=app.config["ebook"], skip_choices=args.skip_choices,
                          ask_if_match_not_found=args.ask_if_match_not_found, combine_exact_defs=args.combine_exact,
                          preference_hsk=args.preference_hsk)

        output_combined(args.words_output_file_name, args.chars_image_folder, words, args.delimiter,
                        thread_count=args.thread_count)
    else:
        if args.input_file_name and not args.resume:
            if Path(args.input_file_name).is_file():
                words = []
                with open(args.input_file_name, encoding="utf-8-sig") as input_file:
                    for word in input_file.readlines():
                        if word.strip() != "":
                            words.append(word)

                words = get_words(words, ebook=app.config["ebook"], skip_choices=args.skip_choices,
                                  ask_if_match_not_found=args.ask_if_match_not_found,
                                  combine_exact_defs=args.combine_exact, preference_hsk=args.preference_hsk)

                # Before creating examples, create a temp file with words data. This allows us to retrieve that data
                # in the event of a problem with the examples.
                with open('~temp', 'wb') as words_temp_file:
                    pickle.dump(words, words_temp_file)

                output_combined(args.words_output_file_name, args.chars_image_folder, words, args.delimiter,
                                args.thread_count, args.show_chrome)
            else:
                print(args.input_file_name + " is not a file or doesn't exist!")
                exit(0)
        elif args.resume:

            with open('~temp', 'rb') as words_temp_file:
                words = pickle.load(words_temp_file)

            output_combined(args.words_output_file_name, args.chars_image_folder, words, args.delimiter,
                            args.thread_count, args.show_chrome)
        else:
            print("No input file name specified! You must provide a word list or run a server!")
            exit(0)


if __name__ == '__main__':
    main()
