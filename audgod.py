#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2022 Anebit Inc.
# All rights reserved.
#
# "Audio God" version 1.0
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#    * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following disclaimer
# in the documentation and/or other materials provided with the
# distribution.
#    * Neither the name of Anebit Inc. nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL__ THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES_; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# ---
# Author:  Richard
# Created: 2022-08-30 10:46:00
# E-mail:  richard.zen.liew@gmail.com
#
# ---
# Description:
#   The god processor for audios.
#
# ---
# Dependences:
#   1. pyenv: [.python-version => ```
#       3.10.6
#   ```];
#   2. pipenv: [Pipfile => ```
#       [[source]]
#       url = "https://pypi.org/simple"
#       verify_ssl = true
#       name = "pypi"
#
#       [packages]
#       psutil = "==7.0.0"
#       treelib = "==1.7.1"
#       enumx = "==0.0.2"
#       prettytable = "==3.2.0"
#       eyed3 = "==0.9.7"
#       mdutils = "==1.6.0"
#
#       [dev-packages]
#       pylint = "==3.3.6"
#
#       [requires]
#       python_version = "3.10.6"
#   ```].
#
# ---
# Directories:
#   1. iCloud Path: /Users/Zichoole/Library/Mobile\ Documents/com~apple~CloudDocs/;
#   2. Mac Application Cache Path: /Users/Zichoole/Library/Containers/;
#   3. QQMusic Download Path: /Users/Zichoole/Library/Containers/com.tencent.QQMusicMac/Data/Library/Application\ Support/QQMusicMac/iQmc/;
#
# ---
# Tools:
#   1. Apple Music Help Online: https://support.apple.com/en-hk/HT210403;
#   2. QQMusic QMC->MP3: https://openyyy.com/;
#   3. Youku KMX->MP4: https://gitee.com/RichardLiew/kmx-MP4;
#   4. MP4->MP3: https: https://github.com/SiD-93/BatchMP3;
#   5. Online Small Tools: https://tool.lu/;
#   6. Format Convert: https://www.aconvert.com/;
#   7. Videos Download: https://github.com/iawia002/annie;
#   8. Mac Audio Processor: https://amvidia.com/;
#
# ---
# Commands:
#   1. View Directory Structure: tree -dN ~/Music;
#
# ---
# Notes:
#   1. None;
#
# ---
# FAQs:
#   1. pipenv 依赖于 pyenv，如果异常，建议先 "pyenv uninstall (python)X.X.X"，
#      然后再重新 "pyenv install (python)X.X.X"；安装完成后，需要在 ~/.zshrc
#     （或者 ~/.bashrc、~/.bash_profile）文件最下方添加如下内容并重载 => ```
#          export PYENV_ROOT="$HOME/.pyenv"
#          export PATH="$PYENV_ROOT/bin:$PATH"
#          eval "$(pyenv init -)"
#      ```
#
# ---
# TODO (@Richard):
#   1. Convert qmc to mp3;
#   2. Convert kmx to mp4;
#   3. Convert mp4 to mp3;
#   4. Convert note to markdown;
#   4. Convert markdown to note;
#
###############################################################################

import os
import re
import sys
import math
import time
import uuid
import json
import copy
import glob
import pydoc
import urllib
import shutil
import logging
import argparse
import plistlib
import datetime
import functools

from string import Template
from collections import ChainMap

import psutil

from treelib import Tree
from enumx import StringEnum
from prettytable import PrettyTable

import eyed3
from eyed3.id3 import Genre, frames
from eyed3.id3.tag import CommentsAccessor


'''
    The god processor for audios.
'''

################################################################################
#                                                                              #
#                                SCRIPT MACROS                                 #
#                                                                              #
################################################################################

__VERSION__ = 'Audio God 1.0'

################################################################################
#                                                                              #
#                                  PRESETS                                     #
#                                                                              #
################################################################################

DEFAULT_LOG_LEVEL = 'WARNING'
DEFAULT_LOG_FILE = 'stderr'

################################################################################
#                                                                              #
#                            CLASSES AND FUNCTIONS                             #
#                                                                              #
################################################################################

def log_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print_func = print
        instance = args[0] if args else None
        if instance:
            logger = getattr(instance, 'logger', None)
            if logger:
                print_func = logger.warning
        func_name, start_time = func.__name__.replace('_', '-'), time.time()
        print_func('*' * 78 + '\n')
        print_func(f'Starting <{func_name}> ...')
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            cost_time = time.time() - start_time
            print_func(f'\n<{func_name}> finished, cost {cost_time:.2f} seconds.\n')
    return wrapper


class FatalLogger(logging.Logger):
    def __init__(self, level=DEFAULT_LOG_LEVEL, log_file=DEFAULT_LOG_FILE):
        super().__init__('fatal', level)
        stdout_streams = ['stdout', 'sys.stdout', sys.stdout]
        stderr_streams = [None, '', 'stderr', 'sys.stderr', sys.stderr]
        if log_file in stdout_streams+stderr_streams:
            console_handler = logging.StreamHandler(
                sys.stderr if log_file in stderr_streams else sys.stdout
            )
            console_handler.setFormatter(logging.Formatter('%(message)s'))
            console_handler.setLevel(level)
            self.addHandler(console_handler)
        else:
            file_handler = logging.FileHandler(
                log_file, encoding='utf-8', delay=False, # type: ignore
            )
            file_handler.setFormatter(logging.Formatter('%(message)s'))
            file_handler.setLevel(level)
            self.addHandler(file_handler)

    def critical(self, msg, *args, **kwargs):
        super().critical(msg, *args, **kwargs)
        sys.exit(1)


