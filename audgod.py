#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2025 Anebit Inc.
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
# Created: 2025-06-30 10:46:00
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
#       pyfiglet = "==1.0.3"
#       pydub = "==0.25.1"
#       tqdm = "==4.67.1"
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
#   1. iCloud Path: ~/Library/Mobile\ Documents/com~apple~CloudDocs/;
#   2. Mac Application Cache Path: ~/Library/Containers/;
#   3. QQMusic Download Path: ~/Library/Containers/com.tencent.QQMusicMac/Data/Library/Application\ Support/QQMusicMac/iQmc/;
#   4. Youku Download Path: ~/Library/Containers/com.youku.mac/Data/download.
#
# ---
# Tools:
#   1.  Apple Music Help Online: https://support.apple.com/en-hk/HT210403;
#   2.  Mac Audio Processor: https://amvidia.com;
#   3.  Online Small Tools: https://tool.lu;
#   4.  Format Convert: https://www.aconvert.com;
#   5.  Format Convert: https://audio.worthsee.com/convert;
#   6.  Videos Download: https://github.com/iawia002/annie;
#   7.  Audio Convert: https://github.com/jiaaro/pydub;
#   8.  QMC->MP3: https://openyyy.com;
#   9.  MGG->OGG: https://www.ncmdump.net;
#   9.  QMC->MP3: https://github.com/Presburger/qmc-decoder;
#   10. QMC->MP3: https://gitcode.com/gh_mirrors/qm/qmc-decoder;
#   11. QMC->MP3: https://github.com/MegrezZhu/qmcdump;
#   12. QMC->MP3: https://github.com/42arch/qmc_file_decrypter;
#   13. KMX->MP4: https://gitee.com/aprl/kmx-MP4;
#   14. MP4->MP3: https://pypi.org/project/ffmpy3;
#   15. MP4->MP3: https://github.com/wchill/ffmpy3;
#   16. MP4->MP3: https://pypi.org/project/moviepy;
#   17. MP4->MP3: https://github.com/Zulko/moviepy;
#   18. MP4->MP3: https://github.com/SiD-93/BatchMP3;
#   19. MGG->MP3: https://github.com/nukemiko/libtakiyasha;
#   20  MGG->MP3: https://gitcode.com/gh_mirrors/li/libtakiyasha;
#   20  MGG->OGG: https://github.com/taurusxin/ncmdump;
#   20  MGG->OGG: https://git.taurusxin.com/taurusxin/ncmdump-go;
#   20  MGG->OGG: https://git.taurusxin.com/taurusxin/ncmdump-gui;
#   21  Bilibili: https://snapany.com/zh/bilibili;
#   20  QMC->MP3: https://git.unlock-music.dev/um/cli.
#
# ---
# Commands:
#   1. View Directory Structure: "tree -dN ~/Music".
#
# ---
# Notes:
#   1. None.
#
# ---
# FAQs:
#   1. 项目依赖很多第三方库，需要一一验证确认是否线程安全，因此，本项目暂不支持多线程；
#   2. pipenv 依赖于 pyenv，如果异常，建议先 "pyenv uninstall (python)X.X.X"，
#      然后再重新 "pyenv install (python)X.X.X"；安装完成后，需要在 ~/.zshrc
#     （或者 ~/.bashrc、~/.bash_profile）文件最下方添加如下内容并重载 => ```
#          export PYENV_ROOT="$HOME/.pyenv"
#          export PATH="$PYENV_ROOT/bin:$PATH"
#          eval "$(pyenv init -)"
#      ```
#
# ---
# TODO (@Richard):
#   1. None.
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
import shlex
import random
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
import pyfiglet

from tqdm import tqdm
from enumx import StringEnum
from treelib.tree import Tree
from prettytable import PrettyTable

import eyed3
from eyed3.id3 import Genre, frames
from eyed3.id3.tag import CommentsAccessor

from pydub import AudioSegment

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

Original  audio file name: "artist${filename_separator}title.mp3"
Formatted audio file name: "artist ${filename_separator} title.mp3"
Pattern of filename to rename: "${fnp_delimiter}{artist} ${filename_separator} ${fnp_delimiter}{title}"

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
    Here is the audio god root folder, which contains cache, source and output folder under it.
    You can reset by shell environment variable "AUDGOD_ROOT".
    You should clear the cache directory when the size is too big.
        ${audgod_root}
          ├── ${audgod_source}
          ├── ${audgod_output}
          └── ${audgod_cache}
                ├── ${audgod_trash}
                └── ${audgod_backup}

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
    Step.2: Download songs, and make sure that file named with "artist${filename_separator}title";
    Step.3: Add detail of songs to original notes, then grouped.

Process Method 1:
    Step.1: Redecorate note, until note file not changed, with subcommand <redecorate-note>;
    Step.2: Fill properties, with subcommand <fill-properties>;
    Step.3: Format properties, with subcommand <format-properties>;
    Step.4: Rename audios, with subcommand <rename-audios>;
    Step.5: Organize grouped files, with subcommand <organize grouped>;
    Step.6: Export note file, with subcommand <export note>;
    Step.7: List repeated audios of grouped, with subcommand <list-repeated>;
    Step.8: Organize ituned files, with subcommand <organize ituned>;
    Step.9: Export plist file, with subcommand <export plist>.

Process Method 2:
    Step.1: Put original note file to source folder (e.g. "${redecorate-note.document}");
    Step.2: Put audio folders named with different extensions or media to source folder (e.g. "${fill-properties.source}");
    Step.3: Put ignored file to source folder (e.g. "${fill-properties.ignored_file}");
    Step.4: Put artworks under a folder to source folder (e.g. "${manage-artworks.bind.artworks}");
    Step.5: Run <generate-script start> subcommand to generate a shell script (e.g. "${generate-script.start.output}");
    Step.6: Execute the shell script above.
    Results under folders below:
        ${audgod_root}
          └── ${audgod_output}
        ${export.plist.output}
        ${organize.ituned.output}

--------------------------------------------------------------------------------

Update steps:

    Read the ./test.zsh file, and follow the steps to update the library when add new songs.

--------------------------------------------------------------------------------

Testing steps:

Ready:
    Step.1: Make sure folder "${testing_root}" is ready;
    Step.2: Make sure folder "${testing_origin}" is ready;
    Step.3: Make sure folder "${testing_orisrc}" is ready;
    Step.4: Put test note origin file to "${testing_orisrc}";
    Step.5: Put test ignored file to "${testing_orisrc}";
    Step.6: Put test media under folders with different extensions to "${testing_orisrc}";
    Step.7: Put test artworks under folder to "${testing_orisrc}";
    step.8: Put files for backup and remove testing to "${testing_orisrc}".

Process Method:
    Step.1: Run <testing generate-script> subcommand to generate a shell script for testing;
    Step.2: Execute the shell script above.

Attention:
    1. Cache folder for testing is "${testing_cache}";
    2. Folders named with different extensions under "${testing_source}";
    3. Outputs are under local folder or "${testing_output}".

--------------------------------------------------------------------------------

