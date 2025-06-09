#!/usr/bin/env zsh

##############################################################################

# Created Time: 2025-06-09T11:51:10Z

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
    --recursive=true \
    --ignored-file=./ignored.txt \
    --source-file=./songs.note \
    --audios-root=~/Music/Source \
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
    --log-level=WARNING \
    --log-file=stderr

pipenv run python audgod.py format-properties \
    --audios-source=~/Music/Source \
    --extensions=mp3,aac \
    --recursive=true \
    --ignored-file=./ignored.txt \
    --log-level=WARNING \
    --log-file=stderr

pipenv run python audgod.py rename-audios \
    --audios-source=~/Music/Source \
    --extensions=mp3,aac \
    --recursive=true \
    --ignored-file=./ignored.txt \
    --filename-pattern="@{artist} * @{title}" \
    --log-level=WARNING \
    --log-file=stderr

pipenv run python audgod.py organize-files \
    --audios-source=~/Music/Source \
    --extensions=mp3,aac \
    --recursive=true \
    --ignored-file=./ignored.txt \
    --audios-root=~/Music/Grouped \
    --organize-type=grouped \
    --log-level=WARNING \
    --log-file=stderr

pipenv run python audgod.py export \
    --audios-source=~/Music/Grouped \
    --extensions=mp3,aac \
    --recursive=true \
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
    --recursive=true \
    --ignored-file=./ignored.txt \
    --output-file=./repeated.txt \
    --log-level=WARNING \
    --log-file=stderr

pipenv run python audgod.py organize-files \
    --audios-source=~/Music/Grouped \
    --extensions=mp3,aac \
    --recursive=true \
    --ignored-file=./ignored.txt \
    --audios-root=~/Music/iTunes/iTunes\ Media/Music \
    --organize-type=ituned \
    --log-level=WARNING \
    --log-file=stderr

pipenv run python audgod.py export \
    --audios-source=~/Music/iTunes/iTunes\ Media/Music \
    --extensions=mp3,aac \
    --recursive=true \
    --ignored-file=./ignored.txt \
    --fields=ituned \
    --field-type=en \
    --itunes-version-plist=/System/Applications/Music.app/Contents/version.plist \
    --itunes-media-folder=~/Music/iTunes/iTunes\ Media/Music \
    --track-initial-id=601 \
    --playlist-initial-id=3001 \
    --output-format=plist \
    --output-file=~/Music/iTunes/Library.xml \
    --log-level=WARNING \
    --log-file=stderr
