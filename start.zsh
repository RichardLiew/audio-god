#!/usr/bin/env zsh

##############################################################################

# Created Time: 2025-07-05T02:03:54Z

# Total Steps: 20

##############################################################################

set -e

##############################################################################

export AUDGOD_ROOT=~/Music

##############################################################################

echo "\n[***] Starting ...\n"

##############################################################################

printf "%.0s@" {1..60}; printf "\n"
echo "Step (1/20):\n\n"

./audio-god operate cleanup \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (2/20):\n\n"

./audio-god convert qmc-to-audio \
    --source='~/Music/Source/Qmc' \
    --extensions=qmc,qmc0,qmc1,qmc2,qmc3,qmcogg,qmcflac \
    --output='~/Music/Output/Qmc-To-Audio' \
    --log-level=WARNING \
    --log-file=stderr \
    --recursive \
    --ignored-file='~/Music/Source/ignores.txt'

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (3/20):\n\n"

./audio-god redecorate-note \
    --document='~/Music/Source/origin.songs.note.txt' \
    --field-type=auto \
    --separators='-,#' \
    --output='~/Music/Output/redecorate.note.txt' \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (4/20):\n\n"

./audio-god pick note \
    --document='~/Music/Source/origin.songs.note.txt' \
    --another='~/Music/Source/another.origin.songs.note.txt' \
    --field-type=auto \
    --output='~/Music/Output/pick.note.txt' \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (5/20):\n\n"

./audio-god sift-sources \
    --source='~/Music/Source/Mp3' \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file='~/Music/Source/ignores.txt' \
    --separators='-,#' \
    --output='~/Music/Output/sift.sources.txt' \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (6/20):\n\n"

./audio-god pick sources \
    --source='~/Music/Source/Mp3' \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file='~/Music/Source/ignores.txt' \
    --another='~/Music/Source/Another' \
    --separators='-,#' \
    --output='~/Music/Output/pick.sources.txt' \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (7/20):\n\n"

./audio-god match-sources \
    --source='~/Music/Source/Mp3' \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file='~/Music/Source/ignores.txt' \
    --document='~/Music/Output/redecorate.note.txt' \
    --field-type=auto \
    --separators='-,#' \
    --output='~/Music/Output/match.sources.txt' \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (8/20):\n\n"

./audio-god merge notes \
    --document='~/Music/Source/origin.songs.note.txt' \
    --field-type=auto \
    --another='~/Music/Source/another.origin.songs.note.txt' \
    --output='~/Music/Output/merge.notes.txt' \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (9/20):\n\n"

./audio-god merge sources \
    --source='~/Music/Source/Mp3' \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file='~/Music/Source/ignores.txt' \
    --separators='-,#' \
    --another='~/Music/Source/Another' \
    --output='~/Music/Output/merge.sources.txt' \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (10/20):\n\n"

./audio-god extract-structure \
    --document='~/Music/Source/origin.songs.note.txt' \
    --output='~/Music/Output/extract.structure.txt' \
    --log-level=WARNING \
    --log-file=stderr \
    --show-count

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (11/20):\n\n"

./audio-god fill-properties \
    --source='~/Music/Source/Mp3' \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file='~/Music/Source/ignores.txt' \
    --document='~/Music/Output/redecorate.note.txt' \
    --root='~/Music/Source/Mp3' \
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
    --output='~/Music/Output/fill.properties.txt' \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (12/20):\n\n"

./audio-god format-properties \
    --source='~/Music/Source/Mp3' \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file='~/Music/Source/ignores.txt' \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (13/20):\n\n"

./audio-god rename-audios \
    --source='~/Music/Source/Mp3' \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file='~/Music/Source/ignores.txt' \
    --filename-pattern='@{artist} # @{title}' \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (14/20):\n\n"

./audio-god organize grouped \
    --source='~/Music/Source/Mp3' \
    --output='~/Music/Output/Grouped' \
    --log-level=WARNING \
    --log-file=stderr \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file='~/Music/Source/ignores.txt'

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (15/20):\n\n"

./audio-god list-repeated \
    --source='~/Music/Output/Grouped' \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file='~/Music/Source/ignores.txt' \
    --output='~/Music/Output/list.repeated.txt' \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (16/20):\n\n"

./audio-god operate tree \
    --source='~/Music/Output' \
    --output='~/Music/Output/operate.tree.txt' \
    --log-level=WARNING \
    --log-file=stderr \
    --show-count

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (17/20):\n\n"

./audio-god export note \
    --source='~/Music/Output/Grouped' \
    --fields=basic \
    --field-type=cn \
    --output='~/Music/Output/export.note.txt' \
    --log-level=WARNING \
    --log-file=stderr \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file='~/Music/Source/ignores.txt'

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (18/20):\n\n"

./audio-god convert note-to-markdown \
    --document='~/Music/Output/export.note.txt' \
    --field-type=cn \
    --output='~/Music/Output/convert.note.to.markdown.md' \
    --log-level=WARNING \
    --log-file=stderr

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (19/20):\n\n"

./audio-god organize ituned \
    --source='~/Music/Source/Mp3' \
    --output='~/Music/iTunes/iTunes Media/Music' \
    --log-level=WARNING \
    --log-file=stderr \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file='~/Music/Source/ignores.txt'

#-----------------------------------------------------------------------------

printf "%.0s-" {1..60}; printf "\n"
echo "Step (20/20):\n\n"

./audio-god export plist \
    --source='~/Music/Source/Mp3' \
    --fields=ituned \
    --field-type=en \
    --output='~/Music/iTunes/Library.xml' \
    --itunes-version-plist=/System/Applications/Music.app/Contents/version.plist \
    --itunes-media-folder='~/Music/iTunes/iTunes Media/Music' \
    --track-initial-id=601 \
    --playlist-initial-id=3001 \
    --log-level=WARNING \
    --log-file=stderr \
    --extensions=mp3,aac \
    --recursive \
    --ignored-file='~/Music/Source/ignores.txt'

##############################################################################

unset AUDGOD_ROOT

##############################################################################

printf "%.0s@" {1..60}; printf "\n"
echo "\n[***] Finished!\n"
