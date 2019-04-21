# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'tarjeta_ui.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QObject
from PyQt4.QtCore import SIGNAL
import os

from urllib.request import urlopen
from urllib.parse import quote
from html.parser import HTMLParser
from unidecode import unidecode # You can install this library with pip install unidecode
from bs4 import BeautifulSoup
from selenium import webdriver
import os.path

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)



class Ui_tarjeta_ui(object):

    list = []
    browser = webdriver

    def __init__(self):
        chop = webdriver.ChromeOptions()
        chop.add_extension('AdBlock_v3.11.2.crx')
        self.browser = webdriver.Chrome(chrome_options=chop)

    def setupUi(self, tarjeta_ui):
        tarjeta_ui.setObjectName(_fromUtf8("tarjeta_ui"))
        tarjeta_ui.resize(1873, 1038)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(tarjeta_ui.sizePolicy().hasHeightForWidth())
        tarjeta_ui.setSizePolicy(sizePolicy)
        self.horizontalLayout = QtGui.QHBoxLayout(tarjeta_ui)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.tab_object_main = QtGui.QTabWidget(tarjeta_ui)
        self.tab_object_main.setObjectName(_fromUtf8("tab_object_main"))
        self.tab_import_words = QtGui.QWidget()
        self.tab_import_words.setObjectName(_fromUtf8("tab_import_words"))
        self.gridLayout = QtGui.QGridLayout(self.tab_import_words)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.scroll_area_import_words = QtGui.QScrollArea(self.tab_import_words)
        self.scroll_area_import_words.setWidgetResizable(True)
        self.scroll_area_import_words.setObjectName(_fromUtf8("scroll_area_import_words"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 1829, 974))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.gridLayout_6 = QtGui.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_6.setObjectName(_fromUtf8("gridLayout_6"))
        self.text_edit_import_words = QtGui.QTextEdit(self.scrollAreaWidgetContents)
        self.text_edit_import_words.setObjectName(_fromUtf8("text_edit_import_words"))
        self.gridLayout_6.addWidget(self.text_edit_import_words, 0, 0, 1, 1)
        self.push_button_save_words = QtGui.QPushButton(self.scrollAreaWidgetContents)
        self.push_button_save_words.setObjectName(_fromUtf8("push_button_save_words"))
        self.gridLayout_6.addWidget(self.push_button_save_words, 0, 1, 1, 1)
        self.scroll_area_import_words.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout.addWidget(self.scroll_area_import_words, 0, 0, 1, 1)
        self.tab_object_main.addTab(self.tab_import_words, _fromUtf8(""))
        self.tab_create_cards = QtGui.QWidget()
        self.tab_create_cards.setObjectName(_fromUtf8("tab_create_cards"))
        self.gridLayout_2 = QtGui.QGridLayout(self.tab_create_cards)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label_front = QtGui.QLabel(self.tab_create_cards)
        self.label_front.setObjectName(_fromUtf8("label_front"))
        self.gridLayout_2.addWidget(self.label_front, 0, 1, 1, 1)
        self.label_back = QtGui.QLabel(self.tab_create_cards)
        self.label_back.setObjectName(_fromUtf8("label_back"))
        self.gridLayout_2.addWidget(self.label_back, 2, 1, 1, 1)
        self.push_button_add_card = QtGui.QPushButton(self.tab_create_cards)
        self.push_button_add_card.setObjectName(_fromUtf8("push_button_add_card"))
        self.gridLayout_2.addWidget(self.push_button_add_card, 4, 0, 1, 1)
        self.tabWidget_2 = QtGui.QTabWidget(self.tab_create_cards)
        self.tabWidget_2.setObjectName(_fromUtf8("tabWidget_2"))
        self.tab_spanishdict = QtGui.QWidget()
        self.tab_spanishdict.setObjectName(_fromUtf8("tab_spanishdict"))
        self.gridLayout_3 = QtGui.QGridLayout(self.tab_spanishdict)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.text_browser_spanish_dict = QtGui.QTextBrowser(self.tab_spanishdict)
        self.text_browser_spanish_dict.setObjectName(_fromUtf8("text_browser_spanish_dict"))
        self.gridLayout_3.addWidget(self.text_browser_spanish_dict, 0, 0, 1, 1)
        self.tabWidget_2.addTab(self.tab_spanishdict, _fromUtf8(""))
        self.tab_dle = QtGui.QWidget()
        self.tab_dle.setObjectName(_fromUtf8("tab_dle"))
        self.gridLayout_4 = QtGui.QGridLayout(self.tab_dle)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.text_browser_dle = QtGui.QTextBrowser(self.tab_dle)
        self.text_browser_dle.setObjectName(_fromUtf8("text_browser_dle"))
        self.gridLayout_4.addWidget(self.text_browser_dle, 0, 0, 1, 1)
        self.tabWidget_2.addTab(self.tab_dle, _fromUtf8(""))
        self.tab_wordreference = QtGui.QWidget()
        self.tab_wordreference.setObjectName(_fromUtf8("tab_wordreference"))
        self.gridLayout_5 = QtGui.QGridLayout(self.tab_wordreference)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.text_browser_wordreference = QtGui.QTextBrowser(self.tab_wordreference)
        self.text_browser_wordreference.setObjectName(_fromUtf8("text_browser_wordreference"))
        self.gridLayout_5.addWidget(self.text_browser_wordreference, 0, 0, 1, 1)
        self.tabWidget_2.addTab(self.tab_wordreference, _fromUtf8(""))
        self.gridLayout_2.addWidget(self.tabWidget_2, 1, 0, 3, 1)
        self.text_edit_card_front = QtGui.QTextEdit(self.tab_create_cards)
        self.text_edit_card_front.setObjectName(_fromUtf8("text_edit_card_back"))
        self.gridLayout_2.addWidget(self.text_edit_card_front, 1, 1, 1, 1)
        self.text_edit_card_back = QtGui.QTextEdit(self.tab_create_cards)
        self.text_edit_card_back.setLineWrapMode(QtGui.QTextEdit.WidgetWidth)
        self.text_edit_card_back.setObjectName(_fromUtf8("textEdit_3"))
        self.gridLayout_2.addWidget(self.text_edit_card_back, 3, 1, 1, 1)
        self.push_button_write_word = QtGui.QPushButton(self.tab_create_cards)
        self.push_button_write_word.setObjectName(_fromUtf8("push_button_write_word"))
        self.gridLayout_2.addWidget(self.push_button_write_word, 5, 1, 1, 1)
        self.push_button_next_word = QtGui.QPushButton(self.tab_create_cards)
        self.push_button_next_word.setObjectName(_fromUtf8("push_button_next_word"))
        self.gridLayout_2.addWidget(self.push_button_next_word, 4, 1, 1, 1)
        self.push_button_skip_word = QtGui.QPushButton(self.tab_create_cards)
        self.push_button_skip_word.setObjectName(_fromUtf8("push_button_skip_word"))
        self.gridLayout_2.addWidget(self.push_button_skip_word, 6, 1, 1, 1)
        self.gridLayout_2.setColumnStretch(0, 2)
        self.gridLayout_2.setColumnStretch(1, 1)
        self.tab_object_main.addTab(self.tab_create_cards, _fromUtf8(""))
        self.tab_quick_lookup = QtGui.QWidget()
        self.tab_quick_lookup.setObjectName(_fromUtf8("tab_quick_lookup"))
        self.gridLayout_7 = QtGui.QGridLayout(self.tab_quick_lookup)
        self.gridLayout_7.setObjectName(_fromUtf8("gridLayout_7"))
        self.text_browser_quick_lookup = QtGui.QTextBrowser(self.tab_quick_lookup)
        self.text_browser_quick_lookup.setObjectName(_fromUtf8("text_browser_quick_lookup"))
        self.gridLayout_7.addWidget(self.text_browser_quick_lookup, 1, 0, 1, 1)
        self.inline_edit_quicklook = QtGui.QLineEdit(self.tab_quick_lookup)
        self.inline_edit_quicklook.setObjectName(_fromUtf8("inline_edit_quicklook"))
        self.gridLayout_7.addWidget(self.inline_edit_quicklook, 1, 1, 1, 1)
        self.push_button_lookup = QtGui.QPushButton(self.tab_quick_lookup)
        self.push_button_lookup.setObjectName(_fromUtf8("push_button_lookup"))
        self.gridLayout_7.addWidget(self.push_button_lookup, 2, 1, 1, 1)
        self.label_quicklook_word = QtGui.QLabel(self.tab_quick_lookup)
        self.label_quicklook_word.setObjectName(_fromUtf8("label_quicklook_word"))
        self.gridLayout_7.addWidget(self.label_quicklook_word, 0, 1, 1, 1)
        self.push_button_add_to_list = QtGui.QPushButton(self.tab_quick_lookup)
        self.push_button_add_to_list.setObjectName(_fromUtf8("push_button_add_to_list"))
        self.gridLayout_7.addWidget(self.push_button_add_to_list, 3, 1, 1, 1)
        self.gridLayout_7.setColumnStretch(0, 2)
        self.gridLayout_7.setColumnStretch(1, 1)
        self.tab_object_main.addTab(self.tab_quick_lookup, _fromUtf8(""))
        self.horizontalLayout.addWidget(self.tab_object_main)

        self.retranslateUi(tarjeta_ui)
        self.tab_object_main.setCurrentIndex(2)
        self.tabWidget_2.setCurrentIndex(2)
        QtCore.QMetaObject.connectSlotsByName(tarjeta_ui)

        QObject.connect(self.push_button_save_words, SIGNAL("clicked()"), self._save_words)
        QObject.connect(self.push_button_next_word, SIGNAL("clicked()"), self._create_card)
        QObject.connect(self.push_button_write_word, SIGNAL("clicked()"), self._write_word)
        QObject.connect(self.push_button_lookup, SIGNAL("clicked()"), self._quick_lookup)
        QObject.connect(self.push_button_add_to_list, SIGNAL("clicked()"), self._add_to_list)
        QObject.connect(self.push_button_skip_word, SIGNAL("clicked()"), self._skip_word)
        QObject.connect(self.push_button_skip_word, SIGNAL("clicked()"), self._skip_word)

        ###########################################
        # Import cards                            #
        ###########################################
        if len(self.list) != 0:
            for word in self.list:
                self.text_edit_import_words.insertPlainText(word + '\n')
        else:
            if os.path.isfile("word_list"):
                with open("word_list", encoding="utf-8") as f:
                    for word in f.readlines():
                        word = word.strip()

                        # This try except block eliminates blank spaces that shouldn't be there
                        try:
                            if word[0].isalpha():
                                self.list.append(word)
                                self.text_edit_import_words.insertPlainText(word + "\n")
                        except IndexError:
                            pass
            else:
                self.text_edit_import_words.insertPlainText("Add words here. One on each line.")

    # Not auto-generated functions
    def _save_words(self):
        del self.list[:]
        for word in self.text_edit_import_words.toPlainText():
            self.list.append(word)

        with open('word_list', 'w+', encoding="utf-8") as f:
            for word in self.list:
                f.write(word + '\n')
            f.close()

    def create_cards_printline(self, text, box):

        if box == "spanishDict":
            self.text_browser_spanish_dict.insertPlainText(text)
        elif box == "dle":
            self.text_browser_dle.insertPlainText(text)
        elif box == "wordreference":
            self.text_browser_wordreference.insertPlainText(text)
        else:
            print("WARNING: Nothing matched")

    def quick_lookup_printline(self, text):
        self.text_browser_quick_lookup.insertPlainText(text)

    def create_cards_printline_front(self, text):
        self.text_edit_card_front.insertPlainText(text)

    def _clear_create_card_text_boxes(self):

        self.text_browser_spanish_dict.clear()
        self.text_browser_dle.clear()
        self.text_browser_wordreference.clear()
        self.text_edit_card_front.clear()
        self.text_edit_card_back.clear()

    def _create_card(self):

        self._clear_create_card_text_boxes()

        parser = SPAHTMLParser(self)

        if len(self.list) > 0:

            # Don't read the empty elements - make sure they are skipped and removed
            try:
                while self.list[-1].strip() == "":
                    self.list.pop()
            except IndexError:
                pass

            word = quote(self.list[-1].replace(" ", "%20"))

            # MDBG
            print("https://www.mdbg.net/chinese/dictionary?page=worddict&wdrst=1&wdqb=" + self.list[-1].replace(" ", "%20"))
            url_string = unidecode("https://www.mdbg.net/chinese/dictionary?page=worddict&wdrst=1&wdqb=" + word)
            parser.process_mdbg(urlopen(url_string).read().decode('utf-8'))

            # Google Chrome
            self.browser.get(unidecode('https://www.google.com/search?tbm=isch&q=' + word))


        else:
            parser.printLine("No more words in list!", "spanishDict")

    def _skip_word(self):
        self.list.pop()

    def _write_word(self):
        with open('new_cards', 'a+', encoding="utf-8") as f:
            # You need the <br/>s in anki for newlines. The strip makes sure there isn't one randomly trailing
            f.write(self.text_edit_card_front.toPlainText().replace("\n", "<br/>").strip('<br/>').replace(";", ":") + ";" + self.text_edit_card_back.toPlainText().replace("\n", "<br/>").strip('<br/>').replace(";", ":") + ";" + ";" + "" + "\n")
            # This begins the section which handles adding cards if examples are included
            self.list.pop()
            f.close()
            self._create_card()

    ###########################################
    # Quick Lookup                            #
    ###########################################

    def _clear_quick_lookup_text_boxes(self):
        self.text_browser_quick_lookup.clear()

    def _quick_lookup(self):

        parser = SPAHTMLParser(self)

        print("https://www.mdbg.net/chinese/dictionary?page=worddict&wdrst=1&wdqb=" + self.inline_edit_quicklook.text().replace(" ", "%20"))
        url_string = unidecode("https://www.mdbg.net/chinese/dictionary?page=worddict&wdrst=1&wdqb=" + self.inline_edit_quicklook.text().replace(" ", "%20"))
        parser.process_mdbg(urlopen(url_string).read().decode('utf-8'), True)

    def _add_to_list(self):

        self.list.append(self.inline_edit_quicklook.text())
        self.text_edit_import_words.insertPlainText(self.inline_edit_quicklook.text() + "\n")

    def retranslateUi(self, tarjeta_ui):
        tarjeta_ui.setWindowTitle(_translate("tarjeta_ui", "Form", None))
        self.push_button_save_words.setText(_translate("tarjeta_ui", "Save Words", None))
        self.tab_object_main.setTabText(self.tab_object_main.indexOf(self.tab_import_words), _translate("tarjeta_ui", "Import Words", None))
        self.label_front.setText(_translate("tarjeta_ui", "Front", None))
        self.label_back.setText(_translate("tarjeta_ui", "Back", None))
        self.push_button_add_card.setText(_translate("tarjeta_ui", "Add Card", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_spanishdict), _translate("tarjeta_ui", "SpanishDict", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_dle), _translate("tarjeta_ui", "DLE", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_wordreference), _translate("tarjeta_ui", "WordReference", None))
        self.push_button_write_word.setText(_translate("tarjeta_ui", "Write Word", None))
        self.push_button_next_word.setText(_translate("tarjeta_ui", "Next Word", None))
        self.push_button_skip_word.setText(_translate("tarjeta_ui", "Skip Word (Remove From List)", None))
        self.tab_object_main.setTabText(self.tab_object_main.indexOf(self.tab_create_cards), _translate("tarjeta_ui", "Create Cards", None))
        self.push_button_lookup.setText(_translate("tarjeta_ui", "Lookup", None))
        self.label_quicklook_word.setText(_translate("tarjeta_ui", "Word", None))
        self.push_button_add_to_list.setText(_translate("tarjeta_ui", "Add To List", None))
        self.tab_object_main.setTabText(self.tab_object_main.indexOf(self.tab_quick_lookup), _translate("tarjeta_ui", "Quick Lookup", None))

