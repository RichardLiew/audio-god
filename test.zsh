#!/usr/bin/env zsh

##############################################################################

# Created Time: 2025-07-05T02:04:02Z

# Total Steps: 39

##############################################################################

set -e

##############################################################################

export AUDGOD_ROOT=./test

##############################################################################

echo "\n[***] Starting ...\n"

##############################################################################

printf "%.0s@" {1..60}; printf "\n"
echo "Step (1/39):\n\n"

./audio-god testing cleanup \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (2/39):\n\n"

./audio-god testing init \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (3/39):\n\n"

./audio-god convert kmx-to-mp4 \
    --source=./test/Source/Kmx \
    --extensions=kmx \
    --output=./test/Output/Kmx-To-Mp4 \
    --log-level=WARNING \
    --log-file=stderr \
    --recursive \
    --ignored-file=./test/Source/testing.ignores.txt

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (4/39):\n\n"

./audio-god convert qmc-to-audio \
    --source=./test/Source/Qmc \
    --extensions=qmc,qmc0,qmc1,qmc2,qmc3,qmcogg,qmcflac \
    --output=./test/Output/Qmc-To-Audio \
    --log-level=WARNING \
    --log-file=stderr \
    --recursive \
    --ignored-file=./test/Source/testing.ignores.txt

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (5/39):\n\n"

./audio-god convert media \
    --source=./test/Source/Media \
    --extensions=mp3,mp4,mov,flac,wav,ogg,ape,wma \
    --output=./test/Output/Media \
    --format=mp3 \
    --log-level=WARNING \
    --log-file=stderr \
    --recursive \
    --ignored-file=./test/Source/testing.ignores.txt

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (6/39):\n\n"

./audio-god redecorate-note \
    --document=./test/Source/testing.origin.songs.note.txt \
    --field-type=auto \
    --separators='-,#' \
    --output=./test/Output/testing.redecorate.note.txt \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (7/39):\n\n"

./audio-god pick note \
    --document=./test/Output/testing.redecorate.note.txt \
    --another='' \
    --field-type=auto \
    --output=./test/Output/testing.pick.note.txt \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (8/39):\n\n"

./audio-god sift-sources \
    --source=./test/Source/Mp3 \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./test/Source/testing.ignores.txt \
    --separators='-,#' \
    --output=./test/Output/testing.sift.sources.txt \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (9/39):\n\n"

./audio-god pick sources \
    --source=./test/Source/Mp3 \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./test/Source/testing.ignores.txt \
    --another='' \
    --separators='-,#' \
    --output=./test/Output/testing.pick.sources.txt \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (10/39):\n\n"

./audio-god match-sources \
    --source=./test/Source/Mp3 \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./test/Source/testing.ignores.txt \
    --document=./test/Output/testing.redecorate.note.txt \
    --field-type=auto \
    --separators='-,#' \
    --output=./test/Output/testing.match.sources.txt \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (11/39):\n\n"

./audio-god redecorate-note \
    --document=./test/Source/testing.another.origin.songs.note.txt \
    --field-type=auto \
    --separators='-,#' \
    --output=./test/Output/testing.another.redecorate.note.txt \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (12/39):\n\n"

./audio-god pick note \
    --document=./test/Output/testing.another.redecorate.note.txt \
    --another='' \
    --field-type=auto \
    --output=./test/Output/testing.another.pick.note.txt \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (13/39):\n\n"

./audio-god sift-sources \
    --source=./test/Source/Another \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./test/Source/testing.ignores.txt \
    --separators='-,#' \
    --output=./test/Output/testing.another.sift.sources.txt \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (14/39):\n\n"

./audio-god pick sources \
    --source=./test/Source/Another \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./test/Source/testing.ignores.txt \
    --another='' \
    --separators='-,#' \
    --output=./test/Output/testing.another.pick.sources.txt \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (15/39):\n\n"

./audio-god match-sources \
    --source=./test/Source/Another \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./test/Source/testing.ignores.txt \
    --document=./test/Output/testing.another.redecorate.note.txt \
    --field-type=auto \
    --separators='-,#' \
    --output=./test/Output/testing.another.match.sources.txt \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (16/39):\n\n"

./audio-god merge notes \
    --document=./test/Output/testing.redecorate.note.txt \
    --field-type=auto \
    --another=./test/Output/testing.another.redecorate.note.txt \
    --output=./test/Output/testing.merge.notes.txt \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (17/39):\n\n"

./audio-god pick note \
    --document=./test/Output/testing.redecorate.note.txt \
    --another=./test/Output/testing.another.redecorate.note.txt \
    --field-type=auto \
    --output=./test/Output/testing.merge.pick.note.txt \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (18/39):\n\n"

./audio-god merge sources \
    --source=./test/Source/Mp3 \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./test/Source/testing.ignores.txt \
    --separators='-,#' \
    --another=./test/Source/Another \
    --output=./test/Output/testing.merge.sources.txt \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (19/39):\n\n"

./audio-god pick sources \
    --source=./test/Source/Mp3 \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./test/Source/testing.ignores.txt \
    --another=./test/Source/Another \
    --separators='-,#' \
    --output=./test/Output/testing.merge.pick.sources.txt \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (20/39):\n\n"

