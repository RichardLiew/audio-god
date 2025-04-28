#!/usr/bin/env zsh

##############################################################################

set -e

##############################################################################

pipenv run python audgod.py preprocess-notes \
    --source-file=./songs.note \
    --field-type=cn \
    --log-level=WARNING \
    --log-file=stderr

pipenv run python audgod.py fill-properties \
    --audios-source=~/Music/Source \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./ignored.txt \
    --source-file=./songs.note \
    --audios-root=~/Music/Source \
    --properties='\{ \
        "default": \{ \
            "sources": ["command"], #(note: command/file/directory/filename) \
            "value": "" \
        \}, \
        "genre": \{ \
            "sources": ["command", "file"], #(note: command/file/directory/filename) \
            "value": "Pop" \
        \} \
    \}' \
    --log-level=WARNING \
    --log-file=stderr

pipenv run python audgod.py format-properties \
    --audios-source=~/Music/Source \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./ignored.txt \
    --log-level=WARNING \
    --log-file=stderr

pipenv run python audgod.py rename-audios \
    --audios-source=~/Music/Source \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./ignored.txt \
    --filename-pattern="@{artist} # @{title}" \
    --log-level=WARNING \
    --log-file=stderr

pipenv run python audgod.py organize-files \
    --audios-source=~/Music/Source \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./ignored.txt \
    --audios-root=~/Music/Grouped \
    --organize-type=grouped \
    --log-level=WARNING \
    --log-file=stderr

pipenv run python audgod.py export \
    --audios-source=~/Music/Grouped \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./ignored.txt \
    --fields=note \
    --field-type=cn \
    --output-format=note \
    --output-file=./songs.note \
    --log-level=WARNING \
    --log-file=stderr

pipenv run python audgod.py list-repeated \
    --audios-source=~/Music/Grouped \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./ignored.txt \
    --output-file=./repeated.txt \
    --log-level=WARNING \
    --log-file=stderr

pipenv run python audgod.py organize-files \
    --audios-source=~/Music/Source \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./ignored.txt \
    --audios-root=~/music/iTunes/iTunes\ Media \
    --organize-type=ituned \
    --log-level=WARNING \
    --log-file=stderr

pipenv run python audgod.py export \
    --audios-source=~/music/iTunes/iTunes\ Media \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./ignored.txt \
    --fields=ituned \
    --field-type=en \
    --itunes-version-plist=/System/Applications/Music.app/Contents/version.plist \
    --itunes-media-folder=~/music/iTunes/iTunes\ Media \
    --track-initial-id=601 \
    --playlist-initial-id=3001 \
    --output-format=plist \
    --output-file=~/music/iTunes/iTunes\ Media/Library.xml \
    --log-level=WARNING \
    --log-file=stderr
