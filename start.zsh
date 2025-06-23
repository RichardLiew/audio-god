#!/usr/bin/env zsh

##############################################################################

# Created Time: 2025-06-24T07:59:16Z

##############################################################################

set -e

##############################################################################

./audio-god preprocess-note \
    --document=./songs.note \
    --field-type=cn \
    --log-level=WARNING \
    --log-file=stderr

./audio-god fill-properties \
    --source='~/Music/Source/MP3' \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./ignored.txt \
    --document=./songs.note \
    --root='~/Music/Source/MP3' \
    --properties=''"'"'{
        "_comment": "sources choose from command/file/directory/filename",
        "default": {
            "sources": ["command", "file"],
            "value": null
        },
        "genre": {
            "sources": ["command", "file"],
            "value": null
        }
    }'"'"'' \
    --log-level=WARNING \
    --log-file=stderr

./audio-god format-properties \
    --source='~/Music/Source/MP3' \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./ignored.txt \
    --log-level=WARNING \
    --log-file=stderr

./audio-god rename-audios \
    --source='~/Music/Source/MP3' \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./ignored.txt \
    --filename-pattern='@{artist} * @{title}' \
    --log-level=WARNING \
    --log-file=stderr

./audio-god organize grouped \
    --source='~/Music/Source/MP3' \
    --root='~/Music/Output/Grouped' \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./ignored.txt \
    --log-level=WARNING \
    --log-file=stderr

./audio-god export note \
    --source='~/Music/Output/Grouped' \
    --fields=note \
    --field-type=cn \
    --output=./songs.note \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./ignored.txt \
    --track-initial-id=601 \
    --playlist-initial-id=3001 \
    --log-level=WARNING \
    --log-file=stderr

./audio-god list-repeated \
    --source='~/Music/Output/Grouped' \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./ignored.txt \
    --output=./repeated.txt \
    --log-level=WARNING \
    --log-file=stderr

./audio-god organize ituned \
    --source='~/Music/Output/Grouped' \
    --root='~/Music/Source/MP3' \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./ignored.txt \
    --log-level=WARNING \
    --log-file=stderr

./audio-god export plist \
    --source='~/Music/Source/MP3' \
    --fields=ituned \
    --field-type=en \
    --output='~/Music/iTunes/Library.xml' \
    --itunes-version-plist=/System/Applications/Music.app/Contents/version.plist \
    --itunes-media-folder='~/Music/iTunes/iTunes\ Media/Music' \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./ignored.txt \
    --track-initial-id=601 \
    --playlist-initial-id=3001 \
    --log-level=WARNING \
    --log-file=stderr
