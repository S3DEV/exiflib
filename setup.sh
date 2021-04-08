#!/usr/bin/env bash

# CREATE BUILD, DIST AND WHEEL
./setup.py sdist bdist_wheel

printf "\nCreating the requirements file ...\n"
pipreqs . --force

printf "\nDone.\n\n"

