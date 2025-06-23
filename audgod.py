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

#-------------------------------------------------------------------------------

from string import Template
from collections import ChainMap

#-------------------------------------------------------------------------------

import psutil

from treelib import Tree
from enumx import StringEnum
from prettytable import PrettyTable

import eyed3
from eyed3.id3 import Genre, frames
from eyed3.id3.tag import CommentsAccessor

################################################################################
#                                                                              #
#                                 DESCRIPTION                                  #
#                                                                              #
################################################################################

'''
    The god processor for audios.
'''

################################################################################
#                                                                              #
#                                SCRIPT MACROS                                 #
#                                                                              #
################################################################################

__VERSION__ = 'Audio God 1.0'


__USAGE__ = '''

All fields:
${audio_properties}

Special fields:
${special_fields}

Special characters:
${special_characters}

--------------------------------------------------------------------------------

Samples of audio file name:

Original  audio file name: "artist${ori_div_char}title.mp3"
Formatted audio file name: "artist ${div_char} title.mp3"
Pattern of filename to rename: "${fnp_delimiter}{artist} ${div_char} ${fnp_delimiter}{title}"

--------------------------------------------------------------------------------

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

--------------------------------------------------------------------------------

Precautions:

    1. Don't contain blank characters in genres and groupings;
    2. Audios in the same group should have a same genre;
    3. In invalid detail line of note.txt file, "," -> "\\" and ":" -> "/".

--------------------------------------------------------------------------------

Attention:
    Here is the cache folder, which contains backups and trash under it.
    You should clear the cache when the size is too big.
        ${cache_dir}
            ├── ${trash_dir}
            └── ${backups_dir}

--------------------------------------------------------------------------------

General commands:

    * Show help information:
        ${cmd} -h/--help

    * Show version of program:
        ${cmd} -v/--version

--------------------------------------------------------------------------------

General steps:

Ready:
    Step.1: Run <operate cleanup> subcommand to clear repeats, backups, grouped folder, and iTunes related;
    Step.2: Download songs, and make sure that file named with "artist${ori_div_char}title";
    Step.3: Add detail of songs to notes, then grouped.

Process Method 1:
    Step.1: Preprocess note, until note file not changed, with subcommand <preprocess-note>;
    Step.2: Fill properties, with subcommand <fill-properties>;
    Step.3: Format properties, with subcommand <format-properties>;
    Step.4: Rename audios, with subcommand <rename-audios>;
    Step.5: Organize grouped files, with subcommand <organize grouped>;
    Step.6: Export note file, with subcommand <export note>;
    Step.7: List repeated audios of grouped, with subcommand <list-repeated>;
    Step.8: Organize ituned files, with subcommand <organize ituned>;
    Step.9: Export plist file, with subcommand <export plist>.

Process Method 2:
    Step.1: Put note file to local folder (e.g. "${preprocess-note.document}");
    Step.2: Put audios to source folder (e.g. "${fill-properties.source}");
    Step.3: Put ignored file to local folder (e.g. "${fill-properties.ignored_file}");
    Step.4: Run <generate-script> subcommand to generate a shell script (e.g. "${generate-script.output}");
    Step.5: Execute the shell script above.
    Results under folders below:
        "${preprocess-note.document}"
        "${list-repeated.output}"
        "${derive-artworks.artwork_path}"
        "${organize.ituned.source}"
        "${export.plist.itunes_media_folder}"
        "${export.plist.output}"

--------------------------------------------------------------------------------

'''

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

################################################################################
#                                                                              #
#                                 AUDIO GOD                                    #
#                                                                              #
################################################################################

