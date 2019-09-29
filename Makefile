SHELL=/bin/bash

.PHONY: all

# Default target, build *and* run tests
all:
	sed -e 's/ .*//g' word_searches.txt | sed -e 's/^.$$//g' | sed -e '/^$$/d' > word_searches_clean
	sed -e 's/ .*//g' character_searches.txt | sed -e 's/^.$$//g' | sed -e '/^$$/d' > character_searches_clean

word:
	sed -e 's/ .*//g' word_searches.txt | sed -e 's/^.$$//g' | sed -e '/^$$/d' > word_searches_clean
	python3 run.py --file word_searches_clean --ebook-path ./chinese_tarjetas/combined.epub --delimiter \ --use-media-folder --anki-username "User 1" --create-combined
	cp -f word_searches.txt /tmp/word_searches_backup.txt
	rm -f word_searches.txt word_searches_clean

character:
	sed -e 's/ .*//g' character_searches.txt | sed -e 's/^.$$//g' | sed -e '/^$$/d' > character_searches_clean	
	python3 run.py --file character_searches_clean --ebook-path ./chinese_tarjetas/combined.epub --delimiter \ --use-media-folder --anki-username "User 1"
	cp -f character_searches.txt /tmp/character_searches_backup.txt
	rm -f character_searches.txt character_searches_clean
