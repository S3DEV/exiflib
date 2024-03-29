#!/usr/bin/env bash

dirs="./build ./dist ./exiflib.egg-info"

# Check for existing build/dist directories.
printf "\nChecking for existing build directories ...\n\n"
for d in ${dirs}; do
    # Delete the directory if it exists.
    if [ -d "${d}" ]; then
        printf "|- Deleting %s\n" ${d}
        rm -rf "${d}"
    fi
done

# Add line between deletion and setup runner.
printf "\n"

# Update requirements file.
printf "Updating the requirements file ...\n"
pipreqs . --force

# Create the package and wheel file.
printf "\nCreating the source distribution and wheel ...\n"
sleep 1
python ./setup.py sdist bdist_wheel

printf "\nDone.\n\n"