class AudioGod(object):
    ORI_DIV_CHAR = '-'
    DIV_CHAR = '*'
    GROUPING_SEPARATOR = '&'

    #---------------------------------------------------------------------------

    CACHE_DIR = os.path.expanduser('~/.audgod-cache')
    TRASH_DIR = os.path.join(CACHE_DIR, 'trash')
    BACKUPS_DIR = os.path.join(CACHE_DIR, 'backups')

    #---------------------------------------------------------------------------

    class PerfectTemplate(Template):
        idpattern = r'(?a:[_a-z-][_a-z0-9-]*(\.[_a-z-][_a-z0-9-]*)*)'
    
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
                    except KeyError as e:
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


    class FatalLogger(logging.Logger):
        def __init__(self, level=None, log_file=None):
            level = level or logging.DEBUG
            log_file = log_file or 'stderr'
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

    #---------------------------------------------------------------------------

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
        NOTE = 'note'
        JSON = 'json'
        MARKDOWN = 'markdown'
        MD = 'md'
        PLIST = 'plist'
        XML = 'xml'


    @StringEnum.unique
    class FieldType(StringEnum):
        ORIGINAL = 'ori'
        CHINESE = 'cn'
        ENGLISH = 'en'


    @StringEnum.unique
    class ReplaceType(StringEnum):
        NONE = 'none'
        PARTIAL = 'partial'
        ENTIRE = 'entire'

    #---------------------------------------------------------------------------

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
    
    #---------------------------------------------------------------------------
    
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

    #---------------------------------------------------------------------------

    NAME = ''
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = None
    ARGUMENTS = None

    #---------------------------------------------------------------------------

    BASIC_KWARGS = {
        'prog': None,
        'description': '',
        'help': '',
        'usage': None,
        'epilog': '😴 Sleeping ...',
        'formatter_class': argparse.ArgumentDefaultsHelpFormatter,
        #'aliases': (),
        #'prefix_chars': '-',
        #'fromfile_prefix_chars': None,
        #'argument_default': None,
        #'conflict_handler': 'error',
        #'add_help': True,
        #'allow_abbrev': True,
        #'exit_on_error': True,
    }

    PUBLIC_ARGUMENTS = {
        'document': {
            'args': ['-s'],
            'kwargs': {
                'action': 'store',
                'type': str,
                'required': False,
                'default': './songs.note',
                'help': 'document to load',
            },
        },
        'ignored_file': {
            'args': ['-i'],
            'kwargs': {
                'action': 'store',
                'type': str,
                'required': False,
                'default': './ignored.txt',
                'help': 'ignored files when load',
            },
        },
        'source': {
            'args': ['-c'],
            'kwargs': {
                'action': 'store',
                'type': str,
                'required': False,
                'default': '~/Music/Source/MP3',
                'help': 'files or directories you want to process',
            },
        },
        'root': {
            'args': ['-d'],
            'kwargs': {
                'action': 'store',
                'type': str,
                'required': False,
                'default': '~/Music/Source/MP3',
                'help': 'root directory',
            },
        },
        'recursive': {
            'args': ['-r'],
            'kwargs': {
                'action': argparse.BooleanOptionalAction,
                'required': False,
                'default': True,
                'help': 'if recursive when traverse the directory',
            },
        },
        'extensions': {
            'args': ['-e'],
            'kwargs': {
                'action': 'store',
                'type': str,
                'required': False,
                'default': 'mp3,aac',
                'help': 'valid extensions of sources',
            },
        },
        'fields': {
            'args': ['-f'],
            'kwargs': {
                'action': 'store',
                'type': str,
                'required': False,
                'default': 'core',
                'help': 'fields to process: {fields}'.format(
                    fields='; '.join([
                        '({}: {})'.format(key, ','.join([f for f in fields]))
                        for key, fields in FIELDS.items()
                    ]),
                ),
            },
        },
        'field_type': {
            'args': ['-8'],
            'kwargs': {
                'action': 'store',
                'type': str,
                'choices': FieldType.members(),
                'required': False,
                'default': FieldType.CHINESE,
                'help': 'type of field name',
            },
        },
        'output': {
            'args': ['-o'],
            'kwargs': {
                'action': 'store',
                'type': str,
                'required': False,
                'default': '',
                'help': 'file or folder to output',
            },
        },
    }

    REQUISITE_ARGUMENTS = {
        'log_level': {
            'args': ['-l'],
            'kwargs': {
                'action': 'store',
                'type': str,
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
                'required': False,
                'default': 'WARNING',
                'help': 'level of logger',
            },
        },
        'log_file': {
            'args': ['-7'],
            'kwargs': {
                'action': 'store',
                'type': str,
                'required': False,
                'default': 'stderr',
                'help': 'log file of logger',
            },
        },
    }

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        self.__parameters = copy.deepcopy(kwargs)

        # init logger
        self.__logger = self.FatalLogger(
            self.parameters.get('log_level', None),
            self.parameters.get('log_file', None),
        )


    @property
    def parameters(self):
        return self.__parameters


    @property
    def logger(self):
        return self.__logger


    @classmethod
    def ARGUMENTS_DEFAULTS(cls):
        ret = {}
        if cls.ARGUMENTS is None:
            return ret
        for argment, params in cls.ARGUMENTS.items(): # type: ignore
            ret[argment] = params['kwargs']['default']
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


    @staticmethod
    def glorify_indents(content, indent=None):
        if indent is None:
            return content
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
                    cache.append(line.strip().rstrip('\\').rstrip())
                    if re.match(history_pattern, line) is not None:
                        break
                cmd = re.sub(history_pattern, r'', ' '.join(reversed(cache))).strip()
                index = cmd.find(' -')
                if index != -1:
                    interpreter = cmd[:index].strip()
                else:
                    interpreter = cmd.strip()
                subcmd_pattern = r'\s*({0})(\s+.*)?$'.format('|'.join(ACTIONS.keys()))
                interpreter = re.sub(subcmd_pattern, r'', interpreter)
        except Exception as e:
            raise Exception(e)
        return interpreter 


    @classmethod
    def render_usage(cls, usage, /, indent=0, kwargs={}) -> str:
        return '\n' + cls.PerfectTemplate(
            cls.glorify_indents(usage, indent=indent),
        ).perfect_substitute(dict(
            cmd=cls.get_command(),
         ) | copy.deepcopy(kwargs))


    @staticmethod
    def replace_underline(s):
        return s.lower().replace('_', '-')


    @staticmethod
    def replace_hyphen(s):
        return s.lower().replace('-', '_')


    @classmethod
    def rewrite_key(cls, key):
        units = key.lower().split('.')
        units[-1] = cls.replace_hyphen(units[-1])
        for i in range(len(units[:-1])):
            units[i] = cls.replace_underline(units[i])
        return '.'.join(units)


    @classmethod
    def repack_dict(cls, dict_, rewrite_key=None):
        if not rewrite_key:
            rewrite_key = cls.rewrite_key
        for key in dict_:
            new_key = rewrite_key(key)
            if new_key == key:
                continue
            value = dict_.pop(key)
            dict_[new_key] = value
        return dict_


    @classmethod
    def decorate(cls):
        # decorate $NAME
        if not cls.__name__.endswith('BaseAction'):
            cls.NAME = cls.replace_underline(
                re.sub(
                    r'([A-Z])([A-Z][a-z])',
                    r'\1_\2',
                    re.sub(
                        r'([a-z0-9])([A-Z])',
                        r'\1_\2',
                        re.sub(
                            r'Action$', r'', cls.__name__.replace('__', '.'),
                        ),
                    ),
                ),
            )

        # decorate $ARGUMENTS
        if cls.ARGUMENTS is not None:
            cls.repack_dict(cls.PUBLIC_ARGUMENTS, cls.replace_hyphen)
            cls.repack_dict(cls.REQUISITE_ARGUMENTS, cls.replace_hyphen)
            cls.repack_dict(cls.ARGUMENTS, cls.replace_hyphen)

            for argument in cls.REQUISITE_ARGUMENTS:
                if argument in cls.ARGUMENTS:
                    continue
                cls.ARGUMENTS[argument] = copy.deepcopy(cls.REQUISITE_ARGUMENTS[argument])

            for argument in cls.ARGUMENTS: # type: ignore
                public_argument = {}
                use_public = cls.ARGUMENTS[argument].pop('use_public', cls.ReplaceType.NONE)
                if cls.ReplaceType.NONE.ne(use_public):
                    public_argument = copy.deepcopy(cls.PUBLIC_ARGUMENTS[argument])
                match use_public:
                    case cls.ReplaceType.NONE:
                        pass
                    case cls.ReplaceType.ENTIRE:
                        cls.ARGUMENTS[argument] = public_argument
                    case cls.ReplaceType.PARTIAL:
                        if 'args' not in cls.ARGUMENTS[argument]:
                            cls.ARGUMENTS[argument]['args'] = public_argument['args']
                        if 'kwargs' not in cls.ARGUMENTS[argument]:
                            cls.ARGUMENTS[argument]['kwargs'] = public_argument['kwargs']
                        else:
                            cls.ARGUMENTS[argument]['kwargs'] = public_argument['kwargs'] | \
                                                                cls.ARGUMENTS[argument]['kwargs']
                cls.ARGUMENTS[argument]['args'].insert(
                    0, f'--{cls.replace_underline(argument)}',
                )
                cls.ARGUMENTS[argument]['kwargs']['dest'] = argument
                type_ = cls.ARGUMENTS[argument]['kwargs'].get('type', None)
                action_ = cls.ARGUMENTS[argument]['kwargs'].get('action', 'store')
                if 'default' not in cls.ARGUMENTS[argument]['kwargs']:
                    default = None
                    match type_:
                        case str():
                            default = ''
                        case int():
                            default = 0
                    if default is None and action_ == argparse.BooleanOptionalAction:
                        default = True
                    cls.ARGUMENTS[argument]['kwargs']['default'] = default
                if isinstance(cls.ARGUMENTS[argument]['kwargs']['default'], str):
                    if '\n' in cls.ARGUMENTS[argument]['kwargs']['default']:
                        cls.ARGUMENTS[argument]['kwargs']['default'] = cls.glorify_indents(
                            cls.ARGUMENTS[argument]['kwargs']['default'], indent=0,
                        ).strip()

        # decorate $KWARGS
        if cls.KWARGS is not None:
            cls.KWARGS = copy.deepcopy(cls.BASIC_KWARGS) | cls.KWARGS
            if not cls.KWARGS.get('prog', None):
                cls.KWARGS['prog'] = '\n${cmd}'
        # decorate $KWARGS['usage']
        if cls.NAME and cls.ARGUMENTS is not None and cls.KWARGS is not None:
            cls.KWARGS['usage'] = '\n{} {} \\\n'.format(
                '${cmd}', ' '.join(cls.NAME.split('.')),
            )
            indent = 4
            for argument in cls.ARGUMENTS: # type: ignore
                label = cls.ARGUMENTS[argument]['args'][0]
                action_ = cls.ARGUMENTS[argument]['kwargs'].get('action', 'store')
                required = cls.ARGUMENTS[argument]['kwargs'].get('required', False)
                default = '<INPUT>' if required else cls.ARGUMENTS[argument]['kwargs']['default']
                if isinstance(default, str):
                    if '\n' in default:
                        default = cls.glorify_indents(default, indent=indent).strip()
                if action_ == argparse.BooleanOptionalAction:
                    argument_pair = label if default else label.replace('--', '--no-')
                else:
                    argument_pair = f'{label}={default}'
                cls.KWARGS['usage'] += '{}{} \\\n'.format(
                    ' ' * indent, argument_pair,
                )
            cls.KWARGS['usage'] = cls.KWARGS['usage'].rstrip().rstrip('\\').rstrip()


    @log_decorator
    def execute(self):
        pass


    @log_decorator
    def test(self):
        print(self.__class__.__name__, self.NAME)