./audio-god match-sources \
    --source=./test/Source/Mp3 \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./test/Source/testing.ignores.txt \
    --document=./test/Output/testing.merge.notes.txt \
    --field-type=auto \
    --separators='-,#' \
    --output=./test/Output/testing.merge.match.sources.txt \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (21/39):\n\n"

./audio-god extract-structure \
    --document=./test/Source/testing.origin.songs.note.txt \
    --output=./test/Output/testing.extract.structure.txt \
    --log-level=WARNING \
    --log-file=stderr \
    --show-count

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (22/39):\n\n"

./audio-god fill-properties \
    --source=./test/Source/Mp3 \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./test/Source/testing.ignores.txt \
    --document=./test/Output/testing.redecorate.note.txt \
    --root=./test/Source/Mp3 \
    --separators='-,#' \
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
    --output=./test/Output/testing.fill.properties.txt \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (23/39):\n\n"

./audio-god format-properties \
    --source=./test/Source/Mp3 \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./test/Source/testing.ignores.txt \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (24/39):\n\n"

./audio-god rename-audios \
    --source=./test/Source/Mp3 \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./test/Source/testing.ignores.txt \
    --filename-pattern='@{artist} # @{title}' \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (25/39):\n\n"

./audio-god manage-artworks bind \
    --source=./test/Source/Mp3 \
    --artworks=./test/Source/Artwork \
    --log-level=WARNING \
    --log-file=stderr \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./test/Source/testing.ignores.txt

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (26/39):\n\n"

./audio-god display \
    --source=./test/Source/Mp3 \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./test/Source/testing.ignores.txt \
    --fields=core \
    --field-type=cn \
    --output=./test/Output/testing.display.txt \
    --data-format=outputted \
    --page-number=1 \
    --page-size=0 \
    --sort='[
        {"_comment": ""},
        ["title,artist", true],
        ["genre", false]
    ]' \
    --filter='{
        "_options": {
            "_comment": "relation choose from and/or",
            "relation": "or"
        },
        "title,core": {
            "_comment": "function choose from equal/search/empty",
            "function": "search",
            "parameters": ["", true, false]
        }
    }' \
    --align='{
        "_comment": "align=l/c/r, valign=t/m/b",
        "title,artist": "l:m"
    }' \
    --style=tabled \
    --numbered \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (27/39):\n\n"

./audio-god organize grouped \
    --source=./test/Source/Mp3 \
    --output=./test/Output/Grouped \
    --log-level=WARNING \
    --log-file=stderr \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./test/Source/testing.ignores.txt

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (28/39):\n\n"

./audio-god list-repeated \
    --source=./test/Output/Grouped \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./test/Source/testing.ignores.txt \
    --output=./test/Output/testing.list.repeated.txt \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (29/39):\n\n"

./audio-god operate tree \
    --source=./test/Output \
    --output=./test/Output/testing.operate.tree.txt \
    --log-level=WARNING \
    --log-file=stderr \
    --show-count

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (30/39):\n\n"

./audio-god export note \
    --source=./test/Output/Grouped \
    --fields=basic \
    --field-type=cn \
    --output=./test/Output/testing.export.note.txt \
    --log-level=WARNING \
    --log-file=stderr \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./test/Source/testing.ignores.txt

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (31/39):\n\n"

./audio-god convert note-to-markdown \
    --document=./test/Output/testing.export.note.txt \
    --field-type=cn \
    --output=./test/Output/testing.convert.note.to.markdown.md \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (32/39):\n\n"

./audio-god export markdown \
    --source=./test/Output/Grouped \
    --fields=basic \
    --field-type=cn \
    --output=./test/Output/testing.export.markdown.md \
    --log-level=WARNING \
    --log-file=stderr \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./test/Source/testing.ignores.txt

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (33/39):\n\n"

./audio-god convert markdown-to-note \
    --document=./test/Output/testing.export.markdown.md \
    --output=./test/Output/testing.convert.markdown.to.note.txt \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (34/39):\n\n"

./audio-god organize ituned \
    --source=./test/Source/Mp3 \
    --output='./test/Output/iTunes/iTunes Media/Music' \
    --log-level=WARNING \
    --log-file=stderr \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./test/Source/testing.ignores.txt

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (35/39):\n\n"

./audio-god export plist \
    --source=./test/Source/Mp3 \
    --fields=ituned \
    --field-type=en \
    --output=./test/Output/iTunes/Library.xml \
    --itunes-version-plist=/System/Applications/Music.app/Contents/version.plist \
    --itunes-media-folder='./test/Output/iTunes/iTunes Media/Music' \
    --track-initial-id=601 \
    --playlist-initial-id=3001 \
    --log-level=WARNING \
    --log-file=stderr \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file=./test/Source/testing.ignores.txt

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (36/39):\n\n"

./audio-god operate backup \
    --source=./test/Source/testing.operate.backup.txt \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (37/39):\n\n"

./audio-god operate remove \
    --source=./test/Source/testing.operate.remove.txt \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (38/39):\n\n"

./audio-god generate-script start \
    --output=./test/Output/testing.start.zsh \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (39/39):\n\n"

./audio-god testing generate-script \
    --output=./test/Output/testing.test.zsh \
    --log-level=WARNING \
    --log-file=stderr

##############################################################################

unset AUDGOD_ROOT

##############################################################################

printf "%.0s@" {1..60}; printf "\n"
echo "\n[***] Finished!\n"
