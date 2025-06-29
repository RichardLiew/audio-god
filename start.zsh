#!/usr/bin/env zsh

##############################################################################

# Created Time: 2025-06-29T08:35:36Z

# Total Steps: 15

##############################################################################

set -e

##############################################################################

export AUDGOD_ROOT=~/Music

##############################################################################

echo "\n[***] Starting ...\n"

##############################################################################

printf "%.0s@" {1..60}; printf "\n"
echo "Step (1/15):\n\n"

./audio-god convert qmc-to-audio \
    --source='~/Music/Source/Qmc' \
    --extensions=qmc,qmc0,qmc1,qmc2,qmc3,qmcogg,qmcflac \
    --output='~/Music/Output/Qmc-To-Audio' \
    --recursive \
    --ignored-file=./ignores.txt \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (2/15):\n\n"

./audio-god redecorate-note \
    --document=./songs.note \
    --field-type=auto \
    --output=./songs.note \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (3/15):\n\n"

./audio-god fill-properties \
    --source='~/Music/Source/Mp3' \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./ignores.txt \
    --document=./songs.note \
    --root='~/Music/Source/Mp3' \
    --properties='{
        "_comment": "sources choose from command/file/directory/filename",
        "default": {
            "sources": ["command", "file"],
            "value": null
        },
        "genre": {
            "sources": ["command", "file"],
            "value": null
        }
    }' \
    --separators='-,#' \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (4/15):\n\n"

./audio-god format-properties \
    --source='~/Music/Source/Mp3' \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./ignores.txt \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (5/15):\n\n"

./audio-god rename-audios \
    --source='~/Music/Source/Mp3' \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./ignores.txt \
    --filename-pattern='@{artist} # @{title}' \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (6/15):\n\n"

./audio-god organize grouped \
    --source='~/Music/Source/Mp3' \
    --root='~/Music/Output/Grouped' \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./ignores.txt \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (7/15):\n\n"

./audio-god export note \
    --source='~/Music/Output/Grouped' \
    --fields=basic \
    --field-type=cn \
    --output=./songs.note \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./ignores.txt \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (8/15):\n\n"

./audio-god export markdown \
    --source='~/Music/Output/Grouped' \
    --fields=basic \
    --field-type=cn \
    --output=./songs.md \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./ignores.txt \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (9/15):\n\n"

./audio-god list-repeated \
    --source='~/Music/Output/Grouped' \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./ignores.txt \
    --output=./repeated.txt \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (10/15):\n\n"

./audio-god organize ituned \
    --source='~/Music/Output/Grouped' \
    --root='~/Music/iTunes/iTunes Media/Music' \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./ignores.txt \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (11/15):\n\n"

./audio-god export plist \
    --source='~/Music/Source/Mp3' \
    --fields=ituned \
    --field-type=en \
    --output='~/Music/iTunes/Library.xml' \
    --itunes-version-plist=/System/Applications/Music.app/Contents/version.plist \
    --itunes-media-folder='~/Music/iTunes/iTunes Media/Music' \
    --track-initial-id=601 \
    --playlist-initial-id=3001 \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./ignores.txt \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (12/15):\n\n"

./audio-god convert note-to-markdown \
    --document=./songs.note \
    --field-type=auto \
    --output=./songs.note.md \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (13/15):\n\n"

./audio-god convert markdown-to-note \
    --document=./songs.md \
    --output=./songs.md.note \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (14/15):\n\n"

./audio-god extract-structure \
    --document=./songs.note \
    --field-type=auto \
    --output='' \
    --show-count \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (15/15):\n\n"

./audio-god operate tree \
    --source='~/Music/Output' \
    --output='' \
    --show-count \
    --log-level=WARNING \
    --log-file=stderr

##############################################################################

unset AUDGOD_ROOT

##############################################################################

printf "%.0s@" {1..60}; printf "\n"
echo "\n[***] Finished!\n"