####################################################V###########################
#                                                                              #
#                                     ACTIONS                                  #
#                                                                              #
################################################################################

class PreprocessNoteAction(AudioGod):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = {
        'description': '✋ Preprocess the note file',
        'help': 'preprocess the note file',
    }

    ARGUMENTS = {
        'document': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'field_type': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
    }

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


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
                    genre = self.format_funcs[self.AudioProperty.GENRE](genre)
                    grouping = self.format_funcs[self.AudioProperty.GROUPING](grouping)
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
                        properties[field] = self.format_funcs[field](value)
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


    @log_decorator
    def execute(self):
        self.output_format = self.FileFormat.NOTE
        self.__analysis_note()
        self.__sort_summaries()
        tmp_file = self.document + '.tmp'
        with open(tmp_file, 'w', encoding='utf-8') as f:
            f.write(self.__summarize_for_note())
        self.backup(self.document)
        self.rename(tmp_file, self.document)

#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

class FillPropertiesAction(AudioGod):
    ACTIVE = True

    #---------------------------------------------------------------------------

    @StringEnum.unique
    class PropertySource(StringEnum):
        COMMAND = 'command'
        FILE = 'file'
        FILENAME = 'filename'
        DIRECTORY = 'directory'

    #---------------------------------------------------------------------------

    KWARGS = {
        'description': '✋ Fill properties of audios',
        'help': 'fill properties of audios',
    }

    ARGUMENTS = {
        'source': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'extensions': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'recursive': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'ignored_file': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'document': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'root': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'properties': {
            'use_public': AudioGod.ReplaceType.NONE,
            'args': ['-p'],
            'kwargs': {
                'action': 'store',
                'type': str,
                'required': False,
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
                'help': 'properties for sources',
            },
        },
    }

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    @log_decorator
    def execute(self):
        pass