'''

################################################################################
#                                                                              #
#                                  DECORATORS                                  #
#                                                                              #
################################################################################

def log_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print_func, func_name = print, func.__name__.replace('_', '-')
        instance = args[0] if args else None
        if instance:
            logger = getattr(instance, 'logger', None)
            if logger:
                print_func = logger.warning
            if instance.__class__.NAME:
                func_name = f'{instance.__class__.NAME}.{func_name}'
        start_time = time.time()
        print_func(f'(###) Starting <{func_name}> ...\n')
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            cost_time = time.time() - start_time
            print_func(f'\n(###) <{func_name}> finished, cost {cost_time:.2f} seconds.\n')
    return wrapper

################################################################################
#                                                                              #
#                                 AUDIO GOD                                    #
#                                                                              #
################################################################################

class BASEOPTIONS(object):
    ARTIST_SEPARATOR = ','
    GROUPING_SEPARATOR = '|'

#===============================================================================

def refresh_options(cls):
    cls.AUDGOD_SOURCE = os.path.join(cls.AUDGOD_ROOT, 'Source')
    cls.AUDGOD_OUTPUT = os.path.join(cls.AUDGOD_ROOT, 'Output')

    cls.AUDGOD_CACHE  = os.path.join(cls.AUDGOD_ROOT, '__AUDGOD_CACHE__')
    cls.AUDGOD_TRASH  = os.path.join(cls.AUDGOD_CACHE, 'trash')
    cls.AUDGOD_BACKUP = os.path.join(cls.AUDGOD_CACHE, 'backup')

    return cls

#===============================================================================

@refresh_options
class OPTIONS(BASEOPTIONS):
    AUDGOD_ROOT = os.environ['AUDGOD_ROOT'] \
                    if os.environ.get('AUDGOD_ROOT', '').strip() \
                    else '~/Music'

#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

class AudioGod(OPTIONS):

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
                    log_file, encoding='utf-8', delay=False,
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
        PLIST = 'plist'
        XML = 'xml'


    @StringEnum.unique
    class FieldType(StringEnum):
        ORIGINAL = 'ori'
        CHINESE = 'cn'
        ENGLISH = 'en'
        AUTO = 'auto'


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

    DEFAULT_FIELDS = [
        AudioProperty.TITLE,
        AudioProperty.ARTIST,
        AudioProperty.ALBUM,
        AudioProperty.GENRE,
        AudioProperty.ALBUM_ARTIST,
    ]

    BASIC_FIELDS = [
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
        'basic': BASIC_FIELDS,
        'default': DEFAULT_FIELDS,
        'simple': SIMPLE_FIELDS,
        'core': CORE_FIELDS,
        'zip': ZIP_FIELDS,
        'note': BASIC_FIELDS,
        'ituned': ITUNED_FIELDS,
    }

    #---------------------------------------------------------------------------

    NAME = ''
    PROG = ''
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
                'default': f'{OPTIONS.AUDGOD_SOURCE}/origin.songs.note.txt',
                'help': 'document to load',
            },
        },
        'ignored_file': {
            'args': ['-i'],
            'kwargs': {
                'action': 'store',
                'type': str,
                'required': False,
                'default': f'{OPTIONS.AUDGOD_SOURCE}/ignores.txt',
                'help': 'ignored files when load',
            },
        },
        'source': {
            'args': ['-c'],
            'kwargs': {
                'action': 'store',
                'type': str,
                'required': False,
                'default': f'{OPTIONS.AUDGOD_SOURCE}/Mp3',
                'help': 'files or directories you want to process',
            },
        },
        'another': {
            'args': ['-z'],
            'kwargs': {
                'action': 'store',
                'type': str,
                'required': True,
                'default': '',
                'help': 'another item to merge',
            },
        },
        'root': {
            'args': ['-d'],
            'kwargs': {
                'action': 'store',
                'type': str,
                'required': False,
                'default': f'{OPTIONS.AUDGOD_SOURCE}/Mp3',
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
        'separators': {
            'args': ['-6'],
            'kwargs': {
                'action': 'store',
                'type': str,
                'required': False,
                'default': '-,#',
                'help': 'separators for matched filename',
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
            self.parameters['log_level'],
            self.parameters['log_file'],
        )
        eyed3.log.setLevel(logging.ERROR)


        self.__sources = ([], [], [], [], [])
        self.__ignored_set = set()


        self.__parse_funcs = {
            field: getattr(
                self, f'parse_{field}', lambda x: x,
            )
            for field in self.FIELDS['all']
        }
        def __parse_func(parse_func):
            def __func(*args):
                ret = parse_func(*args)
                return ret
            return __func
        self.__parse_funcs = {
            field: __parse_func(self.__parse_funcs[field])
            for field in self.FIELDS['all']
        }

        self.__format_funcs = {
            field: getattr(
                self, f'format_{field}', lambda x: x,
            )
            for field in self.FIELDS['all']
        }
        def __format_func(format_func):
            def __func(*args):
                ret = format_func(*args)
                return ret
            return __func
        self.__format_funcs = {
            field: __format_func(self.__format_funcs[field])
            for field in self.FIELDS['all']
        }

        self.__output_funcs = {
            field: getattr(
                self,
                f'output_{field}',
                lambda x, output_format=self.FileFormat.NONE: x,
            )
            for field in self.FIELDS['all']
        }
        def __output_func(output_func):
            def __func(*args):
                ret = output_func(*args)
                if (not isinstance(ret, int)) and (not isinstance(ret, float)) and (not ret):
                    return None
                return ret
            return __func
        self.__output_funcs = {
            field: __output_func(self.__output_funcs[field])
            for field in self.FIELDS['all']
        }


        self.rewrite_parameters()

    #---------------------------------------------------------------------------

    def rewrite_parameters(self):
        if 'fields' in self.parameters:
            self.parameters['fields'] = [
                self.AudioProperty(x) for x in self.resolve_fields(
                    self.parameters['fields'],
                    sortify=False,
                    reversify=False,
                    stringify=False,
                )
            ]

        if 'source' in self.parameters:
            self.parameters['source'] = self.abspath(
                self.parameters['source'],
            )
            if not self.parameters['source']:
                self.logger.fatal(f'Source <{self.parameters["source"]}> invalid!')
                return

        if 'recursive' in self.parameters:
            pass

        if 'extensions' in self.parameters:
            self.parameters['extensions'] = self.split(
                self.parameters['extensions'].lower(),
                ',',
                escaped=True,
                del_blank=True,
                filt_empty=True,
                filt_repeated=True,
                sortify=False,
                reversify=False,
            )

        if 'document' in self.parameters:
            self.parameters['document'] = self.abspath(
                self.parameters['document'],
            )
            if not self.parameters['document']:
                self.logger.fatal(f'File <{self.parameters["document"]}> invalid!')
                return
            if not os.path.exists(self.parameters['document']):
                self.logger.fatal(f'File <{self.parameters["document"]}> not exists!')
                return
            if not os.path.isfile(self.parameters['document']):
                self.logger.fatal(f'<{self.parameters["document"]}> is not file!')
                return

        if 'another' in self.parameters:
            self.parameters['another'] = self.abspath(
                self.parameters['another'],
            )
            if self.parameters['another']:
                if not os.path.exists(self.parameters['another']):
                    self.logger.fatal(f'Another <{self.parameters["another"]}> not exists!')
                    return

        if 'ignored_file' in self.parameters:
            self.parameters['ignored_file'] = self.abspath(
                self.parameters['ignored_file'],
            )
            if self.parameters['ignored_file']:
                if not os.path.exists(self.parameters['ignored_file']):
                    self.logger.fatal(f'File <{self.parameters["ignored_file"]}> not exists!')
                    return
                if not os.path.isfile(self.parameters['ignored_file']):
                    self.logger.fatal(f'<{self.parameters["ignored_file"]}> is not file!')
                    return

        if 'output' in self.parameters:
            self.parameters['output'] = self.abspath(
                self.parameters['output'],
            )

        if 'field_type' in self.parameters:
            self.parameters['field_type'] = self.FieldType(
                self.parameters['field_type'],
            )

        if 'separators' in self.parameters:
            self.parameters['separators'] = self.split(
                self.parameters['separators'],
                ',',
                escaped=True,
                del_blank=True,
                filt_empty=True,
                filt_repeated=True,
                sortify=False,
                reversify=False,
            )
            if not self.parameters['separators']:
                self.logger.fatal('Separators empty!')
                return

    #---------------------------------------------------------------------------

    def reset_parameters(self, kwargs={}):
        self.parameters.update(kwargs)

    #---------------------------------------------------------------------------

    @property
    def parameters(self):
        return self.__parameters


    @property
    def logger(self):
        return self.__logger


    @property
    def original_sources(self):
        return self.__sources[0]

    @property
    def primed_sources(self):
        return self.__sources[1]

    @property
    def invalid_ext_sources(self):
        return self.__sources[2]

    @property
    def omitted_sources(self):
        return self.__sources[3]

    @property
    def ignored_sources(self):
        return self.__sources[4]

    @property
    def ignored_set(self):
        return self.__ignored_set


    @property
    def format_funcs(self):
        return self.__format_funcs

    @property
    def parse_funcs(self):
        return self.__parse_funcs

    @property
    def output_funcs(self):
        return self.__output_funcs

    #---------------------------------------------------------------------------

    @classmethod
    def format_title(cls, title):
        if title is None:
            return None
        ret = re.sub(r'\s*&\s*', r', ', title)
        return cls.unify_format(ret)

    @classmethod
    def format_artist(cls, artist):
        if artist is None:
            return None
        ret = cls.unify_format(artist)
        ret = re.sub(r'[&/,]', cls.ARTIST_SEPARATOR, ret)
        #ret = re.sub(fr'{cls.ARTIST_SEPARATOR}', f' {cls.ARTIST_SEPARATOR} ', ret)
        ret = re.sub(fr'\s*{cls.ARTIST_SEPARATOR}\s*', f'{cls.ARTIST_SEPARATOR}', ret)
        #ret = re.sub(r'([a-zA-Z]\.){2,}', lambda m: m.group(0).replace(' ', ''), ret)
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
            ret[0] = int(value[0])
        if len(value) > 1:
            ret[1] = int(value[1])
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

    #---------------------------------------------------------------------------

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
                 .replace('｜', '|')\
                 .replace('——', '-')
                 #.replace('【', '[')\
                 #.replace('】', ']')\
                 #.replace('《', '<')\
                 #.replace('》', '>')\
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
    def transform_utc(timestamp) -> str:
        #return datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%dT%H:%M:%SZ')
        return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%dT%H:%M:%SZ')


    @classmethod
    def current_time(cls) -> str:
        return cls.transform_utc(time.time())


    @staticmethod
    def timestamp():
        return datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')


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
        if os.path.isdir(src):
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)


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


    def init_cache(self):
        def _init_path(path):
            if not os.path.exists(path):
                os.makedirs(self.abspath(path), exist_ok=True)
                return
            if not os.path.isdir(path):
                self.logger.fatal(f'Path <{path}> not a directory!')
                return
        _init_path(self.AUDGOD_CACHE)
        _init_path(self.AUDGOD_TRASH)
        _init_path(self.AUDGOD_BACKUP)


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


    @classmethod
    def treat_basename(cls, src, tag=''):
        ret = f'{cls.timestamp()}.{os.path.basename(src)}'
        if tag:
            ret = f'{tag}.{ret}'
        return ret


    def remove(self, *paths):
        self.init_cache()
        for path in paths:
            if not path:
                continue
            unit = path if isinstance(path, (tuple, list)) else [path]
            for item in self.expand_globbing(*unit):
                if os.path.exists(item):
                    os.rename(
                        item, os.path.join(
                            self.abspath(self.AUDGOD_TRASH),
                            self.treat_basename(item, 'trash'),
                        ),
                    )
                else:
                    self.logger.debug(f'Remove warning: File {item} not exists!')


    def backup(self, *srcs):
        self.init_cache()
        for src in srcs:
            if not src:
                continue
            unit = src if isinstance(src, (tuple, list)) else [src]
            for item in self.expand_globbing(*unit):
                if os.path.exists(item):
                    self.duplicate(
                        item, os.path.join(
                            self.abspath(self.AUDGOD_BACKUP),
                            self.treat_basename(item, 'backup'),
                        ),
                    )
                else:
                    self.logger.debug(f'Backup warning: File {item} not exists!')


    def resolve_filename(self, source):
        name, _ = os.path.splitext(os.path.basename(source))
        name = name.strip()
        valid, separator = False, ''
        if not name:
            return (valid, separator)
        for item in self.parameters['separators']:
            if name.count(item) == 0:
                continue
            if name.count(item) > 1:
                valid, separator = False, ''
                break
            if name.startswith(item) or name.endswith(item):
                continue
            valid, separator = True, item
            break
        return (valid, separator)


    def check_source(self, source):
        valid, _ = self.resolve_filename(source)
        if not valid:
            return self.SourceType.INVALID_NAME
        return self.SourceType.VALID


    def generate_key_by_filename(self, source):
        _, separator = self.resolve_filename(source)
        filename, _ = os.path.splitext(os.path.basename(source))

        artist, title = self.split(
            filename, separator, escaped=True,
            del_blank=False, filt_empty=False, filt_repeated=False,
            sortify=False, reversify=False,
        )
        return self.generate_key(artist, title)


    @staticmethod
    def chmod(path, mode=0o755):
        if path and os.path.exists(path):
            os.chmod(path, mode)


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


    @staticmethod
    def hyphen_to_camel(s):
        ret = re.sub(
            r'(?:-|\.)([a-z])',
            lambda m: m.group(1).upper(),
            s,
        )
        if ret:
            ret = ret[0].upper() + ret[1:]
        return ret

    #---------------------------------------------------------------------------

    # Successful for zsh, failed for bash.
    # You should set 'PROMPT_COMMAND="history -a"' in "~/.bashrc" or "~/.bash_profile".
    # And then run "source ~/.bashrc" or "source ~/.bash_profile".
    @classmethod
    def get_command(cls) -> str:
        interpreter = f'pipenv run python {sys.argv[0]}'
        try:
            match psutil.Process().parent().name().lower():
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
            raise e
        return interpreter 


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


    @classmethod
    def render_template(cls, usage, /, indent=None, kwargs={}) -> str:
        return cls.PerfectTemplate(
            cls.glorify_indents(usage, indent=indent),
        ).perfect_substitute(dict(
            cmd=cls.get_command(),
            filename_separator=f'<{" or ".join(FillPropertiesAction.ARGUMENTS_DEFAULTS()["separators"].split(","))}>',
            artist_sep=AudioGod.ARTIST_SEPARATOR,
            grouping_sep=AudioGod.GROUPING_SEPARATOR,
            fnp_delimiter=RenameAudiosAction.FilenamePatternTemplate.delimiter,
            audgod_root=AudioGod.AUDGOD_ROOT,
            audgod_source=os.path.basename(OPTIONS.AUDGOD_SOURCE),
            audgod_output=os.path.basename(OPTIONS.AUDGOD_OUTPUT),
            audgod_fullsrc=OPTIONS.AUDGOD_SOURCE,
            audgod_fullout=OPTIONS.AUDGOD_OUTPUT,
            audgod_cache= os.path.basename(OPTIONS.AUDGOD_CACHE),
            audgod_trash= os.path.basename(OPTIONS.AUDGOD_TRASH),
            audgod_backup=os.path.basename(OPTIONS.AUDGOD_BACKUP),
            testing_root=  TESTING_OPTIONS.AUDGOD_ROOT,
            testing_origin=TESTING_OPTIONS.AUDGOD_ORIGIN,
            testing_orisrc=TESTING_OPTIONS.AUDGOD_ORISRC,
            testing_source=TESTING_OPTIONS.AUDGOD_SOURCE,
            testing_output=TESTING_OPTIONS.AUDGOD_OUTPUT,
            testing_cache= TESTING_OPTIONS.AUDGOD_CACHE,
         ) | copy.deepcopy(ACTIONS_DEFAULTS) | copy.deepcopy(kwargs))


    @classmethod
    def reset_defaults(cls, defaults={}):
        if cls.ARGUMENTS:
            for argument, default in defaults.items():
                if argument not in cls.ARGUMENTS:
                    continue
                if 'kwargs' not in cls.ARGUMENTS[argument]:
                    continue
                if 'default' not in cls.ARGUMENTS[argument]['kwargs']:
                    continue
                cls.ARGUMENTS[argument]['kwargs']['default'] = default


    @classmethod
    def set_prog(cls):
        cls.PROG = '${cmd}' + ' {}'.format(' '.join(cls.NAME.split('.'))) if cls.NAME else ''
        if cls.KWARGS is not None:
            cls.KWARGS = copy.deepcopy(cls.BASIC_KWARGS) | cls.KWARGS
            if cls.KWARGS.get('prog', None) is None:
                cls.KWARGS['prog'] = cls.PROG


    @classmethod
    def set_usage(cls):
        if cls.NAME and cls.ARGUMENTS is not None and cls.KWARGS is not None:
            cls.KWARGS['usage'] = '${prog} \\\n'
            indent = 4
            for argument in cls.ARGUMENTS:
                label = cls.ARGUMENTS[argument]['args'][0]
                action_ = cls.ARGUMENTS[argument]['kwargs'].get('action', 'store')
                required = cls.ARGUMENTS[argument]['kwargs'].get('required', False)
                default = cls.ARGUMENTS[argument]['kwargs']['default']
                if required:
                    #default = '<INPUT>'
                    pass
                if isinstance(default, str):
                    if '\n' in default:
                        default = cls.glorify_indents(default, indent=indent).strip()
                if action_ == argparse.BooleanOptionalAction:
                    argument_pair = label if default else label.replace('--', '--no-')
                else:
                    if isinstance(default, str):
                        default = re.sub(r'[\"\']{5}', r'', shlex.quote(default))
                    argument_pair = f'{label}={default}'
                cls.KWARGS['usage'] += '{}{} \\\n'.format(
                    ' ' * indent, argument_pair,
                )
            cls.KWARGS['usage'] = cls.KWARGS['usage'].rstrip().rstrip('\\').rstrip()


    @classmethod
    def render_prog(cls):
        if cls.PROG:
            cls.PROG = AudioGod.render_template(
                cls.PROG, indent=None,
            )
        if cls.KWARGS is not None:
            if 'prog' in cls.KWARGS:
                if cls.KWARGS['prog'] is not None:
                    cls.KWARGS['prog'] = '\n\n' + AudioGod.render_template(
                        cls.KWARGS['prog'], indent=None,
                    )


    @classmethod
    def render_usage(cls):
        if cls.KWARGS is not None:
            if 'usage' in cls.KWARGS:
                if cls.KWARGS['usage'] is not None:
                    cls.KWARGS['usage'] = '\n\n' + AudioGod.render_template(
                        cls.KWARGS['usage'],
                        indent=0,
                        kwargs=dict(
                            prog=cls.PROG,
                        ),
                    )

    #---------------------------------------------------------------------------

    @classmethod
    def auto_extend(cls, class_):
        members = [
            ('PUBLIC_ARGUMENTS', True),
            ('REQUISITE_ARGUMENTS', False),
        ]
        methods = ['rewrite_parameters']

        for member, redecorated in members:
            if not hasattr(class_, member):
                continue
            result, current_value = {}, getattr(class_, member)
            for base in reversed(class_.__bases__):
                if not hasattr(base, member):
                    continue
                base_value = getattr(base, member)
                if redecorated:
                    base_value = cls.redecorate_arguments(
                        base_value, AudioGod.PUBLIC_ARGUMENTS,
                    )
                result.update(copy.deepcopy(base_value))
            result.update(copy.deepcopy(current_value))
            setattr(class_, member, result)

        for method in methods:
            if not hasattr(class_, method):
                continue
            def create_wrapper(mtd, func):
                @functools.wraps(func)
                def wrapper(self, *args, **kwargs):
                    for base in reversed(class_.__bases__):
                        if not hasattr(base, mtd):
                            continue
                        base_func = getattr(base, mtd)
                        if not callable(base_func):
                            continue
                        base_func(self, *args, **kwargs)
                    if mtd in class_.__dict__:
                        func(self, *args, **kwargs)
                return wrapper
            if method in class_.__dict__:
                setattr(class_, method, create_wrapper(method, getattr(class_, method)))
        return class_


    @classmethod
    def optimize_invokes(cls):
        methods = ['rewrite_parameters']
        for method in methods:
            if not hasattr(cls, method):
                continue
            original_func = getattr(cls, method)
            if not callable(original_func):
                continue
            def create_wrapper(func, mtd):
                def wrapper(self, *args, **kwargs):
                    label = f'_{cls.__name__}_{mtd}_called'
                    if not getattr(cls, label, False):
                        if mtd in cls.__dict__:
                            func(self, *args, **kwargs)
                        setattr(cls, label, True)
                return wrapper
            if method in cls.__dict__:
                setattr(cls, method, create_wrapper(original_func, method))


    @classmethod
    def redecorate_arguments(cls, arguments, public_arguments=PUBLIC_ARGUMENTS):
        for argument in arguments:
            public_argument = {}
            use_public = arguments[argument].pop('use_public', cls.ReplaceType.NONE)
            if cls.ReplaceType.NONE.ne(use_public):
                public_argument = copy.deepcopy(public_arguments[argument])
            match use_public:
                case cls.ReplaceType.NONE:
                    pass
                case cls.ReplaceType.ENTIRE:
                    arguments[argument] = public_argument
                case cls.ReplaceType.PARTIAL:
                    if 'args' not in arguments[argument]:
                        arguments[argument]['args'] = public_argument['args']
                    if 'kwargs' not in arguments[argument]:
                        arguments[argument]['kwargs'] = public_argument['kwargs']
                    else:
                        arguments[argument]['kwargs'] = public_argument['kwargs'] | \
                                                            arguments[argument]['kwargs']
            if 'args' in arguments[argument]:
                if len(arguments[argument]['args']) > 0:
                    if not arguments[argument]['args'][0].startswith('--'):
                        arguments[argument]['args'].insert(
                            0, f'--{cls.replace_underline(argument)}',
                        )
            if 'kwargs' in arguments[argument]:
                if 'dest' not in arguments[argument]['kwargs']:
                    arguments[argument]['kwargs']['dest'] = argument
                type_ = arguments[argument]['kwargs'].get('type', None)
                action_ = arguments[argument]['kwargs'].get('action', 'store')
                if 'default' not in arguments[argument]['kwargs']:
                    default = None
                    match type_:
                        case str():
                            default = ''
                        case int():
                            default = 0
                    if default is None and action_ == argparse.BooleanOptionalAction:
                        default = True
                    arguments[argument]['kwargs']['default'] = default
                if isinstance(arguments[argument]['kwargs']['default'], str):
                    if '\n' in arguments[argument]['kwargs']['default']:
                        arguments[argument]['kwargs']['default'] = cls.glorify_indents(
                            arguments[argument]['kwargs']['default'], indent=0,
                        ).strip()
        return copy.deepcopy(arguments)


    @classmethod
    def decorate(cls):
        # decorate $NAME
        if not cls.__name__.endswith('BaseAction'):
            if not cls.NAME:
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

            cls.redecorate_arguments(cls.ARGUMENTS, cls.PUBLIC_ARGUMENTS)

        # decorate $KWARGS
        cls.set_prog()
        cls.set_usage()

    #---------------------------------------------------------------------------

    @classmethod
    def ARGUMENTS_DEFAULTS(cls):
        ret = {}
        if cls.ARGUMENTS is None:
            return ret
        for argment, params in cls.ARGUMENTS.items():
            ret[argment] = params['kwargs']['default']
        return ret

    #---------------------------------------------------------------------------

    def resolve_fields(self, fields, sortify=False, reversify=False, stringify=False):
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
                if field not in self.FIELDS['all']:
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

    @classmethod
    def generate_key(cls, artist, title):
        return '{artist}{div}{title}'.format(
            artist=cls.format_artist(artist.strip()),
            div='#',
            title=cls.format_title(title.strip()),
        ).upper()


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
        if field in cls.FIELDS['all']:
            return field
        return None

    #---------------------------------------------------------------------------

    @classmethod
    def process_with_bar(cls, items, process_func, /, start=1, kwargs={}):
        with tqdm(
            items, 
            desc=cls.hyphen_to_camel(cls.NAME), 
            ncols=100,
            bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}] {postfix}',
        ) as bar:
            colours = ['red', 'yellow', 'green']
            phases = ['Initial 😐', 'Mid 😃', 'Final 😁']
            for i, item in enumerate(bar, start=start):
                tqdm.write(f'▶ Processing {item} ...')
                process_func(i, item, **kwargs)
                index = min(2, i//(len(items) // 3 + (1 if len(items)%3 else 0)))
                bar.colour = colours[index]
                bar.set_postfix({'▶ Phase': phases[index]})


    #@classmethod
    #def process_with_bar(cls, items, process_func, /, start=1, kwargs={}):
    #    with alive_bar(
    #        len(items), 
    #        title=cls.hyphen_to_camel(cls.NAME), 
    #        bar='blocks', 
    #        spinner='twirls',
    #    ) as bar:
    #        for i, item in enumerate(items, start=start):
    #            process_func(i, item, **kwargs)
    #            if i % 1 == 0:
    #                bar.text(f'Processing: {item}')
    #            bar()

    #---------------------------------------------------------------------------

    # Use AudioProperty type field here, you won't check field parameter.
    def save(self, audio_object, field, value, formatted=False):
        if value is None:
            return
        if formatted:
            value = self.format_funcs[field](value)
        match field:
            case self.AudioProperty.COMMENTS:
                audio_object.tag.comments.set(value)
            case _ if field in self.FIELDS['zip']:
                comments = audio_object.tag.comments
                if comments is not None:
                    comments = ''.join([comment.text for comment in comments])
                comments = self.load_json(comments, {})
                comments[field] = value
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
                                        self.parameters['root'] and \
                                        os.path.isfile(self.abspath(
                                            self.parameters['root'], value,
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
        audio_object.tag.save(version=eyed3.id3.ID3_V2_4, encoding='utf-8')


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
            case _ if field in self.FIELDS['zip']:
                comments = audio_object.tag.comments
                if comments:
                    comments = ''.join([comment.text for comment in comments])
                ret = self.load_json(comments, {}).get(field, None)
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
                ret = self.format_funcs[field](ret)
            if self.FileFormat.NONE.ne(output_format):
                ret = self.output_funcs[field](ret, output_format)
        if default is not None and not ret:
            ret = default
        return ret


    def prime_audio(self, audio):
        audio_object = eyed3.load(audio)
        if audio_object is None:
            self.logger.fatal(f'Invalid audio <{audio}>!')
            return None
        if audio_object.tag is None:
            audio_object.initTag()
            audio_object.tag.save()
        return audio_object


    def pack_output(self):
        return ''


    def handle_output(self, content=''):
        if not content:
            content = self.pack_output()
        if not self.parameters['output']:
            self.logger.error(content)
        else:
            if os.path.exists(self.parameters['output']):
                self.remove(self.parameters['output'])
            else:
                dirname = os.path.dirname(self.parameters['output'])
                if dirname:
                    os.makedirs(dirname, exist_ok=True)
            with open(self.parameters['output'], 'w', encoding='utf-8') as f:
                f.write(content)


    def glorify_exportation(self, outputs):
        output_format = getattr(self, 'output_format', self.FileFormat.NONE)

        symbols = (
            ('#', '-'),
            ('#', '####'),
            ('#', '#####'),
            ('#', '-'),
            ('', '###### '),
            ('\t', '  '),
        )

        i = 1 if self.FileFormat.MARKDOWN.eq(output_format) else 0

        ret = f'{symbols[0][i] * 60}\n\n'
        ret += '{symbol} Summary: Collects {collects_count}, Items {items_count}\n'.format(
            symbol=symbols[1][i],
            collects_count=len(outputs),
            items_count=sum([len(x) for _, x in outputs.items()]),
        )
        ret += f'{symbols[2][i]} Created Time: {self.current_time()}\n\n'
        ret += f'{symbols[3][i] * 60}\n'

        collect_number = 0
        for collect, items in outputs.items():
            collect_number += 1
            ret += f'\n{symbols[4][i]}({collect_number}) {collect}:\n'
            item_number = 0
            for item in items:
                item_number += 1
                ret += '{symbol}{number} {content}\n'.format(
                    symbol=symbols[5][i],
                    number=f'{f"{item_number}.":<{len(str(len(items)))+1}}',
                    content=item,
                )
        return ret


    def sort_properties(self, properties):
        ret = {}
        for field in self.FIELDS['all']:
            if field in properties:
                ret[field] = properties[field]
        return ret


    def repack_audio_properties(self, properties):
        ret = {}
        properties = self.sort_properties(properties)
        field_type = self.parameters.get('field_type', self.FieldType.ORIGINAL)
        if self.FieldType.AUTO.eq(field_type):
            field_type = self.FieldType.ORIGINAL
        for field, value in properties.items():
            field_name = self.transform_field_name(field, field_type)
            type_ = self.AUDIO_PROPERTY_TYPES[field]
            ret[field] = (field_name, type_, value)
        return ret


    def stow_ignored(self):
        if self.parameters['ignored_file']:
            with open(self.parameters['ignored_file'], 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    for item in self.expand_globbing(line, recursive=True):
                        self.ignored_set.add(item)


    def __check_extension(self, source):
        extensions = self.parameters.get('extensions', [])
        if not extensions:
            return True
        _, ext = os.path.splitext(os.path.basename(source))
        return ext[1:].lower() in extensions


    def hoard_sources(self, source, recursive):
        ret = []
        for item in self.expand_globbing(source, recursive=True):
            if not os.path.exists(item):
                self.logger.warning(f'Source <{item}> not exists!')
                continue
            if os.path.isfile(item):
                ret.append(item)
                continue
            if not os.path.isdir(item):
                self.logger.warning(f'Source <{item}> not a file or directory!')
                continue
            if recursive:
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
        return self.original_sources.extend(list(dict.fromkeys(ret)))


    def stow_sources(self):
        self.hoard_sources(
            self.parameters['source'], self.parameters['recursive'],
        )
        if self.parameters.get('another', ''):
            self.hoard_sources(
                self.parameters['another'], self.parameters['recursive'],
            )


    def trim_sources(self):
        for source in self.original_sources:
            _source, ignored = source, False
            while True:
                if re.match(r'^/*$', _source) is not None:
                    break
                if _source in self.ignored_set or _source+'/' in self.ignored_set:
                    ignored = True
                    break
                _source = os.path.dirname(_source)
            if ignored:
                self.ignored_sources.append(source)
                continue

            if os.path.basename(source) == '.DS_Store' \
                    or os.path.islink(source) \
                    or not os.path.isfile(source):
                self.omitted_sources.append(source)
                continue

            if not self.__check_extension(source):
                self.invalid_ext_sources.append(source)
                continue

            self.primed_sources.append(source)

        self.logger.warning(
            'Total Sources:   {total}\n\n'
            'Ignored Sources: {ignored}\n'
            'Omitted Sources: {omitted}\n'
            'Inv ext sources: {inv_ext}\n'
            'Primed Sources:  {primed}\n'.format(
                total=len(self.original_sources),
                ignored=len(self.ignored_sources),
                omitted=len(self.omitted_sources),
                inv_ext=len(self.invalid_ext_sources),
                primed=len(self.primed_sources)
            )
        )

        if False and len(self.ignored_sources) > 0:
            self.logger.warning('\nIgnored Sources:')
            for source in self.ignored_sources:
                self.logger.warning(f'\t{source}')
        if False and len(self.omitted_sources) > 0:
            self.logger.warning('\nOmitted Sources:')
            for source in self.omitted_sources:
                self.logger.warning(f'\t{source}')
        if len(self.invalid_ext_sources) > 0:
            self.logger.warning('\nInvalid Extension Sources:')
            for source in self.invalid_ext_sources:
                self.logger.warning(f'\t{source}')


    def prime_sources(self):
        self.stow_sources()
        self.stow_ignored()
        self.trim_sources()

    #---------------------------------------------------------------------------

    @log_decorator
    def run(self):
        self.execute()


    def execute(self):
        pass

    #---------------------------------------------------------------------------

    @log_decorator
    def test(self):
        self.examine()


    def examine(self):
        print(self.__class__.__name__, self.NAME)

####################################################V###########################
#                                                                              #
#                                     ACTIONS                                  #
#                                                                              #
################################################################################

class SummarizeRelatedBaseAction(AudioGod):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = None
    ARGUMENTS = None

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__summaries = {}

    #---------------------------------------------------------------------------

    @property
    def summaries(self):
        return self.__summaries

    @summaries.setter
    def summaries(self, value):
        self.__summaries = value

#===============================================================================

@AudioGod.auto_extend
class NoteRelatedBaseAction(SummarizeRelatedBaseAction):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = None
    ARGUMENTS = None

    PUBLIC_ARGUMENTS = {
        'field_type': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': AudioGod.FieldType.AUTO,
            },
        },
    }

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__clauses = ([], [], {}, {}, [], [])
        self.__clauses_counter = [0, 0, 0, 0, 0, 0]

    #---------------------------------------------------------------------------

    def rewrite_parameters(self):
        if 'another' in self.parameters:
            if self.parameters['another']:
                if not os.path.isfile(self.parameters['another']):
                    self.logger.fatal(f'Another <{self.parameters["another"]}> is not file!')
                    return

    #---------------------------------------------------------------------------

    @property
    def all_clauses(self):
        return self.__clauses[0]

    @property
    def invalid_clauses(self):
        return self.__clauses[1]

    @property
    def valid_clauses(self):
        return self.__clauses[2]

    @property
    def repeated_clauses(self):
        return self.__clauses[3]

    @property
    def grouping_clauses(self):
        return self.__clauses[4]

    @property
    def warn_clauses(self):
        return self.__clauses[5]


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

    #---------------------------------------------------------------------------

    def stow_clauses(self):
        document_name = os.path.basename(self.parameters['document'])
        with open(self.parameters['document'], 'r', encoding='utf-8') as f:
            for line_number, line in enumerate(f, start=1):
                prefix = f'@<{document_name}> &{line_number}:'
                self.all_clauses.append((prefix, line))
        if self.parameters.get('another', ''):
            another_name = os.path.basename(self.parameters['another'])
            if another_name == os.path.basename(self.parameters['document']):
                another_name = f'another.{another_name}'
            with open(self.parameters['another'], 'r', encoding='utf-8') as f:
                for line_number, line in enumerate(f, start=1):
                    prefix = f'@<{another_name}> &{line_number}:'
                    self.all_clauses.append((prefix, line))


    def analysis_note(self):
        self.stow_clauses()

        def _generate_detail_pattern(fields):
            return r'^(?:(?:(?:\s*[0-9]\s*)+\.\s*)?(?:\s*\[\s*[a-zA-Z]?\s*\]\s*)?)?(?:\s*[,，;；]+\s*)?\s*({0})\s*[:：]+((?:\s*\S\s*)+?)((?:\s*[,，;；]+\s*(?:{0})\s*[:：]+(?:\s*\S\s*)+)*)$'.format(
                '|'.join(list(fields)),
            )
        detail_patterns = {
            self.FieldType.CHINESE: self.AUDIO_CN_PROPERTY_SYNONYMS.keys(),
            self.FieldType.ENGLISH: self.AUDIO_EN_PROPERTY_SYNONYMS.keys(),
            self.FieldType.ORIGINAL: self.AUDIO_CN_PROPERTIES.keys(),
        }
        detail_pattern = _generate_detail_pattern([
            item for unit in detail_patterns.values() for item in unit
        ])
        for pattern, fields in detail_patterns.items():
            detail_patterns[pattern] = _generate_detail_pattern(fields)

        grouping_pattern = r'^\s*(?:\s*\(\s*(?:\s*[0-9]\s*)+\s*\)\s*)?\s*@\s*\[\s*((?:\s*\S\s*)+)\s*\]\s*((?:\s*[^:：\s]\s*)+)[:：]?\s*$'
        # field detail contains invalid field name
        warn_pattern = r'(?:\s*[,，;；]+\s*)+(?:(?:\s*\S\s*)+)\s*[:：]+(?:\s*\S\s*)+'

        field_type = self.FieldType.ORIGINAL
        keys, (genre, grouping) = {}, ('', [])

        for prefix, line in self.all_clauses:
            if not line.strip():
                continue
            if re.match(r'^\s*#+', line, re.IGNORECASE) is not None:
                continue
            self.total_clauses_counter += 1
            line_with_no, invalid_info = f'{prefix} {line}'.strip(), 'not matched'
            # grouping line
            grouping_match = re.match(grouping_pattern, line, re.IGNORECASE)
            if grouping_match is not None:
                genre, grouping = tuple(map(
                    lambda x: x.strip(), grouping_match.groups(),
                ))
                genre = self.format_funcs[self.AudioProperty.GENRE](genre)
                grouping = self.format_funcs[self.AudioProperty.GROUPING](grouping)
                if grouping:
                    self.grouping_clauses.append(line_with_no)
                    self.grouping_clauses_counter += 1
                    continue
            # detail line
            detail_match = re.match(detail_pattern, line, re.IGNORECASE)
            if grouping and detail_match is not None:
                for _type, _pattern in detail_patterns.items():
                    if re.match(_pattern, line, re.IGNORECASE) is None:
                        continue
                    field_type = _type
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
                    for field in self.FIELDS['note']:
                        if field not in properties:
                            valid, invalid_info = False, 'lack note fields'
                            break
                if valid:
                    if 'separators' in self.parameters:
                        title = properties[self.AudioProperty.TITLE]
                        artist = properties[self.AudioProperty.ARTIST]
                        for separator in self.parameters['separators']:
                            if separator in title:
                                valid, invalid_info = False, f'Title has separator <{separator}>!'
                                break
                            if separator in artist:
                                valid, invalid_info = False, f'Artist has separator <{separator}>!'
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
                    groups = self.split(
                        grouping, self.GROUPING_SEPARATOR, escaped=True,
                        del_blank=True, filt_empty=True, filt_repeated=True,
                        sortify=False, reversify=False,
                    )
                    for group in groups:
                        if group not in self.summaries:
                            self.summaries[group] = (genre, [properties])
                        else:
                            old_genre, items = self.summaries[group]
                            if genre != old_genre:
                                self.logger.fatal(f'Grouping <{group}> with different genres!')
                                return
                            if curr_key in [self.__generate_key_by_properties(x) for x in items]:
                                valid, invalid_info = False, 'duplicate detail items under same grouping'
                                continue
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

        if 'field_type' in self.parameters:
            if self.FieldType.AUTO.eq(self.parameters['field_type']):
                self.reset_parameters({ 'field_type': field_type })

        for grouping in self.summaries:
            genre, items = self.summaries[grouping]
            for i, properties in enumerate(items):
                items[i] = self.repack_audio_properties(properties)

        self.__transform_summaries_to_clauses()

        #self.logger.warning(f'\n{"#"*78}\n')
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

    #---------------------------------------------------------------------------

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

#===============================================================================

class ExportRelatedBaseAction(SummarizeRelatedBaseAction):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = None
    ARGUMENTS = None

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    #---------------------------------------------------------------------------

    @property
    def output_format(self):
        classname = self.__class__.__name__
        if not classname.startswith('Export__'):
            return self.recognize_file_format(
                self.parameters.get('output', ''),
            )
        if classname.endswith('BaseAction'):
            return self.FileFormat.NOTE
        if not classname.endswith('Action'):
            return self.FileFormat.NOTE
        ret = re.sub(r'(^Export__|Action$)', r'', classname).lower()
        if not self.FileFormat.validate(ret):
            return self.FileFormat.NOTE
        return self.FileFormat(ret)

    #---------------------------------------------------------------------------

    def pack_properties(self, properties):
        output_format = getattr(self, 'output_format', self.FileFormat.NONE)
        symbols = (
            ('', '*'),
        )
        i = 1 if self.FileFormat.MARKDOWN.eq(output_format) else 0

        ret = ''
        for field in properties:
            field_name, _, value = properties[field]
            value = f'{symbols[0][i]}{value}{symbols[0][i]}'
            ret += f'{field_name}: {value}; '
        return ret.strip().rstrip('; ')


    def plain_generalize(self):
        output_format = getattr(self, 'output_format', self.FileFormat.NONE)
        symbols = (
            ('@', '**'),
            ('', '**'),
        )
        i = 1 if self.FileFormat.MARKDOWN.eq(output_format) else 0
        return self.glorify_exportation({
            f'{symbols[0][i]}[{genre}]{symbols[1][i]} {grouping}': [
                self.pack_properties(item) for item in items
            ] for grouping, (genre, items) in self.summaries.items()
        })


    def sort_summaries(self):
        for grouping in self.summaries:
            _, items = self.summaries[grouping]
            items.sort(
                key=lambda x: self.pack_properties(x),
            )
        self.summaries = {
            key: self.summaries[key] for key in sorted(self.summaries)
        }

#===============================================================================

@AudioGod.auto_extend
class TreeRelatedBaseAction(AudioGod):
    ACTIVE = True

    #---------------------------------------------------------------------------

    __FILES_MARK__ = '__files__'

    #---------------------------------------------------------------------------

    KWARGS = None
    ARGUMENTS = None

    REQUISITE_ARGUMENTS = {
        'show_count': {
            'use_public': AudioGod.ReplaceType.NONE,
            'args': ['-0'],
            'kwargs': {
                'action': argparse.BooleanOptionalAction,
                'required': False,
                'default': True,
                'help': 'if show count when extract structure',
            },
        },
    }

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    #---------------------------------------------------------------------------

    def rewrite_parameters(self):
        super().rewrite_parameters()

        if 'show_count' in self.parameters:
            pass

    #---------------------------------------------------------------------------

    def tree(self, data):
        def _build(_data, indent=0, prefix='', is_last=True, is_root=True, current_key='', show_count=True):
            content = ''
            if isinstance(_data, dict):
                def _count_leaves(node):
                    if isinstance(node, list):
                        return len(node)
                    elif isinstance(node, dict):
                        return sum(_count_leaves(v) for v in node.values())
                    return 0

                def _count_children(node):
                    if isinstance(node, dict):
                        return len({ key: node[key] for key in node if key != self.__FILES_MARK__ })
                    return 0

                total_leaves = _count_leaves(_data)
                direct_children = _count_children(_data)

                if is_root:
                    key = list(_data.keys())[0] if len(_data) == 1 else 'Root'
                    direct_children = _count_children(next(iter(_data.values())))
                    if key != self.__FILES_MARK__:
                        content += f'{key}' + (f' (items: {total_leaves}, branches: {direct_children})' if show_count else '')
                        content += '\n'
                    new_prefix = prefix + '    '
                    items = _data[key].items() if len(_data) == 1 else _data.items()
                else:
                    connector = '└── ' if is_last else '├── '
                    current_prefix = prefix + connector
                    key = current_key or 'Node'
                    if key != self.__FILES_MARK__:
                        content += f'{current_prefix}{key}' + (f' (items: {total_leaves}, branches: {direct_children})' if show_count else '')
                        content += '\n'
                    new_prefix = prefix + ('    ' if is_last else '│   ')
                    items = _data.items()

                for i, (key, value) in enumerate(items):
                    child_is_last = i == len(items) - 1
                    if isinstance(value, dict):
                        content += _build(value, indent+1, new_prefix, child_is_last, False, key, show_count)
                    elif isinstance(value, list):
                        if key != self.__FILES_MARK__:
                            content += f'{new_prefix}{"└── " if child_is_last else "├── "}{key} ' + (f'(items: {len(value)}, branches: 0)' if show_count else '')
                            content += '\n'
            elif isinstance(_data, list):
                content += f'{prefix}└── ' + (f'(items: {len(_data)}, branches: 0)' if show_count else '')
                content += '\n'
            else:
                self.logger.fatal('Data must be a dict!')
            return content

        return _build(data, show_count=self.parameters['show_count']).strip()

#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

@AudioGod.auto_extend
class RedecorateNoteAction(
    NoteRelatedBaseAction,
    ExportRelatedBaseAction,
):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = {
        'description': '✋ Redecorate the note file',
        'help': 'redecorate the note file',
    }

    ARGUMENTS = {
        'document': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': f'{OPTIONS.AUDGOD_SOURCE}/origin.songs.note.txt',
            },
        },
        'field_type': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'separators': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'output': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': f'{OPTIONS.AUDGOD_OUTPUT}/redecorate.note.txt',
            },
        },
    }

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    #---------------------------------------------------------------------------

    def pack_output(self):
        return self.plain_generalize()

    #---------------------------------------------------------------------------

    def execute(self):
        self.analysis_note()
        self.sort_summaries()
        self.handle_output()

#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

@AudioGod.auto_extend
class SiftSourcesAction(AudioGod):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = {
        'description': '✋ Sift the sources',
        'help': 'sift the sources',
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
        'separators': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'output': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': f'{OPTIONS.AUDGOD_OUTPUT}/sift.sources.txt',
            },
        },
    }

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__sifted_sources = ([], [], {}, [])

    #---------------------------------------------------------------------------

    @property
    def valid_sources(self):
        return self.__sifted_sources[0]


    @property
    def invalid_sources(self):
        return self.__sifted_sources[1]


    @property
    def repeated_sources(self):
        return self.__sifted_sources[2]


    @property
    def formatted_sources(self):
        return self.__sifted_sources[3]

    #---------------------------------------------------------------------------

    def pack_output(self):
        content = 'Total sources: {total}, Valid sources: {valid}\n\n'.format(
            total=sum([
                len(self.valid_sources),
                len(self.invalid_sources),
                sum(len(files) for files in self.repeated_sources.values()),
            ]),
            valid=len(self.valid_sources),
        )
        content += f'Invalid sources show below: ({len(self.invalid_sources)})\n\n'
        for i, source in enumerate(self.invalid_sources, start=1):
            content += f'\t{i}. {source}\n'
        content += '\n\n'

        content += f'Formatted sources show below: ({len(self.formatted_sources)})\n\n'
        for i, (old, new) in enumerate(self.formatted_sources, start=1):
            content += f'\t{i}. {old}\n'
            content += f'\t\t --> {new}\n'
        content += '\n\n'

        content += 'Repeated sources show below: (name: {name}, file: {file})\n\n'.format(
            name=len(self.repeated_sources),
            file=sum(len(files) for files in self.repeated_sources.values()),
        )
        for name_no, (filename, files) in enumerate(self.repeated_sources.items(), start=1):
            content += f'\t({name_no}) {filename}: ({len(files)})\n'
            for i, file in enumerate(files, start=1):
                content += f'\t\t{i}. {file}\n'
            content += '\n'
        content += '\n\n'
        return content

    #---------------------------------------------------------------------------

    def execute(self):
        self.prime_sources()
        unique_sources = {}
        for source in self.primed_sources:
            valid, separator = self.resolve_filename(source)
            if not valid:
                self.invalid_sources.append(source)
                continue
            filename, ext = os.path.splitext(os.path.basename(source))
            formatted_filename = re.sub(
                r'_(H|L)$',
                r'',
                filename.replace(' _ ', f' {self.ARTIST_SEPARATOR} '),
            )
            artist, title = self.split(
                formatted_filename, separator, escaped=True,
                del_blank=False, filt_empty=False, filt_repeated=False,
                sortify=False, reversify=False,
            )
            artist = self.format_artist(artist)
            title = self.format_title(title)
            formatted_filename = f'{artist} {separator} {title}'
            if filename != formatted_filename:
                self.formatted_sources.append((
                    source,
                    os.path.join(
                        os.path.dirname(source), f'{formatted_filename}{ext.lower()}',
                    ),
                ))
                filename = formatted_filename
            value = os.path.join(os.path.dirname(source), f'{filename}{ext.lower()}')
            if filename not in unique_sources:
                unique_sources[filename] = [value]
            else:
                unique_sources[filename].append(value)

        for name, files in unique_sources.items():
            if len(files) < 1:
                continue
            if len(files) == 1:
                self.valid_sources.append(files[0])
                continue
            self.repeated_sources[name] = files

        for old, new in self.formatted_sources:
            self.rename(old, new)

        self.handle_output()

#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

class PickBaseAction(AudioGod):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = None
    ARGUMENTS = None

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    #---------------------------------------------------------------------------

    def execute(self):
        pass

#===============================================================================

class PickAction(PickBaseAction):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = {
        'description': '✋ Pick files or sources by sort',
        'help': 'pick files or sources by sort',
    }

    ARGUMENTS = None

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        pass

    #---------------------------------------------------------------------------

    def execute(self):
        pass

#===============================================================================

@AudioGod.auto_extend
class Pick__NoteAction(
    NoteRelatedBaseAction,
    PickBaseAction,
    ExportRelatedBaseAction,
):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = {
        'description': '✋ Pick note',
        'help': 'pick note',
    }

    ARGUMENTS = {
        'document': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': f'{OPTIONS.AUDGOD_SOURCE}/origin.songs.note.txt',
            },
        },
        'another': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': f'{OPTIONS.AUDGOD_SOURCE}/another.origin.songs.note.txt',
            },
        },
        'field_type': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'output': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': f'{OPTIONS.AUDGOD_OUTPUT}/pick.note.txt',
            },
        },
    }

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__discrete_clauses = []

    #---------------------------------------------------------------------------

    @property
    def discrete_clauses(self):
        return self.__discrete_clauses

    #---------------------------------------------------------------------------

    def pack_output(self):
        content = f'Total: {len(self.discrete_clauses)}\n\n'
        content += '\n'.join(self.discrete_clauses) + '\n'
        content += '\n\n'
        return content

    #---------------------------------------------------------------------------

    def execute(self):
        self.analysis_note()
        self.sort_summaries()

        for _, (_, items) in self.summaries.items():
            for item in items:
                self.discrete_clauses.append(self.pack_properties(item))
        self.discrete_clauses.sort()

        self.handle_output()

#===============================================================================

@AudioGod.auto_extend
class Pick__SourcesAction(PickBaseAction):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = {
        'description': '✋ Pick sources',
        'help': 'pick sources',
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
        'another': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': f'{OPTIONS.AUDGOD_SOURCE}/Another',
            },
        },
        'separators': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'output': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': f'{OPTIONS.AUDGOD_OUTPUT}/pick.sources.txt',
            },
        },
    }

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__discrete_sources = []

    #---------------------------------------------------------------------------

    @property
    def discrete_sources(self):
        return self.__discrete_sources

    #---------------------------------------------------------------------------

    def pack_output(self):
        content = f'Total: {len(self.discrete_sources)}\n\n'
        for _, (filename, source) in enumerate(self.discrete_sources, start=1):
            content += f'{filename}: {source}\n'
        content += '\n\n'
        return content

    #---------------------------------------------------------------------------

    def execute(self):
        self.prime_sources()
        for source in self.primed_sources:
            valid, separator = self.resolve_filename(source)
            if not valid:
                self.logger.fatal(f'Invalid source <{source}>!')
                return
            filename, _ = os.path.splitext(os.path.basename(source))
            artist, title = self.split(
                filename, separator, escaped=True,
                del_blank=False, filt_empty=False, filt_repeated=False,
                sortify=False, reversify=False,
            )
            self.discrete_sources.append((
                f'{title} {separator} {artist}', source,
            ))
        self.discrete_sources.sort(key=lambda x: x[0])
        self.handle_output()

#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

@AudioGod.auto_extend
class MatchSourcesAction(NoteRelatedBaseAction, ExportRelatedBaseAction):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = {
        'description': '✋ Match the note file and sources',
        'help': 'match the note file and sources',
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
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': f'{OPTIONS.AUDGOD_OUTPUT}/redecorate.note.txt',
            },
        },
        'field_type': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'separators': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'output': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': f'{OPTIONS.AUDGOD_OUTPUT}/match.sources.txt',
            },
        },
    }

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__data = ([], [], [], [])

    #---------------------------------------------------------------------------

    @property
    def matched_sources(self):
        return self.__data[0]

    @property
    def notmatched_sources(self):
        return self.__data[1]

    @property
    def matched_clauses(self):
        return self.__data[2]

    @property
    def notmatched_clauses(self):
        return self.__data[3]

    #---------------------------------------------------------------------------

    def pack_output(self):
        content = 'Total sources: {total}, Notmatched sources: {notmatched}\n\n'.format(
            total=len(self.primed_sources),
            notmatched=len(self.notmatched_sources),
        )
        for i, source in enumerate(self.notmatched_sources, start=1):
            content += f'\t{i}. {source}\n'
        content += '\n\n'
        content += 'Total clauses: {total}, Notmatched clauses: {notmatched}\n\n'.format(
            total=sum([len(self.matched_clauses), len(self.notmatched_clauses)]),
            notmatched=len(self.notmatched_clauses),
        )
        for i, clause in enumerate(self.notmatched_clauses, start=1):
            content += f'\t{i}. {clause}\n'
        content += '\n\n'
        return content

    #---------------------------------------------------------------------------

    def execute(self):
        self.analysis_note()
        self.prime_sources()

        for source in self.primed_sources:
            key = self.generate_key_by_filename(source)
            if key in self.valid_clauses:
                self.matched_sources.append(source)
                self.matched_clauses.append(key)
            else:
                self.notmatched_sources.append(source)

        for key in list(set(self.valid_clauses.keys()) - set(self.matched_clauses)):
            self.notmatched_clauses.append(
                self.pack_properties(
                    self.repack_audio_properties(self.valid_clauses[key]),
                ),
            )

        self.handle_output()

#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

class MergeBaseAction(AudioGod):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = None
    ARGUMENTS = None

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    #---------------------------------------------------------------------------

    def execute(self):
        pass

#===============================================================================

class MergeAction(MergeBaseAction):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = {
        'description': '✋ Merge files or sources',
        'help': 'merge files or sources',
    }

    ARGUMENTS = None

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        pass

    #---------------------------------------------------------------------------

    def execute(self):
        pass

#===============================================================================

@AudioGod.auto_extend
class Merge__NotesAction(
    MergeBaseAction,
    NoteRelatedBaseAction,
    ExportRelatedBaseAction,
):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = {
        'description': '✋ Merge notes',
        'help': 'merge notes',
    }

    ARGUMENTS = {
        'document': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': f'{OPTIONS.AUDGOD_SOURCE}/origin.songs.note.txt',
            },
        },
        'field_type': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'another': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': f'{OPTIONS.AUDGOD_SOURCE}/another.origin.songs.note.txt',
            },
        },
        'output': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': f'{OPTIONS.AUDGOD_OUTPUT}/merge.notes.txt',
            },
        },
    }

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    #---------------------------------------------------------------------------

    def pack_output(self):
        return self.plain_generalize()

    #---------------------------------------------------------------------------

    def execute(self):
        self.analysis_note()
        self.sort_summaries()
        self.handle_output()

#===============================================================================

@AudioGod.auto_extend
class Merge__SourcesAction(MergeBaseAction):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = {
        'description': '✋ Merge sources',
        'help': 'merge sources',
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
        'separators': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'another': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': f'{OPTIONS.AUDGOD_SOURCE}/Another',
            },
        },
        'output': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': f'{OPTIONS.AUDGOD_OUTPUT}/merge.sources.txt',
            },
        },
    }

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__data = ([], [], [])

    #---------------------------------------------------------------------------

    @property
    def main_sources(self):
        return self.__data[0]


    @property
    def another_sources(self):
        return self.__data[1]


    @property
    def conflicts(self):
        return self.__data[2]

    #---------------------------------------------------------------------------

    def rewrite_parameters(self):
        if 'another' in self.parameters:
            if self.parameters['another']:
                pass

    #---------------------------------------------------------------------------

    def load_sources(self):
        self.stow_ignored()

        self.hoard_sources(self.parameters['source'], self.parameters['recursive'])
        self.trim_sources()
        self.main_sources.extend(self.primed_sources)

        self.original_sources.clear()
        self.primed_sources.clear()

        self.hoard_sources(self.parameters['another'], self.parameters['recursive'])
        self.trim_sources()
        self.another_sources.extend(self.primed_sources)


    def pack_output(self):
        content = 'Total another sources: {total}, Conflicting sources: {conflict}\n\n'.format(
            total=len(self.another_sources),
            conflict=len(self.conflicts),
        )
        for number, (file, conflicts) in enumerate(self.conflicts, start=1):
            content += f'\t({number}) {file}: ({len(conflicts)})\n'
            for i, conflict in enumerate(conflicts, start=1):
                content += f'\t\t{i}. {conflict}\n'
            content += '\n'
        content += '\n\n'
        return content

    #---------------------------------------------------------------------------

    def execute(self):
        self.load_sources()

        main_set = {}
        for source in self.main_sources:
            filename, _ = os.path.splitext(os.path.basename(source))
            if filename not in main_set:
                main_set[filename] = [source]
            else:
                main_set[filename].append(source)

        for source in self.another_sources:
            filename, _ = os.path.splitext(os.path.basename(source))
            if filename not in main_set:
                continue
            self.conflicts.append((source, main_set[filename]))

        self.handle_output()

#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

@AudioGod.auto_extend
class FillPropertiesAction(NoteRelatedBaseAction, ExportRelatedBaseAction):
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
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': f'{OPTIONS.AUDGOD_OUTPUT}/redecorate.note.txt',
            },
        },
        'root': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'separators': {
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
        'output': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': f'{OPTIONS.AUDGOD_OUTPUT}/fill.properties.txt',
            },
        },
    }

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__data = ([], [])

    #---------------------------------------------------------------------------

    @property
    def filled_sources(self):
        return self.__data[0]


    @property
    def notfilled_sources(self):
        return self.__data[1]

    #---------------------------------------------------------------------------

    def rewrite_parameters(self):
        if 'properties' in self.parameters:
            self.parameters['properties'] = self.__resolve_properties(
                self.parameters['properties'],
            )

    #---------------------------------------------------------------------------

    def __resolve_properties(self, properties):
        ret = self.load_json(properties, {})
        if type(ret) is not dict:
            self.logger.fatal(f'Properties <{ret}> is not a dict type!')
            return ret
        keys = [
            key for key in list(ret.keys())
            if key != 'default'
        ]
        for key in keys:
            value = ret.pop(key)
            new_keys = self.resolve_fields(
                key, sortify=True, reversify=False, stringify=False,
            )
            for new_key in new_keys:
                ret[new_key] = value
        for key in ret.keys():
            value = ret[key]
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


    def __fetch_from_outside(self, audio, field):
        format_ = self.format_funcs[field]
        parse_ = self.parse_funcs[field]
        default = self.__resolve_properties(
            self.ARGUMENTS_DEFAULTS()['properties'],
        )['default']
        sources = self.parameters['properties'].get('default', {}).get(
            'sources', default['sources'],
        )
        if field in self.parameters['properties'].keys():
            sources = self.parameters['properties'][field].get('sources', sources)
        ret = self.parameters['properties'].get('default', {}).get(
            'value', default['value'],
        )
        for source in sources:
            match source:
                case self.PropertySource.COMMAND:
                    if field in self.parameters['properties'].keys():
                        _value = self.parameters['properties'][field].get('value', None)
                        if _value is not None:
                            ret = _value
                            break
                case self.PropertySource.FILE:
                    key = self.generate_key_by_filename(audio)
                    if key not in self.valid_clauses:
                        continue
                    _value = self.valid_clauses[key].get(field, None)
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
                                    re.escape(re.sub(r'/+$', r'', self.parameters['root'])),
                                ),
                                r'',
                                _value,
                            )
                    ret = _value
                    break
        return None if ret is None else format_(parse_(ret))


    def __fill_audio_properties(self):
        for source in self.primed_sources:
            filled, audio_object = False, self.prime_audio(source)
            for field in self.FIELDS['all']:
                property_ = self.__fetch_from_outside(source, field)
                if property_ is not None:
                    filled = True
                    self.save(audio_object, field, property_, True)
            if filled:
                self.filled_sources.append(source)
            else:
                self.notfilled_sources.append(source)


    #def __load_properties_from_file(self):
    #    if self.parameters['document']:
    #        file_format = self.recognize_file_format(self.parameters['document'])
    #        getattr(self, f'_import_{file_format}')()

    #def _import_note(self):
    #    self.analysis_note()

    #def _import_plist(self):
    #    pass

    #def _import_markdown(self):
    #    pass

    #def _import_xml(self):
    #    pass

    #def _import_json(self):
    #    pass

    #---------------------------------------------------------------------------

    def pack_output(self):
        content = 'Total sources: {total}, Notfilled sources: {notfilled}\n\n'.format(
            total=len(self.primed_sources),
            notfilled=len(self.notfilled_sources),
        )
        for i, source in enumerate(self.notfilled_sources, start=1):
            content += f'\t{i}. {source}\n'
        content += '\n\n'
        return content

    #---------------------------------------------------------------------------

    def execute(self):
        self.analysis_note()
        self.prime_sources()
        self.__fill_audio_properties()
        self.handle_output()

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

    #---------------------------------------------------------------------------

    def execute(self):
        self.prime_sources()
        count, audios = 0, self.primed_sources
        #self.logger.warning(f'\n{"#"*78}\n')
        for audio in audios:
            self.logger.debug(f'Formatting <{audio}> ...')
            filled, audio_object = False, self.prime_audio(audio)
            for field in self.FIELDS['all']:
                property_ = self.fetchx(
                    audio_object,
                    field,
                    formatted=False,
                    output_format=self.FileFormat.NONE,
                    default=None,
                )
                if property_ is None:
                    continue
                formatted_property = self.format_funcs[field](property_)
                if formatted_property == property_:
                    continue
                filled = True
                self.save(audio_object, field, formatted_property, True)
            if filled:
                count += 1
        self.logger.warning(f'Total Sources: {len(audios)}, Formatted Sources: {count}\n')

#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

@AudioGod.auto_extend
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
                'default': '{delimiter}{{artist}} # {delimiter}{{title}}'.format(
                    delimiter=FilenamePatternTemplate.delimiter,
                ),
                'help': 'filename pattern to rename sources',
            },
        },
    }

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    #---------------------------------------------------------------------------

    def rewrite_parameters(self):
        if 'filename_pattern' in self.parameters:
            pass

    #---------------------------------------------------------------------------

    def execute(self):
        self.prime_sources()
        for audio in self.primed_sources:
            audio_object = self.prime_audio(audio)
            _old = os.path.basename(audio)
            _, ext = os.path.splitext(_old)
            _new = self.FilenamePatternTemplate(self.parameters['filename_pattern']).safe_substitute({
                field: self.fetchx(
                    audio_object, field, formatted=True,
                ) for field in self.FIELDS['all']
            }) + ext.lower()
            if _old == _new:
                continue
            _path = os.path.dirname(audio)
            self.rename(self.abspath(_path, _old), self.abspath(_path, _new))

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
                'default': f'{OPTIONS.AUDGOD_OUTPUT}/Grouped',
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
                'default': f'{OPTIONS.AUDGOD_OUTPUT}/list.repeated.txt',
            },
        },
    }

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    #---------------------------------------------------------------------------

    def execute(self):
        self.prime_sources()

        results = {}
        for audio in self.primed_sources:
            audio_object = self.prime_audio(audio)
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
        content = f'{self.glorify_exportation(results)}'

        self.handle_output(content)

#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

@AudioGod.auto_extend
class ManageArtworksBaseAction(AudioGod):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = None
    ARGUMENTS = None

    REQUISITE_ARGUMENTS = {
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

#===============================================================================

class ManageArtworksAction(ManageArtworksBaseAction):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = {
        'description': '✋ Manage artworks',
        'help': 'manage artworks',
    }

    ARGUMENTS = None

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        pass

    #---------------------------------------------------------------------------

    def execute(self):
        pass

#===============================================================================

@AudioGod.auto_extend
class ManageArtworks__BindAction(ManageArtworksBaseAction):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = {
        'description': '✋ Bind artworks',
        'help': 'bind artworks',
    }

    ARGUMENTS = {
        'source': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'artworks': {
            'use_public': AudioGod.ReplaceType.NONE,
            'args': ['-3'],
            'kwargs': {
                'action': 'store',
                'type': str,
                'required': False,
                'default': f'{OPTIONS.AUDGOD_SOURCE}/Artwork',
                'help': 'source artworks to bind',
            },
        },
    }

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    #---------------------------------------------------------------------------

    def rewrite_parameters(self):
        if 'artworks' in self.parameters:
            self.parameters['artworks'] = self.abspath(
                self.parameters['artworks'],
            )
            # need some other checks
            # ...
            # ...
            # ...
            # ...
            # ...

    #---------------------------------------------------------------------------

    def execute(self):
        pass

#===============================================================================

class ManageArtworks__DeriveAction(ManageArtworksBaseAction):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = {
        'description': '✋ Derive artworks',
        'help': 'derive artworks',
    }

    ARGUMENTS = {
        'source': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': f'{OPTIONS.AUDGOD_ROOT}/iTunes/iTunes Media/Music',
            },
        },
        'output': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': f'{OPTIONS.AUDGOD_OUTPUT}/Artwork',
            },
        },
    }

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    #---------------------------------------------------------------------------

    def execute(self):
        pass
        #self.prime_sources()
        #for audio in self.primed_sources:
        #    _name, _ = os.path.splitext(os.path.basename(audio))
        #    _path = os.path.dirname(audio)
        #    if self.parameters['output']:
        #        _path = self.parameters['output']
        #    audio_object = self.prime_audio(audio)
        #    if not audio_object:
        #        continue
        #    if not audio_object.tag:
        #        continue
        #    if not audio_object.tag.images:
        #        continue
        #    for i, image in enumerate(audio_object.tag.images):
        #        image_file = self.abspath(_path, _name)
        #        if len(audio_object.tag.images) > 1:
        #            image_file += f'@{i}'
        #        image_file += '.jpg'
        #        self.backup(image_file)
        #        with open(image_file, 'wb') as f:
        #            f.write(image.image_data)

#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

@AudioGod.auto_extend
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
        'field_type': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'output': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
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
    }

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    #---------------------------------------------------------------------------

    def rewrite_parameters(self):
        if 'page_number' in self.parameters:
            pass

        if 'page_size' in self.parameters:
            pass

        if 'numbered' in self.parameters:
            pass

        if 'style' in self.parameters:
            self.parameters['style'] = self.DisplayStyle(
                self.parameters['style'],
            )

        if 'data_format' in self.parameters:
            self.parameters['data_format'] = self.DataFormat(
                self.parameters['data_format'],
            )

        if 'sort' in self.parameters:
            self.parameters['sort'] = self.__resolve_sort(
                self.parameters['sort'],
            )

        if 'filter' in self.parameters:
            self.parameters['filter'] = self.__resolve_filter(
                self.parameters['filter'],
            )

        if 'align' in self.parameters:
            self.parameters['align'] = self.__resolve_align(
                self.parameters['align'],
            )

    #---------------------------------------------------------------------------

    def __resolve_sort(self, sort_):
        sort_ = self.load_json(sort_, [])
        if type(sort_) is not list:
            self.logger.fatal(f'Sort <{sort_}> is not a list!')
            return
        for i in range(len(sort_)):
            if type(sort_[i]) is not list:
                self.logger.fatal(f'Item <{sort_[i]}> in sort <{sort_}> is not a list!')
                return
            if len(sort_[i]) != 2:
                self.logger.fatal(f'Length of item <{sort_[i]}> in sort <{sort_}> is not 2!')
                return
            if type(sort_[i][1]) is not bool:
                self.logger.fatal(f'Second of item <{sort_[i]}> in sort <{sort_}> is not boolean!')
                return
            sort_[i][0] = self.resolve_fields(
                sort_[i][0], sortify=False, reversify=False, stringify=True,
            )
        return sort_


    def __resolve_filter(self, filter_):
        filter_ = self.load_json(filter_, {})
        if type(filter_) is not dict:
            self.logger.fatal(f'Filter <{filter_}> is not a dict!')
            return
        filter_keys = [
            key for key in list(filter_.keys())
            if key != '_options'
        ]
        for key in filter_keys:
            new_key = self.resolve_fields(
                key, sortify=True, reversify=False, stringify=True,
            )
            filter_[new_key] = filter_.pop(key)
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
                key for key in list(filter_.keys())
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
        return filter_


    def __resolve_align(self, align_):
        align_ = self.load_json(align_, {})
        if type(align_) is not dict:
            self.logger.fatal(f'Align <{align_}> is not a dict!')
            return
        align_keys = list(align_.keys())
        for key in align_keys:
            new_key = self.resolve_fields(
                key, sortify=True, reversify=False, stringify=True,
            )
            align_[new_key] = align_.pop(key)
        align_keys = list(align_.keys())
        for key in align_keys:
            value = align_[key]
            if type(value) is not str:
                self.logger.fatal(f'Invalid type of <{value}>!')
                return
            if re.match(r'^[lcr]:[tmb]$', value) is None:
                self.logger.fatal(f'Invalid format of <{value}>!')
                return
        return align_

    #---------------------------------------------------------------------------

    @classmethod
    def wrap_table(
        cls,
        table_string,
        table_fields,
        start=1,
        numbered=True,
        style=DisplayStyle.TABLED,
    ):
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

        if cls.DisplayStyle.TABLED.ne(style):
            beg = result.find('|\n+', 0)
            end = result.find('|\n+', beg+3)
            result = result[:beg+2] + result[end+2:]
            result = re.sub(r'\+[\+-]*\n', r'', result)
            result = re.sub(r'[^\S\n\r]*\|[^\S\n\r]*', r'|', result)
            result = re.sub(r'^[^\S\n\r]*\|', r'', result)
            result = re.sub(r'\|[^\S\n\r]*$', r'\n', result)
            result = re.sub(r'\|\n\|', r'\n', result)

        if cls.DisplayStyle.VERTICAL.eq(style):
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
                _xlen_(field) for field in table_fields
            ]))

            while True:
                end = _result.find('\n', beg+1)
                if end < 0:
                    break
                row = _result[beg+1:end]
                if not row.strip():
                    break

                fields = ([rl_number] if numbered else []) + table_fields
                is_cn_field_name = False
                if len(table_fields) > 0:
                    matched = re.search(
                        r'[\u4e00-\u9fff]', table_fields[0], re.IGNORECASE,
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

    @classmethod
    def charting(cls, rows, pair_fields, options):
        page_number, page_size, sort_, filter_, align_, fields_to_show, numbered, style = options

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
                raise Exception(f'Invalid field <{field}>!')
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
                                raise Exception(
                                    f'Invalid field <{_field}> when filter!',
                                )
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
                        raise Exception(
                            f'Invalid function <{function}>!',
                        )
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
                        raise Exception(
                            f'Invalid field <{_field}> when sort!',
                        )
                    index = fields.index(_field)
                    function = sort_functions['default']
                    if _field in sort_functions.keys():
                        function = sort_functions[_field]
                    rows = function(rows, index, reverse)

        total_rows, start = len(rows), 0
        table_title = f'Total Sources: {total_rows}'

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

        return cls.wrap_table(
            table_string,
            rl_fields_to_show,
            start=start,
            numbered=numbered,
            style=style,
        )

    #---------------------------------------------------------------------------

    def execute(self):
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

        self.prime_sources()

        results = []
        all_fields = [
            (field, self.transform_field_name(field, self.parameters['field_type']))
            for field in self.FIELDS['all']
        ]
        formatted, output_format = True, self.FileFormat.NOTE
        match self.parameters['data_format']:
            case self.DataFormat.ORIGINAL:
                formatted, output_format = False, self.FileFormat.NONE
            case self.DataFormat.FORMATTED:
                formatted, output_format = True, self.FileFormat.NONE
            case self.DataFormat.OUTPUTTED:
                formatted, output_format = True, self.FileFormat.NOTE
        for audio in self.primed_sources:
            audio_object = self.prime_audio(audio)
            results.append([
                self.fetchx(
                    audio_object, self.AudioProperty(x[0]), formatted, output_format,
                )
                for x in all_fields
            ])

        self.handle_output(
            self.charting(
                results,
                all_fields,
                [
                    self.parameters['page_number'],
                    self.parameters['page_size'],
                    self.parameters['sort'],
                    self.parameters['filter'],
                    self.parameters['align'],
                    self.parameters['fields'],
                    self.parameters['numbered'],
                    self.parameters['style'],
                ],
            ),
        )

#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

@AudioGod.auto_extend
class OrganizeBaseAction(AudioGod):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = None
    ARGUMENTS = None

    REQUISITE_ARGUMENTS = {
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

    #---------------------------------------------------------------------------

    def rewrite_parameters(self):
        if 'root' in self.parameters:
           if not self.parameters['root']:
               self.logger.fatal('Invalid root!')
               return

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

    #---------------------------------------------------------------------------

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
        'output': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': f'{OPTIONS.AUDGOD_OUTPUT}/Grouped',
            },
        },
    }

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    #---------------------------------------------------------------------------

    def execute(self):
        self.prime_sources()
        for audio in self.primed_sources:
            audio_object = self.prime_audio(audio)
            grouping = self.fetchx(
                audio_object, self.AudioProperty.GROUPING, formatted=True,
            )
            groups = self.split(
                grouping, self.GROUPING_SEPARATOR, escaped=True,
                del_blank=True, filt_empty=True, filt_repeated=True,
                sortify=False, reversify=False,
            )
            if not groups:
                self.logger.warning(f'Invalid grouping of <{audio}>')
                continue
            target = self.abspath(
                self.parameters['output'], groups[0], os.path.basename(audio),
            )
            if target != audio:
                os.makedirs(os.path.dirname(target), exist_ok=True)
                self.duplicate(audio, target)
                ao = self.prime_audio(target)
                self.save(
                    ao, self.AudioProperty.GROUPING, groups[0], True,
                )
            if len(groups) < 2:
                continue
            for group in groups[1:]:
                link = self.abspath(self.parameters['output'], group, os.path.basename(audio))
                if link == target:
                    continue
                os.makedirs(os.path.dirname(link), exist_ok=True)
                if os.path.exists(link):
                    self.remove(link)
                self.duplicate(target, link)
                ao = self.prime_audio(link)
                self.save(
                    ao, self.AudioProperty.GROUPING, group, True,
                )

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
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'output': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': f'{OPTIONS.AUDGOD_ROOT}/iTunes/iTunes Media/Music',
            },
        },
    }

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    #---------------------------------------------------------------------------

    def execute(self):
        self.prime_sources()
        for audio in self.primed_sources:
            audio_object = self.prime_audio(audio)

            artist = self.fetchx(audio_object, self.AudioProperty.ARTIST, formatted=True)
            if not artist:
                self.logger.warning(f'Invalid artist of <{audio}>')
                continue

            album = self.fetchx(audio_object, self.AudioProperty.ALBUM, formatted=True)
            if not album:
                self.logger.warning(f'Invalid album of <{audio}>')
                continue

            newname = self.abspath(self.parameters['output'], artist, album, os.path.basename(audio))
            if newname == audio:
                continue

            if not os.path.exists(newname):
                os.makedirs(os.path.dirname(newname), exist_ok=True)
                self.duplicate(audio, newname)
                continue

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

            existed_object = self.prime_audio(newname)
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

            if bool(set(current_groups) & set(existed_groups)):
                self.logger.warning(
                    f'Duplicate groupings between current <{audio}> and existed <{newname}>!',
                )
                continue

            self.save(
                existed_object,
                self.AudioProperty.GROUPING,
                self.GROUPING_SEPARATOR.join(existed_groups+current_groups),
                formatted=True,
            )

#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

@AudioGod.auto_extend
class ExportBaseAction(ExportRelatedBaseAction):
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

    REQUISITE_ARGUMENTS = {
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

        self.__audios_tree = self.TreeX(
            tree=None,
            deep=False,
            node_class=None,
            identifier=None,
            logger=self.logger,
        )
        self.audios_tree.create_node(
            self.AUDIOS_TREE_ROOT_TAG, self.AUDIOS_TREE_ROOT_NID,
        )

    #---------------------------------------------------------------------------

    @property
    def audios_tree(self):
        return self.__audios_tree

    #---------------------------------------------------------------------------

    @staticmethod
    def generate_persistent_id() -> str:
        return str(uuid.uuid4()).replace('-', '')[:16].upper()

    #---------------------------------------------------------------------------

    def summarize(self):
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

        self.sort_summaries()

    #---------------------------------------------------------------------------

    def __gain_audio_properties(self, audio_object):
        ret = {}
        for field in self.parameters['fields']:
            value = self.fetchx(
                audio_object,
                field,
                formatted=True,
                output_format=self.output_format,
            )
            if value is None:
                continue
            ret[field] = value
        return self.repack_audio_properties(ret)


    def __fill_audios_tree(self) -> None:
        self.prime_sources()

        track_id = self.parameters.get('track_initial_id', 601)

        for audio in self.primed_sources:
            track_persistent_id = self.generate_persistent_id()
            audio_object = self.prime_audio(audio)
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
                subtree = self.TreeX(logger=self.logger)
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

        playlist_id = self.parameters.get('playlist_initial_id', 3001)
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

    #---------------------------------------------------------------------------

    def generalize(self):
        return ''

    #---------------------------------------------------------------------------

    def execute(self):
        self.summarize()
        self.handle_output(self.generalize())

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

    #---------------------------------------------------------------------------

    def execute(self):
        pass

#===============================================================================

@AudioGod.auto_extend
class Export__NoteAction(ExportBaseAction, NoteRelatedBaseAction):
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
                'default': f'{OPTIONS.AUDGOD_OUTPUT}/Grouped',
            },
        },
        'fields': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': 'basic',
            },
        },
        'field_type': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': AudioGod.FieldType.CHINESE,
            },
        },
        'output': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': f'{OPTIONS.AUDGOD_OUTPUT}/export.note.txt',
            },
        },
    }

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    #---------------------------------------------------------------------------
    def generalize(self):
        return self.plain_generalize()

#===============================================================================

@AudioGod.auto_extend
class Export__PlistAction(ExportBaseAction):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = {
        'description': '⭐ Export audio details to plist file',
        'help': 'export audio details to plist file',
    }

    ARGUMENTS = {
        'source': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': f'{OPTIONS.AUDGOD_ROOT}/iTunes/iTunes Media/Music',
            },
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
                'default': f'{OPTIONS.AUDGOD_ROOT}/iTunes/Library.xml',
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
                'default': f'{OPTIONS.AUDGOD_ROOT}/iTunes/iTunes Media/Music',
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

    #---------------------------------------------------------------------------

    def rewrite_parameters(self):
        if 'itunes_version_plist' in self.parameters:
            self.parameters['itunes_version_plist'] = self.abspath(
                self.parameters['itunes_version_plist'],
            )

        if 'itunes_media_folder' in self.parameters:
            self.parameters['itunes_media_folder'] = self.abspath(
                self.parameters['itunes_media_folder'],
            )

        if 'track_initial_id' in self.parameters:
            pass

        if 'playlist_initial_id' in self.parameters:
            pass

    #---------------------------------------------------------------------------

    @staticmethod
    def encode(src) -> str:
        return urllib.parse.quote(src, safe='/', encoding='utf-8', errors=None)


    @classmethod
    def encode_location(cls, location) -> str:
        ret = f'file://{cls.encode(location)}'
        if os.path.isfile(location):
            return ret
        return f'{ret}/'

    #---------------------------------------------------------------------------

    @staticmethod
    def __get_itunes_version(itunes_version_plist) -> str:
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


    @staticmethod
    def __format_template(template) -> str:
        return template.strip().replace(' '*4, '\t') + '\n'


    @staticmethod
    def __repack_plist(content) -> str:
        result = f'\n{content}'.replace('\n', '\n\t\t')
        return result[:-1]


    @staticmethod
    def pack_properties(properties):
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


    @classmethod
    def __pack_track(cls, track) -> str:
        _, track_id, persistent_id, _, _, properties = track.data
        return Template(cls.__format_template('''
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
            properties=cls.pack_properties(properties),
            date_added=cls.current_time(),
            kind='MPEG audio file',
            persistent_id=persistent_id,
            track_type='File',
            location=cls.encode_location(track.tag),
            file_folder_count='-1',
            library_folder_count='-1',
        ))


    @staticmethod
    def __unique_tracks(tracks) -> list:
        results, track_set = [], set()
        for track in tracks:
            if track.tag in track_set:
                continue
            results.append(track)
            track_set.add(track.tag)
        return results


    def __pack_tracks(self) -> str:
        result = ''
        tracks = self.__unique_tracks(self.audios_tree.leaves())
        for track in tracks:
            if track.identifier == self.AUDIOS_TREE_ROOT_NID:
                continue
            if not isinstance(track.data, list):
                continue
            node_type = track.data[0]
            if self.AudiosTreeNodeType.TRACK.ne(node_type):
                continue
            result += self.__pack_track(track)
        return self.__repack_plist(result)


    def __pack_simple_tracks(self, node) -> str:
        result = ''
        tracks = self.__unique_tracks(self.audios_tree.leaves(node.identifier))
        for track in tracks:
            if track.identifier == self.AUDIOS_TREE_ROOT_NID:
                continue
            if not isinstance(track.data, list):
                continue
            node_type = track.data[0]
            if self.AudiosTreeNodeType.TRACK.ne(node_type):
                continue
            track_id = track.data[1]
            result += Template(self.__format_template('''
<dict>
	<key>Track ID</key><integer>${track_id}</integer>
</dict>
        ''')).safe_substitute(dict(
            track_id=track_id,
        ))
        return self.__repack_plist(result)


    def __pack_library(self) -> str:
        return Template(self.__format_template('''
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
            tracks=self.__pack_simple_tracks(self.audios_tree[self.audios_tree.root]),
        ))


    def __pack_playlist(self, node) -> str:
        node_type, id, pid, _, _, ppid = node.data
        return Template(self.__format_template('''
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
            tracks=self.__pack_simple_tracks(node),
        ))


    def __pack_playlists(self) -> str:
        result = self.__pack_library()
        for node in self.audios_tree.all_nodes():
            if node.is_root():
                continue
            node_type = node.data[0]
            if self.AudiosTreeNodeType.TRACK.eq(node_type):
                continue
            result += self.__pack_playlist(node)
        return self.__repack_plist(result)


    def __pack_plist(self) -> str:
        return Template(self.__format_template('''
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
            itunes_version = self.__get_itunes_version(
                self.parameters['itunes_version_plist'],
            ),
            features = '5',
            show_content_ratings = 'true',
            itunes_media_folder = self.encode_location(
                self.parameters['itunes_media_folder'],
            ),
            library_persistent_id = self.generate_persistent_id(),
            tracks = self.__pack_tracks(),
            playlists = self.__pack_playlists(),
        ))

    #---------------------------------------------------------------------------

    def generalize(self):
        return self.__pack_plist()

#===============================================================================

class Export__MarkdownAction(ExportBaseAction):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = {
        'description': '⭐ Export audio details to markdown file',
        'help': 'export audio details to markdown file',
    }

    ARGUMENTS = {
        'source': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': f'{OPTIONS.AUDGOD_OUTPUT}/Grouped',
            },
        },
        'fields': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': 'basic',
            },
        },
        'field_type': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'output': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': f'{OPTIONS.AUDGOD_OUTPUT}/export.markdown.md',
            },
        },
    }

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    #---------------------------------------------------------------------------

    def generalize(self):
        return self.plain_generalize()

#===============================================================================

class Export__XmlAction(ExportBaseAction):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = {
        'description': '⭐ Export audio details to xml file',
        'help': 'export audio details to xml file',
    }

    ARGUMENTS = {
        'source': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': f'{OPTIONS.AUDGOD_OUTPUT}/Grouped',
            },
        },
        'fields': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': 'ituned',
            },
        },
        'field_type': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'output': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': f'{OPTIONS.AUDGOD_OUTPUT}/export.xml',
            },
        },
    }

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    #---------------------------------------------------------------------------

    def generalize(self):
        return 'None'

#===============================================================================

class Export__JsonAction(ExportBaseAction):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = {
        'description': '⭐ Export audio details to json file',
        'help': 'export audio details to json file',
    }

    ARGUMENTS = {
        'source': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': f'{OPTIONS.AUDGOD_OUTPUT}/Grouped',
            },
        },
        'fields': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': 'basic',
            },
        },
        'field_type': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'output': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': f'{OPTIONS.AUDGOD_OUTPUT}/export.json',
            },
        },
    }

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    #---------------------------------------------------------------------------

    def generalize(self):
        return 'None'

#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

class ConvertBaseAction(AudioGod):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = None
    ARGUMENTS = None

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

#===============================================================================

@AudioGod.auto_extend
class ConvertMediaBaseAction(ConvertBaseAction):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = None
    ARGUMENTS = None

    REQUISITE_ARGUMENTS = {
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

    #---------------------------------------------------------------------------

    def rewrite_parameters(self):
        if 'output' in self.parameters:
            if self.parameters['output']:
                if not os.path.exists(self.parameters['output']):
                    os.makedirs(self.parameters['output'], exist_ok=True)
                else:
                    if not os.path.isdir(self.parameters['output']):
                        self.logger.fatal(f'Output <{self.parameters["output"]}> not a directory!')
                        return

    #---------------------------------------------------------------------------

    @staticmethod
    def transform_ext(ext=''):
        if not ext:
            return ext
        if ext.startswith('.'):
            ext = ext[1:]
        return ext.lower()


    def ensure_output(self, src):
        output = self.parameters['output']
        if not output:
            output = os.path.dirname(src)
        name, ext = os.path.splitext(os.path.basename(src))
        return os.path.join(output, f'{name}.{self.transform_ext(ext)}')

    #---------------------------------------------------------------------------

    def convert(self, src):
        pass

    #---------------------------------------------------------------------------

    def execute(self):
        self.prime_sources()
        self.process_with_bar(
            self.primed_sources,
            lambda i, item: self.convert(item),
            start=1,
        )

#===============================================================================

@AudioGod.auto_extend
class ConvertDocumentBaseAction(ConvertBaseAction):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = None
    ARGUMENTS = None

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    #---------------------------------------------------------------------------

    def rewrite_parameters(self):
        if 'document' in self.parameters:
            if not self.parameters['document']:
                self.logger.fatal(f'File <{self.parameters["document"]}> invalid!')
                return

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

    #---------------------------------------------------------------------------

    def execute(self):
        pass

#===============================================================================

class Convert__QmcToAudioAction(ConvertMediaBaseAction):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = {
        'description': '⭐ Convert qmc to common format',
        'help': 'convert qmc to common format',
    }

    ARGUMENTS = {
        'source': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': f'{OPTIONS.AUDGOD_SOURCE}/Qmc',
            },
        },
        'extensions': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': 'qmc,qmc0,qmc1,qmc2,qmc3,qmcogg,qmcflac',
            },
        },
        'output': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': f'{OPTIONS.AUDGOD_OUTPUT}/Qmc-To-Audio',
            },
        },
    }

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    #---------------------------------------------------------------------------

    @staticmethod
    def maps(i):
        return [
            0x77, 0x48, 0x32, 0x73, 0xDE, 0xF2, 0xC0, 0xC8, 0x95, 0xEC, 0x30, 0xB2, 0x51, 0xC3, 0xE1, 0xA0,
            0x9E, 0xE6, 0x9D, 0xCF, 0xFA, 0x7F, 0x14, 0xD1, 0xCE, 0xB8, 0xDC, 0xC3, 0x4A, 0x67, 0x93, 0xD6,
            0x28, 0xC2, 0x91, 0x70, 0xCA, 0x8D, 0xA2, 0xA4, 0xF0, 8, 0x61, 0x90, 0x7E, 0x6F, 0xA2, 0xE0, 0xEB,
            0xAE, 0x3E, 0xB6, 0x67, 0xC7, 0x92, 0xF4, 0x91, 0xB5, 0xF6, 0x6C, 0x5E, 0x84, 0x40, 0xF7, 0xF3,
            0x1B, 2, 0x7F, 0xD5, 0xAB, 0x41, 0x89, 0x28, 0xF4, 0x25, 0xCC, 0x52, 0x11, 0xAD, 0x43, 0x68, 0xA6,
            0x41, 0x8B, 0x84, 0xB5, 0xFF, 0x2C, 0x92, 0x4A, 0x26, 0xD8, 0x47, 0x6A, 0x7C, 0x95, 0x61, 0xCC,
            0xE6, 0xCB, 0xBB, 0x3F, 0x47, 0x58, 0x89, 0x75, 0xC3, 0x75, 0xA1, 0xD9, 0xAF, 0xCC, 8, 0x73, 0x17,
            0xDC, 0xAA, 0x9A, 0xA2, 0x16, 0x41, 0xD8, 0xA2, 6, 0xC6, 0x8B, 0xFC, 0x66, 0x34, 0x9F, 0xCF, 0x18,
            0x23, 0xA0, 0xA, 0x74, 0xE7, 0x2B, 0x27, 0x70, 0x92, 0xE9, 0xAF, 0x37, 0xE6, 0x8C, 0xA7, 0xBC, 0x62,
            0x65, 0x9C, 0xC2, 8, 0xC9, 0x88, 0xB3, 0xF3, 0x43, 0xAC, 0x74, 0x2C, 0xF, 0xD4, 0xAF, 0xA1, 0xC3, 1,
            0x64, 0x95, 0x4E, 0x48, 0x9F, 0xF4, 0x35, 0x78, 0x95, 0x7A, 0x39, 0xD6, 0x6A, 0xA0, 0x6D, 0x40,
            0xE8, 0x4F, 0xA8, 0xEF, 0x11, 0x1D, 0xF3, 0x1B, 0x3F, 0x3F, 7, 0xDD, 0x6F, 0x5B, 0x19, 0x30, 0x19,
            0xFB, 0xEF, 0xE, 0x37, 0xF0, 0xE, 0xCD, 0x16, 0x49, 0xFE, 0x53, 0x47, 0x13, 0x1A, 0xBD, 0xA4, 0xF1,
            0x40, 0x19, 0x60, 0xE, 0xED, 0x68, 9, 6, 0x5F, 0x4D, 0xCF, 0x3D, 0x1A, 0xFE, 0x20, 0x77, 0xE4, 0xD9,
            0xDA, 0xF9, 0xA4, 0x2B, 0x76, 0x1C, 0x71, 0xDB, 0, 0xBC, 0xFD, 0xC, 0x6C, 0xA5, 0x47, 0xF7, 0xF6, 0,
            0x79, 0x4A, 0x11,
        ][(i * i + 80923) % 256]


    @classmethod
    def seed(cls, i):
        if i >= 0x8000:
            return cls.maps(i % 0x7fff)
        return cls.maps(i)


    def transform_ext(self, ext):
        return re.sub(r'^qmc[0-9]', r'', super().transform_ext(ext)) or 'mp3'


    def decrypt(self, src):
        with open(src, 'rb') as fin:
            data = bytearray(fin.read())
            for i in range(len(data)):
                data[i] ^= self.seed(i)

            with open(self.ensure_output(src), 'wb') as fout:
                fout.write(data)

    #---------------------------------------------------------------------------

    def convert(self, src):
        self.decrypt(src)

#===============================================================================

class Convert__KmxToMp4Action(ConvertMediaBaseAction):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = {
        'description': '⭐ Convert kmx to mp4',
        'help': 'convert kmx to mp4',
    }

    ARGUMENTS = {
        'source': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': f'{OPTIONS.AUDGOD_SOURCE}/Kmx',
            },
        },
        'extensions': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': 'kmx',
            },
        },
        'output': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': f'{OPTIONS.AUDGOD_OUTPUT}/Kmx-To-Mp4',
            },
        },
    }

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    #---------------------------------------------------------------------------

    @staticmethod
    def transform_ext(ext=''):
        return 'mp4'


    def decrypt(self, src):
        seek, buffer_size = 34, 200
        with open(src, 'rb') as fin:
            fin.seek(seek)
            with open(self.ensure_output(src), 'wb') as fout:
                while True:
                    buffer = fin.read(buffer_size)
                    if len(buffer) == 0:
                        break
                    fout.write(buffer)
                    #out_file_size = path.getsize(out_path)
                    #print('已完成{0}%'.format(round(out_file_size/file_size * 100, 2)), end='\r')

    #---------------------------------------------------------------------------

    def convert(self, src):
        self.decrypt(src)

#===============================================================================

@AudioGod.auto_extend
class Convert__MediaAction(ConvertMediaBaseAction):
    ACTIVE = True

    #---------------------------------------------------------------------------

    SUPPORTED_FORMATS = ['mp3', 'mp4', 'mov', 'flac', 'wav', 'ogg', 'ape', 'wma']

    #---------------------------------------------------------------------------

    KWARGS = {
        'description': '⭐ Convert audios to different format',
        'help': 'convert audios to different format',
    }

    ARGUMENTS = {
        'source': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': f'{OPTIONS.AUDGOD_SOURCE}/Media',
            },
        },
        'extensions': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': ','.join(SUPPORTED_FORMATS),
            },
        },
        'output': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': f'{OPTIONS.AUDGOD_OUTPUT}/Media',
            },
        },
        'format': {
            'use_public': AudioGod.ReplaceType.NONE,
            'args': ['-5'],
            'kwargs': {
                'action': 'store',
                'type': str,
                'choices': SUPPORTED_FORMATS,
                'required': False,
                'default': SUPPORTED_FORMATS[0],
                'help': 'the format for output',
            },
        },
    }

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    #---------------------------------------------------------------------------

    def rewrite_parameters(self):
        if 'format' in self.parameters:
            self.parameters['format'] = self.parameters['format'].lower()

    #---------------------------------------------------------------------------

    def transform_ext(self, ext=''):
        return self.parameters['format']


    def convert(self, src):
        AudioSegment.from_file(src).export(
            self.ensure_output(src),
            format=self.transform_ext(self.parameters['format']),
        )

#===============================================================================

@AudioGod.auto_extend
class Convert__NoteToMarkdownAction(
    ConvertDocumentBaseAction,
    NoteRelatedBaseAction,
    ExportRelatedBaseAction,
):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = {
        'description': '⭐ Convert note to markdown',
        'help': 'convert note to markdown',
    }

    ARGUMENTS = {
        'document': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': f'{OPTIONS.AUDGOD_OUTPUT}/export.note.txt',
            },
        },
        'field_type': {
            'use_public': AudioGod.ReplaceType.ENTIRE,
        },
        'output': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': f'{OPTIONS.AUDGOD_OUTPUT}/convert.note.to.markdown.md',
            },
        },
    }

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    #---------------------------------------------------------------------------

    def pack_output(self):
        return self.plain_generalize()

    #---------------------------------------------------------------------------

    def execute(self):
        self.analysis_note()
        self.sort_summaries()
        self.handle_output()

#===============================================================================

class Convert__MarkdownToNoteAction(ConvertDocumentBaseAction):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = {
        'description': '⭐ Convert markdown to note',
        'help': 'convert markdown to note',
    }

    ARGUMENTS = {
        'document': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': f'{OPTIONS.AUDGOD_OUTPUT}/export.markdown.md',
            },
        },
        'output': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': f'{OPTIONS.AUDGOD_OUTPUT}/convert.markdown.to.note.txt',
            },
        },
    }

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    #---------------------------------------------------------------------------

    def execute(self):
        with open(self.parameters['document'], 'r', encoding='utf-8') as f:
            content = ''
            for line in f:
                line = re.sub(r'##+', r'#', line)
                if re.match(r'^-{3,}', line) is not None:
                    line = re.sub(r'-', r'#', line)
                ct_pattern = r'^(\s*#+\s*Created Time:\s*)([0-9-: TtZz]+).*$'
                if re.match(ct_pattern, line) is not None:
                    line = re.sub(ct_pattern, r'\1', line).rstrip('\n')
                    line += f'{self.current_time()}\n'
                blank_pattern = r'^[ \t]+'
                if re.match(blank_pattern, line) is not None:
                    line = re.sub(blank_pattern, r'\t', line)
                line = re.sub(r'#+\s*(\([0-9]+\)\s*.*)$', r'\1', line)
                line = line.replace('**[', '@[')
                line = line.replace('*', '')
                content += line
            self.handle_output(content)

#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

@AudioGod.auto_extend
class ExtractStructureAction(
    TreeRelatedBaseAction,
    ConvertDocumentBaseAction,
    NoteRelatedBaseAction,
    ExportRelatedBaseAction,
):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = {
        'description': '✋ Extract the structure by note file',
        'help': 'extract the structure by note file',
    }

    ARGUMENTS = {
        'document': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': f'{OPTIONS.AUDGOD_SOURCE}/origin.songs.note.txt',
            },
        },
        'output': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': f'{OPTIONS.AUDGOD_OUTPUT}/extract.structure.txt',
            },
        },
    }

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    #---------------------------------------------------------------------------

    def __stow_tree(self):
        result = {}
        for grouping, (genre, items) in self.summaries.items():
            groups = self.split(
                grouping,
                '/',
                escaped=True,
                del_blank=True,
                filt_empty=True,
                filt_repeated=False,
                sortify=False,
                reversify=False,
            )
            if not groups:
                continue
            cache = result
            for i, group in enumerate(groups):
                if group not in cache:
                    if i == len(groups) - 1:
                        cache[group] = [(genre, item)for item in items]
                        break
                    cache[group] = {}
                    cache = cache[group]
                    continue
                if isinstance(cache[group], dict):
                    cache = cache[group]
                    continue
                old_genre, _ = cache[group]
                if old_genre != genre:
                    self.logger.fatal(f'Grouping <{grouping}> maps to different genres!')
                    return
                cache[group].extend([(genre, item)for item in items])
                break
        return { 'Music': result }


    def pack_output(self):
        return self.tree(self.__stow_tree())

    #---------------------------------------------------------------------------

    def execute(self):
        self.analysis_note()
        self.sort_summaries()
        self.handle_output()

#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

class OperateBaseAction(AudioGod):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = None
    ARGUMENTS = None

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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

    #---------------------------------------------------------------------------

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
            },
        },
    }

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    #---------------------------------------------------------------------------

    def execute(self):
        items = self.expand_globbing(self.parameters['source'], recursive=True)
        for item in items:
            self.backup(item)

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
            },
        },
    }

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    #---------------------------------------------------------------------------

    def execute(self):
        items = self.expand_globbing(self.parameters['source'], recursive=True)
        for item in items:
            self.remove(item)

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

    #---------------------------------------------------------------------------

    def execute(self):
        items = [
            '${audgod_fullout}',
            '${export.plist.output}',
            '${organize.ituned.output}',
        ]
        for item in items:
            self.remove(self.render_template(item, indent=None))

#===============================================================================

@AudioGod.auto_extend
class Operate__TreeAction(TreeRelatedBaseAction, OperateBaseAction):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = {
        'description': '⭐ Tree directories, and show the number',
        'help': 'tree directories, and show the number',
    }

    ARGUMENTS = {
        'source': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'required': True,
                'default': f'{OPTIONS.AUDGOD_OUTPUT}/Grouped',
            },
        },
        'output': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': f'{OPTIONS.AUDGOD_OUTPUT}/operate.tree.txt',
            },
        },
    }

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    #---------------------------------------------------------------------------

    def rewrite_parameters(self):
        if 'source' in self.parameters:
            if not os.path.exists(self.parameters['source']):
                self.logger.fatal(f'Source <{self.parameters["source"]}> not exists!')
                return
            if not os.path.isdir(self.parameters['source']):
                self.logger.fatal(f'Source <{self.parameters["source"]}> not a directory!')
                return

    #---------------------------------------------------------------------------

    @classmethod
    def stow_tree(cls, path):
        def _tree(dir_):
            ret = {}
            if not os.path.isdir(dir_):
                return ret
            for item in os.listdir(dir_):
                if item.startswith('.'):
                    continue
                full_path = os.path.join(dir_, item)
                if os.path.isdir(full_path):
                    ret[item] = _tree(full_path)
                    continue
                if cls.__FILES_MARK__ not in ret:
                    ret[cls.__FILES_MARK__] = []
                ret[cls.__FILES_MARK__].append(item)
            return ret
        return { os.path.basename(path): _tree(path) }

    def pack_output(self):
        return self.tree(self.stow_tree(self.parameters['source']))

    #---------------------------------------------------------------------------

    def execute(self):
        self.handle_output()

#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

class GenerateScriptBaseAction(AudioGod):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = None
    ARGUMENTS = None

    #---------------------------------------------------------------------------

    STEPS = []

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    #---------------------------------------------------------------------------

    def generate(self):
        steps = [step for step in self.STEPS if step[0]]
        content = '#!/usr/bin/env zsh\n\n'
        content += '#' * 78 + '\n\n'
        content += f'# Created Time: {self.current_time()}\n\n'
        content += f'# Total Steps: {len(steps)}\n\n'
        content += '#' * 78 + '\n\n'
        content += 'set -e\n\n'
        content += '#' * 78 + '\n\n'
        content += f'export AUDGOD_ROOT={self.AUDGOD_ROOT}\n\n'
        content += '#' * 78 + '\n\n'
        content += 'echo "\\n[***] Starting ...\\n"\n\n'
        content += '#' * 78 + '\n\n'
        for i, step in enumerate(steps):
            if i == 0:
                content += 'printf "%.0s@" {1..60}; printf "\\n"\n'
            else:
                content += 'printf "%.0s-" {1..60}; printf "\\n"\n'
            content += f'echo "Step ({i+1}/{len(steps)}):\\n\\n"\n\n'
            if len(step) == 2:
                content += f'{step[1]}\n\n'
            else:
                if len(step) == 3:
                    carrier = ACTIONS[step[1]]['carrier']
                else:
                    carrier = ACTIONS[step[1]]['branches'][step[2]]['carrier']
                if step[-1]:
                    carrier.reset_defaults(defaults=step[-1])
                    carrier.set_usage()
                    carrier.render_usage()
                content += carrier.KWARGS['usage'].strip()
                if i < len(steps) - 1:
                    content += '\n\n' + '#' + '-' * 77 + '\n\n'
        content += '\n\n'
        content += '#' * 78 + '\n\n'
        content += 'unset AUDGOD_ROOT\n\n'
        content += '#' * 78 + '\n\n'
        content += 'printf "%.0s@" {1..60}; printf "\\n"\n'
        content += 'echo "\\n[***] Finished!\\n"\n'

        self.handle_output(content)

        if self.parameters['output']:
            if os.path.exists(self.parameters['output']):
                self.chmod(self.parameters['output'], mode=0o755)

    #---------------------------------------------------------------------------

    def execute(self):
        self.generate()

#===============================================================================

class GenerateScriptAction(GenerateScriptBaseAction):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = {
        'description': '✋ Generate a shell script',
        'help': 'generate a shell script',
    }

    ARGUMENTS = None

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        pass

    #---------------------------------------------------------------------------

    def execute(self):
        pass

#===============================================================================

class GenerateScript__StartAction(GenerateScriptBaseAction):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = {
        'description': '✋ Generate shell script to start',
        'help': 'generate shell script to start',
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

    STEPS = [
        (True, 'operate', 'cleanup', {}),
        (False, 'convert', 'kmx-to-mp4', {}),
        (True,  'convert', 'qmc-to-audio', {}),
        (False, 'convert', 'media', {}),
        (True,  'redecorate-note', {}),
        (True,  'pick', 'note', {}),
        (True,  'sift-sources', {}),
        (True,  'pick', 'sources', {}),
        (True,  'match-sources', {}),
        (True,  'merge', 'notes', {}),
        (True,  'merge', 'sources', {}),
        (True,  'extract-structure', {}),
        (True,  'fill-properties', {}),
        (True,  'format-properties', {}),
        (True,  'rename-audios', {}),
        (False, 'manage-artworks', 'bind', {}),
        (False, 'display', {}),
        (True,  'organize', 'grouped', {}),
        (True,  'list-repeated', {}),
        (True,  'operate', 'tree', {}),
        (True,  'export', 'note', {}),
        (True,  'convert', 'note-to-markdown', {}),
        (False, 'export', 'markdown', {}),
        (False, 'convert', 'markdown-to-note', {}),
        (False, 'export', 'xml', {}),
        (False, 'export', 'json', {}),
        (True,  'organize', 'ituned', {}),
        (True,  'export', 'plist', {}),
        (False, 'manage-artworks', 'derive', {}),
        (False, 'operate', 'backup', {}),
        (False, 'operate', 'remove', {}),
        (False, 'generate-script', 'start', {}),
        (False, 'testing', 'generate-script', {}),
        (False, 'testing', 'init', {}),
        (False, 'testing', 'cleanup', {}),
    ]

#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

@refresh_options
class TESTING_OPTIONS(BASEOPTIONS):
    AUDGOD_ROOT = './test'

    AUDGOD_ORIGIN = os.path.join(AUDGOD_ROOT, 'Origin')
    AUDGOD_ORISRC = os.path.join(AUDGOD_ORIGIN, 'Source')

#===============================================================================

class TestingBaseAction(TESTING_OPTIONS, AudioGod):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = None
    ARGUMENTS = None

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

#===============================================================================

class TestingAction(TestingBaseAction):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = {
        'description': '✋ Testing module',
        'help': 'Testing module',
    }

    ARGUMENTS = None

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        pass

    #---------------------------------------------------------------------------

    def execute(self):
        pass

#===============================================================================

class Testing__InitAction(TestingBaseAction):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = {
        'description': '⭐ Testing init',
        'help': 'testing init',
    }

    ARGUMENTS = {}

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    #---------------------------------------------------------------------------

    def execute(self):
        if AudioGod.AUDGOD_ROOT != self.AUDGOD_ROOT:
            self.logger.fatal('${AUDGOD_ROOT} error!')
            return

        SOURCE_KINDS = {
            'Mp3': RenameAudiosAction.ARGUMENTS_DEFAULTS()['extensions'],
            'Another': RenameAudiosAction.ARGUMENTS_DEFAULTS()['extensions'],
            'Kmx': Convert__KmxToMp4Action.ARGUMENTS_DEFAULTS()['extensions'],
            'Media': Convert__MediaAction.ARGUMENTS_DEFAULTS()['extensions'],
            'Qmc': Convert__QmcToAudioAction.ARGUMENTS_DEFAULTS()['extensions'],
            'Artwork': 'png,jpg,jpeg',
        }

        srcs = list(map(
            lambda x: os.path.join(self.AUDGOD_ORISRC, x),
            SOURCE_KINDS.keys(),
        ))

        dirs = [
            self.AUDGOD_ROOT,
            self.AUDGOD_ORIGIN,
            self.AUDGOD_ORISRC,
        ] + srcs

        files = list(map(
            lambda x: os.path.join(self.AUDGOD_ORISRC, x),
            [
                'testing.origin.songs.note.txt',
                'testing.another.origin.songs.note.txt',
                'testing.ignores.txt',
                'testing.operate.backup.txt',
                'testing.operate.remove.txt',
            ],
        ))

        for dir_ in dirs:
            if not os.path.exists(dir_):
                self.logger.fatal(f'Directory <{dir_}> not exists!')
                return
            if not os.path.isdir(dir_):
                self.logger.fatal(f'<{dir_}> not a directory!')
                return

        for file_ in files:
            if not os.path.exists(file_):
                self.logger.fatal(f'File <{file_}> not exists!')
                return
            if not os.path.isfile(file_):
                self.logger.fatal(f'<{file_}> not a file!')
                return

        for src in srcs:
            has_children = False
            exts = SOURCE_KINDS[os.path.basename(src)].lower().split(',')
            for item in os.listdir(src):
                if item.startswith('.'):
                    continue
                fullname = os.path.join(src, item)
                if not os.path.isfile(fullname):
                    continue
                _, ext = os.path.splitext(item)
                if ext:
                    ext = ext[1:].lower()
                if ext not in exts:
                    continue
                has_children = True
                break
            if not has_children:
                self.logger.fatal(f'Directory <{src}> contains no valid files!')
                return

        for item in os.listdir(self.AUDGOD_ORIGIN):
            if item.startswith('.'):
                continue
            self.duplicate(
                os.path.join(self.AUDGOD_ORIGIN, item),
                os.path.join(self.AUDGOD_ROOT, item),
            )

#===============================================================================

class Testing__CleanupAction(TestingBaseAction):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = {
        'description': '⭐ Testing cleanup',
        'help': 'testing cleanup',
    }

    ARGUMENTS = {}

    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    #---------------------------------------------------------------------------

    def execute(self):
        if AudioGod.AUDGOD_ROOT != self.AUDGOD_ROOT:
            self.logger.fatal('${AUDGOD_ROOT} error!')
            return

        if not os.path.exists(self.AUDGOD_ROOT):
            return
        if not os.path.isdir(self.AUDGOD_ROOT):
            return
        items = [
            self.AUDGOD_SOURCE,
            self.AUDGOD_OUTPUT,
        ]
        for item in items:
            self.remove(item)

#===============================================================================

class Testing__GenerateScriptAction(GenerateScriptBaseAction, TestingBaseAction):
    ACTIVE = True

    #---------------------------------------------------------------------------

    KWARGS = {
        'description': '✋ Generate shell script for testing',
        'help': 'generate shell script for testing',
    }

    ARGUMENTS = {
        'output': {
            'use_public': AudioGod.ReplaceType.PARTIAL,
            'kwargs': {
                'default': './test.zsh',
            },
        },
    }

    #---------------------------------------------------------------------------

    STEPS = [
        (False, 'operate', 'cleanup', {}), # same as <test cleanup>
        # testing part
        (True, 'testing', 'cleanup', {}),
        (True, 'testing', 'init', {}),
        # convert part
        (True, 'convert', 'kmx-to-mp4', dict(
            source=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/Kmx',
            ignored_file=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/testing.ignores.txt',
            output=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/Kmx-To-Mp4',
        )),
        (True, 'convert', 'qmc-to-audio', dict(
            source=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/Qmc',
            ignored_file=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/testing.ignores.txt',
            output=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/Qmc-To-Audio',
        )),
        (True, 'convert', 'media', dict(
            source=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/Media',
            ignored_file=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/testing.ignores.txt',
            output=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/Media',
            format='mp3',
        )),
        # main part
        (True, 'redecorate-note', dict(
            document=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/testing.origin.songs.note.txt',
            output=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/testing.redecorate.note.txt',
        )),
        (True, 'pick', 'note', dict(
            document=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/testing.redecorate.note.txt',
            another='',
            output=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/testing.pick.note.txt',
        )),
        (True, 'sift-sources', dict(
            source=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/Mp3',
            ignored_file=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/testing.ignores.txt',
            output=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/testing.sift.sources.txt',
        )),
        (True, 'pick', 'sources', dict(
            source=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/Mp3',
            another='',
            ignored_file=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/testing.ignores.txt',
            output=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/testing.pick.sources.txt',
        )),
        (True, 'match-sources', dict(
            source=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/Mp3',
            ignored_file=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/testing.ignores.txt',
            document=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/testing.redecorate.note.txt',
            output=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/testing.match.sources.txt',
        )),
        # another part
        (True, 'redecorate-note', dict(
            document=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/testing.another.origin.songs.note.txt',
            output=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/testing.another.redecorate.note.txt',
        )),
        (True, 'pick', 'note', dict(
            document=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/testing.another.redecorate.note.txt',
            another='',
            output=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/testing.another.pick.note.txt',
        )),
        (True, 'sift-sources', dict(
            source=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/Another',
            ignored_file=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/testing.ignores.txt',
            output=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/testing.another.sift.sources.txt',
        )),
        (True, 'pick', 'sources', dict(
            source=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/Another',
            another='',
            ignored_file=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/testing.ignores.txt',
            output=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/testing.another.pick.sources.txt',
        )),
        (True, 'match-sources', dict(
            source=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/Another',
            ignored_file=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/testing.ignores.txt',
            document=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/testing.another.redecorate.note.txt',
            output=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/testing.another.match.sources.txt',
        )),
        # merge part
        (True, 'merge', 'notes', dict(
            document=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/testing.redecorate.note.txt',
            another=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/testing.another.redecorate.note.txt',
            output=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/testing.merge.notes.txt',
        )),
        (True, 'pick', 'note', dict(
            document=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/testing.redecorate.note.txt',
            another=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/testing.another.redecorate.note.txt',
            output=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/testing.merge.pick.note.txt',
        )),
        (True, 'merge', 'sources', dict(
            source=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/Mp3',
            another=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/Another',
            ignored_file=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/testing.ignores.txt',
            output=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/testing.merge.sources.txt',
        )),
        (True, 'pick', 'sources', dict(
            source=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/Mp3',
            another=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/Another',
            ignored_file=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/testing.ignores.txt',
            output=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/testing.merge.pick.sources.txt',
        )),
        ## mv another sources folder to main sources folder, then execute commands below
        (True, 'match-sources', dict(
            source=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/Mp3',
            ignored_file=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/testing.ignores.txt',
            document=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/testing.merge.notes.txt',
            output=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/testing.merge.match.sources.txt',
        )),
        # normal steps
        (True, 'extract-structure', dict(
            document=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/testing.origin.songs.note.txt',
            output=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/testing.extract.structure.txt',
        )),
        (True, 'fill-properties', dict(
            source=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/Mp3',
            ignored_file=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/testing.ignores.txt',
            document=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/testing.redecorate.note.txt',
            root=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/Mp3',
            output=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/testing.fill.properties.txt',
        )),
        (True, 'format-properties', dict(
            source=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/Mp3',
            ignored_file=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/testing.ignores.txt',
        )),
        (True, 'rename-audios', dict(
            source=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/Mp3',
            ignored_file=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/testing.ignores.txt',
        )),
        # to complete
        (True, 'manage-artworks', 'bind', dict(
            source=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/Mp3',
            ignored_file=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/testing.ignores.txt',
            artworks=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/Artwork',
        )),
        (True, 'display', dict(
            source=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/Mp3',
            ignored_file=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/testing.ignores.txt',
            output=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/testing.display.txt',
        )),
        (True, 'organize', 'grouped', dict(
            source=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/Mp3',
            ignored_file=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/testing.ignores.txt',
            output=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/Grouped',
        )),
        (True, 'list-repeated', dict(
            source=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/Grouped',
            ignored_file=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/testing.ignores.txt',
            output=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/testing.list.repeated.txt',
        )),
        (True, 'operate', 'tree', dict(
            source=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/Grouped',
            output=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/testing.operate.tree.txt',
        )),
        (True, 'export', 'note', dict(
            source=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/Grouped',
            ignored_file=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/testing.ignores.txt',
            output=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/testing.export.note.txt',
        )),
        (True, 'convert', 'note-to-markdown', dict(
            document=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/testing.export.note.txt',
            output=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/testing.convert.note.to.markdown.md',
        )),
        (True, 'export', 'markdown', dict(
            source=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/Grouped',
            ignored_file=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/testing.ignores.txt',
            output=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/testing.export.markdown.md',
        )),
        (True, 'convert', 'markdown-to-note', dict(
            document=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/testing.export.markdown.md',
            output=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/testing.convert.markdown.to.note.txt',
        )),
        # to complete
        (False, 'export', 'xml', dict(
            source=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/Grouped',
            ignored_file=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/testing.ignores.txt',
            output=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/testing.export.xml',
         )),
        # to complete
        (False, 'export', 'json', dict(
            source=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/Grouped',
            ignored_file=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/testing.ignores.txt',
            output=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/testing.export.json',
         )),
        (True, 'organize', 'ituned', dict(
            source=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/Mp3',
            ignored_file=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/testing.ignores.txt',
            output=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/iTunes/iTunes Media/Music',
        )),
        (True, 'export', 'plist', dict(
            source=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/iTunes/iTunes Media/Music',
            ignored_file=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/testing.ignores.txt',
            itunes_media_folder=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/iTunes/iTunes Media/Music',
            output=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/iTunes/Library.xml',
        )),
        # to complete
        (False, 'manage-artworks', 'derive', dict(
            source=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/iTunes/iTunes Media/Music',
            ignored_file=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/testing.ignores.txt',
            output=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/Artwork',
        )),
        # operate part
        (True, 'operate', 'backup', dict(
            source=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/testing.operate.backup.txt',
        )),
        (True, 'operate', 'remove', dict(
            source=f'{TESTING_OPTIONS.AUDGOD_SOURCE}/testing.operate.remove.txt',
        )),
        # script part
        (True, 'generate-script', 'start', dict(
            output=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/testing.start.zsh',
        )),
        (True, 'testing', 'generate-script', dict(
            output=f'{TESTING_OPTIONS.AUDGOD_OUTPUT}/testing.test.zsh',
        )),
    ]

####################################################V###########################

def _get_all_subclasses(cls):
    all_subclasses = []
    for subclass in cls.__subclasses__():
        all_subclasses.append(subclass)
        all_subclasses.extend(_get_all_subclasses(subclass))
    return all_subclasses


def _get_valid_subclasses(cls):
    ret = []
    for subclass in _get_all_subclasses(cls):
        if not subclass.ACTIVE:
            continue
        if subclass.__name__.endswith('BaseAction'):
            continue
        ret.append(subclass)
    return ret


def _optimize_invokes():
    AudioGod.optimize_invokes()
    for cls in _get_all_subclasses(AudioGod):
        cls.optimize_invokes()


def _decorate_actions():
    for cls in _get_valid_subclasses(AudioGod):
        cls.decorate()


def _summarize_actions():
    actions = {}
    for cls in _get_valid_subclasses(AudioGod):
        if not cls.NAME:
            continue
        units = cls.NAME.split('.')
        match len(units):
            case 1:
                if units[0] not in actions:
                    actions[units[0]] = { 'carrier': cls }
                else:
                    actions[units[0]]['carrier'] = cls
            case 2:
                if units[0] not in actions:
                    actions[units[0]] = { 'branches': { units[1]: { 'carrier': cls } } }
                else:
                    if 'branches' not in actions[units[0]]:
                        actions[units[0]]['branches'] = { units[1]: { 'carrier': cls } }
                    else:
                        actions[units[0]]['branches'][units[1]] = { 'carrier': cls }
    ret, steps = {}, Testing__GenerateScriptAction.STEPS
    for step in steps:
        if len(step) <= 2:
            continue
        if len(step) == 3:
            ret[step[1]] = {
                key: actions[step[1]][key]
                for key in actions[step[1]].keys()
                if key != 'branches'
            }
            continue
        if step[1] not in ret:
            ret[step[1]] = {
                key: actions[step[1]][key]
                for key in actions[step[1]].keys()
                if key != 'branches'
            }
            ret[step[1]]['branches'] = {
                key: actions[step[1]]['branches'][key]
                for key in actions[step[1]]['branches'].keys()
                if key == step[2]
            }
            continue
        if 'carrier' not in ret[step[1]]:
            if 'carrier' in actions[step[1]]:
                ret[step[1]]['carrier'] = actions[step[1]]['carrier']
        if 'branches' not in ret[step[1]]:
            if 'branches' in actions[step[1]]:
                ret[step[1]]['branches'] = {
                    key: actions[step[1]]['branches'][key]
                    for key in actions[step[1]]['branches'].keys()
                    if key == step[2]
                }
            continue
        ret[step[1]]['branches'][step[2]] = actions[step[1]]['branches'][step[2]]
    return ret


def _summarize_actions_defaults():
    ret = {}
    for cls in _get_valid_subclasses(AudioGod):
        if not cls.NAME or not cls.ARGUMENTS:
            continue
        defaults = copy.deepcopy(cls.ARGUMENTS_DEFAULTS())
        if not defaults:
            continue
        for argument, default in defaults.items():
            ret[f'{cls.NAME}.{argument}'] = default
    return ret


def _render_actions():
    for cls in _get_valid_subclasses(AudioGod):
        cls.render_prog()
        cls.render_usage()

#-------------------------------------------------------------------------------

_optimize_invokes()
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
    FIGLETED = True

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

    @classmethod
    def __figleted(cls):
        return cls.FIGLETED

    @classmethod
    def __inactive_figleted(cls):
        cls.FIGLETED = False

    def format_help(self):
        help_text = ''
        if self.__figleted():
            prog = re.sub(
                fr'^{AudioGod.get_command()}',
                r'',
                self.prog.strip(),
            ).strip()
            help_text += pyfiglet.Figlet(
                # list fonts: "pipenv run python -m pyfiglet -l"
                font=random.choice([
                    'slant',
                    #'standard',
                    #'banner3-D',
                    #'starwars',
                    #'script',
                    #'block',
                    #'small',
                    #'big',
                ]),
            ).renderText(prog or 'Audio God')
            self.__inactive_figleted()
        help_text += super().format_help()
        for (action, branch), subparser in self.__subparsers:
            symbol = '-' if branch else '@'
            label = 'Branch' if branch else 'Action'
            command = f'{action} {branch}' if branch else action
            help_text += '\n' + symbol * 78 + '\n'
            help_text += pyfiglet.Figlet(
                font='mini' if len(command)>16 else 'small',
            ).renderText(command)
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
    carrier(**arguments).run()


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
    for number, field in enumerate(AudioGod.FIELDS['all']):
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
    for j in range(len(AudioGod.FIELDS['all'])):
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
        (AudioGod.ARTIST_SEPARATOR, 'Separator for several artists property of audio file.'),
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
    prog = AudioGod.get_command()
    main_parser = PerfectArgumentParser(
        prog=prog,
        usage='\n' + AudioGod.render_template(
            __USAGE__,
            indent=0,
            kwargs=dict(
                audio_properties=_audio_properties(),
                special_fields=_special_fields(),
                special_characters=_special_characters(),
            ),
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
        prog=prog,
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
                prog=prog,
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