class SPAHTMLParser(HTMLParser):

    x = 0
    y = 0

    tarjeta_ui = Ui_tarjeta_ui

    def __init__(self, tarjeta_ui):
        self.tarjeta_ui = tarjeta_ui

    def process_mdbg(self, html, quick_look=False):
        soup = BeautifulSoup(html, 'html.parser')

        pinyin = soup.find("div", {"class": "pinyin"}).string.strip()
        print(pinyin)

        """
        if not quick_look:
            self.tarjeta_ui.create_cards_printline_front(word.lower())

        def _process_character(tag):
            if tag is not None:
                for string in tag.stripped_strings:
                    if len(string) > 2:
                        print(repr(string).replace('\'', '') + '\n')

                        if quick_look:
                            self.tarjeta_ui.quick_lookup_printline(repr(string).replace('\'', '') + '\n')
                        else:
                            self.tarjeta_ui.create_cards_printline(repr(string).replace('\'', '') + '\n', "spanishDict")

                if quick_look:
                    self.tarjeta_ui.quick_lookup_printline("\n\n-------------------------- END DICTIONARY --------------------------\n\n")
                else:
                    self.tarjeta_ui.create_cards_printline("\n\n-------------------------- END DICTIONARY --------------------------\n\n", "spanishDict")

                return False

            return True

        _process_character(soup.find("div", {"class": "dictionary-entry dictionary-neodict"}))
        """