#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

class FormatPropertiesAction(AudioGod):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = {
        'description': '✋ Format properties of audios',
        'help': 'format properties of audios',
    }

    ARGUMENTS = {
        'source': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'extensions': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'recursive': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'ignored_file': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
    }

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    @log_decorator
    def execute(self):
        pass

#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

class RenameAudiosAction(AudioGod):
    ACTIVE = True

    #---------------------------------------------------------------------------

    class FilenamePatternTemplate(Template):
        delimiter = '@'

    #---------------------------------------------------------------------------

    KWARGS = {
        'description': '✋ Rename audios',
        'help': 'rename audios',
    }

    ARGUMENTS = {
        'source': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'extensions': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'recursive': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'ignored_file': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'filename_pattern': {
            'use_public': AudioGod.ReplaceType.NONE,
            'args': ['-t'],
            'kwargs': {
                'action': 'store',
                'type': str,
                'required': False,
                'default': '{delimiter}{{artist}} {div_char} {delimiter}{{title}}'.format(
                    delimiter=FilenamePatternTemplate.delimiter,
                    div_char=AudioGod.DIV_CHAR,
                ),
                'help': 'filename pattern to rename sources',
            },
        },
    }

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    @log_decorator
    def execute(self):
        pass

#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

class ListRepeatedAction(AudioGod):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = {
        'description': '✋ List repeated audios by artist and title',
        'help': 'list repeated audios',
    }

    ARGUMENTS = {
        'source': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': '~/Music/Output/Grouped',
            },
        },
        'extensions': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'recursive': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'ignored_file': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'output': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': './repeated.txt',
            },
        },
    }

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    @log_decorator
    def execute(self):
        pass

#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

class DeriveArtworksAction(AudioGod):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = {
        'description': '✋ Derive artworks',
        'help': 'derive artworks',
    }

    ARGUMENTS = {
        'source': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'extensions': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'recursive': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'ignored_file': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'artwork_path': {
            'use_public': AudioGod.ReplaceType.NONE,
            'args': ['-k'],
            'kwargs': {
                'action': 'store',
                'type': str,
                'required': False,
                'default': '~/Music/Output/Artworks',
                'help': 'the path for export artworks',
            },
        },
    }

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    @log_decorator
    def execute(self):
        pass

#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