class TreeX(Tree):
    def __init__(self, logger=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if logger is None:
            logger = FatalLogger(DEFAULT_LOG_LEVEL, DEFAULT_LOG_FILE)
        self.logger = logger

    def perfect_merge(self, nid, new_tree, deep=False) -> None:
        if not (isinstance(new_tree, Tree) or isinstance(new_tree, TreeX)):
            self.logger.fatal('The new tree to merge is not a valid tree.')
            return

        if new_tree is None:
            return

        if new_tree.root is None:
            return

        if nid is None:
            if self.root is None:
                self.add_node(new_tree[new_tree.root])
            nid = self.root

        if not self.contains(nid):
            self.logger.fatal(f'Node <{nid}> is not in the tree!')
            return

        current_node = self[nid]

        if current_node.tag != new_tree[new_tree.root].tag:
            self.logger.fatal('Current node not same with root of new tree.')
            return

        childs = self.children(nid)
        child_tags = [child.tag for child in childs]
        new_childs = new_tree.children(new_tree.root)
        new_subtrees = [new_tree.subtree(child.identifier) for child in new_childs]

        if not childs:
            for new_subtree in new_subtrees:
                self.paste(nid=nid, new_tree=new_subtree, deep=deep)
        else:
            for new_child in new_childs:
                if new_child.tag not in child_tags:
                    self.paste(nid=nid, new_tree=new_tree.subtree(new_child.identifier), deep=deep)
                    continue
                self.perfect_merge(
                    childs[child_tags.index(new_child.tag)].identifier,
                    new_tree.subtree(new_child.identifier),
                    deep=deep,
                )

################################################################################
#                                                                              #
#                                 Audio God                                    #
#                                                                              #
################################################################################

class AudioGod(object):
    CACHE_DIR = os.path.expanduser('~/.audgod-cache')
    TRASH_DIR = os.path.join(CACHE_DIR, 'trash')
    BACKUPS_DIR = os.path.join(CACHE_DIR, 'backups')


    ORI_DIV_CHAR = '-'
    DIV_CHAR = '*'
    GROUPING_SEPARATOR = '&'


    class FilenamePatternTemplate(Template):
        delimiter = '@'


    class PerfectTemplate(Template):
        idpattern = r'(?a:[_-a-z][_-a-z0-9]*(\.[_-a-z][_-a-z0-9]*)*)'

        def perfect_substitute(self, mapping, /, **kwargs):
            if kwargs:
                mapping = ChainMap(kwargs, mapping)
            def _convert(matched):
                named = matched.group('named') or matched.group('braced')
                if named is not None:
                    try:
                        return str(
                            AudioGod.repack_dict(mapping)[AudioGod.rewrite_key(named)],
                        )
                    except KeyError:
                        return matched.group()
                if matched.group('escaped') is not None:
                    return self.delimiter
                if matched.group('invalid') is not None:
                    return matched.group()
                raise ValueError(
                    'Unrecognized named group in pattern',
                    self.pattern,
                )
            return self.pattern.sub(_convert, self.template)


    @StringEnum.unique
    class SourceType(StringEnum):
        VALID = 'valid'
        MATCHED = 'matched'
        NOTMATCHED = 'notmatched'
        OMITTED = 'omitted'
        IGNORED = 'ignored'
        INVALID_EXT = 'invalid-ext'
        INVALID_NAME = 'invalid-name'


    @StringEnum.unique
    class FileFormat(StringEnum):
        NONE = 'none'
        JSON = 'json'
        MARKDOWN = 'markdown'
        PLIST = 'plist'
        NOTE = 'note'


    @StringEnum.unique
    class PropertySource(StringEnum):
        COMMAND = 'command'
        FILE = 'file'
        FILENAME = 'filename'
        DIRECTORY = 'directory'


    @StringEnum.unique
    class DisplayStyle(StringEnum):
        TABLED = 'tabled'
        COMPACT = 'compact'
        VERTICAL = 'vertical'


    @StringEnum.unique
    class DataFormat(StringEnum):
        ORIGINAL = 'original'
        FORMATTED = 'formatted'
        OUTPUTTED = 'outputted'


    @StringEnum.unique
    class AudiosTreeNodeType(StringEnum):
        ROOT = 'root'
        FOLDER = 'folder'
        PLAYLIST = 'playlist'
        TRACK = 'track'


    @StringEnum.unique
    class FieldType(StringEnum):
        ORIGINAL = 'ori'
        CHINESE = 'cn'
        ENGLISH = 'en'
    

    AUDIO_PROPERTIES = {
        'title': (('歌曲名', 'Name'), 'string'),
        'artist': (('歌手名', 'Artist'), 'string'),
        'album': (('专辑名', 'Album'), 'string'),
        'genre': (('流派', 'Genre'), 'string'),
        'grouping': (('分组', 'Grouping'), 'string'),
        'album_artist': (('专辑出品人', 'Album Artist'), 'string'),
        'comments': (('备注', 'Comments'), 'string'),
        'track_num': (('音轨号', 'Track Number'), 'integer'),
        'composer': (('作曲人', 'Composer'), 'string'),
        'publisher': (('出版公司', 'Publisher'), 'string'),
        'mtime': (('修改时间', 'Date Modified'), 'date'),
        'duration': (('时长', 'Total Time'), 'integer'),
        'bit_rate': (('比特率', 'Bit Rate'), 'integer'),
        'sample_freq': (('采样率', 'Sample Rate'), 'integer'),
        'mode': (('模式', 'Mode'), 'string'),
        'size': (('文件大小', 'Size'), 'integer'),
        'name': (('文件名', 'File Name'), 'string'),
        'path': (('文件路径', 'File Directory'), 'string'),
        'selected': (('已选择', 'Selected'), 'boolean'),
        'liked': (('喜欢', 'Liked'), 'boolean'),
        'rating': (('评分', 'Rating'), 'integer'),
        'artwork': (('封面', 'Artwork'), 'string'),
    }

    AUDIO_CN_PROPERTIES = {
        key: value[0][0] for key, value in AUDIO_PROPERTIES.items()
    }

    AUDIO_CN_PROPERTY_SYNONYMS = {
        value.lower(): key for key, value in AUDIO_CN_PROPERTIES.items()
    }

    AUDIO_EN_PROPERTIES = {
        key: value[0][1] for key, value in AUDIO_PROPERTIES.items()
    }

    AUDIO_EN_PROPERTY_SYNONYMS = {
        value.lower(): key for key, value in AUDIO_EN_PROPERTIES.items()
    }

    AUDIO_PROPERTY_TYPES = {
        key: value[1] for key, value in AUDIO_PROPERTIES.items()
    }

    AudioProperty = StringEnum.unique(StringEnum(
        'AudioProperty', {
            prop.upper(): prop for prop in AUDIO_CN_PROPERTIES.keys()
        },
    ))

    DEFAULTS_FIELDS = [
        AudioProperty.TITLE,
        AudioProperty.ARTIST,
        AudioProperty.ALBUM,
        AudioProperty.GENRE,
        AudioProperty.ALBUM_ARTIST,
    ]

    NOTE_FIELDS = [
        AudioProperty.TITLE,
        AudioProperty.ARTIST,
        AudioProperty.ALBUM,
    ]

    SIMPLE_FIELDS = [
        AudioProperty.TITLE,
        AudioProperty.ARTIST,
        AudioProperty.ALBUM,
        AudioProperty.GENRE,
        AudioProperty.GROUPING,
    ]
    
    ZIP_FIELDS = [
        AudioProperty.GROUPING,
        AudioProperty.SELECTED,
        AudioProperty.LIKED,
        AudioProperty.RATING,
        AudioProperty.ARTWORK,
    ]

    CORE_FIELDS = [
        AudioProperty.TITLE,
        AudioProperty.ARTIST,
        AudioProperty.ALBUM,
        AudioProperty.GENRE,
        AudioProperty.GROUPING,
        AudioProperty.ALBUM_ARTIST,
        AudioProperty.ARTWORK,
    ]

    ITUNED_FIELDS = [
        AudioProperty.TITLE,
        AudioProperty.ARTIST,
        AudioProperty.ALBUM,
        AudioProperty.GENRE,
        AudioProperty.ALBUM_ARTIST,
        AudioProperty.SIZE,
        AudioProperty.DURATION,
        AudioProperty.BIT_RATE,
        AudioProperty.SAMPLE_FREQ,
        AudioProperty.MTIME,
    ]

    ALL_FIELDS = AudioProperty.members(excepts=[
        AudioProperty.COMMENTS,
    ])

    FIELDS = {
        'all': ALL_FIELDS,
        'defaults': DEFAULTS_FIELDS,
        'note': NOTE_FIELDS,
        'simple': SIMPLE_FIELDS,
        'zip': ZIP_FIELDS,
        'core': CORE_FIELDS,
        'ituned': ITUNED_FIELDS,
    }


    AUDIOS_TREE_ROOT_TAG = '--root-tag--'
    AUDIOS_TREE_ROOT_NID = '--root-nid--'

    DEFAULT_GENRE = 'Default'
    DEFAULT_GROUPING = 'Default'


    PUBLIC_ARGUMENTS = {
    }

    COMMON_ARGUMENTS = {
    }

    _______COMMON_ARGUMENTS = {
        'document': { 'default': './songs.note' },
        'source': { 'default': '~/Music/Source' },
        'recursive': { 'default': 'true' },
        'root': { 'default': '~/Music/Source' },
        'properties': {
            'default': '''
                \'{
                    "_comment": "sources choose from command/file/directory/filename",
                    "default": {
                        "sources": ["command", "file"],
                        "value": null
                    },
                    "genre": {
                        "sources": ["command", "file"],
                        "value": null
                    }
                }\'
            ''',
        },
        'fields': { 'default': 'core' },
        'page_number': { 'default': 1 },
        'page_size': { 'default': 0 },
        'sort': {
            'default': '''
                \'[
                    {"_comment": ""},
                    ["title,artist", true],
                    ["genre", false]
                ]\'
            ''',
        },
        'filter': {
            'default': '''
                \'{
                    "_options": {
                        "_comment": "relation choose from and/or",
                        "relation": "or"
                    },
                    "title,core": {
                        "_comment": "function choose from equal/search/empty",
                        "function": "search",
                        "parameters": ["", true, false]
                    }
                }\'
            ''',
        },
        'align': {
            'default': '''
                \'{
                    "_comment": "align=l/c/r, valign=t/m/b",
                    "title,artist": "l:m"
                }\'
            ''',
        },
        'numbered': { 'default': 'true' },
        'style': {
            'default': DisplayStyle.TABLED,
            'choices': DisplayStyle.members(),
        },
        'data_format': {
            'default': DataFormat.OUTPUTTED,
            'choices': DataFormat.members(),
        },
        'field_type': {
            'default': FieldType.ORIGINAL,
            'choices': FieldType.members(),
        },
        'output': { 'default': "" },
        'type': {
            #'default': OrganizeType.ITUNED,
            #'choices': OrganizeType.members(),
        },
        'track_initial_id': { 'default': 601 },
        'playlist_initial_id': { 'default': 3001 },
        'music_source_folder': { 'default': '~/Music/Source' },
        'music_source_qmc_folder': { 'default': '~/Music/Source/QMC' },
        'music_source_kmx_folder': { 'default': '~/Music/Source/KMX' },
        'music_source_mp4_folder': { 'default': '~/Music/Source/MP4' },
        'music_source_mp3_folder': { 'default': '~/Music/Source/MP3' },
        'music_grouped_folder': { 'default': '~/Music/Grouped' },
        'artwork_path': { 'default': '~/Music/Artworks' },
        'itunes_media_folder': { 'default': '~/Music/iTunes/iTunes\ Media/Music' }, # type: ignore
        'itunes_library_plist': { 'default': '~/Music/iTunes/Library.xml' }, # type: ignore
        'itunes_version_plist': { 'default': '/System/Applications/Music.app/Contents/version.plist' },
        'ignored_file': { 'default': './ignored.txt' },
        'note_file': { 'default': './songs.note' },
        'repeated_file': { 'default': './repeated.txt' },
        'extensions': { 'default': 'mp3,aac' },
        'filename_pattern': {
            'default': '{delimiter}{{artist}} {div_char} {delimiter}{{title}}'.format(
                delimiter=FilenamePatternTemplate.delimiter,
                div_char=DIV_CHAR,
            ),
        },
        'script_file': { 'default': './start.zsh' },







        'log_level': {
            'default': DEFAULT_LOG_LEVEL,
            'choices': [
                'NOTSET',
                'DEBUG',
                'INFO',
                'WARN',
                'WARNING',
                'ERROR',
                'FATAL',
                'CRITICAL',
            ],
        },
        'log_file': { 'default': DEFAULT_LOG_FILE },
    }


    ACTIONS = {
        'preprocess-notes': {
            'arguments': [
                {'document': {'default': './songs.note'}},
                {'field_type': {'default': FieldType.CHINESE, 'choices': FieldType.members()}},
            ],
            'kwargs': {
                'description': '✋ Preprocess the notes file',
                'help': 'preprocess the notes file',
                'usage': '''
                    ${cmd} preprocess-notes \\
                        --document=${document} \\
                        --field-type=${field_type} \\
                        --log-level=${log_level} \\
                        --log-file=${log_file}
                ''',
            },
        },
        'fill-properties': {
            'arguments': [
                {'source': {'default': '~/Music/Source/MP3'}},
                {'extensions': {'default': 'mp3,aac'}},
                {'recursive': {'default': 'true', 'choices': []}},
                {'ignored_file': {'default': './ignored.txt'}},
                {'document': {'default': './songs.note'}},
                {'root': {'default': '~/Music/Source/MP3'}},
                {'properties': {
                    'default': '''
                        \'{
                            "_comment": "sources choose from command/file/directory/filename",
                            "default": {
                                "sources": ["command", "file"],
                                "value": null
                            },
                            "genre": {
                                "sources": ["command", "file"],
                                "value": null
                            }
                        }\'
                    ''',
                }},
            ],
            'kwargs': {
                'description': '✋ Fill properties of audios',
                'help': 'fill properties of audios',
                'usage': '''
                    ${cmd} fill-properties \\
                        --source=${source} \\
                        --extensions=${extensions} \\
                        --recursive=${recursive} \\
                        --ignored-file=${ignored_file} \\
                        --document=${document} \\
                        --root=${root} \\
                        --properties=${properties} \\
                        --log-level=${log_level} \\
                        --log-file=${log_file}
                ''',
                },
        },
        'format-properties': {
            'arguments': [
                'source',
                'extensions',
                'recursive',
                'ignored_file',
            ],
            'kwargs': {
                'description': '✋ Format properties of audios',
                'help': 'format properties of audios',
                'usage': '''
                    ${cmd} format-properties \\
                        --source=${source} \\
                        --extensions=${extensions} \\
                        --recursive=${recursive} \\
                        --ignored-file=${ignored_file} \\
                        --log-level=${log_level} \\
                        --log-file=${log_file}
                ''',
            },
        },
        'rename-audios': {
            'arguments': [
                'source',
                'extensions',
                'recursive',
                'ignored_file',
                'filename_pattern',
            ],
            'kwargs': {
                'description': '✋ Rename audios',
                'help': 'rename audios',
                'usage': '''
                    ${cmd} rename-audios \\
                        --source=${source} \\
                        --extensions=${extensions} \\
                        --recursive=${recursive} \\
                        --ignored-file=${ignored_file} \\
                        --filename-pattern="${filename_pattern}" \\
                        --log-level=${log_level} \\
                        --log-file=${log_file}
                ''',
            },
        },
        'organize': {
            'branches': {
                'grouped': {
                    'arguments': [
                        {'root': {'default': {}, 'choices': {}}},
                        {'source': {'default': {}, 'choices': {}}},
                        {'extensions': {'default': {}, 'choices': {}}},
                        {'recursive': {'default': {}, 'choices': {}}},
                        {'ignored_file': {'default': {}, 'choices': {}}},
                    ],
                    'kwargs': {
                        'description': '✋ Organize files',
                        'help': 'organize files',
                        'usage': '''
                            ${cmd} organize grouped \\
                                --source=${source} \\
                                --extensions=${extensions} \\
                                --recursive=${recursive} \\
                                --ignored-file=${ignored_file} \\
                                --root=${root} \\
                                --log-level=${log_level} \\
                                --log-file=${log_file}
                        ''',
                    },
                },
                'ituned': {
                    'arguments': [
                        'root',
                        'source',
                        'extensions',
                        'recursive',
                        'ignored_file',
                    ],
                    'kwargs': {
                        'description': '✋ Organize files',
                        'help': 'organize files',
                        'usage': '''
                            ${cmd} organize ituned \\
                                --source=${source} \\
                                --extensions=${extensions} \\
                                --recursive=${recursive} \\
                                --ignored-file=${ignored_file} \\
                                --root=${root} \\
                                --log-level=${log_level} \\
                                --log-file=${log_file}
                        ''',
                    },
                },
            },
        },
        'list-repeated': {
            'arguments': [
                'source',
                'extensions',
                'recursive',
                'ignored_file',
                'output',
            ],
            'kwargs': {
                'description': '✋ List repeated audio files by artist and title',
                'help': 'list repeated',
                'usage': '''
                    ${cmd} list-repeated \\
                        --source=${source} \\
                        --extensions=${extensions} \\
                        --recursive=${recursive} \\
                        --ignored-file=${ignored_file} \\
                        --output=${output} \\
                        --log-level=${log_level} \\
                        --log-file=${log_file}
                ''',
            },
        },
        'derive-artworks': {
            'arguments': [
                'source',
                'extensions',
                'recursive',
                'ignored_file',
                'artwork_path',
            ],
            'kwargs': {
                'description': '✋ Derive artworks',
                'help': 'derive artworks',
                'usage': '''
                    ${cmd} derive-artworks \\
                        --source=${source} \\
                        --extensions=${extensions} \\
                        --recursive=${recursive} \\
                        --ignored-file=${ignored_file} \\
                        --artwork-path=${artwork_path} \\
                        --log-level=${log_level} \\
                        --log-file=${log_file}
                ''',
            },
        },
        'display': {
            'arguments': [
                'source',
                'extensions',
                'recursive',
                'ignored_file',
                'fields',
                'page_number',
                'page_size',
                'sort',
                'filter',
                'align',
                'style',
                'data_format',
                'field_type',
                'numbered',
                'output',
            ],
            'kwargs': {
                'description': '✋ Display audios',
                'help': 'display audios',
                'usage': '''
                    ${cmd} display \\
                        --source=${source} \\
                        --extensions=${extensions} \\
                        --recursive=${recursive} \\
                        --ignored-file=${ignored_file} \\
                        --fields=${fields} \\
                        --page-number=${page_number} \\
                        --page-size=${page_size} \\
                        --sort=${sort} \\
                        --filter=${filter} \\
                        --align=${align} \\
                        --style=${style} \\
                        --data-format=${data_format} \\
                        --field-type=${field_type} \\
                        --numbered=${numbered} \\
                        --output=${output} \\
                        --log-level=${log_level} \\
                        --log-file=${log_file}
                ''',
            },
        },
        'export': {
            'arguments': [
                'source',
                'extensions',
                'recursive',
                'ignored_file',
                'fields',
                'field_type',
                'output',
                'itunes_version_plist',
                'itunes_media_folder',
                'track_initial_id',
                'playlist_initial_id',
            ],
            'kwargs': {
                'description': '✋ Export details to file',
                'help': 'export details to file',
                'usage': {
                    FileFormat.NOTE: f'''
                        $cmd export {FileFormat.NOTE} \\
                            --source=$source \\
                            --extensions=$extensions \\
                            --recursive=$recursive \\
                            --ignored-file=$ignored_file \\
                            --fields=$fields \\
                            --field-type=$field_type \\
                            --output=$output \\
                            --log-level=$log_level \\
                            --log-file=$log_file
                    ''',
                    FileFormat.PLIST: f'''
                        $cmd export {FileFormat.PLIST} \\
                            --source=$source \\
                            --extensions=$extensions \\
                            --recursive=$recursive \\
                            --ignored-file=$ignored_file \\
                            --fields=$fields \\
                            --field-type=$field_type \\
                            --itunes-version-plist=$itunes_version_plist \\
                            --itunes-media-folder=$itunes_media_folder \\
                            --track-initial-id=$track_initial_id \\
                            --playlist-initial-id=$playlist_initial_id \\
                            --output=$output \\
                            --log-level=$log_level \\
                            --log-file=$log_file
                    ''',
                },
            },
        },
        'convert': {
            'arguments': {
                'source': {},
                'extensions': {},
                'recursive': {
                    'use_public': False,
                    'args': ['-r'],
                    'kwargs': {
                        'action': argparse.BooleanOptionalAction,
                        'default': True,
                        'help': 'the files or directories you want to process',
                    },
                },
                'ignored_file': {},
                'executer': {},
            },
            'kwargs': {
                'description': '✋ Convert media',
                'help': 'convert media',
                'usage': {
                    'qmc_to_mp3': '''
                        ${cmd} convert \\
                            --source=${music_source_qmc_folder} \\
                            --extensions=${extensions} \\
                            --recursive=${recursive} \\
                            --ignored-file=${ignored_file} \\
                            --executer=${executer} \\
                            --output=${music_source_mp3_folder} \\
                            --log-level=${log_level} \\
                            --log-file=${log_file}
                    ''',
                },
            },
        },
        'generate-script': {
            'arguments': [
                'output',
            ],
            'kwargs': {
                'description': '✋ Generate script',
                'help': 'generate script',
                'usage': '''
                    ${cmd} generate-script \\
                        --output=${output} \\
                        --log-level=${log_level} \\
                        --log-file=${log_file}
                ''',
            },
        },
        'operate': {
            'kwargs': {
                'description': '',
                'help': '',
                'usage': '',
            },
            'branches': {
                'backup': {
                    'arguments': {
                        'source': {
                            'use_public': False,
                            'args': ['--source', '-c'],
                            'kwargs': {
                                'action': 'store',
                                'type': str,
                                'required': True,
                                'help': 'the files or directories you want to process',
                            },
                        },
                        'ignored_file': {
                            'args': ['--ignored-file', '-i'],
                            'kwargs': {
                                'action': 'store',
                                'type': str,
                                'required': False,
                                'default': './ignored.txt',
                                'help': 'ignored files',
                            },
                        },
                    },
                    'kwargs': {
                        'description': '✋ Backup files, directories and so on',
                        'help': 'Backup files, directories and so on',
                        'usage': '''
                            ${cmd} ${action} ${branch} \\
                                --log-level=${log_level} \\
                                --log-file=${log_file}
                        ''',
                    },
                },
                'remove': {
                    'arguments': [
                    ],
                    'kwargs': {
                        'description': '✋ Remove files, directories and so on',
                        'help': 'remove files, directories and so on',
                        'usage': '''
                            ${cmd} operate remove \\
                                --log-level=${log_level} \\
                                --log-file=${log_file}
                        ''',
                    },
                },
                'cleanup': {
                    'arguments': [],
                    'kwargs': {
                        'description': '✋ Clean up directories, backups and so on',
                        'help': 'clean up directories, backups and so on',
                        'usage': '''
                            ${cmd} operate cleanup \\
                                --log-level=${log_level} \\
                                --log-file=${log_file}
                        ''',
                    },
                },
            },
        },
    }

    @staticmethod
    def replace_underline(key):
        return key.lower().replace('_', '-')

    @staticmethod
    def replace_hyphen(key):
        return key.lower().replace('-', '_')

    @classmethod
    def rewrite_key(cls, key):
        units = key.lower().split('.')
        units[-1] = cls.replace_hyphen(units[-1])
        for i in range(len(units[:-1])):
            units[i] = cls.replace_underline(units[i])
        return '.'.join(units)

    @classmethod
    def repack_dict(cls, dict_, rewrite_key=rewrite_key):
        for key in dict_:
            new_key = rewrite_key(key)
            if new_key == key:
                continue
            value = dict_.pop(key)
            dict_[new_key] = value
        return dict_

    @classmethod
    def rewrite_actions(cls):
        cls.repack_dict(cls.PUBLIC_ARGUMENTS, cls.replace_hyphen)
        cls.repack_dict(cls.COMMON_ARGUMENTS, cls.replace_hyphen)
        cls.repack_dict(cls.ACTIONS, cls.replace_underline)
        for action in cls.ACTIONS:
            if 'arguments' in cls.ACTIONS[action]:
                cls.repack_dict(cls.ACTIONS[action]['arguments'], cls.replace_hyphen)
            if 'branches' in cls.ACTIONS[action]:
                cls.repack_dict(cls.ACTIONS[action]['branches'], cls.replace_underline)
                for branch in cls.ACTIONS[action]['branches']:
                    if 'arguments' in cls.ACTIONS[action]['branches'][branch]:
                        cls.repack_dict(
                            cls.ACTIONS[action]['branches'][branch]['arguments'],
                            cls.replace_hyphen,
                        )

        def _process_unit(action, branch, /, render_kwargs={}):
            params = cls.ACTIONS[action]['branches'][branch] if branch else cls.ACTIONS[action]
            if 'arguments' in params:
                params['arguments'].update(copy.deepcopy(cls.COMMON_ARGUMENTS))
                for argument in params['arguments']:
                    use_public = params['arguments'][argument].pop('use_public', False)
                    if use_public:
                        params['arguments'][argument] = copy.deepcopy(cls.PUBLIC_ARGUMENTS[argument])
                    params['arguments'][argument]['args'].insert(
                        0, f'--{cls.replace_underline(argument)}',
                    )
                    params['arguments'][argument]['kwargs']['dest'] = argument
                    
                    type_ = params['arguments'][argument]['kwargs'].get('type', None)
                    action_ = params['arguments'][argument]['kwargs'].get('action', 'store')
                    if 'default' not in params['arguments'][argument]['kwargs']:
                        default = None
                        match type_:
                            case str():
                                default = ''
                            case int():
                                default = 0
                        if default is None and action_ == argparse.BooleanOptionalAction:
                            default = True
                        params['arguments'][argument]['kwargs']['default'] = default
            if 'kwargs' in params:
                if 'usage' not in params['kwargs']:
                    params['kwargs']['usage'] = f'''
                        $cmd {action} {branch} \\
                    ''' if branch else f'''
                        $cmd {action} \\
                    '''
                    for argument in params['arguments']:
                        label = params['arguments'][argument]['args'][0]
                        action_ = params['arguments'][argument]['kwargs'].get('action', 'store')
                        required = params['arguments'][argument]['kwargs'].get('required', False)
                        default = '<INPUT>' if required else params['arguments'][argument]['kwargs']['default']
                        if action_ == argparse.BooleanOptionalAction:
                            no_label = label.replace('--', '--no-')
                            params['kwargs']['usage'] += f'''
                                {label if default else no_label} \\
                            '''
                        else:
                            params['kwargs']['usage'] += f'''
                                {label}={default} \\
                            '''
                    params['kwargs']['usage'] = params['kwargs']['usage'].rstrip().rstrip('\\').rstrip()
                params['kwargs']['usage'] = cls.render_usage(
                    params['kwargs']['usage'],
                    kwargs=render_kwargs,
                )

        for action in cls.ACTIONS:
            _process_unit(action, None)
            if 'branches' in cls.ACTIONS[action]:
                for branch in cls.ACTIONS[action]['branches']:
                    _process_unit(action, branch)

    #@classmethod
    #def nntegrate_default_arguments(cls, action=None, branch=None):
    #    ret = copy.deepcopy(cls.PUBLIC_ARGUMENTS) | copy.deepcopy(cls.COMMON_ARGUMENTS)
    #    prefix, arguments = '', {}
    #    if action:
    #        if branch:
    #            prefix = f'{action}.{branch}.'
    #            arguments = cls.ACTIONS[action]['branches'][branch].get('arguments', {})
    #        else:
    #            prefix = f'{action}.'
    #            arguments = cls.ACTIONS[action].get('arguments', {})
    #    for argument, params in arguments.items():
    #        if prefix:
    #            arguments[f'{prefix}{argument}'] = params
    #    return ret | copy.deepcopy(arguments)
    
    #@classmethod
    #def integrate_plain_defaults(cls, action=None, branch=None):
    #    ret, arguments = {}, cls.integrate_default_arguments(action, branch)
    #    for argument, params in arguments.items():
    #        if 'default' in params['kwargs']:
    #            ret[argument] = params['kwargs']['default']
    #    return ret
    
    @classmethod
    def integrate_default_arguments(cls, action=None, branch=None, with_customized=False):
        original_defaults = {
            argument: params['default']
            for argument, params in (
                copy.deepcopy(cls.PUBLIC_ARGUMENTS) | copy.deepcopy(cls.COMMON_ARGUMENTS)
            ).items()
        }

        customized_defaults = {}
        for _action, action_params in cls.ACTIONS.items():
            if 'arguments' in action_params:
                for argument, argument_params in action_params['arguments']:
                    key = f'{_action}.{argument}'
                    customized_defaults[key] = argument_params['default']
            if 'branches' in action_params:
                for _branch, branch_params in action_params['branches'].items():
                    if 'arguments' in branch_params:
                        for argument, argument_params in branch_params['arguments']:
                            key = f'{_action}.{_branch}.{argument}'
                            customized_defaults[key] = argument_params['default']

        defaults = copy.deepcopy(original_defaults)
        prefix = ''
        if action:
            if branch:
                prefix = f'{action}.{branch}.'
            else:
                prefix = f'{action}.'
        if prefix:
            for argument, default in copy.deepcopy(customized_defaults).items():
                if argument.startswith(prefix):
                    if prefix.count('.') == argument.count('.'):
                        defaults[argument.replace(prefix, '')] = default
        if with_customized:
            defaults = defaults | copy.deepcopy(customized_defaults)

        return defaults


    USAGE = '''
All fields:
${audio_properties}

Special fields:
${special_fields}

Special characters:
${special_characters}

------------------------------------------------------------------------------

Samples of audio file name:

Original  audio file name: "artist${ori_div_char}title.mp3"
Formatted audio file name: "artist ${div_char} title.mp3"
Pattern of filename to rename: "${fnp_delimiter}{artist} ${div_char} ${fnp_delimiter}{title}"

------------------------------------------------------------------------------

Sample in note to import:

# Support annotation.
(1) @[Pop] Vocals/Explosive/English:
1.[x]title：Star Sky, artist：Two Steps From Hell/Thomas Bergersen, album：Battlecry
2.[]歌曲名：Horizon, 歌手名：Janji, 专辑名：Horizon, 分组：a/b/c${grouping_sep}d/e/f
歌曲名：Rise And Fall (DJ版), 歌手名：Camelot, 专辑名：Rise And Fall
[]歌曲名：Drag Me Down, artist：One Direction, 专辑名：Drag Me Down, genre：Electronic
@[Pop] Vocals/ppp/qqq
1. []title：Star Sky, artist：Two Steps From Hell/Thomas Bergersen, album：Battlecry
2.[]歌曲名：Horizon, 歌手名：Janji, 专辑名：Horizon, 分组：a/b/c${grouping_sep}d/e/f

------------------------------------------------------------------------------

Precautions:

    1. Don't contain blank characters in genres and groupings;
    2. Audios in the same group should have a same genre;
    3. In invalid detail line of note.txt file, "," -> "\\" and ":" -> "/".

------------------------------------------------------------------------------

Attention:
    Here is the cache folder, which contains backups and trash under it.
    You should clear the cache when the size is too big.
        ~/.audgod-cache
            ├── backups
            └── trash

------------------------------------------------------------------------------

General steps:

Ready:
    Step.1: Run <clean-up> subcommand to clear repeats, backups, grouped folder, and iTunes related;
    Step.2: Download songs, and make sure that file named with "artist${ori_div_char}title";
    Step.3: Add detail of songs to notes, then grouped.

Process Method 1:
    Step.1: Preprocess notes, until note file not changed, with subcommand <preprocess-notes>;
    Step.2: Fill properties, with subcommand <fill-properties>;
    Step.3: Format properties, with subcommand <format-properties>;
    Step.4: Rename audios, with subcommand <rename-audios>;
    Step.5: Organize grouped files, with subcommand <organize>;
    Step.6: Export note file, with subcommand <export>;
    Step.7: List repeated audios of grouped, with subcommand <list-repeated>;
    Step.8: Organize ituned files, with subcommand <organize>;
    Step.9: Export plist file, with subcommand <export>.

Process Method 2:
    Step.1: Put audios to source folder (e.g. "${music_source_mp3_folder}");
    Step.2: Put note file to local folder (e.g. "${note_file}");
    Step.3: Put ignored file to local folder (e.g. "${ignored_file}");
    Step.4: Run <generate-script> subcommand to generate a shell script (e.g. "${script_file}");
    Step.5: Execute the shell script above.
    Results under folders below:
        "${note_file}"
        "${repeated_file}"
        "${artwork_path}"
        "${music_grouped_folder}"
        "${itunes_media_folder}"
        "${itunes_library_plist}"

------------------------------------------------------------------------------

General commands:

    * Show help information:
        ${cmd} -h/--help

    * Show version of program:
        ${cmd} -v/--version

------------------------------------------------------------------------------
    '''


    def __init__(self, action=None, branch=None, **kwargs):
        self.__action = action
        self.__branch = branch

        self.__default_arguments = self.integrate_default_arguments(
            action=self.action,
            branch=self.branch,
            with_customized=False,
        )

        kwargs = self.default_arguments | kwargs

        # init logger
        self.__logger_options = self.__resolve_logger_options(
            kwargs['log_level'],
            kwargs['log_file'],
        )
        self.__logger = FatalLogger(*self.logger_options)
        eyed3.log.setLevel(logging.ERROR)

        # process first
        self.__fields = [
            self.AudioProperty(x) for x in self.__resolve_fields(
                kwargs['fields'],
                sortify=False,
                reversify=False,
                stringify=False,
            )
        ]

        self.__audsrc_options = self.__resolve_audsrc_options(
            kwargs['source'],
            kwargs['recursive'],
            kwargs['extensions'],
        )

        self.__document = self.abspath(kwargs['document'])
        self.__ignored_file = self.abspath(kwargs['ignored_file'])
        self.__root = self.abspath(kwargs['root'])
        self.__artwork_path = self.abspath(kwargs['artwork_path'])
        self.__output = self.abspath(kwargs['output'])

        self.__data_format = self.DataFormat(kwargs['data_format'])
        self.__filename_pattern = kwargs['filename_pattern']
        self.__field_type = AudioGod.FieldType(kwargs['field_type'])
        self.__properties = self.__resolve_properties(kwargs['properties'])
        
        self.__clauses = ([], {}, {}, [], [])
        self.__clauses_counter = [0, 0, 0, 0, 0, 0]
        self.__sources = ([], [], [], [], [], [])
        self.__ignored_set = set()
        self.__summaries = {}

        self.__display_options = self.__resolve_display_options(
            kwargs['page_number'],
            kwargs['page_size'],
            kwargs['sort'],
            kwargs['filter'],
            kwargs['align'],
            kwargs['numbered'],
            kwargs['style'],
        )

        self.__itunes_options = self.__resolve_itunes_options(
            kwargs['itunes_version_plist'],
            kwargs['itunes_media_folder'],
            kwargs['track_initial_id'],
            kwargs['playlist_initial_id'],
        )

        self.__output_format = self.__resolve_output_format()

        self.__audios_tree = TreeX(
            tree=None,
            deep=False,
            node_class=None,
            identifier=None,
            logger=self.logger,
        )
        self.audios_tree.create_node(
            self.AUDIOS_TREE_ROOT_TAG, self.AUDIOS_TREE_ROOT_NID,
        )

        self.__parse_func = {
            field: getattr(
                self, f'parse_{field}', lambda x: x,
            )
            for field in self.ALL_FIELDS
        }
        def __parse_func(parse_func):
            def __func(*args):
                ret = parse_func(*args)
                return ret
            return __func
        self.__parse_func = {
            field: __parse_func(self.__parse_func[field])
            for field in self.ALL_FIELDS
        }

        self.__format_func = {
            field: getattr(
                self, f'format_{field}', lambda x: x,
            )
            for field in self.ALL_FIELDS
        }
        def __format_func(format_func):
            def __func(*args):
                ret = format_func(*args)
                return ret
            return __func
        self.__format_func = {
            field: __format_func(self.__format_func[field])
            for field in self.ALL_FIELDS
        }

        self.__output_func = {
            field: getattr(
                self,
                f'output_{field}',
                lambda x, output_format=self.FileFormat.NONE: x,
            )
            for field in self.ALL_FIELDS
        }
        def __output_func(output_func):
            def __func(*args):
                ret = output_func(*args)
                if (not isinstance(ret, int)) and (not isinstance(ret, float)) and (not ret):
                    return None
                return ret
            return __func
        self.__output_func = {
            field: __output_func(self.__output_func[field])
            for field in self.ALL_FIELDS
        }

    def __resolve_fields(self, fields, sortify=False, reversify=False, stringify=False):
        fields_ = self.split(
            fields.lower(), ',',
            escaped=True,
            del_blank=True,
            filt_empty=True,
            filt_repeated=True,
            sortify=False,
            reversify=False,
        )
        ret = []
        for field in fields_:
            if field in self.FIELDS.keys():
                ret.extend(self.FIELDS[field])
            else:
                if field not in self.ALL_FIELDS:
                    self.logger.fatal(f'Invalid field <{field}>!')
                    return ret
                ret.append(field)
        ret = list(dict.fromkeys(ret))
        if sortify:
            ret.sort()
        if reversify:
            ret = list(reversed(ret))
        if stringify:
            ret = ','.join(ret)
        return ret

    def __resolve_properties(self, properties):
        ret = self.load_json(properties, {})
        if type(ret) is not dict:
            self.logger.fatal(f'Properties <{ret}> is not a dict type!')
            return ret
        keys = [
            key for key in list(ret.keys()) # type: ignore
            if key != 'default'
        ]
        for key in keys:
            value = ret.pop(key) # type: ignore
            new_keys = self.__resolve_fields(
                key, sortify=True, reversify=False, stringify=False,
            )
            for new_key in new_keys:
                ret[new_key] = value # type: ignore
        for key in ret.keys(): # type: ignore
            value = ret[key] # type: ignore
            if type(value) is not dict:
                self.logger.fatal(f'Value <{value}> is not a dict type!')
                return ret
            if 'sources' not in value:
                self.logger.fatal(f'Lack sources in <{value}>!')
                return ret
            sources = value['sources']
            if type(sources) is not list:
                self.logger.fatal(f'Sources in <{value}> is not a list!')
                return ret
            for i in range(len(sources)):
                sources[i] = self.PropertySource(sources[i])
        return ret

    def __resolve_output_format(self):
        return self.recognize_file_format(self.output)

    def __resolve_logger_options(self, log_level, log_file):
        return (log_level, log_file)

    def __resolve_audsrc_options(
            self,
            source,
            recursive,
            extensions,
        ):
        return (
            self.abspath(source),
            recursive,
            self.split(
                extensions.lower(), ',',
                escaped=True,
                del_blank=True,
                filt_empty=True,
                filt_repeated=True,
                sortify=False,
                reversify=False,
            ),
        )
    
    def __resolve_itunes_options(
            self,
            itunes_version_plist,
            itunes_media_folder,
            track_initial_id,
            playlist_initial_id,
        ):
        return (
            self.abspath(itunes_version_plist),
            self.abspath(itunes_media_folder),
            track_initial_id,
            playlist_initial_id,
        )

    def __resolve_display_options(
            self,
            page_number,
            page_size,
            sort_,
            filter_,
            align_,
            numbered,
            style,
        ):
        fields_to_show = self.fields
        sort_ = self.load_json(sort_, [])
        filter_ = self.load_json(filter_, {})
        align_ = self.load_json(align_, {})
        style = self.DisplayStyle(style)

        # sort
        if type(sort_) is not list:
            self.logger.fatal(f'Sort <{sort_}> is not a list!')
            return
        for i in range(len(sort_)): # type: ignore
            if type(sort_[i]) is not list:
                self.logger.fatal(f'Item <{sort_[i]}> in sort <{sort_}> is not a list!')
                return
            if len(sort_[i]) != 2:
                self.logger.fatal(f'Length of item <{sort_[i]}> in sort <{sort_}> is not 2!')
                return
            if type(sort_[i][1]) is not bool:
                self.logger.fatal(f'Second of item <{sort_[i]}> in sort <{sort_}> is not boolean!')
                return
            sort_[i][0] = self.__resolve_fields( # type: ignore
                sort_[i][0], sortify=False, reversify=False, stringify=True, # type: ignore
            )

        # filter
        if type(filter_) is not dict:
            self.logger.fatal(f'Filter <{filter_}> is not a dict!')
            return
        filter_keys = [
            key for key in list(filter_.keys()) # type: ignore
            if key != '_options'
        ]
        for key in filter_keys:
            new_key = self.__resolve_fields(
                key, sortify=True, reversify=False, stringify=True,
            )
            filter_[new_key] = filter_.pop(key) # type: ignore
        if filter_:
            if '_options' not in filter_.keys():
                self.logger.fatal(f'Lack _options in <{filter_}>!')
                return
            filter_options = filter_['_options']
            if type(filter_options) is not dict:
                self.logger.fatal(f'The _options in <{filter_}> is not dict!')
                return
            if 'relation' not in filter_options:
                self.logger.fatal(f'Lack relation of _options in <{filter_}>!')
                return
            if filter_options['relation'] not in ('and', 'or'):
                self.logger.fatal(f'Invalid relation of _options in <{filter_}>!')
                return
            filter_keys = [
                key for key in list(filter_.keys()) # type: ignore
                if key != '_options'
            ]
            for key in filter_keys:
                value = filter_[key]
                if type(value) is not dict:
                    self.logger.fatal(f'Value <{value}> is not a dict type!')
                    return
                if 'function' not in value:
                    self.logger.fatal(f'Lack function in <{value}>!')
                    return
                if value['function'] not in ('equal', 'search', 'empty'):
                    self.logger.fatal(f'Invalid function in <{value}>!')
                    return
                if value['function'] != 'empty':
                    if 'parameters' not in value:
                        self.logger.fatal(f'Lack parameters in <{value}>!')
                        return
                    if type(value['parameters']) is not list:
                        self.logger.fatal(f'Invalid parameters in <{value}>!')
                        return

        # align
        if type(align_) is not dict:
            self.logger.fatal(f'Align <{align_}> is not a dict!')
            return
        align_keys = list(align_.keys()) # type: ignore
        for key in align_keys:
            new_key = self.__resolve_fields(
                key, sortify=True, reversify=False, stringify=True,
            )
            align_[new_key] = align_.pop(key) # type: ignore
        align_keys = list(align_.keys()) # type: ignore
        for key in align_keys:
            value = align_[key]
            if type(value) is not str:
                self.logger.fatal(f'Invalid type of <{value}>!')
                return
            if re.match(r'^[lcr]:[tmb]$', value) is None:
                self.logger.fatal(f'Invalid format of <{value}>!')
                return

        return (
            page_number,
            page_size,
            sort_,
            filter_,
            fields_to_show,
            align_,
            numbered,
            style,
        )

    @property
    def action(self):
        return self.__action

    @property
    def branch(self):
        return self.__branch

    @property
    def default_arguments(self):
        return self.__default_arguments

    @property
    def logger(self):
        return self.__logger

    @property
    def format_func(self):
        return self.__format_func

    @property
    def parse_func(self):
        return self.__parse_func

    @property
    def output_func(self):
        return self.__output_func

    @property
    def display_options(self):
        return self.__display_options

    @property
    def itunes_options(self):
        return self.__itunes_options

    @property
    def field_type(self):
        return self.__field_type

    @property
    def logger_options(self):
        return self.__logger_options
    
    @property
    def log_level(self):
        return self.logger_options[0]
    
    @property
    def log_file(self):
        return self.logger_options[1]
    
    @property
    def output(self):
        return self.__output

    @property
    def output_format(self):
        return self.__output_format
    
    @output_format.setter
    def output_format(self, value):
        self.__output_format = value
    
    @property
    def document(self):
        return self.__document

    @property
    def ignored_file(self):
        return self.__ignored_file

    @property
    def root(self):
        return self.__root

    @property
    def audios_tree(self):
        return self.__audios_tree

    @property
    def properties(self):
        return self.__properties

    @property
    def audsrc_options(self):
        return self.__audsrc_options
    
    @property
    def source(self):
        return self.audsrc_options[0]

    @property
    def recursive(self):
        return self.audsrc_options[1]

    @property
    def extensions(self):
        return self.audsrc_options[2]

    @property
    def fields(self):
        return self.__fields

    @property
    def data_format(self):
        return self.__data_format

    @property
    def artwork_path(self):
        return self.__artwork_path

    @property
    def filename_pattern(self):
        return self.__filename_pattern

    @property
    def ignored_set(self):
        return self.__ignored_set

    @property
    def summaries(self):
        return self.__summaries
    
    @summaries.setter
    def summaries(self, value):
        self.__summaries = value

    @property
    def invalid_clauses(self):
        return self.__clauses[0]

    @property
    def valid_clauses(self):
        return self.__clauses[1]

    @property
    def repeated_clauses(self):
        return self.__clauses[2]

    @property
    def grouping_clauses(self):
        return self.__clauses[3]

    @property
    def warn_clauses(self):
        return self.__clauses[4]

    @property
    def total_clauses_counter(self) -> int:
        return self.__clauses_counter[0]

    @total_clauses_counter.setter
    def total_clauses_counter(self, value):
        self.__clauses_counter[0] = value

    @property
    def invalid_clauses_counter(self) -> int:
        return self.__clauses_counter[1]

    @invalid_clauses_counter.setter
    def invalid_clauses_counter(self, value):
        self.__clauses_counter[1] = value

    @property
    def valid_clauses_counter(self) -> int:
        return self.__clauses_counter[2]

    @valid_clauses_counter.setter
    def valid_clauses_counter(self, value):
        self.__clauses_counter[2] = value

    @property
    def repeated_clauses_counter(self) -> int:
        return self.__clauses_counter[3]

    @repeated_clauses_counter.setter
    def repeated_clauses_counter(self, value):
        self.__clauses_counter[3] = value

    @property
    def grouping_clauses_counter(self) -> int:
        return self.__clauses_counter[4]

    @grouping_clauses_counter.setter
    def grouping_clauses_counter(self, value):
        self.__clauses_counter[4] = value

    @property
    def warn_clauses_counter(self) -> int:
        return self.__clauses_counter[5]

    @warn_clauses_counter.setter
    def warn_clauses_counter(self, value):
        self.__clauses_counter[5] = value

    @property
    def plain_sources(self):
        ret = []
        for item in self.expand_globbing(self.source, recursive=True):
            if not os.path.exists(item):
                self.logger.warning(f'Source <{item}> not exists!')
                continue
            if os.path.isfile(item):
                ret.append(item)
                continue
            if not os.path.isdir(item):
                self.logger.warning(f'Source <{item}> not a file or directory!')
                continue
            if self.recursive:
                for _root, _dirs, _files in os.walk(item):
                    for _dir in _dirs:
                        ret.append(self.abspath(_root, _dir))
                    for _file in _files:
                        ret.append(self.abspath(_root, _file))
            else:
                ret.extend([
                    self.abspath(item, target)
                    for target in os.listdir(item)
                ])
        return list(dict.fromkeys(ret))

    @property
    def invalid_ext_sources(self):
        return self.__sources[0]

    @property
    def invalid_name_sources(self):
        return self.__sources[1]

    @property
    def omitted_sources(self):
        return self.__sources[2]

    @property
    def ignored_sources(self):
        return self.__sources[3]

    @property
    def matched_sources(self):
        return self.__sources[4]

    @property
    def notmatched_sources(self):
        return self.__sources[5]

    @property
    def concerned_sources(self):
        return list(dict.fromkeys(
            self.invalid_name_sources \
                + self.matched_sources \
                + self.notmatched_sources,
        ))

    @staticmethod
    def load_json(content, default=None) -> list | dict | None:
        def _remove_comments(data):
            comment_tag = '_comment'
            if isinstance(data, dict):
                if comment_tag in data:
                    del data[comment_tag]
                for key in data:
                    data[key] = _remove_comments(data[key])
            elif isinstance(data, list):
                comment_indexes = []
                for i in range(len(data)):
                    if isinstance(data[i], dict):
                        old_len = len(data[i])
                        data[i] = _remove_comments(data[i])
                        new_len = len(data[i])
                        if  old_len > 0 and new_len == 0:
                            comment_indexes.append(i)
                    else:
                        data[i] = _remove_comments(data[i])
                for i in comment_indexes:
                    del data[i]
            return data

        ret = None
        if content:
            ret = _remove_comments(json.loads(content.strip().strip("'")))
        if ret is None:
            ret = default
        return ret

    @staticmethod
    def split(
        s, pattern=None, escaped=False,
        del_blank=True, filt_empty=True, filt_repeated=True,
        sortify=False, reversify=False,
        *args, **kwargs,
    ) -> list:
        if not s:
            return []
        if not pattern:
            return [s]
        if escaped:
            pattern = re.escape(pattern)
        ret = re.split(pattern, s, *args, **kwargs)
        if del_blank:
            ret = [item.strip() for item in ret]
        if filt_empty:
            ret = list(filter(lambda x: x, ret))
        if filt_repeated:
            ret = list(dict.fromkeys(ret))
        if sortify:
            ret.sort()
        if reversify:
            ret = list(reversed(ret))
        return ret

    @staticmethod
    def abspath(path, *paths):
        ret, paths = '', list(filter(lambda x: x, [path] + list(paths)))
        if len(paths) > 0:
            ret = paths[0]
        if len(paths) > 1:
            for path in paths[1:]:
                ret = os.path.join(ret, path)
        if not ret:
            return ret
        return os.path.normpath(os.path.abspath(os.path.expanduser(ret)))

    def rename(self, old, new):
        if not os.path.exists(old):
            self.logger.fatal(f'File {old} not exists!')
            return
        if os.path.exists(new):
            self.remove(new)
        os.rename(old, new)

    def duplicate(self, src, dst):
        if not os.path.exists(src):
            self.logger.fatal(f'File {src} not exists!')
            return
        if os.path.exists(dst):
            self.remove(dst)
        shutil.copy2(src, dst)
    
    @classmethod
    def init_cache(cls):
        os.makedirs(cls.CACHE_DIR, exist_ok=True)
        os.makedirs(cls.TRASH_DIR, exist_ok=True)
        os.makedirs(cls.BACKUPS_DIR, exist_ok=True)

    @staticmethod
    def timestamp():
        return datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')

    @classmethod
    def treat_basename(cls, src, tag=''):
        ret = f'{cls.timestamp()}.{os.path.basename(src)}'
        if tag:
            ret = f'{tag}.{ret}'
        return ret

    @classmethod
    def expand_globbing(cls, *paths, recursive=True):
        ret = []
        for path in paths:
            if not path:
                continue
            if not isinstance(path, (list, tuple)):
                path = [path]
            for item in path:
                item = cls.abspath(item)
                if not item:
                    continue
                targets = glob.glob(item, recursive=recursive)
                if not targets:
                    targets = [item]
                for target in targets:
                    target = cls.abspath(target)
                    if target and target not in ret:
                        ret.append(target)
        return list(dict.fromkeys(ret))

    @staticmethod
    def chmod(path, mode=0o755):
        if path and os.path.exists(path):
            os.chmod(path, mode)

    def remove(self, *paths):
        self.init_cache()
        for item in self.expand_globbing(*paths):
            if os.path.exists(item):
                os.rename(
                    item, os.path.join(
                        self.TRASH_DIR, self.treat_basename(item, 'trash'),
                    ),
                )
            else:
                self.logger.error(f'Remove warning: File {item} not exists!')

    def backup(self, src):
        self.init_cache()
        if os.path.exists(src):
            self.duplicate(
                src, os.path.join(
                    self.BACKUPS_DIR, self.treat_basename(src, 'backup'),
                ),
            )
        else:
            self.logger.error(f'Backup warning: File {src} not exists!')

    @staticmethod
    def transform_utc(timestamp) -> str:
        #return datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%dT%H:%M:%SZ')
        return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%dT%H:%M:%SZ')

    @classmethod
    def current_time(cls) -> str:
        return cls.transform_utc(time.time())

    @staticmethod
    def encode(src) -> str:
        return urllib.parse.quote(src, safe='/', encoding='utf-8', errors=None) # type: ignore

    @classmethod
    def encode_location(cls, location) -> str:
        ret = f'file://{cls.encode(location)}'
        if os.path.isfile(location):
            return ret
        return f'{ret}/'

    @staticmethod
    def escape_characters(content):
        if not content:
            return content
        if isinstance(content, str):
            return content.replace('&', '&#38;')\
                      .replace('<', '&#60;')\
                      .replace('>', '&#62;')\
                      .replace("'", '&#39;')\
                      .replace('"', '&#34;')
        return content

    @staticmethod
    def unify_format(content):
        if content is None:
            return None
        ret = re.sub(
            r'(?P<english>[a-zA-Z]+)',
            lambda x: x.group('english'),
            #lambda x: x.group('english').lower().capitalize(),
            content,
        )
        ret = ret.replace('（', '(')\
                 .replace('）', ')')\
                 .replace('，', ',')\
                 .replace('：', ':')\
                 .replace('；', ';')\
                 .replace('‘', "'")\
                 .replace('’', "'")\
                 .replace('“', '"')\
                 .replace('”', '"')\
                 .replace('！', '!')\
                 .replace('？', '?')\
                 .replace('。', '.')\
                 .replace('【', '[')\
                 .replace('】', ']')\
                 .replace('｜', '|')\
                 .replace('《', '<')\
                 .replace('》', '>')\
                 .replace('——', '-')
        ret = re.sub(r'([\(\[\<\|])', r' \1', ret)
        ret = re.sub(r'([\)\]\>\|:,;\!\?])', r'\1 ', ret)
        ret = re.sub(r'([\&])', r' \1 ', ret)
        # 依据情况而定，看看是否有必要将下面正则激活
        #ret = re.sub(r'\s*&\s*', r' & ', ret)
        ret = re.sub(r'([\(\[])\s+', r'\1', ret)
        ret = re.sub(r'\s+([\)\]])', r'\1', ret)
        ret = re.sub(r'\s+', r' ', ret).strip()
        ret = re.sub(r'([\)\]\>\|]) ([:,;\.\!\?])', r'\1\2', ret)
        return ret

    @staticmethod
    def validate_url(url) -> bool:
        regex = re.compile(
            r'^(?:http|ftp)s?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'
            r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$',
            re.IGNORECASE,
        )
        return re.match(regex, url) is not None

    @staticmethod
    def validate_image(image):
        regex = re.compile(
            r'^.*\.(jp[e]g|png|[gt]if|bmp)$',
            re.IGNORECASE,
        )
        return re.match(regex, image) is not None

    @classmethod
    def recognize_file_format(cls, file):
        if not file:
            return cls.FileFormat.NONE
        _, ext = os.path.splitext(os.path.basename(file))
        ext = ext.lower()
        if ext in ['.json']:
            return cls.FileFormat.JSON
        if ext in ['.md', '.markdown']:
            return cls.FileFormat.MARKDOWN
        if ext in ['.xml', '.plist']:
            return cls.FileFormat.PLIST
        return cls.FileFormat.NOTE

    @classmethod
    def generate_key(cls, artist, title):
        return '{artist}{div}{title}'.format(
            artist=cls.format_artist(artist.strip()),
            div=cls.DIV_CHAR,
            title=cls.format_title(title.strip()),
        ).upper()

    @staticmethod
    def generate_persistent_id() -> str:
        return str(uuid.uuid4()).replace('-', '')[:16].upper()

    @classmethod
    def transform_field_name(cls, field, field_type=FieldType.ORIGINAL):
        match field_type:
            case cls.FieldType.CHINESE:
                return cls.AUDIO_CN_PROPERTIES[field]
            case cls.FieldType.ENGLISH:
                return cls.AUDIO_EN_PROPERTIES[field]
        return field

    @classmethod
    def transform_field_name_synonyms(cls, field):
        field = field.lower()
        if field in cls.AUDIO_CN_PROPERTY_SYNONYMS:
            return cls.AUDIO_CN_PROPERTY_SYNONYMS[field]
        if field in cls.AUDIO_EN_PROPERTY_SYNONYMS:
            return cls.AUDIO_EN_PROPERTY_SYNONYMS[field]
        if field in cls.ALL_FIELDS:
            return field
        return None
    
    @classmethod
    def parse_genre(cls, genre):
        if genre is None:
            return None
        ret = Genre(genre)
        return ret

    @classmethod
    def parse_comments(cls, comments):
        if comments is None:
            return None
        ret = CommentsAccessor(frames.FrameSet())
        ret.set(comments)
        return ret

    @classmethod
    def parse_track_num(cls, track_num):
        ret = [None, None]
        if track_num is None:
            return ret
        value = cls.split(
            track_num, ',',
            escaped=True,
            del_blank=True,
            filt_empty=True,
            filt_repeated=False,
            sortify=False,
            reversify=False,
        )
        if len(value) >= 1:
            ret[0] = int(value[0]) # type: ignore
        if len(value) > 1:
            ret[1] = int(value[1]) # type: ignore
        return ret

    @classmethod
    def format_title(cls, title):
        if title is None:
            return None
        ret = title
        return cls.unify_format(ret)

    @classmethod
    def format_artist(cls, artist):
        if artist is None:
            return None
        ret = cls.unify_format(artist)
        ret = re.sub(r'[、，/,]', r'&', ret) # type: ignore
        ret = re.sub(r'&', r' & ', ret)
        ret = re.sub(r'\s*&\s*', r' & ', ret)
        return ret

    @classmethod
    def format_album(cls, album):
        if album is None:
            return None
        ret = album
        return cls.unify_format(ret)

    @classmethod
    def format_album_artist(cls, album_artist):
        if album_artist is None:
            return None
        return cls.format_artist(album_artist)

    @classmethod
    def format_genre(cls, genre):
        if genre is None:
            return None
        ret = genre
        return ret

    @classmethod
    def format_grouping(cls, grouping):
        if grouping is None:
            return None
        grouping = re.sub(r'(\s*\/\s*)+', r'/', grouping)
        pattern = r'(?:\s*\/\s*)*\s*{0}\s*(?:\s*\/\s*)*'.format(
            re.escape(cls.GROUPING_SEPARATOR),
        )
        grouping = re.sub(pattern, cls.GROUPING_SEPARATOR, grouping)
        grouping = re.sub(r'(?:^\/+|\/+$)', r'', grouping)
        groups = cls.split(
            grouping,
            cls.GROUPING_SEPARATOR,
            escaped=True,
            del_blank=True,
            filt_empty=True,
            filt_repeated=False,
            sortify=False,
            reversify=False,
        )
        return cls.GROUPING_SEPARATOR.join(groups)

    @classmethod
    def format_comments(cls, comments):
        if comments is None:
            return None
        ret = comments
        return ret

    @classmethod
    def format_track_num(cls, track_num):
        if track_num is None:
            return None
        ret = track_num
        return ret

    @classmethod
    def format_artwork(cls, artwork):
        if artwork is None:
            return None
        ret = artwork
        return ret

    @classmethod
    def output_title(cls, title, output_format=FileFormat.NONE):
        if not title:
            return ''
        ret = title
        if cls.FileFormat.PLIST.eq(output_format):
            ret = cls.escape_characters(ret)
        return ret

    @classmethod
    def output_album(cls, album, output_format=FileFormat.NONE):
        if not album:
            return ''
        ret = album
        if cls.FileFormat.PLIST.eq(output_format):
            ret = cls.escape_characters(ret)
        return ret

    @classmethod
    def output_album_artist(cls, album_artist, output_format=FileFormat.NONE):
        if not album_artist:
            return ''
        ret = album_artist
        if cls.FileFormat.PLIST.eq(output_format):
            ret = cls.escape_characters(ret)
        return ret

    @classmethod
    def output_artist(cls, artist, output_format=FileFormat.NONE):
        if not artist:
            return ''
        ret = artist
        if cls.FileFormat.PLIST.eq(output_format):
            ret = cls.escape_characters(ret)
        return ret

    @classmethod
    def output_genre(cls, genre, output_format=FileFormat.NONE):
        if not genre:
            return ''
        ret = genre
        if isinstance(genre, Genre):
            ret = genre.name
        if cls.FileFormat.PLIST.eq(output_format):
            ret = cls.escape_characters(ret)
        return ret

    @classmethod
    def output_grouping(cls, grouping, output_format=FileFormat.NONE):
        if not grouping:
            return ''
        ret = grouping
        return ret

    @classmethod
    def output_bit_rate(cls, bit_rate, output_format=FileFormat.NONE):
        if not bit_rate:
            return ''
        if isinstance(bit_rate, tuple):
            bit_rate = bit_rate[1]
        if output_format in [cls.FileFormat.NONE, cls.FileFormat.PLIST]:
            return bit_rate
        return f'{bit_rate} kb/s'

    @classmethod
    def output_sample_freq(cls, sample_freq, output_format=FileFormat.NONE):
        if not sample_freq:
            return ''
        return sample_freq

    @classmethod
    def output_comments(cls, comments, output_format=FileFormat.NONE):
        if not comments:
            return ''
        if isinstance(comments, CommentsAccessor):
            ret = ''
            for i in range(len(comments)):
                ret += comments[i].text
                if i < len(comments) - 1:
                    ret += '\n'
            return ret
        return comments

    @classmethod
    def output_track_num(cls, track_num, output_format=FileFormat.NONE):
        if not track_num:
            return ''
        if isinstance(track_num, tuple):
            return str(track_num)
        return track_num

    @classmethod
    def output_artwork(cls, artwork, output_format=FileFormat.NONE):
        if not artwork:
            return ''
        return artwork

    @classmethod
    def output_duration(cls, duration, output_format=FileFormat.NONE):
        if not duration:
            duration = 0.0
        match output_format:
            case cls.FileFormat.NONE:
                return duration
            case cls.FileFormat.PLIST:
                return int(round(duration, 3) * 1000)
        s = duration
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)
        return '{:02d}:{:02d}:{:02d}'.format(
            int(h), int(m), int(s),
        )

    @classmethod
    def output_size(cls, size, output_format=FileFormat.NONE):
        if not size:
            return '0'
        if output_format in [cls.FileFormat.NONE, cls.FileFormat.PLIST]:
            return size
        suffix='B'
        for unit in ['','K','M','G','T','P','E','Z']:
            if abs(size) < 1024.0:
                return '%3.1f%s%s' % (size, unit, suffix)
            size /= 1024.0
        return '%.1f%s%s' % (size, 'Y', suffix)

    @classmethod
    def output_mtime(cls, mtime, output_format=FileFormat.NONE):
        if not mtime:
            return ''
        if cls.FileFormat.PLIST.eq(output_format):
            return cls.transform_utc(mtime)
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime))

    def __generate_key_by_filename(self, source):
        if not self.__check_name(source):
            self.logger.fatal(f'Invalid name of audio <{source}>!')
            return
        name, _ = os.path.splitext(os.path.basename(source))
        if name.count(self.DIV_CHAR) == 1:
            return self.generate_key(
                *self.split(
                    name, self.DIV_CHAR, escaped=True,
                    del_blank=False, filt_empty=False, filt_repeated=False,
                    sortify=False, reversify=False,
                ),
            )
        return self.generate_key(
            *self.split(
                name, self.ORI_DIV_CHAR, escaped=True,
                del_blank=False, filt_empty=False, filt_repeated=False,
                sortify=False, reversify=False,
            ),
        )

    def __fetch_from_outside(self, audio, field):
        format_ = self.format_func[field]
        parse_ = self.parse_func[field]
        default = self.__resolve_properties(
            self.default_arguments['properties'],
        )['default'] # type: ignore
        sources = self.properties.get('default', {}).get( # type: ignore
            'sources', default['sources'],
        )
        if field in self.properties.keys(): # type: ignore
            sources = self.properties[field].get('sources', sources) # type: ignore
        ret = self.properties.get('default', {}).get( # type: ignore
            'value', default['value'],
        )
        for source in sources:
            match source:
                case self.PropertySource.COMMAND:
                    if field in self.properties.keys(): # type: ignore
                        _value = self.properties[field].get('value', None) # type: ignore
                        if _value is not None:
                            ret = _value
                            break
                case self.PropertySource.FILE:
                    key = self.__generate_key_by_filename(audio)
                    _value = self.valid_clauses.get(key, {}).get(field, None)
                    if _value is not None:
                        ret = _value
                        break
                case self.PropertySource.DIRECTORY:
                    _value = dirname = os.path.dirname(audio)
                    match field:
                        case self.AudioProperty.GENRE:
                            _value = os.path.basename(dirname)
                        case self.AudioProperty.GROUPING:
                            _value = re.sub(
                                r'^%s/+' % (
                                    re.escape(re.sub(r'/+$', r'', self.root)),
                                ),
                                r'',
                                _value,
                            )
                    ret = _value
                    break
        return None if ret is None else format_(parse_(ret))

    # Use AudioProperty type field here, you won't check field parameter.
    def save(self, audio_object, field, value, formatted=False):
        if value is None:
            return
        if formatted:
            value = self.format_func[field](value)
        match field:
            case self.AudioProperty.COMMENTS:
                audio_object.tag.comments.set(value)
            case _ if field in self.ZIP_FIELDS:
                comments = audio_object.tag.comments
                if comments is not None:
                    comments = ''.join([comment.text for comment in comments])
                comments = self.load_json(comments, {})
                comments[field] = value # type: ignore
                audio_object.tag.comments.set(json.dumps(comments))
                if self.AudioProperty.ARTWORK.eq(field):
                    _, value = value
                    if self.validate_url(value):
                        audio_object.tag.images.set(
                            type_=3,
                            img_data=None,
                            mime_type=None,
                            img_url=value,
                        )
                    else:
                        valid = self.validate_image(value) and (
                                    os.path.isfile(value) or (
                                        (not self.artwork_path) and \
                                        os.path.isfile(self.abspath(
                                            self.artwork_path, value,
                                        ))
                                    )
                                )
                        if valid:
                            _, ext = os.path.splitext(os.path.basename(value))
                            audio_object.tag.images.set(
                                type_=3,
                                img_data=open(value, 'rb').read(),
                                mime_type=f'image/{ext[1:].lower()}',
                            )
                        else:
                            self.logger.fatal(
                                'Audio <{name}> has invalid artwork "{value}"'.format(
                                    name=audio_object.tag.file_info.name,
                                    value=value,
                                ),
                            )
                            return
            case _:
                setattr(audio_object.tag, field, value)
        audio_object.tag.save(version=eyed3.id3.ID3_V2_4, encoding='utf-8') # type: ignore

    # Use AudioProperty type field here, you won't check field parameter.
    def fetch(self, audio_object, field):
        ret, filename = None, audio_object.tag.file_info.name
        match field:
            case AudioGod.AudioProperty.GENRE:
                if audio_object.tag.genre is not None:
                    ret = audio_object.tag.genre.name
            case AudioGod.AudioProperty.TRACK_NUM:
                ret = audio_object.tag.track_num
            case AudioGod.AudioProperty.DURATION:
                ret = audio_object.info.time_secs
            case AudioGod.AudioProperty.MTIME:
                ret = audio_object.tag.file_info.mtime
            case AudioGod.AudioProperty.SIZE:
                ret = audio_object.info.size_bytes
            case AudioGod.AudioProperty.NAME:
                ret = os.path.basename(filename)
            case AudioGod.AudioProperty.PATH:
                ret = os.path.dirname(filename)
            case AudioGod.AudioProperty.COMMENTS:
                ret = audio_object.tag.comments
            case _ if field in self.ZIP_FIELDS:
                comments = audio_object.tag.comments
                if comments:
                    comments = ''.join([comment.text for comment in comments])
                ret = self.load_json(comments, {}).get(field, None) # type: ignore
                match field:
                    case AudioGod.AudioProperty.ARTWORK:
                        if len(audio_object.tag.images) == 0 and not ret:
                            ret = None
                        else:
                            ret = (len(audio_object.tag.images), ret if ret else '')
            case _:
                if hasattr(audio_object.tag, field):
                    ret = getattr(audio_object.tag, field)
                elif hasattr(audio_object.info, field):
                    ret = getattr(audio_object.info, field)
                elif hasattr(audio_object.tag.file_info, field):
                    ret = getattr(audio_object.tag.file_info, field)
        return ret

    def fetchx(self, audio_object, field,
               formatted=False, output_format=FileFormat.NONE, default=None):
        ret = self.fetch(audio_object, field)
        if ret is not None:
            if formatted:
                ret = self.format_func[field](ret)
            if self.FileFormat.NONE.ne(output_format):
                ret = self.output_func[field](ret, output_format)
        if default is not None and not ret:
            ret = default
        return ret

    def __load_ignored(self):
        if not self.ignored_file:
            return
        if not os.path.exists(self.ignored_file):
            return
        with open(self.ignored_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                for item in self.expand_globbing(line, recursive=True):
                    self.ignored_set.add(item)

    def __generate_key_by_properties(self, properties):
        if self.AudioProperty.ARTIST not in properties:
            self.logger.fatal(f'"Artist" not in <{properties}>!')
            return
        if self.AudioProperty.TITLE not in properties:
            self.logger.fatal(f'"Title" not in <{properties}>!')
            return
        return self.generate_key(
            properties[self.AudioProperty.ARTIST],
            properties[self.AudioProperty.TITLE],
        )

    def __transform_summaries_to_clauses(self):
        for grouping in self.summaries:
            genre, items = self.summaries[grouping]
            for item in items:
                properties = {
                    self.AudioProperty.GENRE: genre,
                    self.AudioProperty.GROUPING: grouping,
                }
                properties.update({
                    field: item[field][2]
                    for field in item
                })
                key = self.__generate_key_by_properties(properties)
                if key not in self.valid_clauses:
                    self.valid_clauses[key] = properties
                else:
                    ori_grouping = self.valid_clauses[key][self.AudioProperty.GROUPING]
                    self.valid_clauses[key].update(properties)
                    self.valid_clauses[key][self.AudioProperty.GROUPING] = '{ori}{sep}{new}'.format(
                        ori=ori_grouping,
                        sep=self.GROUPING_SEPARATOR,
                        new=grouping,
                    )

    def __analysis_note(self):
        grouping_pattern = r'^\s*(?:\s*\(\s*(?:\s*[0-9]\s*)+\s*\)\s*)?\s*@\s*\[\s*((?:\s*\S\s*)+)\s*\]\s*((?:\s*[^:：\s]\s*)+)[:：]?\s*$'
        fields_pattern = '|'.join(
            list(self.AUDIO_CN_PROPERTIES.keys()) + \
            list(self.AUDIO_EN_PROPERTY_SYNONYMS.keys()) + \
            list(self.AUDIO_CN_PROPERTY_SYNONYMS.keys()),
        )
        detail_pattern = \
                r'^(?:(?:(?:\s*[0-9]\s*)+\.\s*)?(?:\s*\[\s*[a-zA-Z]?\s*\]\s*)?)?(?:\s*[,，;；]+\s*)?\s*({0})\s*[:：]+((?:\s*\S\s*)+?)((?:\s*[,，;；]+\s*(?:{0})\s*[:：]+(?:\s*\S\s*)+)*)$'.format(
            fields_pattern,
        )
        warn_pattern = r'(?:\s*[,，;；]+\s*)+(?:(?:\s*\S\s*)+)\s*[:：]+(?:\s*\S\s*)+'

        with open(self.document, 'r', encoding='utf-8') as f:
            keys, (genre, grouping) = {}, ('', '')
            for line_number, line in enumerate(f, start=1):
                if not line.strip():
                    continue
                if re.match(r'^\s*#+', line, re.IGNORECASE) is not None:
                    continue
                self.total_clauses_counter += 1
                line_with_no, invalid_info = f'&{line_number}: {line}'.strip(), 'not matched'
                # grouping line
                grouping_match = re.match(grouping_pattern, line, re.IGNORECASE)
                if grouping_match is not None:
                    genre, grouping = tuple(map(
                        lambda x: x.strip(), grouping_match.groups(),
                    ))
                    genre = self.format_func[self.AudioProperty.GENRE](genre)
                    grouping = self.format_func[self.AudioProperty.GROUPING](grouping)
                    if grouping and grouping in self.summaries:
                        genre, grouping = '', ''
                        invalid_info = 'grouping already exists'
                    if grouping:
                        self.grouping_clauses.append(line_with_no)
                        self.grouping_clauses_counter += 1
                        continue
                # detail line
                detail_match = re.match(detail_pattern, line, re.IGNORECASE)
                if grouping and detail_match is not None:
                    valid, repeated = True, False
                    curr_key, properties = '', {}
                    temp_line = line
                    while True:
                        temp_match = re.match(detail_pattern, temp_line, re.IGNORECASE)
                        if not temp_match:
                            break
                        temp_line = temp_match.group(3)
                        if not temp_line:
                            temp_line = ''
                        key, value = tuple(map(
                            lambda x: x.strip(), temp_match.groups()[:2],
                        ))
                        if re.search(warn_pattern, value, re.IGNORECASE) is not None:
                            self.warn_clauses.append(line_with_no)
                            self.warn_clauses_counter += 1
                        field = self.transform_field_name_synonyms(key)
                        if not field:
                            valid, invalid_info = False, 'invalid field name'
                            break
                        if field in properties:
                            valid, invalid_info = False, 'duplicate field existed'
                            break
                        properties[field] = self.format_func[field](value)
                    if valid:
                        for field in self.NOTE_FIELDS:
                            if field not in properties:
                                valid, invalid_info = False, 'lack note fields'
                                break
                    if valid:
                        curr_key = self.__generate_key_by_properties(properties)
                        if curr_key not in keys:
                            keys[curr_key] = set([genre])
                        else:
                            keys[curr_key].add(genre)
                            if len(keys[curr_key]) > 1:
                                valid, invalid_info = False, 'more than one genres for one detail item'
                            repeated = True
                    if valid:
                        if grouping not in self.summaries:
                            self.summaries[grouping] = (genre, [properties])
                        else:
                            _, items = self.summaries[grouping]
                            if curr_key in [self.__generate_key_by_properties(x) for x in items]:
                                valid, invalid_info = False, 'duplicate detail items under same grouping'
                            else:
                                items.append(properties)
                    if valid:
                        if repeated:
                            if curr_key not in self.repeated_clauses:
                                self.repeated_clauses[curr_key] = [line_with_no]
                            else:
                                self.repeated_clauses[curr_key].append(line_with_no)
                            self.repeated_clauses_counter += 1
                        self.valid_clauses_counter += 1
                        continue
                self.invalid_clauses.append((line_with_no, invalid_info))
                self.invalid_clauses_counter += 1

        for grouping in self.summaries:
            genre, items = self.summaries[grouping]
            for i, properties in enumerate(items):
                items[i] = self.__repack_audio_properties(properties)

        self.__transform_summaries_to_clauses()
        
        self.logger.warning(f'\n{"#"*78}\n')
        self.logger.warning(
            'Total Clauses:    {total}\n\n'
            'Valid Clauses:    {valid}\n'
            'Grouping Clauses: {grouping}\n'
            'Warn Clauses:     {warn}\n'
            'Repeated Clauses: {repeated}\n'
            'Invalid Clauses:  {invalid}\n'.format(
                total=self.total_clauses_counter,
                valid=self.valid_clauses_counter,
                grouping=self.grouping_clauses_counter,
                warn=self.warn_clauses_counter,
                repeated=self.repeated_clauses_counter,
                invalid=self.invalid_clauses_counter,
            )
        )
        if len(self.warn_clauses) > 0:
            self.logger.warning('\nWarn Clauses:')
            for item in self.warn_clauses:
                self.logger.warning(f'{item}')
        if len(self.invalid_clauses) > 0:
            self.logger.warning('\nInvalid Clauses:')
            for item in self.invalid_clauses:
                self.logger.warning(f'\t{item[0]}\n\t{item[1]}')
        if len(self.repeated_clauses) > 0:
            self.logger.warning('\nRepeated Clauses:')
            for key in self.repeated_clauses:
                self.logger.warning('\t{key}: [{repeated}]'.format(
                    key=key,
                    repeated='｜'.join(self.repeated_clauses[key]),
                ))

    def import_(self):
        file_format = self.recognize_file_format(self.document)
        if self.FileFormat.NONE.eq(file_format):
            self.logger.fatal(f'Invalid source file <{self.document}>.')
            return
        getattr(self, f'_import_{file_format}')()

    def _import_note(self):
        self.__analysis_note()

    def _import_json(self):
        pass

    def _import_markdown(self):
        pass

    _import_md = _import_markdown

    def _import_plist(self):
        pass

    _import_xml = _import_plist

    def __load_properties_from_file(self):
        if not os.path.exists(self.document):
            self.logger.fatal(f'Source file <{self.document}> not exists!')
            return
        self.import_()

    def __check_source(self, source):
        _source = source
        while True:
            if re.match(r'^/*$', _audio) is not None:
                break
            if _audio in self.ignored_set or _source+'/' in self.ignored_set:
                return self.SourceType.IGNORED
            _audio = os.path.dirname(_audio)

        if os.path.basename(source) == '.DS_Store':
            return self.SourceType.OMITTED
        if os.path.islink(source):
            return self.SourceType.OMITTED
        if not os.path.isfile(source):
            return self.SourceType.OMITTED

        if not self.__check_extension(source):
            return self.SourceType.INVALID_EXT
        if not self.__check_name(source):
            return self.SourceType.INVALID_NAME

        return self.SourceType.VALID

    def __load_sources(self, matched=False):
        self.__load_ignored()

        for source in self.plain_sources:
            self.logger.debug(f'Loading <{source}> ...')
            _type = self.__check_source(source)
            match _type:
                case self.SourceType.INVALID_EXT:
                    self.invalid_ext_sources.append(source)
                    self.logger.debug(self.SourceType.INVALID_EXT)
                    continue
                case self.SourceType.INVALID_NAME:
                    self.invalid_name_sources.append(source)
                    self.logger.debug(self.SourceType.INVALID_NAME)
                    continue
                case self.SourceType.OMITTED:
                    self.omitted_sources.append(source)
                    self.logger.debug(self.SourceType.OMITTED)
                    continue
                case self.SourceType.IGNORED:
                    self.ignored_sources.append(source)
                    self.logger.debug(self.SourceType.IGNORED)
                    continue
            key = self.__generate_key_by_filename(source)
            if key in self.valid_clauses:
                self.matched_sources.append(source)
                self.logger.debug(self.SourceType.MATCHED)
            else:
                self.notmatched_sources.append(source)
                self.logger.debug(self.SourceType.NOTMATCHED)

        self.logger.warning(f'\n{"#"*78}\n')

        self.logger.warning(
            'Total Sources:   {total}\n\n'
            'Invalid Sources: {invalid} '
            '(Invalid Extension: {inv_ext}, Invalid Name: {inv_name})\n'
            'Omitted Sources: {omitted}\n'
            'Ignored Sources: {ignored}\n'
            'Valid Sources:   {valid}{match_detail}'.format(
                total=len(self.invalid_ext_sources) \
                    + len(self.invalid_name_sources) \
                    + len(self.omitted_sources) \
                    + len(self.ignored_sources) \
                    + len(self.matched_sources) \
                    + len(self.notmatched_sources),
                invalid=len(self.invalid_ext_sources) + len(self.invalid_name_sources),
                inv_ext=len(self.invalid_ext_sources),
                inv_name=len(self.invalid_name_sources),
                omitted=len(self.omitted_sources),
                ignored=len(self.ignored_sources),
                valid=len(self.matched_sources) + len(self.notmatched_sources),
                match_detail='\n' if not matched else ' (Matched: {matched}, NotMatched: {notmatched})\n'.format(
                    matched=len(self.matched_sources),
                    notmatched=len(self.notmatched_sources),
                ),
            )
        )

        if False and len(self.omitted_sources) > 0:
            self.logger.warning('\nOmitted Sources:')
            for source in self.omitted_sources:
                self.logger.warning(f'\t{source}')
        if False and len(self.ignored_sources) > 0:
            self.logger.warning('\nIgnored Sources:')
            for source in self.ignored_sources:
                self.logger.warning(f'\t{source}')
        if len(self.invalid_ext_sources) > 0:
            self.logger.warning('\nInvalid Extension Sources:')
            for source in self.invalid_ext_sources:
                self.logger.warning(f'\t{source}')
        if len(self.invalid_name_sources) > 0:
            self.logger.warning('\nInvalid Name Sources:')
            for source in self.invalid_name_sources:
                self.logger.warning(f'\t{source}')
        if matched and len(self.notmatched_sources) > 0:
            self.logger.warning('\nNot Matched Sources:')
            for source in self.notmatched_sources:
                self.logger.warning(f'\t{source}')

    def __repack_audio_properties(self, properties):
        ret = {}
        for field, value in properties.items():
            field_name = self.transform_field_name(field, self.field_type)
            type_ = self.AUDIO_PROPERTY_TYPES[field]
            ret[field] = (field_name, type_, value)
        return ret

    def __gain_audio_properties(self, audio_object):
        ret = {}
        for field in self.fields:
            value = self.fetchx(
                audio_object,
                field,
                formatted=True,
                output_format=self.output_format,
            )
            if value is None:
                continue
            ret[field] = value
        return self.__repack_audio_properties(ret)

    def __prime_audio(self, audio):
        audio_object = eyed3.load(audio)
        if audio_object is None:
            self.logger.fatal(f'Invalid audio <{audio}>!')
            return None
        if audio_object.tag is None:
            audio_object.initTag()
            audio_object.tag.save() # type: ignore
        return audio_object

    def __fill_audios_tree(self) -> None:
        self.__load_sources(matched=False)

        _, _, track_initial_id, playlist_initial_id = self.itunes_options
        track_id, audios = track_initial_id, self.concerned_sources

        for audio in audios:
            track_persistent_id = self.generate_persistent_id()
            audio_object = self.__prime_audio(audio)
            genre = self.fetchx(
                audio_object,
                self.AudioProperty.GENRE,
                formatted=True,
                default=self.DEFAULT_GENRE,
            )
            grouping = self.fetchx(
                audio_object,
                self.AudioProperty.GROUPING,
                formatted=True,
                default=self.DEFAULT_GROUPING,
            )
            for group in self.split(
                grouping, self.GROUPING_SEPARATOR, escaped=True,
                del_blank=True, filt_empty=True, filt_repeated=True,
                sortify=False, reversify=False,
            ):
                tags = self.split(
                    group, r'/', escaped=True,
                    del_blank=True, filt_empty=True, filt_repeated=False,
                    sortify=False, reversify=False,
                )
                if not tags:
                    continue
                tags = [self.AUDIOS_TREE_ROOT_TAG] + tags
                subtree = TreeX(logger=self.logger)
                last_nid = self.AUDIOS_TREE_ROOT_NID
                last_tag = parent_tag = ''
                for i, tag in enumerate(tags):
                    nid = self.generate_persistent_id()
                    parent, node_type = last_nid, self.AudiosTreeNodeType.FOLDER
                    if i == 0:
                        nid = self.AUDIOS_TREE_ROOT_NID
                        parent, node_type = None, self.AudiosTreeNodeType.ROOT
                    else:
                        if last_tag:
                            parent_tag += f'{last_tag}'
                        if i == len(tags) - 1:
                            node_type = self.AudiosTreeNodeType.PLAYLIST
                        else:
                            if last_tag:
                                parent_tag += '/'
                        last_tag = tag
                    subtree.create_node(
                        tag, nid, parent=parent,
                        data=[
                            node_type,
                            -1,
                            nid,
                            genre if i == len(tags)-1 else '',
                            re.sub(r'[^/]+/$', r'', parent_tag).rstrip('/'),
                            '',
                        ],
                    )
                    last_nid = nid
                subtree.create_node(
                    audio,
                    self.generate_persistent_id(),
                    parent=last_nid,
                    data=[
                        self.AudiosTreeNodeType.TRACK,
                        track_id,
                        track_persistent_id,
                        genre,
                        group,
                        self.__gain_audio_properties(audio_object),
                    ],
                )
                self.audios_tree.perfect_merge(self.AUDIOS_TREE_ROOT_NID, subtree, deep=False)
            track_id += 1

        playlist_id = playlist_initial_id
        for node in self.audios_tree.all_nodes():
            if node.is_root():
                continue
            node_type = node.data[0]
            if self.AudiosTreeNodeType.TRACK.eq(node_type):
                continue
            node.data[1] = playlist_id
            playlist_id += 1

        for node in self.audios_tree.all_nodes():
            parent = self.audios_tree.parent(node.identifier)
            if parent is None:
                continue
            if parent.is_root():
                continue
            node_type = node.data[0]
            if node_type in [self.AudiosTreeNodeType.TRACK, self.AudiosTreeNodeType.ROOT]:
                continue
            node.data[5] = parent.identifier

    def __check_extension(self, source):
        _, ext = os.path.splitext(os.path.basename(source))
        return ext[1:].lower() in self.extensions

    @staticmethod
    def __check_name(source):
        name, _ = os.path.splitext(os.path.basename(source))
        name = name.strip()
        if not name:
            return False
        if name.count(AudioGod.DIV_CHAR) > 1:
            return False
        if name.count(AudioGod.DIV_CHAR) == 1 and (name[0] == AudioGod.DIV_CHAR or name[-1] == AudioGod.DIV_CHAR):
            return False
        if name.count(AudioGod.DIV_CHAR) == 0:
            if name.count(AudioGod.ORI_DIV_CHAR) != 1:
                return False
            if name[0] == AudioGod.ORI_DIV_CHAR or name[-1] == AudioGod.ORI_DIV_CHAR:
                return False
        return True

    def __fill_audio_properties(self):
        audios = self.concerned_sources
        filled_count = 0
        self.logger.warning(f'\n{"#"*78}\n')
        for audio in audios:
            self.logger.debug(f'Filling <{audio}> ...')
            filled, audio_object = False, self.__prime_audio(audio)
            for field in self.fields:
                property_ = self.__fetch_from_outside(audio, field)
                if property_ is not None:
                    filled = True
                    self.save(audio_object, field, property_, True)
                    self.logger.debug(f'Field <{field}> assigned!')
            if filled:
                filled_count += 1
                self.logger.debug(f'Audio <{audio}> filled!\n')
        self.logger.warning(
            'Audios To Fill: {total}, Filled Audios: {filled}\n'.format(
                total=len(audios),
                filled=filled_count,
            )
        )

    @log_decorator
    def fill_properties(self):
        self.__load_properties_from_file()
        self.__load_sources(matched=True)
        self.__fill_audio_properties()

    @log_decorator
    def format_properties(self):
        self.__load_sources(matched=False)
        audios = self.concerned_sources
        self.logger.warning(f'\n{"#"*78}\n')
        for audio in audios:
            self.logger.debug(f'Formatting <{audio}> ...')
            audio_object = self.__prime_audio(audio)
            for field in self.fields:
                property_ = self.fetchx(audio_object, field, formatted=True)
                if property_ is not None:
                    self.save(audio_object, field, property_, True)
        self.logger.warning(f'Formatted Audios: {len(audios)}\n')

    @log_decorator
    def rename_audios(self):
        self.__load_sources(matched=False)
        audios = self.concerned_sources
        for audio in audios:
            audio_object = self.__prime_audio(audio)
            _old = os.path.basename(audio)
            _, ext = os.path.splitext(_old)
            _new = self.FilenamePatternTemplate(self.filename_pattern).safe_substitute({
                field: self.fetchx(
                    audio_object, field, formatted=True,
                ) for field in self.ALL_FIELDS
            }) + ext.lower()
            if _old == _new:
                continue
            _path = os.path.dirname(audio)
            self.rename(self.abspath(_path, _old), self.abspath(_path, _new))

    @log_decorator
    def derive_artworks(self):
        self.__load_sources(matched=False)
        audios = self.concerned_sources
        for audio in audios:
            _name, _ = os.path.splitext(os.path.basename(audio))
            _path = os.path.dirname(audio)
            if self.artwork_path:
                _path = self.artwork_path
            audio_object = self.__prime_audio(audio)
            if not audio_object:
                continue
            if not audio_object.tag:
                continue
            if not audio_object.tag.images:
                continue
            for i, image in enumerate(audio_object.tag.images):
                image_file = self.abspath(_path, _name)
                if len(audio_object.tag.images) > 1:
                    image_file += f'@{i}'
                image_file += '.jpg'
                self.backup(image_file)
                with open(image_file, 'wb') as f:
                    f.write(image.image_data)

    @log_decorator
    def organize(self):
        pass

    @log_decorator
    def organize__ituned(self):
        if not self.root:
            self.logger.fatal('Invalid root!')
            return
        self.__load_sources(matched=False)
        audios = self.concerned_sources
        for audio in audios:
            audio_object = self.__prime_audio(audio)
            artist = self.fetchx(audio_object, self.AudioProperty.ARTIST, formatted=True)
            if not artist:
                self.logger.fatal(f'Invalid artist of <{audio}>')
                return
            album = self.fetchx(audio_object, self.AudioProperty.ALBUM, formatted=True)
            if not album:
                self.logger.fatal(f'Invalid album of <{audio}>')
                return
            newname = self.abspath(self.root, artist, album, os.path.basename(audio))
            if newname != audio:
                if not os.path.exists(newname):
                    os.makedirs(os.path.dirname(newname), exist_ok=True)
                    self.duplicate(audio, newname)
                else:
                    current_grouping = self.fetchx(
                        audio_object, self.AudioProperty.GROUPING, formatted=True,
                    )
                    current_groups = self.split(
                        current_grouping,
                        self.GROUPING_SEPARATOR,
                        escaped=True,
                        del_blank=True,
                        filt_empty=True,
                        filt_repeated=True,
                        sortify=False,
                        reversify=False,
                    )
                    existed_object = self.__prime_audio(newname)
                    existed_grouping = self.fetchx(
                        existed_object, self.AudioProperty.GROUPING, formatted=True,
                    )
                    existed_groups = self.split(
                        existed_grouping,
                        self.GROUPING_SEPARATOR,
                        escaped=True,
                        del_blank=True,
                        filt_empty=True,
                        filt_repeated=True,
                        sortify=False,
                        reversify=False,
                    )
                    if not bool(set(current_groups) & set(existed_groups)):
                        self.save(
                            existed_object,
                            self.AudioProperty.GROUPING,
                            self.GROUPING_SEPARATOR.join(existed_groups+current_groups),
                            formatted=True,
                        )
                    else:
                        self.logger.fatal(
                            f'Duplicate groupings between current <{audio}> and existed <{newname}>!',
                        )
                        return

    @log_decorator
    def organize__grouped(self):
        if not self.root:
            self.logger.fatal('Invalid root!')
            return
        self.__load_sources(matched=False)
        audios = self.concerned_sources
        for audio in audios:
            audio_object = self.__prime_audio(audio)
            grouping = self.fetchx(
                audio_object, self.AudioProperty.GROUPING, formatted=True,
            )
            groups = self.split(
                grouping, self.GROUPING_SEPARATOR, escaped=True,
                del_blank=True, filt_empty=True, filt_repeated=True,
                sortify=False, reversify=False,
            )
            if not groups:
                self.logger.fatal(f'Invalid grouping of <{audio}>')
                return
            target = self.abspath(
                self.root, groups[0], os.path.basename(audio),
            )
            if target != audio:
                os.makedirs(os.path.dirname(target), exist_ok=True)
                self.duplicate(audio, target)
                ao = self.__prime_audio(target)
                self.save(
                    ao, self.AudioProperty.GROUPING, groups[0], True,
                )
            if len(groups) < 2:
                continue
            for group in groups[1:]:
                link = self.abspath(self.root, group, os.path.basename(audio))
                if link == target:
                    continue
                os.makedirs(os.path.dirname(link), exist_ok=True)
                if os.path.exists(link):
                    self.remove(link)
                self.duplicate(target, link)
                ao = self.__prime_audio(link)
                self.save(
                    ao, self.AudioProperty.GROUPING, group, True,
                )

    def __glorify_exportation(self, outputs):
        ret = f'{"#"*78}\n\n'
        ret += '# Summary: Collects {collects_count}, Items {items_count}\n'.format(
            collects_count=len(outputs),
            items_count=sum([len(x) for _, x in outputs.items()]),
        )
        ret += f'# Created Time: {self.current_time()}\n\n'

        collect_number = 0
        for collect, items in outputs.items():
            collect_number += 1
            ret += f'\n({collect_number}) {collect}:\n'
            item_number = 0
            for item in items:
                item_number += 1
                ret += '\t{number} {content}\n'.format(
                    number=f'{f"{item_number}.":<{len(str(len(items)))+1}}',
                    content=item,
                )
        return ret

    def __handle_output(self, content):
        if not self.output:
            print(content)
        else:
            self.backup(self.output)
            with open(self.output, 'w', encoding='utf-8') as f:
                f.write(content)

    @log_decorator
    def list_repeated(self):
        self.__load_sources(matched=False)
        
        audios, results = self.concerned_sources, {}
        for audio in audios:
            audio_object = self.__prime_audio(audio)
            artist = self.fetchx(audio_object, self.AudioProperty.ARTIST, formatted=True)
            if not artist:
                self.logger.fatal(f'Invalid artist of <{audio}>')
                return
            title = self.fetchx(audio_object, self.AudioProperty.TITLE, formatted=True)
            if not title:
                self.logger.fatal(f'Invalid title of <{audio}>')
                return
            key = self.generate_key(artist, title)
            if key in results:
                results[key].append(audio)
            else:
                results[key] = [audio]
        
        results = { key: items for key, items in results.items() if len(items) > 1 }
        content = f'{self.__glorify_exportation(results)}'

        self.__handle_output(content)

    def display(self):
        #print("# {}".format('=' * 78))
        #print("Track Name:     {}".format(tag.title))
        #print("Track Artist:   {}".format(tag.artist))
        #print("Track Album:    {}".format(tag.album))
        #print("Track Duration: {}".format(_format_duration(a.info.time_secs)))
        #print("Track Number:   {}".format(tag.track_num))
        #print("Track BitRate:  {}".format(a.info.bit_rate))
        #print("Track BitRate:  {}".format(a.info.bit_rate_str))
        #print("Sample Rate:    {}".format(a.info.sample_freq))
        #print("Mode:           {}".format(a.info.mode))
        #print("# {}".format('=' * 78))
        #print("Album Artist:         {}".format(tag.album_artist))
        #print("Album Year:           {}".format(tag.getBestDate()))
        #print("Album Recording Date: {}".format(tag.recording_date))
        #print("Album Type:           {}".format(tag.album_type))
        #print("Disc Num:             {}".format(tag.disc_num))
        #print("Artist Origin:        {}".format(tag.artist_origin))
        #print("# {}".format('=' * 78))
        #print("Artist URL:         {}".format(tag.artist_url))
        #print("Audio File URL:     {}".format(tag.audio_file_url))
        #print("Audio Source URL:   {}".format(tag.audio_source_url))
        #print("Commercial URL:     {}".format(tag.commercial_url))
        #print("Copyright URL:      {}".format(tag.copyright_url))
        #print("Internet Radio URL: {}".format(tag.internet_radio_url))
        #print("Publisher URL:      {}".format(tag.publisher_url))
        #print("Payment URL:        {}".format(tag.payment_url))
        #print("# {}".format('=' * 78))
        #print("Publisher: {}".format(tag.publisher))
        #print("Original Release Date: {}".format(tag.original_release_date))
        #print("Play Count: {}".format(tag.play_count))
        #print("Tagging Date: {}".format(tag.tagging_date))
        #print("Release Date: {}".format(tag.release_date))
        #print("Terms Of Use: {}".format(tag.terms_of_use))
        #print("isV1: {}".format(tag.isV1()))
        #print("isV2: {}".format(tag.isV2()))
        #print("BPM: {}".format(tag.bpm))
        #print("Cd Id: {}".format(tag.cd_id))
        #print("Composer: {}".format(tag.composer))
        #print("Encoding date: {}".format(tag.encoding_date))
        #print("# {}".format('=' * 78))
        #print("Genre: {}".format(tag.genre.name))
        #print("Non Std Genre Name: {}".format(tag.non_std_genre.name))
        #print("Genre ID: {}".format(tag.genre.id))
        #print("Non Std Genre ID: {}".format(tag.non_std_genre.id))
        #print("LAME Tag:       {}".format(a.info.lame_tag))
        #print("# {}".format('=' * 78))
        #print("Header Version: {}".format(tag.header.version))
        #print("Header Major Version: {}".format(tag.header.major_version))
        #print("Header Minor Version: {}".format(tag.header.minor_version))
        #print("Header Rev Version: {}".format(tag.header.rev_version))
        #print("Header Extended: {}".format(tag.header.extended))
        #print("Header Footer: {}".format(tag.header.footer))
        #print("Header Experimental: {}".format(tag.header.experimental))
        #print("Header SIZE: {}".format(tag.header.SIZE))
        #print("Header Tag Size: {}".format(tag.header.tag_size))
        #print("Extended Header Size: {}".format(tag.extended_header.size))
        #print("# {}".format('=' * 78))
        #print("File Name: {}".format(tag.file_info.name))
        #print("File Tag Size: {}".format(tag.file_info.tag_size))
        #print("File Tag Padding Size: {}".format(tag.file_info.tag_padding_size))
        #print("File Read Only: {}".format(tag.read_only))
        #print("File Size: {}".format(a.info.size_bytes))
        #print("Last Modified: {}".format(time.strftime('%Y-%m-%d %H:%M:%S',
        #                                 time.localtime(tag.file_info.mtime))))
        #print("Last Accessed: {}".format(time.strftime('%Y-%m-%d %H:%M:%S',
        #                                 time.localtime(tag.file_info.atime))))
        #print("# {}".format('=' * 78))

        self.__load_sources(matched=False)

        results, audios = [], self.concerned_sources
        all_fields = [
            (field, self.transform_field_name(field, self.field_type))
            for field in self.ALL_FIELDS
        ]
        formatted, output_format = True, self.FileFormat.NOTE
        match self.data_format:
            case self.DataFormat.ORIGINAL:
                formatted, output_format = False, self.FileFormat.NONE
            case self.DataFormat.FORMATTED:
                formatted, output_format = True, self.FileFormat.NONE
            case self.DataFormat.OUTPUTTED:
                formatted, output_format = True, self.FileFormat.NOTE
        for audio in audios:
            audio_object = self.__prime_audio(audio)
            results.append([
                self.fetchx(
                    audio_object, self.AudioProperty(x[0]), formatted, output_format,
                )
                for x in all_fields
            ])

        def _charting(rows, pair_fields, options):
            page_number, page_size, sort_, filter_, fields_to_show, align_, numbered, style = options

            rl_fields_to_show = [dict(pair_fields)[x] for x in fields_to_show]
            fields = [x[0] for x in pair_fields]

            if align_:
                keys = list(align_.keys())
                for _fields in keys:
                    h, v = align_[_fields].split(':')
                    h, v = h.strip(), v.strip()
                    for _field in _fields.split(','):
                        if _field:
                            align_[_field] = (h if h else 'l', v if v else 'm')

            swaps = []
            for i, field in enumerate(fields_to_show):
                if field not in fields:
                    self.logger.fatal(f'Invalid field <{field}>!')
                    return
                index = fields.index(field)
                if index != i:
                    fields[i], fields[index] = \
                            fields[index], fields[i]
                    swaps.append((i, index))

            for row in rows:
                for l, r in swaps:
                    row[l], row[r] = row[r], row[l]

            rl_fields = [dict(pair_fields)[x] for x in fields]

            table = PrettyTable()
            table.field_names = rl_fields

            for field in table.field_names:
                table.align[field] = 'l'
                table.valign[field] = 'm'
                if align_:
                    if field in align_.keys():
                        table.align[field], table.valign[field] = align_[field]

            def _equal(rows, index, value, ignorecase=True, reverse=False):
                if index < 0:
                    return rows
                return list(filter(
                    lambda x: (( \
                        ignorecase and (True if x[index] is None else x[index].lower() != value.lower()) \
                    ) or ( \
                        (not ignorecase) and x[index] != value \
                    )) if reverse else (( \
                        ignorecase and (False if x[index] is None else x[index].lower() == value.lower()) \
                    ) or ( \
                        (not ignorecase) and x[index] == value \
                    )),
                    rows,
                ))

            def _search(rows, index, value, ignorecase=True, reverse=False):
                if index < 0:
                    return rows
                return list(filter(
                    lambda x: (( \
                        ignorecase and (True if x[index] is None else x[index].lower().find(value.lower()) == -1) \
                    ) or ( \
                        (not ignorecase) and (True if x[index] is None else x[index].find(value) == -1) \
                    )) if reverse else (( \
                        ignorecase and (False if x[index] is None else x[index].lower().find(value.lower()) > -1) \
                    ) or ( \
                        (not ignorecase) and (False if x[index] is None else x[index].find(value) > -1) \
                    )),
                    rows,
                ))

            def _empty(rows, index, reverse=False):
                if index < 0:
                    return rows
                return list(filter(
                    lambda x: x[index] if reverse else not x[index], rows,
                ))

            filter_functions = {
                'equal': _equal,
                'search': _search,
                'empty': _empty,
            }

            if filter_:
                _options = filter_.pop('_options', {})
                relation = _options.get('relation', 'and')
                if filter_:
                    rows = [tuple(row) for row in rows]
                    rows_set = set() if relation == 'or' else set(rows)
                    for _fields in filter_:
                        function = filter_[_fields].get('function', 'search')
                        parameters = filter_[_fields].get('parameters', [])
                        if function in filter_functions.keys():
                            for _field in _fields.split(','):
                                if _field not in fields:
                                    self.logger.fatal(
                                        f'Invalid field <{_field}> when filter!',
                                    )
                                    return
                                index = fields.index(_field)
                                if relation == 'or':
                                    rows_set.update(filter_functions[function](
                                        rows, index, *parameters,
                                    ))
                                else:
                                    rows_set = set(filter_functions[function](
                                        list(rows_set), index, *parameters,
                                    ))
                        else:
                            self.logger.fatal(
                                f'Invalid function <{function}>!',
                            )
                            return
                    rows = [list(row) for row in list(rows_set)]

            def _default_sort(rows, index, reverse):
                if index < 0:
                    return rows
                return list(sorted(
                    rows,
                    key=lambda x: x[index].lower(),
                    reverse=reverse,
                ))

            sort_functions = {
                'default': _default_sort,
            }

            if sort_:
                for _fields, reverse in reversed(sort_):
                    for _field in reversed(_fields.split(',')):
                        if _field not in fields:
                            self.logger.fatal(
                                f'Invalid field <{_field}> when sort!',
                            )
                            return
                        index = fields.index(_field)
                        function = sort_functions['default']
                        if _field in sort_functions.keys():
                            function = sort_functions[_field]
                        rows = function(rows, index, reverse)

            total_rows, start = len(rows), 0
            table_title = f'Total Audios: {total_rows}'

            if total_rows > 0:
                if page_size is None or page_size < 1:
                    page_size = total_rows
                total_pages = math.ceil(total_rows / page_size)
                page_number = min(max(page_number, 1), total_pages)
                start = (min(page_number, total_pages) - 1) * page_size + 1
                end = min(page_number * page_size, total_rows)
                for row in rows[start-1:end]:
                    table.add_row(row)

                table_title += f', Page Size: {page_size}'
                table_title += f', Page Number: {page_number} / {total_pages}'

            table_string = table.get_string(
                title=table_title,
                fields=rl_fields_to_show,
            )

            def _wrap_table(table_string, start=1, numbered=True,
                            style=AudioGod.DisplayStyle.TABLED):

                def _xlen_(s):
                    length = len(s)
                    utf8_length = len(s.encode('utf-8'))
                    length = (utf8_length - length) / 2 + length
                    return int(length)

                rl_number = '--'

                _total = table_string.count('\n') - 6
                offset = 0
                if numbered:
                    offset = max(len(str(start+_total-1)), _xlen_(rl_number)) + 3
                result = re.sub(r'\n\+[\+-]+\+$', r'\n', table_string)

                beg = result.find('\n|', 0)
                end = result.find('\n+', beg)

                surplus = end - 2 * beg - 1

                pos = result.find('+\n|', 0)
                result = '{}{}+\n|{}{}'.format(
                    result[:pos],
                    '-' * (offset + surplus),
                    ' ' * int(offset / 2),
                    result[pos+3:],
                )
                pos = result.find('|\n', pos)
                result = '{}{}|\n{}'.format(
                    result[:pos],
                    ' ' * (offset - int(offset / 2)),
                    result[pos+2:],
                )
                pos = result.find('|\n', pos)
                beg = pos + 2
                pos = result.find('+\n', pos)
                end = pos + 1
                split_line = '{}{}{}{}+'.format(
                    '+' if numbered else '',
                    '-' * (offset - 1) if numbered else '',
                    result[beg:end-1],
                    '-' * surplus,
                )
                result= '{}{}{}'.format(
                    result[:beg],
                    split_line,
                    result[end:],
                )
                pos = result.find('+\n', pos)

                _offset = offset-2
                _offset -= len(re.compile(r'[\u4E00-\u9FA5]').findall(rl_number))

                result= '{}{}{}'.format(
                    result[:pos+2],
                    # 这里 offset-2-2
                    ('|{0:>%s} ' % (_offset)).format(rl_number) \
                    if numbered else '',
                    result[pos+2:],
                )
                pos = result.find('|\n', pos)
                result= '{}{}{}'.format(
                    result[:pos],
                    ' ' * surplus,
                    result[pos:],
                )
                pos = result.find('\n+', pos)
                beg = pos + 1
                pos = result.find('+\n', pos)
                end = pos + 1
                result= '{}{}{}'.format(
                    result[:beg],
                    split_line,
                    result[end:],
                )
                if start > 0:
                    index = start
                    while pos > 0:
                        pos = result.find('\n|', pos)
                        if pos < 0:
                            break
                        result= '{}{}{}'.format(
                            result[:pos+1],
                            ('|{0:>%s} ' % (offset-2)).format(index) \
                            if numbered else '',
                            result[pos+1:],
                        )
                        pos = result.find('|\n', pos)
                        if pos < 0:
                            break
                        result= '{}{}{}'.format(
                            result[:pos],
                            ' ' * surplus,
                            result[pos:],
                        )
                        pos = result.find('|\n', pos)
                        result= '{}{}\n{}'.format(
                            result[:pos+2],
                            split_line,
                            result[pos+2:],
                        )
                        index += 1

                if AudioGod.DisplayStyle.TABLED.ne(style):
                    beg = result.find('|\n+', 0)
                    end = result.find('|\n+', beg+3)
                    result = result[:beg+2] + result[end+2:]
                    result = re.sub(r'\+[\+-]*\n', r'', result)
                    result = re.sub(r'[^\S\n\r]*\|[^\S\n\r]*', r'|', result)
                    result = re.sub(r'^[^\S\n\r]*\|', r'', result)
                    result = re.sub(r'\|[^\S\n\r]*$', r'\n', result)
                    result = re.sub(r'\|\n\|', r'\n', result)

                if AudioGod.DisplayStyle.VERTICAL.eq(style):
                    _result= result
                    result = '\n'
                    result += '#' * 78
                    result += '\n\n'
                    beg = _result.find('\n', 0)
                    result += '\n'.join([
                        '{0:<14}{1}'.format(
                            item.split(': ')[0] + ':',
                            item.split(': ')[1],
                        )
                        for item in _result[:beg].split(', ')
                    ])
                    result += '\n\n'
                    result += '#' * 78
                    result += '\n\n'
                    field_width = 2 + max(*([_xlen_(rl_number) if numbered else 0]+[
                        _xlen_(field) for field in rl_fields_to_show
                    ]))

                    while True:
                        end = _result.find('\n', beg+1)
                        if end < 0:
                            break
                        row = _result[beg+1:end]
                        if not row.strip():
                            break

                        fields = ([rl_number] if numbered else []) + rl_fields_to_show
                        is_cn_field_name = False
                        if len(rl_fields_to_show) > 0:
                            matched = re.search(
                                r'[\u4e00-\u9fff]', rl_fields_to_show[0], re.IGNORECASE,
                            )
                            if matched is not None:
                                is_cn_field_name = True
                        
                        for i, value in enumerate(row.split('|')):
                            if is_cn_field_name:
                                result += '{}{}{}\n'.format(
                                    f'{fields[i]}:',
                                    '\u3000' * int((field_width-_xlen_(fields[i]))/2),
                                    value,
                                )
                            else:
                                result += '{}{}\n'.format(
                                    ('{0:<%s}' % (field_width,)).format(
                                        fields[i]+':',
                                    ),
                                    value,
                                )
                        result += '\n'
                        result += '-' * 78
                        result += '\n\n'
                        beg = end
                    result = re.sub(r'\s+$', r'\n', result)
                return result

            content = _wrap_table(
                table_string, start=start, numbered=numbered, style=style,
            )
            self.__handle_output(content)
            return content

        _ = _charting(
            results,
            all_fields,
            self.display_options,
        )

    def _pack_properties_for_note(self, properties):
        ret = ''
        for field in properties:
            field_name, _, value = properties[field]
            ret += f'{field_name}: {value}; '
        return ret.strip().rstrip(';')
    
    def _pack_properties_for_json(self, properties):
        return ''

    def _pack_properties_for_markdown(self, properties):
        return ''

    _pack_properties_for_md = _pack_properties_for_markdown

    def _pack_properties_for_plist(self, properties):
        ret = ''
        for field in properties:
            field_name, type_, value = properties[field]
            ret += '\t'
            ret += f'<key>{field_name}</key>'
            if type_ != 'boolean':
                ret += f'<{type_}>{value}</{type_}>'
            else:
                ret += f'<{value}/>'
            ret += '\n'
        return ret.strip()

    _pack_properties_for_xml = _pack_properties_for_plist

    def __summarize_for_note(self):
        return self.__glorify_exportation({
            f'@[{genre}] {grouping}': [
                self._pack_properties_for_note(item) for item in items
            ] for grouping, (genre, items) in self.summaries.items()
        })

    def __sort_summaries(self):
        for grouping in self.summaries:
            _, items = self.summaries[grouping]
            items.sort(
                key=lambda x: getattr(self, f'_pack_properties_for_{self.output_format}')(x),
            )
        self.summaries = {
            key: self.summaries[key] for key in sorted(self.summaries)
        }

    @log_decorator
    def preprocess_notes(self):
        self.output_format = self.FileFormat.NOTE
        self.__analysis_note()
        self.__sort_summaries()
        tmp_file = self.document + '.tmp'
        with open(tmp_file, 'w', encoding='utf-8') as f:
            f.write(self.__summarize_for_note())
        self.backup(self.document)
        self.rename(tmp_file, self.document)

    def __summarize(self):
        self.__fill_audios_tree()

        group_nodes = []
        for node in self.audios_tree.all_nodes():
            if node.is_root():
                continue
            node_type = node.data[0]
            if self.AudiosTreeNodeType.PLAYLIST.eq(node_type):
                group_nodes.append(node)

        group_nodes.sort(key=lambda x: (x.data[4], x.tag))

        for group_node in group_nodes:
            genre, parent_group = group_node.data[3], group_node.data[4]
            group = f'{parent_group}/{group_node.tag}'
            items = self.audios_tree.leaves(group_node.identifier)
            self.summaries[group] = (genre, list(map(lambda x: x.data[5], items)))

        self.__sort_summaries()

    @log_decorator
    def export(self):
        pass

    @log_decorator
    def export__note(self):
        self.output_format = self.FileFormat.NOTE
        self.__summarize()
        self.__handle_output(self.__summarize_for_note())

    @log_decorator
    def export__json(self):
        self.output_format = self.FileFormat.JSON
        self.__summarize()
        self.__handle_output('')

    @log_decorator
    def export__markdown(self):
        self.output_format = self.FileFormat.MARKDOWN
        self.__summarize()
        self.__handle_output('')

    export__md = export__markdown

    @log_decorator
    def export__plist(self):
        self.output_format = self.FileFormat.PLIST
        self.__summarize()
        
        itunes_version_plist, itunes_media_folder, _, _ = self.itunes_options

        def _get_itunes_version(itunes_version_plist) -> str:
            with open(itunes_version_plist, 'rb') as f:
                plist = plistlib.load(f)
                origin_version = plist.get('SourceVersion', '')
                if origin_version:
                    pos = len(origin_version) % 3
                    if pos == 0:
                        pos = 3
                    formatted_version = str(int(origin_version[0:pos]))
                    while pos < len(origin_version):
                        formatted_version += f'.{str(int(origin_version[pos:pos+3]))}'
                        pos += 3
                    return formatted_version.rstrip('.0')
            return '1.0'

        def _format_template(template) -> str:
            return template.strip().replace(' '*4, '\t') + '\n'

        def _repack_plist(content) -> str:
            result = f'\n{content}'.replace('\n', '\n\t\t')
            return result[:-1]

        def _pack_track(track) -> str:
            _, track_id, persistent_id, _, _, properties = track.data
            result = Template(_format_template('''
<key>${track_id}</key>
<dict>
	<key>Track ID</key><integer>${track_id}</integer>
	${properties}
	<key>Date Added</key><date>${date_added}</date>
	<key>Kind</key><string>${kind}</string>
	<key>Persistent ID</key><string>${persistent_id}</string>
	<key>Track Type</key><string>${track_type}</string>
	<key>Location</key><string>${location}</string>
	<key>File Folder Count</key><integer>${file_folder_count}</integer>
	<key>Library Folder Count</key><integer>${library_folder_count}</integer>
</dict>
            ''')).safe_substitute(dict(
                track_id=track_id,
                properties=self._pack_properties_for_plist(properties),
                date_added=self.current_time(),
                kind='MPEG audio file',
                persistent_id=persistent_id,
                track_type='File',
                location=self.encode_location(track.tag),
                file_folder_count='-1',
                library_folder_count='-1',
            ))
            return result

        def _unique_tracks(tracks) -> list:
            results, track_set = [], set()
            for track in tracks:
                if track.tag in track_set:
                    continue
                results.append(track)
                track_set.add(track.tag)
            return results

        def _pack_tracks() -> str:
            result = ''
            tracks = _unique_tracks(self.audios_tree.leaves())
            for track in tracks:
                if track.identifier == self.AUDIOS_TREE_ROOT_NID:
                    continue
                if not isinstance(track.data, list):
                    continue
                node_type = track.data[0]
                if self.AudiosTreeNodeType.TRACK.ne(node_type):
                    continue
                result += _pack_track(track)
            return _repack_plist(result)

        def _pack_simple_tracks(node) -> str:
            result, tracks = '', _unique_tracks(self.audios_tree.leaves(node.identifier))
            for track in tracks:
                if track.identifier == self.AUDIOS_TREE_ROOT_NID:
                    continue
                if not isinstance(track.data, list):
                    continue
                node_type = track.data[0]
                if self.AudiosTreeNodeType.TRACK.ne(node_type):
                    continue
                track_id = track.data[1]
                result += Template(_format_template('''
<dict>
	<key>Track ID</key><integer>${track_id}</integer>
</dict>
            ''')).safe_substitute(dict(
                track_id=track_id,
            ))
            return _repack_plist(result)

        def _pack_library() -> str:
            result = Template(_format_template('''
<dict>
	<key>Name</key><string>${name}</string>
	<key>Description</key><string>${description}</string>
	<key>Master</key><${master}/>
	<key>Playlist ID</key><integer>${playlist_id}</integer>
	<key>Playlist Persistent ID</key><string>${playlist_persistent_id}</string>
	<key>Visible</key><${visible}/>
	<key>All Items</key><${show_all_items}/>
	<key>Playlist Items</key>
	<array>${tracks}</array>
</dict>
            ''')).safe_substitute(dict(
                name='Library',
                description=self.escape_characters(''),
                master='true',
                playlist_id=-1,
                playlist_persistent_id=self.generate_persistent_id(),
                visible='false',
                show_all_items='true',
                tracks=_pack_simple_tracks(self.audios_tree[self.audios_tree.root]),
            ))
            return result

        def _pack_playlist(node) -> str:
            node_type, id, pid, _, _, ppid = node.data
            result = Template(_format_template('''
<dict>
	<key>Name</key><string>${name}</string>
	<key>Description</key><string>${description}</string>
	<key>Playlist ID</key><integer>${playlist_id}</integer>
	<key>Playlist Persistent ID</key><string>${playlist_persistent_id}</string>
''' + ('' if (not ppid) or (ppid == self.AUDIOS_TREE_ROOT_NID) else \
'''\t<key>Parent Persistent ID</key><string>${parent_persistent_id}</string>
''') + '''\t<key>All Items</key><${show_all_items}/>
    <key>Folder</key><${is_folder}/>
    <key>Playlist Items</key>
    <array>${tracks}</array>
</dict>
            ''')).safe_substitute(dict(
                name=self.escape_characters(node.tag),
                description=self.escape_characters(''),
                playlist_id=id,
                playlist_persistent_id=pid,
                parent_persistent_id=ppid,
                show_all_items='true',
                is_folder=str(self.AudiosTreeNodeType.FOLDER.eq(node_type)).lower(),
                tracks=_pack_simple_tracks(node),
            ))
            return result

        def _pack_playlists() -> str:
            result = _pack_library()
            for node in self.audios_tree.all_nodes():
                if node.is_root():
                    continue
                node_type = node.data[0]
                if self.AudiosTreeNodeType.TRACK.eq(node_type):
                    continue
                result += _pack_playlist(node)
            return _repack_plist(result)

        def _pack_plist() -> str:
            return Template(_format_template('''
<?xml version="${xml_version}" encoding="${xml_encoding}"?>
<!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="${plist_version}">
<dict>
	<key>Major Version</key><integer>${major_version}</integer>
	<key>Minor Version</key><integer>${minor_version}</integer>
	<key>Date</key><date>${created_date}</date>
	<key>Application Version</key><string>${itunes_version}</string>
	<key>Features</key><integer>${features}</integer>
	<key>Show Content Ratings</key><${show_content_ratings}/>
	<key>Music Folder</key><string>${itunes_media_folder}</string>
	<key>Library Persistent ID</key><string>${library_persistent_id}</string>
	<key>Tracks</key>
	<dict>${tracks}</dict>
	<key>Playlists</key>
	<array>${playlists}</array>
</dict>
</plist>
            ''')).safe_substitute(dict(
                xml_version = '1.0',
                xml_encoding = 'UTF-8',
                plist_version = '1.0',
                major_version = '1',
                minor_version = '1',
                created_date = self.current_time(),
                itunes_version = _get_itunes_version(itunes_version_plist),
                features = '5',
                show_content_ratings = 'true',
                itunes_media_folder = self.encode_location(itunes_media_folder),
                library_persistent_id = self.generate_persistent_id(),
                tracks = _pack_tracks(),
                playlists = _pack_playlists(),
            ))

        return self.__handle_output(_pack_plist())
    
    export__xml = export__plist

    @log_decorator
    def convert(self):
        pass

    @log_decorator
    def convert__qmc_to_mp3(self):
        pass

    @log_decorator
    def convert__kmx_to_mp4(self):
        pass

    @log_decorator
    def convert__mp4_to_mp3(self):
        pass

    @log_decorator
    def convert__note_to_markdown(self):
        pass

    convert__note_to_md = convert__note_to_markdown

    @log_decorator
    def convert__markdown_to_note(self):
        pass

    convert__md_to_note = convert__markdown_to_note

    @log_decorator
    def generate_script(self):
        content = '#!/usr/bin/env zsh\n\n'
        content += '#' * 78 + '\n\n'
        content += f'# Created Time: {self.current_time()}\n\n'
        content += '#' * 78 + '\n\n'
        content += 'set -e\n\n'
        content += '#' * 78 + '\n'
        steps = [
            'preprocess-notes',
            'fill-properties',
            'format-properties',
            'rename-audios',
            ('organize', 'grouped'),
            ('export', self.FileFormat.NOTE),
            'list-repeated',
            ('organize', 'ituned'),
            ('export', self.FileFormat.PLIST),
        ]
        for i, step in enumerate(steps):
            if isinstance(step, tuple):
                usage = self.render_usage(
                    usage=self.ACTIONS[step[0]]['branches'][step[1]]['kwargs']['usage'],
                    action=step[0],
                    branch=step[1],
                )
            else:
                usage = self.render_usage(
                    usage=self.ACTIONS[step]['kwargs']['usage'],
                    action=step,
                    branch=None,
                )
            content += f'\n{usage.strip()}'
            if i < len(steps) - 1:
                content += '\n'
        self.__handle_output(
            self.render_usage(content.rstrip(' \\') + '\n').lstrip(),
        )
        self.chmod(self.output, 0o755)

    @log_decorator
    def clean_up(self):
        self.remove(
            './*.tmp',
            './repeated.txt*',
            '~/Music/Grouped',
            '~/Music/iTunes/iTunes Media/Music/*',
            '~/Music/iTunes/Library.xml',
        )

    ############################################################################

    @classmethod
    def audio_properties(cls) -> str:
        table = PrettyTable()
        table.field_names = [
            'Number',
            'Field',
            'Chinese Name',
            'English Name',
            'Type',
        ]
        for field in table.field_names:
            table.align[field] = 'l'
        for number, field in enumerate(cls.ALL_FIELDS):
            chinese_name = cls.AUDIO_PROPERTIES[field][0][0]
            english_name = cls.AUDIO_PROPERTIES[field][0][1]
            field_type = cls.AUDIO_PROPERTIES[field][1]
            table.add_row([
                number+1,
                field,
                chinese_name,
                english_name,
                field_type,
            ])
        return table.get_string(
            title='AUDIO PROPERTIES',
        )

    @classmethod
    def special_fields(cls) -> str:
        table = PrettyTable()
        table.field_names = cls.FIELDS.keys()
        for field in table.field_names:
            table.align[field] = 'l'
        rows = list(cls.FIELDS.values())
        for j in range(len(cls.ALL_FIELDS)):
            row = []
            for i in range(len(rows)):
                if j < len(rows[i]):
                    row.append(rows[i][j])
                else:
                    row.append('')
            table.add_row(row)
        return table.get_string(
            title='SPECIAL FIELDS',
        )

    @classmethod
    def special_characters(cls) -> str:
        table = PrettyTable()
        table.field_names = [
            'Number',
            'Character',
            'Introduction',
        ]
        for field in table.field_names:
            table.align[field] = 'l'
        characters = [
            (cls.ORI_DIV_CHAR, 'Separator for origin audio file name.'),
            (cls.DIV_CHAR, 'Separator for formatted audio file name.'),
            (cls.GROUPING_SEPARATOR, 'Separator for several grouping property of audio file.'),
            (cls.FilenamePatternTemplate.delimiter, 'Delimiter of template for filename pattern.'),
        ]
        for number, char in enumerate(characters):
            table.add_row([
                number+1,
                char[0],
                char[1],
            ])
        return table.get_string(
            title='SPECIAL CHARACTERS',
        )
    
    @staticmethod
    def glorify_indents(content, indent=0):
        def _calculate_min_indent(text):
            min_indent, lines = None, text.split('\n')
            for line in lines:
                stripped_line = line.lstrip(' ')
                if not stripped_line:
                    continue
                current_indent = len(line) - len(stripped_line)
                if min_indent is None or current_indent < min_indent:
                    min_indent = current_indent
            return min_indent if min_indent is not None else 0
        filler, min_indent = ' ', _calculate_min_indent(content)
        if min_indent > 0:
            content = re.sub(
                r'\n%s{%s}' % (filler, min_indent), '\n', content,
            )
        if indent > 0:
            content = re.sub(
                r'\n', f'\n{filler * indent}', content,
            )
        return content

    # Successful for zsh, failed for bash.
    # You should set 'PROMPT_COMMAND="history -a"' in "~/.bashrc" or "~/.bash_profile".
    # And then run "source ~/.bashrc" or "source ~/.bash_profile".
    @classmethod
    def get_command(cls) -> str:
        interpreter = f'pipenv run python {sys.argv[0]}'
        try:
            match psutil.Process().parent().name().lower(): # type: ignore
                case 'bash':
                    history_file = '~/.bash_history'
                case 'zsh':
                    history_file = '~/.zsh_history'
            history_file = cls.abspath(history_file)
            with open(history_file, 'r', errors='ignore') as f:
                cache, history_pattern = [], r'^: *[0-9\.]+:[0-9\.]+[:;]'
                for line in reversed(f.readlines()):
                    cache.append(line.strip().strip('\\').strip())
                    if re.match(history_pattern, line) is not None:
                        break
                cmd = re.sub(history_pattern, r'', ' '.join(reversed(cache))).strip()
                index = cmd.find(' -')
                if index != -1:
                    interpreter = cmd[:index].strip()
                else:
                    interpreter = cmd.strip()
                subcmd_pattern = r'\s*({0})(\s+.*)?$'.format('|'.join(cls.ACTIONS.keys()))
                interpreter = re.sub(subcmd_pattern, r'', interpreter)
        except Exception as e:
            pass
        return interpreter 

    @classmethod
    def render_usage(cls, usage, kwargs={}) -> str:
        _kwargs = cls.integrate_default_arguments(with_customized=True)
        #aliens = [('properties', 4), ('sort', 4), ('filter', 4), ('align', 4)]
        #for alien in aliens:
        #    _kwargs[alien[0]] = cls.glorify_indents(
        #        _kwargs[alien[0]], indent=alien[1],
        #    ).strip()
        kwargs = _kwargs | kwargs
        return '\n' + cls.PerfectTemplate(
            cls.glorify_indents(usage, indent=0),
        ).perfect_substitute(dict(
            audio_properties=cls.audio_properties(),
            special_fields=cls.special_fields(),
            special_characters=cls.special_characters(),
            cmd=cls.get_command(),
            ori_div_char=cls.ORI_DIV_CHAR,
            div_char=cls.DIV_CHAR,
            grouping_sep=cls.GROUPING_SEPARATOR,
            fnp_delimiter=cls.FilenamePatternTemplate.delimiter,
         ) | kwargs)

################################################################################

AudioGod.rewrite_actions()

################################################################################
#                                                                              #
#                                MAIN FUNCTION                                 #
#                                                                              #
################################################################################

def _add_arguments(parser, arguments) -> None:
    arguments = arguments | AudioGod.COMMON_ARGUMENTS
    for argument, params in arguments:
        use_public = params.get('use_public', False)
        if use_public:
            params = AudioGod.PUBLIC_ARGUMENTS[argument]
        parser.add_argument(*params['args'], **params['kwargs'])
    return









    parser.add_argument(
        '--log-level', '-l',
        type=str,
        choices=AudioGod.ARGUMENTS_CHOICES['log_level'],
        required=False,
        default=AudioGod.ARGUMENTS_DEFAULTS['log_level'],
        dest='log_level',
        help='level of logger',
    )

    parser.add_argument(
        '--log-file', '-7',
        type=str,
        required=False,
        default=AudioGod.ARGUMENTS_DEFAULTS['log_file'],
        dest='log_file',
        help='log file of logger',
    )

    if 'document' in arguments:
        parser.add_argument(
            '--document', '-s',
            type=str,
            required=False,
            default=AudioGod.ARGUMENTS_DEFAULTS['document'],
            dest='document',
            help='source file to match',
        )
    
    if 'ignored_file' in arguments:
        parser.add_argument(
            '--ignored-file', '-i',
            type=str,
            required=False,
            default=AudioGod.ARGUMENTS_DEFAULTS['ignored_file'],
            dest='ignored_file',
            help='ignored files',
        )
    
    if 'source' in arguments:
        parser.add_argument(
            '--source', '-c',
            type=str,
            required=False,
            default=AudioGod.ARGUMENTS_DEFAULTS['source'],
            dest='source',
            help='audio file or directory you want to process',
        )
    
    if 'root' in arguments:
        parser.add_argument(
            '--root', '-d',
            type=str,
            required=False,
            default=AudioGod.ARGUMENTS_DEFAULTS['root'],
            dest='root',
            help='root directory',
        )
    
    if 'properties' in arguments:
        parser.add_argument(
            '--properties', '-p',
            type=str,
            required=False,
            default=AudioGod.ARGUMENTS_DEFAULTS['properties'],
            dest='properties',
            help='properties for audios',
        )
    
    if 'recursive' in arguments:
        parser.add_argument(
            '--recursive', '-r',
            type=AudioGod.BooleanType,
            required=False,
            default=AudioGod.ARGUMENTS_DEFAULTS['recursive'],
            dest='recursive',
            help='if recursive when traverse the audios directory',
        )
    
    if 'extensions' in arguments:
        parser.add_argument(
            '--extensions', '-e',
            type=str,
            required=False,
            default=AudioGod.ARGUMENTS_DEFAULTS['extensions'],
            dest='extensions',
            help='valid extensions of audios',
        )
    
    if 'fields' in arguments:
        parser.add_argument(
            '--fields', '-f',
            type=str,
            required=False,
            default=AudioGod.ARGUMENTS_DEFAULTS['fields'],
            dest='fields',
            help='fields of audio to process: {fields}'.format(
                fields='; '.join([
                    '({}: {})'.format(key, ','.join([f for f in fields]))
                    for key, fields in AudioGod.FIELDS.items()
                ]),
            ),
        )
    
    if 'page_number' in arguments:
        parser.add_argument(
            '--page-number', '-m',
            type=int,
            required=False,
            default=AudioGod.ARGUMENTS_DEFAULTS['page_number'],
            dest='page_number',
            help='page number for audios display',
        )
    
    if 'page_size' in arguments:
        parser.add_argument(
            '--page-size', '-j',
            type=int,
            required=False,
            default=AudioGod.ARGUMENTS_DEFAULTS['page_size'],
            dest='page_size',
            help='page size for audios display',
        )
    
    if 'sort' in arguments:
        parser.add_argument(
            '--sort', '-q',
            type=str,
            required=False,
            default=AudioGod.ARGUMENTS_DEFAULTS['sort'],
            dest='sort',
            help='sort options for audios display',
        )
    
    if 'filter' in arguments:
        parser.add_argument(
            '--filter', '-b',
            type=str,
            required=False,
            default=AudioGod.ARGUMENTS_DEFAULTS['filter'],
            dest='filter',
            help='filter options for audios display',
        )
    
    if 'align' in arguments:
        parser.add_argument(
            '--align', '-w',
            type=str,
            required=False,
            default=AudioGod.ARGUMENTS_DEFAULTS['align'],
            dest='align',
            help='align options for audios display',
        )
    
    if 'numbered' in arguments:
        parser.add_argument(
            '--numbered', '-n',
            type=Boolean,
            required=False,
            default=AudioGod.ARGUMENTS_DEFAULTS['numbered'],
            dest='numbered',
            help='if show number for audios display',
        )
    
    if 'style' in arguments:
        parser.add_argument(
            '--style', '-y',
            type=str,
            choices=AudioGod.ARGUMENTS_CHOICES['style'],
            required=False,
            default=AudioGod.ARGUMENTS_DEFAULTS['style'],
            dest='style',
            help='display style for audios',
        )
    
    if 'data_format' in arguments:
        parser.add_argument(
            '--data-format', '-x',
            type=str,
            choices=AudioGod.ARGUMENTS_CHOICES['data_format'],
            required=False,
            default=AudioGod.ARGUMENTS_DEFAULTS['data_format'],
            dest='data_format',
            help='the data format for audios to display',
        )
    
    if 'field_type' in arguments:
        parser.add_argument(
            '--field-type', '-8',
            type=str,
            choices=AudioGod.ARGUMENTS_CHOICES['field_type'],
            required=False,
            default=AudioGod.ARGUMENTS_DEFAULTS['field_type'],
            dest='field_type',
            help='type of field name',
        )
    
    if 'output_format' in arguments:
        parser.add_argument(
            '--output-format', '-9',
            type=str,
            choices=AudioGod.ARGUMENTS_CHOICES['output_format'],
            required=False,
            default=AudioGod.ARGUMENTS_DEFAULTS['output_format'],
            dest='output_format',
            help='format of output content',
        )
    
    if 'output' in arguments:
        parser.add_argument(
            '--output', '-o',
            type=str,
            required=False,
            default=AudioGod.ARGUMENTS_DEFAULTS['output'],
            dest='output',
            help='output file or folder',
        )
    
    if 'artwork_path' in arguments:
        parser.add_argument(
            '--artwork-path', '-k',
            type=str,
            required=False,
            default=AudioGod.ARGUMENTS_DEFAULTS['artwork_path'],
            dest='artwork_path',
            help='path to export artworks',
        )
    
    if 'filename_pattern' in arguments:
        parser.add_argument(
            '--filename-pattern', '-t',
            type=str,
            required=False,
            default=AudioGod.ARGUMENTS_DEFAULTS['filename_pattern'],
            dest='filename_pattern',
            help='filename pattern to rename audios',
        )
    
    if 'type' in arguments:
        parser.add_argument(
            '--type', '-g',
            type=str,
            choices=AudioGod.ARGUMENTS_CHOICES['type'],
            required=False,
            default=AudioGod.ARGUMENTS_DEFAULTS['type'],
            dest='type',
            help='types',
        )
    
    if 'itunes_version_plist' in arguments:
        parser.add_argument(
            '--itunes-version-plist', '-1',
            type=str,
            required=False,
            default=AudioGod.ARGUMENTS_DEFAULTS['itunes_version_plist'],
            dest='itunes_version_plist',
            help='the version plist file of itunes or apple music',
        )
    
    if 'itunes_media_folder' in arguments:
        parser.add_argument(
            '--itunes-media-folder', '-2',
            type=str,
            required=False,
            default=AudioGod.ARGUMENTS_DEFAULTS['itunes_media_folder'],
            dest='itunes_media_folder',
            help='the media folder of itunes or apple music',
        )
    
    if 'track_initial_id' in arguments:
        parser.add_argument(
            '--track-initial-id', '-3',
            type=int,
            required=False,
            default=AudioGod.ARGUMENTS_DEFAULTS['track_initial_id'],
            dest='track_initial_id',
            help='initial id of tracks for itunes or apple music plist file',
        )
    
    if 'playlist_initial_id' in arguments:
        parser.add_argument(
            '--playlist-initial-id', '-4',
            type=int,
            required=False,
            default=AudioGod.ARGUMENTS_DEFAULTS['playlist_initial_id'],
            dest='playlist_initial_id',
            help='initial id of playlists for itunes or apple music plist file',
        )


def _handle_execute(args) -> None:
    action, branch = args.action, None
    if hasattr(args, 'branch'):
        branch = args.branch
    
    arguments = AudioGod.integrate_default_arguments(
        action=action,
        branch=branch,
        with_customized=False,
    )
    for argument in arguments:
        if hasattr(args, argument):
            arguments[argument] = getattr(args, argument)

    func = AudioGod.replace_hyphen(f'{action}__{branch}' if branch else action)
    getattr(AudioGod(action=action, branch=branch, **arguments), func)()


def _add_subparser(mainparser, subparsers, name, action, branch=None, execute=None):
    params = AudioGod.ACTIONS[action]
    if branch and 'branches' in params:
        params = params['branches'][branch]
    arguments = params.get('arguments', None)
    kwargs = params['kwargs']
    kwargs = {
        'description': '',
        'help': '',
        'epilog': '😴 Sleeping ...',
        'formatter_class': argparse.ArgumentDefaultsHelpFormatter,
        #'usage': '',
        #'prog': None,
        #'aliases': (),
        #'prefix_chars': '-',
        #'fromfile_prefix_chars': None,
        #'argument_default': None,
        #'conflict_handler': 'error',
        #'add_help': True,
        #'allow_abbrev': True,
        #'exit_on_error': True,
    } | kwargs
    if 'usage' in kwargs:
        kwargs['usage'] = AudioGod.render_usage(kwargs['usage'], action, branch)
    subparser = subparsers.add_parser(name, **kwargs)

    if arguments is not None:
        _add_arguments(subparser, arguments)
    if execute is not None:
        subparser.set_defaults(execute=execute)
    mainparser.add_subparser((name, subparser))

    return subparser


class GreatArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__subparsers = []

    def add_subparser(self, subparser):
        self.__subparsers.append(subparser)

    def parse_args(self):
        ret = super().parse_args()
        if len(sys.argv) == 1:
            self.print_help()
        return ret

    def format_help(self):
        help_text = super().format_help()
        for name, subparser in self.__subparsers:
            help_text += '\n' + '@' * 78 + '\n'
            help_text += f'\nSubcommand <{name}> help info:\n\n'
            help_text += subparser.format_help()
        return help_text

    def print_help(self):
        pydoc.pager(self.format_help())
        self.exit(0)


def main():
    main_parser = GreatArgumentParser(
        prog=sys.argv[0],
        usage=AudioGod.render_usage(AudioGod.USAGE),
        description='🎻 God of audios 🎸',
        epilog='🤔 Thinking ...',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        #prefix_chars='-',
        #fromfile_prefix_chars=None,
        #argument_default=None,
        #conflict_handler='error',
        #add_help=True,
        #allow_abbrev=True,
        #exit_on_error=True,
    )
    
    main_parser.add_argument(
        '--version', '-v',
        action='version',
        version=__VERSION__,
    )

    action_parsers = main_parser.add_subparsers(
        prog=sys.argv[0],
        title='Actions',
        description='the available actions show below:',
        dest='action',
        required=False,
        parser_class=GreatArgumentParser,
        metavar='action name:   ',
        help='action statement:',
    )

    for action in AudioGod.ACTIONS:
        action_parser = _add_subparser(
            mainparser=main_parser,
            subparsers=action_parsers,
            name=action,
            action=action,
            branch=None,
            execute=_handle_execute,
        )
        if 'branches' in AudioGod.ACTIONS[action]:
            branch_parsers = action_parser.add_subparsers(
                prog=sys.argv[0],
                title='Branches',
                description='the available branches show below:',
                dest='branch',
                required=False,
                metavar='branch name:   ',
                help='branch statement:',
            )
            for branch in AudioGod.ACTIONS[action]['branches']:
                _ = _add_subparser(
                    mainparser=action_parser,
                    subparsers=branch_parsers,
                    name=branch,
                    action=action,
                    branch=branch,
                    execute=_handle_execute,
                )

    args = main_parser.parse_args()
    # only for subparsers, error for main parser
    args.execute(args)

################################################################################
#                                                                              #
#                               SCRIPT ENTRANCE                                #
#                                                                              #
################################################################################

if __name__ == '__main__':
    main()
