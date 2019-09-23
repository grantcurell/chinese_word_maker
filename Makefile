SHELL=/bin/bash

.PHONY: all

# Default target, build *and* run tests
all:
        sed -e 's/ .*//g' word_searches.txt | sed -e 's/^.$$//g' | sed -e '/^$$/d' > word_searches_clean