class DisplayAction(AudioGod):
    ACTIVE = True

    #---------------------------------------------------------------------------

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

    #---------------------------------------------------------------------------

    KWARGS = {
        'description': '✋ Display details of audios',
        'help': 'display details of audios',
    }

    ARGUMENTS = {
        'source': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'extensions': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'recursive': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'ignored_file': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'fields': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'page_number': {
            'use_public': AudioGod.ReplaceType.NONE,
            'args': ['-m'],
            'kwargs': {
                'action': 'store',
                'type': int,
                'required': False,
                'default': 1,
                'help': 'page number for display',
            },
        },
        'page_size': {
            'use_public': AudioGod.ReplaceType.NONE,
            'args': ['-j'],
            'kwargs': {
                'action': 'store',
                'type': int,
                'required': False,
                'default': 0,
                'help': 'page size for display',
            },
        },
        'sort': {
            'use_public': AudioGod.ReplaceType.NONE,
            'args': ['-q'],
            'kwargs': {
                'action': 'store',
                'type': str,
                'required': False,
                'default': '''
                    \'[
                        {"_comment": ""},
                        ["title,artist", true],
                        ["genre", false]
                    ]\'
                ''',
                'help': 'sort options for display',
            },
        },
        'filter': {
            'use_public': AudioGod.ReplaceType.NONE,
            'args': ['-b'],
            'kwargs': {
                'action': 'store',
                'type': str,
                'required': False,
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
                'help': 'filter options for display',
            },
        },
        'align': {
            'use_public': AudioGod.ReplaceType.NONE,
            'args': ['-w'],
            'kwargs': {
                'action': 'store',
                'type': str,
                'required': False,
                'default': '''
                    \'{
                        "_comment": "align=l/c/r, valign=t/m/b",
                        "title,artist": "l:m"
                    }\'
                ''',
                'help': 'align options for display',
            },
        },
        'style': {
            'use_public': AudioGod.ReplaceType.NONE,
            'args': ['-y'],
            'kwargs': {
                'action': 'store',
                'type': str,
                'choices': DisplayStyle.members(),
                'required': False,
                'default': DisplayStyle.TABLED,
                'help': 'style for display',
            },
        },
        'data_format': {
            'use_public': AudioGod.ReplaceType.NONE,
            'args': ['-x'],
            'kwargs': {
                'action': 'store',
                'type': str,
                'choices': DataFormat.members(),
                'required': False,
                'default': DataFormat.OUTPUTTED,
                'help': 'data format for display',
            },
        },
        'numbered': {
            'use_public': AudioGod.ReplaceType.NONE,
            'args': ['-n'],
            'kwargs': {
                'action': argparse.BooleanOptionalAction,
                'required': False,
                'default': True,
                'help': 'if show number when display',
            },
        },
        'field_type': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'output': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
    }

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    @log_decorator
    def execute(self):
        pass

#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

class GenerateScriptAction(AudioGod):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = {
        'description': '✋ Generate a grouped bash/zsh script',
        'help': 'generate a grouped bash/zsh script',
    }

    ARGUMENTS = {
        'output': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': './start.zsh',
            },
        },
    }

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    @log_decorator
    def execute(self):
        pass

#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

class OrganizeBaseAction(AudioGod):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = None
    ARGUMENTS = None
    
    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    @log_decorator
    def execute(self):
        pass

#===============================================================================

class OrganizeAction(OrganizeBaseAction):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = {
        'description': '✋ Organize files',
        'help': 'organize files',
    }

    ARGUMENTS = None

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        pass


    @log_decorator
    def execute(self):
        pass

#===============================================================================

class Organize__GroupedAction(OrganizeBaseAction):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = {
        'description': '⭐ Organize grouped files',
        'help': 'organize grouped files',
    }

    ARGUMENTS = {
        'source': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'extensions': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'recursive': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'ignored_file': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'root': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': '~/Music/Output/Grouped',
            },
        },
    }

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    @log_decorator
    def execute(self):
        pass

#===============================================================================

class Organize__ItunedAction(OrganizeBaseAction):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = {
        'description': '⭐ Organize ituned files',
        'help': 'organize ituned files',
    }

    ARGUMENTS = {
        'source': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': '~/Music/Output/Grouped',
            },
        },
        'extensions': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'recursive': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'ignored_file': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'root': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
    }

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    @log_decorator
    def execute(self):
        pass

#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

class ExportBaseAction(AudioGod):
    ACTIVE = True

    #---------------------------------------------------------------------------

    DEFAULT_GENRE = 'Default'
    DEFAULT_GROUPING = 'Default'
    
    AUDIOS_TREE_ROOT_TAG = '--root-tag--'
    AUDIOS_TREE_ROOT_NID = '--root-nid--'

    #---------------------------------------------------------------------------

    @StringEnum.unique
    class AudiosTreeNodeType(StringEnum):
        ROOT = 'root'
        FOLDER = 'folder'
        PLAYLIST = 'playlist'
        TRACK = 'track'

    #---------------------------------------------------------------------------

    class TreeX(Tree):
        def __init__(self, logger=None, *args, **kwargs):
            super().__init__(*args, **kwargs)
            if logger is None:
                logger = logging.getLogger()
            self.logger = logger
    
        def perfect_merge(self, nid, new_tree, deep=False) -> None:
            if not (isinstance(new_tree, Tree) or isinstance(new_tree, self.__class__)):
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

    #---------------------------------------------------------------------------

    KWARGS = None
    ARGUMENTS = None

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    @log_decorator
    def execute(self):
        pass

#===============================================================================

class ExportAction(ExportBaseAction):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = {
        'description': '✋ Export audio details to file',
        'help': 'export audio details to file',
    }

    ARGUMENTS = None

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        pass


    @log_decorator
    def execute(self):
        pass

#===============================================================================

class Export__NoteAction(ExportBaseAction):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = {
        'description': '⭐ Export audio details to note file',
        'help': 'export audio details to note file',
    }

    ARGUMENTS = {
        'source': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': '~/Music/Output/Grouped',
            },
        },
        'extensions': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'recursive': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'ignored_file': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'fields': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': 'note',
            },
        },
        'field_type': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'output': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': './songs.note',
            },
        },
    }

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    @log_decorator
    def execute(self):
        pass

#===============================================================================

class Export__PlistAction(ExportBaseAction):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = {
        'description': '⭐ Export audio details to plist file',
        'help': 'export audio details to plist file',
    }

    ARGUMENTS = {
        'source': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'extensions': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'recursive': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'ignored_file': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'fields': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': 'ituned',
            },
        },
        'field_type': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': AudioGod.FieldType.ENGLISH,
            },
        },
        'output': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': '~/Music/iTunes/Library.xml',
            },
        },
        'itunes_version_plist': {
            'use_public': AudioGod.ReplaceType.NONE,
            'args': ['-1'],
            'kwargs': {
                'action': 'store',
                'type': str,
                'required': False,
                'default': '/System/Applications/Music.app/Contents/version.plist',
                'help': 'the version plist file of itunes or apple music',
            },
        },
        'itunes_media_folder': {
            'use_public': AudioGod.ReplaceType.NONE,
            'args': ['-2'],
            'kwargs': {
                'action': 'store',
                'type': str,
                'required': False,
                'default': '~/Music/iTunes/iTunes\ Media/Music', # type: ignore
                'help': 'the media folder of itunes or apple music',
            },
        },
        'track_initial_id': {
            'use_public': AudioGod.ReplaceType.NONE,
            'args': ['-3'],
            'kwargs': {
                'action': 'store',
                'type': int,
                'required': False,
                'default': 601,
                'help': 'initial id of tracks for itunes or apple music plist file',
            },
        },
        'playlist_initial_id': {
            'use_public': AudioGod.ReplaceType.NONE,
            'args': ['-4'],
            'kwargs': {
                'action': 'store',
                'type': int,
                'required': False,
                'default': 3001,
                'help': 'initial id of playlists for itunes or apple music plist file',
            },
        },
    }

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    @log_decorator
    def execute(self):
        pass

#===============================================================================

class Export__MarkdownAction(ExportBaseAction):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = {
    }

    ARGUMENTS = {
    }

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    @log_decorator
    def execute(self):
        pass

#===============================================================================

class Export__XmlAction(ExportBaseAction):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = {
    }

    ARGUMENTS = {
    }

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    @log_decorator
    def execute(self):
        pass

#===============================================================================

class Export__JsonAction(ExportBaseAction):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = {
    }

    ARGUMENTS = {
    }

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    @log_decorator
    def execute(self):
        pass

#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

class ConvertBaseAction(AudioGod):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = None
    ARGUMENTS = None

    PUBLIC_ARGUMENTS = copy.deepcopy(AudioGod.PUBLIC_ARGUMENTS) | {
        'executer': {
            'args': ['-9'],
            'kwargs': {
                'action': 'store',
                'type': str,
                'required': False,
                'default': '',
                'help': 'the executer for convert sources',
            },
        },
    }

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    @log_decorator
    def execute(self):
        pass

#===============================================================================

class ConvertAction(ConvertBaseAction):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = {
        'description': '✋ Convert media',
        'help': 'convert media',
    }

    ARGUMENTS = None

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        pass


    @log_decorator
    def execute(self):
        pass

#===============================================================================

class Convert__QmcToMp3Action(ConvertBaseAction):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = {
        'description': '⭐ Convert qmc to mp3',
        'help': 'convert qmc to mp3',
    }

    ARGUMENTS = {
        'source': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'extensions': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'recursive': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'ignored_file': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'executer': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': './executers/qmc-to-mp3/decoder',
            },
        },
    }

    #---------------------------------------------------------------------------
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    @log_decorator
    def execute(self):
        pass

#===============================================================================

class Convert__KmxToMp4Action(ConvertBaseAction):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = {
    }

    ARGUMENTS = {
    }

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    @log_decorator
    def execute(self):
        pass

#===============================================================================

class Convert__Mp4ToMp3Action(ConvertBaseAction):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = {
    }

    ARGUMENTS = {
    }

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    @log_decorator
    def execute(self):
        pass

#===============================================================================

class Convert__NoteToMarkdownAction(ConvertBaseAction):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = {
    }

    ARGUMENTS = {
    }

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    @log_decorator
    def execute(self):
        pass

#===============================================================================

class Convert__MarkdownToNoteAction(ConvertBaseAction):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = {
    }

    ARGUMENTS = {
    }

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    @log_decorator
    def execute(self):
        pass

#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

class OperateBaseAction(AudioGod):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = None
    ARGUMENTS = None

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    @log_decorator
    def execute(self):
        pass

#===============================================================================

class OperateAction(OperateBaseAction):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = {
        'description': '✋ Some common operations',
        'help': 'some common operations',
    }

    ARGUMENTS = None

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        pass


    @log_decorator
    def execute(self):
        pass

#===============================================================================

class Operate__BackupAction(OperateBaseAction):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = {
        'description': '⭐ Backup files, directories and so on',
        'help': 'backup files, directories and so on',
    }

    ARGUMENTS = {
        'source': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'required': True,
                'default': '',
            },
        },
        'ignored_file': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
    }

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    @log_decorator
    def execute(self):
        pass

#===============================================================================

class Operate__RemoveAction(OperateBaseAction):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = {
        'description': '⭐ Remove files, directories and so on',
        'help': 'remove files, directories and so on',
    }

    ARGUMENTS = {
        'source': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'required': True,
                'default': '',
            },
        },
        'ignored_file': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
    }

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    @log_decorator
    def execute(self):
        pass

#===============================================================================

class Operate__CleanupAction(OperateBaseAction):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = {
        'description': '⭐ Cleanup directories, backups and so on',
        'help': 'cleanup directories, backups and so on',
    }

    ARGUMENTS = {}

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    @log_decorator
    def execute(self):
        pass

####################################################V###########################

def _get_all_subclasses(cls):
    all_subclasses = []
    for subclass in cls.__subclasses__():
        all_subclasses.append(subclass)
        all_subclasses.extend(_get_all_subclasses(subclass))
    return all_subclasses


def _get_active_subclasses(cls):
    ret = []
    for subclass in _get_all_subclasses(cls):
        if not subclass.ACTIVE:
            continue
        ret.append(subclass)
    return ret


def _decorate_actions():
    for cls in _get_active_subclasses(AudioGod):
        cls.decorate()


def _summarize_actions():
    ret = {}
    for cls in _get_active_subclasses(AudioGod):
        if not cls.NAME:
            continue
        units = cls.NAME.split('.')
        match len(units):
            case 1:
                if units[0] not in ret:
                    ret[units[0]] = { 'carrier': cls }
                else:
                    ret[units[0]]['carrier'] = cls
            case 2:
                if units[0] not in ret:
                    ret[units[0]] = { 'branches': { units[1]: { 'carrier': cls } } }
                else:
                    if 'branches' not in ret[units[0]]:
                        ret[units[0]]['branches'] = { units[1]: { 'carrier': cls } }
                    else:
                        ret[units[0]]['branches'][units[1]] = { 'carrier': cls }
    return ret


def _summarize_actions_defaults():
    ret = {}
    for cls in _get_active_subclasses(AudioGod):
        if not cls.NAME or not cls.ARGUMENTS:
            continue
        defaults = copy.deepcopy(cls.ARGUMENTS_DEFAULTS())
        if not defaults:
            continue
        for argument, default in defaults.items():
            ret[f'{cls.NAME}.{argument}'] = default
    return ret


def _render_actions():
    for cls in _get_active_subclasses(AudioGod):
        if not cls.KWARGS:
            continue
        if cls.KWARGS.get('prog', None):
            cls.KWARGS['prog'] = AudioGod.render_usage(
                cls.KWARGS['prog'],
                indent=0,
            )
        if cls.KWARGS.get('usage', None):
            cls.KWARGS['usage'] = AudioGod.render_usage(
                cls.KWARGS['usage'],
                indent=0,
            )

#-------------------------------------------------------------------------------

_decorate_actions()
ACTIONS = _summarize_actions()
ACTIONS_DEFAULTS = _summarize_actions_defaults()
_render_actions()

#-------------------------------------------------------------------------------

def _get_carrier(action, branch):
    if not action:
        return None
    if action not in ACTIONS:
        return None
    if not branch:
        if 'carrier' not in ACTIONS[action]:
            return None
        return ACTIONS[action]['carrier']
    if 'branches' not in ACTIONS[action]:
        return None
    if branch not in ACTIONS[action]['branches']:
        return None
    if 'carrier' not in ACTIONS[action]['branches'][branch]:
        return None
    return ACTIONS[action]['branches'][branch]['carrier']


def _get_carrier_arguments(action, branch):
    carrier = _get_carrier(action, branch)
    if carrier is None:
        return None
    return copy.deepcopy(carrier.ARGUMENTS)


def _get_carrier_defaults(action, branch):
    carrier = _get_carrier(action, branch)
    if carrier is None:
        return {}
    return copy.deepcopy(carrier.ARGUMENTS_DEFAULTS())


def _get_carrier_kwargs(action, branch):
    carrier = _get_carrier(action, branch)
    if carrier is None:
        return None
    return copy.deepcopy(carrier.KWARGS)

####################################################V###########################
#                                                                              #
#                                 MAIN FUNCTION                                #
#                                                                              #
################################################################################

class PerfectArgumentParser(argparse.ArgumentParser):
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
        for (action, branch), subparser in self.__subparsers:
            symbol = '-' if branch else '@'
            label = 'Branch' if branch else 'Action'
            command = f'{action} {branch}' if branch else action
            help_text += '\n' + symbol * 78 + '\n'
            help_text += f'\n🔥 {label} command <{command}> help info:\n\n'
            help_text += subparser.format_help()
        return help_text

    def print_help(self):
        pydoc.pager(self.format_help())
        self.exit(0)

#-------------------------------------------------------------------------------

def _add_arguments(parser, arguments) -> None:
    for _, params in arguments.items():
        parser.add_argument(*params['args'], **params['kwargs'])


def _handle_execute(args) -> None:
    action, branch = args.action, None
    if hasattr(args, 'branch'):
        branch = args.branch

    carrier = _get_carrier(action, branch)
    if carrier is None:
        raise Exception(f'Invalid carrier <{action} {branch}>!')

    arguments = _get_carrier_defaults(action, branch)
    for argument in arguments:
        if hasattr(args, argument):
            arguments[argument] = getattr(args, argument)

    #carrier(**arguments).test()
    carrier(**arguments).execute()


def _add_subparser(mainparser, subparsers, action, branch=None):
    kwargs = _get_carrier_kwargs(action, branch)
    if not kwargs:
        raise Exception(f'Invalid carrier by <{action} {branch}>!')
    subparser = subparsers.add_parser(branch if branch else action, **kwargs)

    arguments = _get_carrier_arguments(action, branch)
    if arguments:
        _add_arguments(subparser, arguments)

    subparser.set_defaults(execute=_handle_execute)
    mainparser.add_subparser(((action, branch), subparser))

    return subparser

#-------------------------------------------------------------------------------

def _audio_properties() -> str:
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
    for number, field in enumerate(AudioGod.ALL_FIELDS):
        chinese_name = AudioGod.AUDIO_PROPERTIES[field][0][0]
        english_name = AudioGod.AUDIO_PROPERTIES[field][0][1]
        field_type = AudioGod.AUDIO_PROPERTIES[field][1]
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


def _special_fields() -> str:
    table = PrettyTable()
    table.field_names = AudioGod.FIELDS.keys()
    for field in table.field_names:
        table.align[field] = 'l'
    rows = list(AudioGod.FIELDS.values())
    for j in range(len(AudioGod.ALL_FIELDS)):
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


def _special_characters() -> str:
    table = PrettyTable()
    table.field_names = [
        'Number',
        'Character',
        'Introduction',
    ]
    for field in table.field_names:
        table.align[field] = 'l'
    characters = [
        (AudioGod.ORI_DIV_CHAR, 'Separator for origin audio file name.'),
        (AudioGod.DIV_CHAR, 'Separator for formatted audio file name.'),
        (AudioGod.GROUPING_SEPARATOR, 'Separator for several grouping property of audio file.'),
        (RenameAudiosAction.FilenamePatternTemplate.delimiter, 'Delimiter of template for filename pattern.'),
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

#-------------------------------------------------------------------------------

def main():
    main_parser = PerfectArgumentParser(
        prog=sys.argv[0],
        usage=AudioGod.render_usage(
            __USAGE__,
            indent=0,
            kwargs=dict(
                audio_properties=_audio_properties(),
                special_fields=_special_fields(),
                special_characters=_special_characters(),
                ori_div_char=AudioGod.ORI_DIV_CHAR,
                div_char=AudioGod.DIV_CHAR,
                grouping_sep=AudioGod.GROUPING_SEPARATOR,
                fnp_delimiter=RenameAudiosAction.FilenamePatternTemplate.delimiter,
                cache_dir=f'~/{os.path.basename(AudioGod.CACHE_DIR)}',
                trash_dir=os.path.basename(AudioGod.TRASH_DIR),
                backups_dir=os.path.basename(AudioGod.BACKUPS_DIR),
            ) | ACTIONS_DEFAULTS,
        ),
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
        title='🎉 Actions',
        description='🫡 the available actions show below:',
        dest='action',
        required=False,
        parser_class=PerfectArgumentParser,
        metavar='<action-name>',
        help='action statement',
    )

    for action in ACTIONS:
        action_parser = _add_subparser(
            mainparser=main_parser,
            subparsers=action_parsers,
            action=action,
            branch=None,
        )
        if 'branches' in ACTIONS[action]:
            branch_parsers = action_parser.add_subparsers(
                prog=sys.argv[0],
                title='🤝 Branches',
                description='🦁 the available branches show below:',
                dest='branch',
                required=False,
                metavar='<branch-name>',
                help='branch statement',
            )
            for branch in ACTIONS[action]['branches']:
                _ = _add_subparser(
                    mainparser=action_parser,
                    subparsers=branch_parsers,
                    action=action,
                    branch=branch,
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
