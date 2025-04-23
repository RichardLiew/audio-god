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
#       psutil = "*"
#       treelib = "*"
#       enumx = "*"
#       send2trash = "*"
#       prettytable = "*"
#       eyed3 = "*"
#       mdutils = "*"
#
#       [dev-packages]
#       pylint = "*"
#
#       [requires]
#       python_version = "3.10.6"
#   ```].
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
#   1. 增加 qmc0 转 mp3 的功能;
#   2. 增加 kmx 转 mp4 的功能;
#   3. 增加 mp4 转 mp3 的功能.
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
import pydoc
import urllib
import shutil
import logging
import argparse
import plistlib
import datetime

from string import Template

import psutil

from treelib import Tree
from enumx import StringEnum
from send2trash import send2trash
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

# Remain ...

################################################################################
#                                                                              #
#                            CLASSES AND FUNCTIONS                             #
#                                                                              #
################################################################################

class FatalLogger(logging.Logger):
    def __init__(self, level=logging.DEBUG):
        super().__init__('fatal', level)
        handler = logging.StreamHandler()
        handler.setLevel(level)
        self.addHandler(handler)

    def critical(self, msg, *args, **kwargs):
        super().critical(msg, *args, **kwargs)
        sys.exit(1)


class TreeX(Tree):
    def __init__(self, logger=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if logger is None:
            logger = FatalLogger(logging.DEBUG)
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
    ORI_DIV_CHAR = '-'
    DIV_CHAR = '#'
    GROUPING_SEPARATOR = '|'


    DEFAULT_MUSIC_FOLDER = '~/Music'
    DEFAULT_ITUNES_VERSION_PLIST = '/System/Applications/Music.app/Contents/version.plist'
    DEFAULT_TEMP_FOLDER = os.path.join(DEFAULT_MUSIC_FOLDER, 'temp')
    DEFAULT_ITUNES_FOLDER = os.path.join(DEFAULT_MUSIC_FOLDER, 'iTunes')
    DEFAULT_ITUNES_MEDIA_FOLDER = os.path.join(DEFAULT_ITUNES_FOLDER, 'iTunes Media')
    DEFAULT_ITUNES_LIBRARY_PLIST = os.path.join(DEFAULT_ITUNES_MEDIA_FOLDER, 'Library.xml')


    DEFAULT_SOURCE_FILE = './source.txt'
    DEFAULT_IGNORED_FILE = './ignored.txt'


    class FilenamePatternTemplate(Template):
        delimiter = '@'


    @StringEnum.unique
    class AudioType(StringEnum):
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

    DEFAULT_SOURCES = PropertySource.members()


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
    class OrganizeType(StringEnum):
        ITUNED = 'ituned'
        GROUPED = 'grouped'


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

    DEFAULT_FIELDS = [
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

    ZIP_FIELDS = [
        AudioProperty.GROUPING,
        AudioProperty.SELECTED,
        AudioProperty.LIKED,
        AudioProperty.RATING,
        AudioProperty.ARTWORK,
    ]

    ALL_FIELDS = AudioProperty.members()

    FIELDS = {
        'default': DEFAULT_FIELDS,
        'note': NOTE_FIELDS,
        'simple': SIMPLE_FIELDS,
        'zip': ZIP_FIELDS,
        'core': CORE_FIELDS,
        'ituned': ITUNED_FIELDS,
        'all': ALL_FIELDS,
    }


    AUDIOS_TREE_ROOT_TAG = '--root-tag--'
    AUDIOS_TREE_ROOT_NID = '--root-nid--'

    DEFAULT_GENRE = 'Default'
    DEFAULT_GROUPING = 'Default'

    DEFAULT_TRACK_INITIAL_ID = 601
    DEFAULT_PLAYLIST_INITIAL_ID = 3001

    DEFAULT_EXTENSIONS = ['mp3']


    def __init__(
        self,
        source_file,
        ignored_file,
        audios_root,
        audios_source,
        recursive=False,
        properties={},
        extensions=DEFAULT_EXTENSIONS,
        fields=CORE_FIELDS,
        data_format=DataFormat.OUTPUTTED,
        display_options=[
            1, None, None, None, None, None, True,
            DisplayStyle.TABLED,
        ],
        itunes_options=[
            DEFAULT_ITUNES_VERSION_PLIST,
            DEFAULT_ITUNES_MEDIA_FOLDER,
            DEFAULT_TRACK_INITIAL_ID,
            DEFAULT_PLAYLIST_INITIAL_ID,
        ],
        artwork_path=None,
        filename_pattern='{delimiter}{{artist}} {div_char} {delimiter}{{title}}'.format(
            delimiter=FilenamePatternTemplate.delimiter,
            div_char=DIV_CHAR,
        ),
        field_type=FieldType.ORIGINAL,
        output_format=FileFormat.NONE,
        output_file=None,
        organize_type=OrganizeType.ITUNED,
        log_level=logging.DEBUG,
    ):
        self.__logger = FatalLogger(log_level)
        eyed3.log.setLevel(
            #log_level,
            logging.ERROR,
        )

        self.__source_file = self.abspath(source_file)
        self.__ignored_file = self.abspath(ignored_file)
        self.__audios_root = self.abspath(audios_root)
        self.__audios_source = self.abspath(audios_source)
        self.__recursive = recursive
        self.__properties = properties
        self.__extensions = list(map(lambda x: x.lower(), filter(None, extensions)))
        self.__fields = [
            self.AudioProperty(x) for x in self.__resolve_fields(fields)
        ]
        self.__clauses = ([], {}, {}, [])
        self.__clauses_counter = [0, 0, 0, 0, 0]
        self.__audios = ([], [], [], [], set(), set())
        self.__audios_tree = TreeX(
            tree=None,
            deep=False,
            node_class=None,
            identifier=None,
            logger=self.logger,
        )
        self.audios_tree.create_node(self.AUDIOS_TREE_ROOT_TAG, self.AUDIOS_TREE_ROOT_NID)
        self.__ignored_set = set()
        self.__summaries = {}

        self.__parse = {
            field: getattr(
                self, f'parse_{field}', lambda x: x,
            )
            for field in self.ALL_FIELDS
        }
        def __parse(parse_func):
            def __func(*args):
                ret = parse_func(*args)
                return ret
            return __func
        self.__parse = {
            field: __parse(self.__parse[field])
            for field in self.ALL_FIELDS
        }

        self.__format = {
            field: getattr(
                self, f'format_{field}', lambda x: x,
            )
            for field in self.ALL_FIELDS
        }
        def __format(format_func):
            def __func(*args):
                ret = format_func(*args)
                return ret
            return __func
        self.__format = {
            field: __format(self.__format[field])
            for field in self.ALL_FIELDS
        }

        self.__output = {
            field: getattr(
                self,
                f'output_{field}',
                lambda x, output_format=self.FileFormat.NONE: x,
            )
            for field in self.ALL_FIELDS
        }
        def __output(output_func):
            def __func(*args):
                ret = output_func(*args)
                if (not isinstance(ret, int)) and (not isinstance(ret, float)) and (not ret):
                    return None
                return ret
            return __func
        self.__output = {
            field: __output(self.__output[field])
            for field in self.ALL_FIELDS
        }

        self.__data_format = self.DataFormat(data_format)
        self.__display_options = self.__rewrite_options(display_options)
        self.__artwork_path = self.abspath(artwork_path)
        self.__organize_type = AudioGod.OrganizeType(organize_type)
        self.__filename_pattern = filename_pattern
        self.__field_type = AudioGod.FieldType(field_type)
        self.__output_file = self.abspath(output_file)
        
        self.__itunes_options = itunes_options
        self.__itunes_options[0] = self.abspath(self.__itunes_options[0])
        self.__itunes_options[1] = self.abspath(self.__itunes_options[1])

        self.__output_format = AudioGod.FileFormat(output_format)
        if self.FileFormat.NONE.eq(self.__output_format):
            self.__output_format = self.recognize_file_format(self.output_file)

    def __resolve_fields(self, fields):
        fields_ = self.split(fields, r',')
        for key in self.FIELDS.keys():
            try:
                index = fields_.index(key)
                fields_ = fields_[0:index] + \
                        [x for x in self.FIELDS[key]] + \
                        fields_[index+1:]
            except:
                pass
        ret = []
        for field in fields_:
            if field not in ret:
                ret.append(field)
        return ret

    def __rewrite_options(self, options):
        page_number = options[0]
        page_size = options[1]
        sort_ = options[2] if options[2] else []
        filter_ = options[3] if options[3] else {}
        fields_to_show = self.__resolve_fields(options[4])
        align_ = options[5] if options[5] else {}
        numbered = options[6]
        style = self.DisplayStyle(options[7])

        for key in self.FIELDS.keys():
            if key in filter_.keys():
                keyword = ','.join([x for x in self.FIELDS[key]])
                filter_[keyword] = filter_.pop(key)

        return [
            page_number,
            page_size,
            sort_,
            filter_,
            fields_to_show,
            align_,
            numbered,
            style,
        ]

    @property
    def logger(self):
        return self.__logger

    @property
    def format(self):
        return self.__format

    @property
    def parse(self):
        return self.__parse

    @property
    def output(self):
        return self.__output

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
    def output_format(self):
        return self.__output_format

    @property
    def output_file(self):
        return self.__output_file

    @property
    def source_file(self):
        return self.__source_file

    @property
    def ignored_file(self):
        return self.__ignored_file

    @property
    def audios_root(self):
        return self.__audios_root

    @property
    def audios_source(self):
        return self.__audios_source

    @property
    def recursive(self):
        return self.__recursive

    @property
    def audios_tree(self):
        return self.__audios_tree

    @property
    def properties(self):
        return self.__properties

    @property
    def extensions(self):
        return self.__extensions

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
    def organize_type(self):
        return self.__organize_type

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
    def source_audios(self):
        ret = []
        if not os.path.exists(self.audios_source):
            self.logger.fatal(f'Source <{self.audios_source}> not exists!')
            return ret
        if os.path.isfile(self.audios_source):
            if not self.__check_extension(self.audios_source):
                self.logger.fatal(f'Source <{self.audios_source}> invalid extension!')
                return ret
            ret.append(self.audios_source)
            return ret
        if not os.path.isdir(self.audios_source):
            self.logger.fatal(f'Source <{self.audios_source}> not a directory!')
            return ret
        if self.recursive:
            for _root, _dirs, _files in os.walk(self.audios_source):
                for _dir in _dirs:
                    ret.append(self.abspath(_root, _dir))
                for _file in _files:
                    ret.append(self.abspath(_root, _file))
        else:
            ret.extend([
                self.abspath(self.audios_source, audio)
                for audio in os.listdir(self.audios_source)
            ])
        return ret

    @property
    def invalid_ext_audios(self):
        return self.__audios[0]

    @property
    def invalid_name_audios(self):
        return self.__audios[1]

    @property
    def omitted_audios(self):
        return self.__audios[2]

    @property
    def ignored_audios(self):
        return self.__audios[3]

    @property
    def matched_audios(self):
        return self.__audios[4]

    @property
    def notmatched_audios(self):
        return self.__audios[5]

    @property
    def concerned_audios(self):
        return self.invalid_name_audios \
               + list(self.matched_audios) \
               + list(self.notmatched_audios)

    @staticmethod
    def split(s, pattern=None, del_blank=True, filt_empty=True, filt_repeated=True, *args, **kwargs) -> list:
        if not s:
            return []
        if not pattern:
            return [s]
        ret = re.split(pattern, s, *args, **kwargs)
        if del_blank:
            ret = [item.strip() for item in ret]
        if filt_empty:
            ret = list(filter(lambda x: x, ret))
        if filt_repeated:
            ret = list(dict.fromkeys(ret))
        return ret

    @staticmethod
    def remove(file):
        if not os.path.exists(file):
            return
        send2trash(file)

    @classmethod
    def rename(cls, old, new):
        if not os.path.exists(old):
            raise Exception(f'File {old} not exists!')
        if os.path.exists(new):
            cls.remove(new)
        os.rename(old, new)

    @classmethod
    def duplicate(cls, src, dst):
        if not os.path.exists(src):
            raise Exception(f'File {src} not exists!')
        if os.path.exists(dst):
            cls.remove(dst)
        shutil.copy2(src, dst)
    
    @staticmethod
    def abspath(path, *paths):
        ret, paths = '', list(filter(lambda x: x, [path] + list(paths)))
        if len(paths) > 0:
            ret = paths[0]
        if len(paths) > 1:
            for path in paths[1:]:
                ret = os.path.join(ret, path)
        return os.path.normpath(os.path.abspath(os.path.expanduser(ret)))

    @classmethod
    def backup(cls, src):
        if not os.path.exists(src):
            raise Exception(f'File {src} not exists!')
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
        cls.duplicate(src, f'{src}.backup.{timestamp}')

    @staticmethod
    def transform_utc(timestamp) -> str:
        return datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%dT%H:%M:%SZ')

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
        ext = ext[1:].lower()
        if ext in ['json']:
            return cls.FileFormat.JSON
        if ext in ['md', 'markdown']:
            return cls.FileFormat.MARKDOWN
        if ext in ['xml', 'plist']:
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
        if track_num is None:
            return (None, None)
        ret = tuple(map(int, track_num.split(',')[:2]))
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
        grouping = re.sub(r'\s*\/\s*', r'/', grouping)
        grouping = re.sub(r'\/+', r'/', grouping)
        pattern = r'(?:\/\s*)*\s*{}\s*(?:\/\s*)*'.format(cls.GROUPING_SEPARATOR)
        grouping = re.sub(pattern, cls.GROUPING_SEPARATOR, grouping)
        grouping = re.sub(r'(?:^\/|\/$)', r'', grouping)
        groups = cls.split(grouping, cls.GROUPING_SEPARATOR)
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

    def __generate_key_by_filename(self, audio):
        if not self.__check_name(audio):
            self.logger.fatal(f'Invalid name of audio <{audio}>!')
            return
        name, _ = os.path.splitext(os.path.basename(audio))
        if name.count(self.DIV_CHAR) == 1:
            return self.generate_key(
                *self.split(name, self.DIV_CHAR, filt_empty=False, filt_repeated=False),
            )
        return self.generate_key(
            *self.split(name, self.ORI_DIV_CHAR, filt_empty=False, filt_repeated=False),
        )

    def __fetch_from_outside(self, audio, field):
        format_ = self.format[field]
        parse_ = self.parse[field]
        sources = self.properties.get('default', {}).get(
            'sources', self.DEFAULT_SOURCES,
        )
        if field in self.properties.keys():
            sources = self.properties[field].get('sources', sources)
        sources = [
            self.PropertySource(source) for source in sources
        ]
        ret = self.properties.get('default', {}).get('value', None)
        for source in sources:
            match source:
                case self.PropertySource.COMMAND:
                    if field in self.properties.keys():
                        _value = self.properties[field].get('value', None)
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
                                    re.escape(re.sub(r'/+$', r'', self.audios_root)),
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
            value = self.format[field](value)
        match field:
            case self.AudioProperty.COMMENTS:
                audio_object.tag.comments.set(value)
            case _ if field in self.ZIP_FIELDS:
                comments = audio_object.tag.comments
                if comments is None:
                    comments = '{}'
                else:
                    comments = ''.join([comment.text for comment in comments])
                try:
                    comments = json.loads(comments)
                except:
                    comments = {}
                comments[field] = value
                audio_object.tag.comments.set(json.dumps(comments))
                if self.AudioProperty.ARTWORK.eq(field):
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
                                    name=audio_object.file_info.name,
                                    value=value,
                                ),
                            )
                            return
            case _:
                setattr(audio_object.tag, field, value)
        audio_object.tag.save()

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
                    try:
                        ret = json.loads(comments).get(field, None)
                    except:
                        pass
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
                ret = self.format[field](ret)
            if self.FileFormat.NONE.ne(output_format):
                ret = self.output[field](ret, output_format)
        if default is not None:
            if not ret:
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
                if line:
                    self.ignored_set.add(self.abspath(line))

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
                    self.valid_clauses[key].update(properties)
                    self.valid_clauses[key][self.AudioProperty.GROUPING] += '{sep}grouping'.format(
                        sep=self.GROUPING_SEPARATOR,
                    )

    def __analysis_note(self):
        grouping_pattern = r'^\s*(?:\s*\(\s*(?:\s*[0-9]\s*)+\s*\)\s*)?\s*#\s*\[\s*((?:\s*\S\s*)+)\s*\]\s*((?:\s*[^:：\s]\s*)+)[:：]?\s*$'
        fields_pattern = '|'.join(
            list(self.AUDIO_CN_PROPERTIES.keys()) + \
            list(self.AUDIO_EN_PROPERTY_SYNONYMS.keys()) + \
            list(self.AUDIO_CN_PROPERTY_SYNONYMS.keys()),
        )
        detail_pattern = \
                r'^(?:(?:(?:\s*[0-9]\s*)+\.\s*)?(?:\s*\[\s*[a-zA-Z]?\s*\]\s*)?)?(?:\s*[,，;；]+\s*)?\s*({0})\s*[:：]+((?:\s*\S\s*)+?)((?:\s*[,，;；]+\s*(?:{0})\s*[:：]+(?:\s*\S\s*)+)*)$'.format(
            fields_pattern,
        )

        with open(self.source_file, 'r', encoding='utf-8') as f:
            keys, (genre, grouping) = {}, ('', '')
            for line_number, line in enumerate(f, start=1):
                if not line.strip():
                    continue
                self.total_clauses_counter += 1
                line_with_no, invalid_info = f'&{line_number}: {line}'.strip(), 'not matched'
                # grouping line
                grouping_match = re.match(grouping_pattern, line, re.IGNORECASE)
                if grouping_match is not None:
                    genre, grouping = tuple(map(
                        lambda x: x.strip(), grouping_match.groups(),
                    ))
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
                        field = self.transform_field_name_synonyms(key)
                        if not field:
                            valid, invalid_info = False, 'invalid field name'
                            break
                        if field in properties:
                            valid, invalid_info = False, 'duplicate field existed'
                            break
                        properties[field] = value
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
            'Total Clauses: {total}\n\n'
            'Valid Clauses: {valid}, '
            'Grouping Clauses: {grouping}, '
            'Invalid Clauses: {invalid}, '
            'Repeated Clauses: {repeated}\n'.format(
                total=self.total_clauses_counter,
                valid=self.valid_clauses_counter,
                grouping=self.grouping_clauses_counter,
                invalid=self.invalid_clauses_counter,
                repeated=self.repeated_clauses_counter,
            )
        )
        if len(self.invalid_clauses) > 0:
            self.logger.info('\nInvalid Clauses:')
            for item in self.invalid_clauses:
                self.logger.info(f'\t{item[0]}\n\t{item[1]}')
        if len(self.repeated_clauses) > 0:
            self.logger.info('\nRepeated Clauses:')
            for key in self.repeated_clauses:
                self.logger.info('\t{key}: [{repeated}]'.format(
                    key=key,
                    repeated='｜'.join(self.repeated_clauses[key]),
                ))

    def import_(self):
        file_format = self.recognize_file_format(self.source_file)
        if self.FileFormat.NONE.eq(file_format):
            self.logger.fatal(f'Invalid source file <{self.source_file}>.')
            return
        getattr(self, f'__import_{file_format}')()

    def __import_note(self):
        self.__analysis_note()

    def __import_json(self):
        pass

    def __import_markdown(self):
        pass

    __import_md = __import_markdown

    def __import_plist(self):
        pass

    __import_xml = __import_plist

    def __load_properties_from_file(self):
        if not os.path.exists(self.source_file):
            self.logger.fatal(f'Source file <{self.source_file}> not exists!')
            return
        self.import_()

    def __load_audios(self):
        self.__load_ignored()

        audios = self.source_audios
        for audio in audios:
            self.logger.debug(f'Loading <{audio}> ...')
            _type = self.__check_audio(audio)
            match _type:
                case self.AudioType.INVALID_EXT:
                    self.invalid_ext_audios.append(audio)
                    self.logger.debug(self.AudioType.INVALID_EXT)
                    continue
                case self.AudioType.INVALID_NAME:
                    self.invalid_name_audios.append(audio)
                    self.logger.debug(self.AudioType.INVALID_NAME)
                    continue
                case self.AudioType.OMITTED:
                    self.omitted_audios.append(audio)
                    self.logger.debug(self.AudioType.OMITTED)
                    continue
                case self.AudioType.IGNORED:
                    self.ignored_audios.append(audio)
                    self.logger.debug(self.AudioType.IGNORED)
                    continue
            key = self.__generate_key_by_filename(audio)
            if key in self.valid_clauses:
                self.matched_audios.add(audio)
                self.logger.debug(self.AudioType.MATCHED)
            else:
                self.notmatched_audios.add(audio)
                self.logger.debug(self.AudioType.NOTMATCHED)

        self.logger.warning(f'\n{"#"*78}\n')

        self.logger.warning(
            'Total Audios: {total}\n\n'
            'Invalid Audios: {invalid} '
            '(Invalid Extension Audios: {inv_ext}, Invalid Name Audios: {inv_name})\n'
            'Omitted Audios: {omitted}\n'
            'Ignored Audios: {ignored}\n'
            'Valid Audios: {valid} '
            '(Matched: {matched}, NotMatched: {notmatched})\n'.format(
                total=len(self.invalid_ext_audios) \
                    + len(self.invalid_name_audios) \
                    + len(self.omitted_audios) \
                    + len(self.ignored_audios) \
                    + len(self.matched_audios) \
                    + len(self.notmatched_audios),
                invalid=len(self.invalid_ext_audios) + len(self.invalid_name_audios),
                inv_ext=len(self.invalid_ext_audios),
                inv_name=len(self.invalid_name_audios),
                omitted=len(self.omitted_audios),
                ignored=len(self.ignored_audios),
                valid=len(self.matched_audios) + len(self.notmatched_audios),
                matched=len(self.matched_audios),
                notmatched=len(self.notmatched_audios),
            )
        )
        if len(self.invalid_ext_audios) > 0:
            self.logger.info('\nInvalid Extension Audios:')
            for audio in self.invalid_ext_audios:
                self.logger.info(f'\t{audio}')
        if len(self.invalid_name_audios) > 0:
            self.logger.info('\nInvalid Name Audios:')
            for audio in self.invalid_name_audios:
                self.logger.info(f'\t{audio}')
        if len(self.notmatched_audios) > 0:
            self.logger.info('\nNot Matched Audios:')
            for audio in self.notmatched_audios:
                self.logger.info(f'\t{audio}')

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

    def __fill_audios_tree(self) -> None:
        self.__load_audios()

        _, _, track_initial_id, playlist_initial_id = self.itunes_options
        track_id, audios = track_initial_id, self.concerned_audios

        for audio in audios:
            track_persistent_id = self.generate_persistent_id()
            audio_object = eyed3.load(audio)
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
            for group in self.split(grouping, self.GROUPING_SEPARATOR): # type: ignore
                tags = self.split(group, r'/', filt_repeated=False)
                if not tags:
                    continue
                tags = [self.AUDIOS_TREE_ROOT_TAG] + tags
                subtree = TreeX(logger=self.logger)
                last_nid, parent_tag = self.AUDIOS_TREE_ROOT_NID, ''
                for i, tag in enumerate(tags):
                    nid = self.generate_persistent_id()
                    parent, node_type = last_nid, self.AudiosTreeNodeType.FOLDER
                    if i == 0:
                        nid = self.AUDIOS_TREE_ROOT_NID
                        parent, node_type = None, self.AudiosTreeNodeType.ROOT
                    else:
                        parent_tag += f'{tag}'
                        if i == len(tags) - 1:
                            node_type = self.AudiosTreeNodeType.PLAYLIST
                        else:
                            parent_tag += '/'
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

    def __check_extension(self, audio):
        _, ext = os.path.splitext(os.path.basename(audio))
        return ext[1:].lower() in self.extensions

    @staticmethod
    def __check_name(audio):
        name, _ = os.path.splitext(os.path.basename(audio))
        name = name.strip()
        if not name:
            return False
        if name.count(AudioGod.DIV_CHAR) > 1 or not name:
            return False
        if name.count(AudioGod.DIV_CHAR) == 1 and (name[0] == AudioGod.DIV_CHAR or name[-1] == AudioGod.DIV_CHAR):
            return False
        if name.count(AudioGod.DIV_CHAR) == 0:
            if name.count(AudioGod.ORI_DIV_CHAR) != 1:
                return False
            if name[0] == AudioGod.ORI_DIV_CHAR or name[-1] == AudioGod.ORI_DIV_CHAR:
                return False
        return True

    def __check_audio(self, audio):
        _audio = audio
        while True:
            if re.match('^/*$', _audio) is not None:
                break
            if _audio in self.ignored_set or _audio+'/' in self.ignored_set:
                return self.AudioType.IGNORED
            _audio = os.path.dirname(_audio)

        if os.path.basename(audio) == '.DS_Store':
            return self.AudioType.OMITTED
        if os.path.islink(audio):
            return self.AudioType.OMITTED
        if not os.path.isfile(audio):
            return self.AudioType.OMITTED

        if not self.__check_extension(audio):
            return self.AudioType.INVALID_EXT
        if not self.__check_name(audio):
            return self.AudioType.INVALID_NAME

        return self.AudioType.VALID

    def __fill_audio_properties(self):
        audios = self.concerned_audios
        filled_count = 0
        self.logger.warning(f'\n{"#"*78}\n')
        for audio in audios:
            self.logger.debug(f'Filling <{audio}> ...')
            filled, audio_object = False, eyed3.load(audio)
            for field in self.fields:
                property_ = self.__fetch_from_outside(audio, field)
                if property_ is not None:
                    filled = True
                    self.save(audio_object, field, property_, True)
                    self.logger.debug(f'Field <{field}> assigned!')
            if filled:
                filled_count += 1
                self.logger.debug(f'Audio <{audio}> filled!')
        self.logger.warning(
            'Audios To Fill: {total}, Filled Audios: {filled}\n'.format(
                total=len(audios),
                filled=filled_count,
            )
        )

    def fill_properties(self):
        self.__load_properties_from_file()
        self.__load_audios()
        self.__fill_audio_properties()

    def format_properties(self):
        self.__load_audios()
        audios = self.concerned_audios
        self.logger.warning(f'\n{"#"*78}\n')
        for audio in audios:
            self.logger.debug(f'Formatting <{audio}> ...')
            audio_object = eyed3.load(audio)
            for field in self.fields:
                property_ = self.fetchx(audio_object, field, formatted=True)
                if property_ is not None:
                    self.save(audio_object, field, property_, True)
        self.logger.warning(f'Formatted Audios: {len(audios)}\n')

    def rename_audios(self):
        self.__load_audios()
        audios = self.concerned_audios
        for audio in audios:
            audio_object = eyed3.load(audio)
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

    def derive_artworks(self):
        self.__load_audios()
        audios = self.concerned_audios
        for audio in audios:
            _name, _ = os.path.splitext(os.path.basename(audio))
            _path = os.path.dirname(audio)
            if self.artwork_path:
                _path = self.artwork_path
            audio_object = eyed3.load(audio)
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

    def organize_files(self):
        if not self.audios_root:
            self.logger.fatal('Invalid audios root!')
            return
        self.__load_audios()
        audios = self.concerned_audios
        for audio in audios:
            audio_object = eyed3.load(audio)
            match self.organize_type:
                case self.OrganizeType.ITUNED:
                    artist = self.fetchx(audio_object, self.AudioProperty.ARTIST, formatted=True)
                    if not artist:
                        self.logger.fatal(f'Invalid artist of <{audio}>')
                        return
                    album = self.fetchx(audio_object, self.AudioProperty.ALBUM, formatted=True)
                    if not album:
                        self.logger.fatal(f'Invalid album of <{audio}>')
                        return
                    newname = self.abspath(self.audios_root, artist, album, os.path.basename(audio))
                    if newname != audio:
                        os.makedirs(os.path.dirname(newname), exist_ok=True)
                        self.rename(audio, newname)
                case self.OrganizeType.GROUPED:
                    grouping = self.fetchx(
                        audio_object, self.AudioProperty.GROUPING, formatted=True,
                    )
                    if not grouping:
                        self.logger.fatal(f'Invalid grouping of <{audio}>')
                        return
                    groups = self.split(grouping, self.GROUPING_SEPARATOR) # type: ignore
                    target = self.abspath(
                        self.audios_root, groups[0], os.path.basename(audio),
                    )
                    if target != audio:
                        os.makedirs(os.path.dirname(target), exist_ok=True)
                        self.rename(audio, target)
                        ao = eyed3.load(target)
                        self.save(
                            ao, self.AudioProperty.GROUPING, groups[0], True,
                        )
                    if len(groups) < 2:
                        continue
                    for group in groups[1:]:
                        link = self.abspath(self.audios_root, group, os.path.basename(audio))
                        if link == target:
                            continue
                        os.makedirs(os.path.dirname(link), exist_ok=True)
                        if os.path.exists(link):
                            self.remove(link)
                        self.duplicate(target, link)
                        ao = eyed3.load(link)
                        self.save(
                            ao, self.AudioProperty.GROUPING, group, True,
                        )

    def list_repeated(self):
        self.__load_audios()
        
        audios, results = self.concerned_audios, {}
        for audio in audios:
            audio_object = eyed3.load(audio)
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
        
        content = ''
        for key in results:
            items = results[key]
            if len(items) < 2:
                continue
            content += f'{key}\n'
            for item in items:
                content += f'{item}\n'
            content += '\n'

        if not content:
            content = 'No repeated!'

        if not self.output_file:
            print(content)
        else:
            self.backup(self.output_file)
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write(content)

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

        self.__load_audios()

        results, audios = [], self.concerned_audios
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
            audio_object = eyed3.load(audio)
            results.append([
                self.fetchx(
                    audio_object, self.AudioProperty(x[0]), formatted, output_format,
                )
                for x in all_fields
            ])

        def _charting(rows, pair_fields, options, output_file):
            page_number = options[0]
            page_size = options[1]
            sort_ = options[2] if options[2] else []
            filter_ = options[3] if options[3] else {}
            fields_to_show = options[4] if options[4] else []
            align_ = options[5] if options[5] else {}
            numbered = options[6]
            style = AudioGod.DisplayStyle(options[7])

            rl_fields_to_show = [dict(pair_fields)[x] for x in fields_to_show]
            fields = [x[0] for x in pair_fields]

            if align_:
                for _fields in align_.keys():
                    h, v = align_[_fields].split(':')
                    h, v = h.strip(), v.strip()
                    for _field in filter(None, _fields.split(',')):
                        _field = _field.strip()
                        if _field:
                            align_[_field] = (h if h else 'l', v if v else 'm')

            swaps = []
            for i, field in enumerate(fields_to_show):
                index = fields.index(field)
                if index < 0:
                    self.logger.fatal(f'Invalid field <{field}>!')
                    return
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
                        ignorecase and x[index].lower() != value.lower() \
                    ) or ( \
                        (not ignorecase) and x[index] != value \
                    )) if reverse else (( \
                        ignorecase and x[index].lower() == value.lower() \
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
                        ignorecase and x[index].lower().find(value.lower()) == -1 \
                    ) or ( \
                        (not ignorecase) and x[index].find(value) == -1 \
                    )) if reverse else (( \
                        ignorecase and x[index].lower().find(value.lower()) > -1 \
                    ) or ( \
                        (not ignorecase) and x[index].find(value) > -1 \
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
                            for _field in filter(None, _fields.split(',')):
                                index = fields.index(_field.strip())
                                if index < 0:
                                    self.logger.fatal(
                                        f'Invalid field <{_field}> when filter!',
                                    )
                                    return
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
                    for _field in reversed(list(filter(None, _fields.split(',')))):
                        index = fields.index(_field.strip())
                        if index < 0:
                            self.logger.fatal(
                                f'Invalid field <{_field}> when sort!',
                            )
                            return
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

                rl_number = '···'

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
                    result = re.sub(r'\s*\|\s*', r'|', result)
                    result = re.sub(r'^\s*\|', r'', result)
                    result = re.sub(r'\|\s*$', r'\n', result)
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
                        result += '\n'.join([
                            '{}{}'.format(
                                ('{0:<%s}' % (field_width,)).format(
                                    (
                                        ([rl_number] if numbered \
                                        else []) + rl_fields_to_show
                                    )[i]+':',
                                ),
                                value,
                            )
                            for i, value in enumerate(row.split('|'))
                        ])
                        result += '\n\n'
                        result += '-' * 78
                        result += '\n\n'
                        beg = end
                    result = re.sub(r'\s+$', r'\n', result)
                return result

            content = _wrap_table(
                table_string, start=start, numbered=numbered, style=style,
            )
            if not output_file:
                print(content)
            else:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(content)
            return content

        _ = _charting(
            results,
            all_fields,
            self.display_options,
            self.output_file,
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
        ret = 'Summary: Groups {group_number}, Items {item_number}\n\n'.format(
            group_number=len(self.summaries),
            item_number=sum([len(x) for _, (_, x) in self.summaries.items()]),
        )

        group_number = 0
        for group, (genre, items) in self.summaries.items():
            group_number += 1
            ret += f'\n({group_number}) #[{genre}] {group}:\n'
            item_number = 0
            for item in items:
                item_number += 1
                ret += '{number} {content}\n'.format(
                    number=f'{f"{item_number}.":<{len(str(len(items)))+1}}',
                    content=self._pack_properties_for_note(item),
                )
        return ret

    def __sort_summaries(self):
        for grouping in self.summaries:
            _, items = self.summaries[grouping]
            items.sort(
                key=lambda x: getattr(self, f'_pack_properties_for_{self.output_format}')(x),
            )
        self.summaries = {
            key: self.summaries[key] for key in sorted(self.summaries)
        }

    def preprocess_notes(self):
        self.__analysis_note()
        self.__sort_summaries()
        tmp_file = self.source_file + '.tmp'
        with open(tmp_file, 'w', encoding='utf-8') as f:
            f.write(self.__summarize_for_note())
        self.backup(self.source_file)
        self.rename(tmp_file, self.source_file)

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
        
    def export(self):
        self.__summarize()

        content = ''
        if self.FileFormat.NONE.eq(self.output_format):
            self.logger.fatal('Please set <output-format> or <output-file> options.')
            return

        content = getattr(self, f'__export_{self.output_format}')()

        if not self.output_file:
            print(content)
        else:
            self.backup(self.output_file)
            with open(self.output_file, mode='w', encoding='utf-8') as f:
                f.write(content)

    def __export_note(self):
        ret = self.__summarize_for_note()
        return ret

    def __export_json(self) -> str:
        return ''

    def __export_markdown(self) -> str:
        return ''

    __export_md = __export_markdown

    def __export_plist(self):
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

        return _pack_plist()
    
    __export_xml = __export_plist

    def convert(self):
        pass

################################################################################
#                                                                              #
#                                USAGE DETAILS                                 #
#                                                                              #
################################################################################

def audio_properties() -> str:
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


def special_characters() -> str:
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
        (AudioGod.FilenamePatternTemplate.delimiter, 'Delimiter of template for filename pattern.'),
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

################################################################################

__USAGE__ = '''
All fields:
${audio_properties}

Special characters:
${special_characters}

------------------------------------------------------------------------------

Samples of audio file name:

Original  audio file name: "傅梦彤-潮汐 (Natural).mp3"
Formatted audio file name: "傅梦彤 # 潮汐 (Natural).mp3"

------------------------------------------------------------------------------

Sample in note to import:

(1) #[Pop] Vocals/Explosive/English:
1.[x]title：Star Sky, artist：Two Steps From Hell/Thomas Bergersen, album：Battlecry
2.[]歌曲名：Horizon, 歌手名：Janji, 专辑名：Horizon, 分组：a/b/c|d/e/f|g/h/k
歌曲名：Rise And Fall (DJ版), 歌手名：Camelot, 专辑名：Rise And Fall
[]歌曲名：Drag Me Down, artist：One Direction, 专辑名：Drag Me Down, genre：Electronic
#[Pop] Vocals/ppp/qqq
1. []title：Star Sky, artist：Two Steps From Hell/Thomas Bergersen, album：Battlecry
2.[]歌曲名：Horizon, 歌手名：Janji, 专辑名：Horizon, 分组：a/b/c|d/e/f|g/h/k

------------------------------------------------------------------------------

Precautions:

1. Don't contain blank characters in genres and groupings;
2. Audios in the same group should have a same genre;
3. In invalid detail line of note.txt file, "," -> "\\" and ":" -> "/";

------------------------------------------------------------------------------

General steps:

    Step.1: Download songs, and make sure that file named with "artist-title";
    Step.2: Add detail of songs to notes, then grouped;
    Step.3: Preprocess notes, until note file not changed;
    Step.4: Fill properties;
    Step.5: Format properties;
    Step.6: Rename audios;
    Step.7: Organize files;
    Step.8: List repeated audios;
    Step.9: Export plist, json, markdown and note file.

------------------------------------------------------------------------------

General commands:

    * Show help information:
        ${cmd} -h/--help

    * Show version of program:
        ${cmd} -v/--version

------------------------------------------------------------------------------
'''

################################################################################
#                                                                              #
#                          PUBLIC PARSER ARGUMENTS                             #
#                                                                              #
################################################################################

# Successful for zsh, failed for bash.
# You should set 'PROMPT_COMMAND="history -a"' in "~/.bashrc" or "~/.bash_profile".
# And then run "source ~/.bashrc" or "source ~/.bash_profile".
def _get_command() -> str:
    interpreter = f'python {sys.argv[0]}'
    try:
        match psutil.Process().parent().name().lower(): # type: ignore
            case 'bash':
                history_file = '~/.bash_history'
            case 'zsh':
                history_file = '~/.zsh_history'
        history_file = AudioGod.abspath(history_file)
        with open(history_file, 'r', errors='ignore') as f:
            cmd = re.sub(
                r'^: *[0-9\.]+:[0-9\.]+[:;]',
                r'',
                f.readlines()[-1].strip(),
            ).strip()
            index = cmd.find(' -')
            if index != -1:
                interpreter = cmd[:index].strip()
            else:
                interpreter = cmd.strip()
    except Exception as e:
        pass
    return interpreter

def _render_usage(usage) -> str:
    _usage = '\n' + usage
    pos = next((i for i, c in enumerate(_usage[2:], 1) if c != ' '), -1)
    if pos != -1:
        _usage = re.sub(r'\n {%s}' % (pos-1,), '\n', _usage)
    return(Template(_usage).safe_substitute(dict(
        audio_properties=audio_properties(),
        special_characters=special_characters(),
        cmd=_get_command(),
        music=AudioGod.DEFAULT_MUSIC_FOLDER,
        local='.',
        delimiter=AudioGod.FilenamePatternTemplate.delimiter,
        div_char=AudioGod.DIV_CHAR,
    )))


ARGUMENTS={
    'log_level': 'DEBUG',
    'source_file': AudioGod.DEFAULT_SOURCE_FILE,
    'ignored_file': AudioGod.DEFAULT_IGNORED_FILE,
    'audios_source': AudioGod.DEFAULT_TEMP_FOLDER,
    'recursive': False,
    'audios_root': AudioGod.DEFAULT_TEMP_FOLDER,
    'properties': None,
    'extensions': ','.join(AudioGod.DEFAULT_EXTENSIONS),
    'fields': 'core',
    'page_number': 1,
    'page_size': None,
    'sort': None,
    'filter': None,
    'align': None,
    'numbered': False,
    'style': AudioGod.DisplayStyle.TABLED,
    'data_format': AudioGod.DataFormat.OUTPUTTED,
    'field_type': AudioGod.FieldType.ORIGINAL,
    'output_format': AudioGod.FileFormat.NONE,
    'output_file': None,
    'artwork_path': None,
    'filename_pattern': '{delimiter}{{artist}} {div_char} {delimiter}{{title}}'.format(
        delimiter=AudioGod.FilenamePatternTemplate.delimiter,
        div_char=AudioGod.DIV_CHAR,
    ),
    'organize_type': AudioGod.OrganizeType.ITUNED,
    'itunes_version_plist': AudioGod.DEFAULT_ITUNES_VERSION_PLIST,
    'itunes_media_folder': AudioGod.DEFAULT_ITUNES_MEDIA_FOLDER,
    'track_initial_id': AudioGod.DEFAULT_TRACK_INITIAL_ID,
    'playlist_initial_id': AudioGod.DEFAULT_PLAYLIST_INITIAL_ID,
}


ACTIONS={
    'preprocess-notes': {
        'arguments': [
            'source_file',
            'field_type',
        ],
        'kwargs': {
            'description': '✋ Preprocess the notes file',
            'help': 'preprocess the notes file',
            'usage': _render_usage('''
                ${cmd} preprocess-notes \\
                    --source-file=${local}/notes.txt \\
                    --field-type=cn
            '''),
        },
    },
    'fill-properties': {
        'arguments': [
            'audios_source',
            'extensions',
            'recursive',
            'ignored_file',
            'source_file',
            'audios_root',
            'properties',
        ],
        'kwargs': {
            'description': '✋ Fill properties of audios',
            'help': 'fill properties of audios',
            'usage': _render_usage('''
                ${cmd} fill-properties \\
                    --audios-source=${music} \\
                    --extensions=mp3,aac \\
                    --recursive \\
                    --ignored-file=${local}/ignored.txt \\
                    --source-file=${local}/notes.txt \\
                    --audios-root=${music} \\
                    --properties='\\{ \\
                        "default": \\{ \\
                            "sources": ["command"], #(note: command/file/directory/filename) \\
                            "value": "" \\
                        \\}, \\
                        "genre": \\{ \\
                            "sources": ["command", "file"], #(note: command/file/directory/filename) \\
                            "value": "Pop" \\
                        \\} \\
                    \\}'
            '''),
            },
    },
    'format-properties': {
        'arguments': [
            'audios_source',
            'extensions',
            'recursive',
            'ignored_file',
        ],
        'kwargs': {
            'description': '✋ Format properties of audios',
            'help': 'format properties of audios',
            'usage': _render_usage('''
                ${cmd} format-properties \\
                    --audios-source=${music} \\
                    --extensions=mp3,aac \\
                    --recursive \\
                    --ignored-file=${local}/ignored.txt
            '''),
        },
    },
    'rename-audios': {
        'arguments': [
            'audios_source',
            'extensions',
            'recursive',
            'ignored_file',
            'filename_pattern',
        ],
        'kwargs': {
            'description': '✋ Rename audios',
            'help': 'rename audios',
            'usage': _render_usage('''
                ${cmd} rename-audios \\
                    --audios-source=${music} \\
                    --extensions=mp3,aac \\
                    --recursive \\
                    --ignored-file=${local}/ignored.txt \\
                    --filename-pattern="${delimiter}{artist} ${div_char} ${delimiter}{title}"
            '''),
        },
    },
    'organize-files': {
        'arguments': [
            'audios_root',
            'audios_source',
            'extensions',
            'recursive',
            'ignored_file',
            'organize_type',
        ],
        'kwargs': {
            'description': '✋ Organize files',
            'help': 'organize files',
            'usage': _render_usage('''
                ${cmd} organize-files \\
                    --audios-root=${music} \\
                    --audios-source=${music} \\
                    --extensions=mp3,aac \\
                    --recursive \\
                    --ignored-file=${local}/ignored.txt \\
                    --organize-type=grouped
            '''),
        },
    },
    'list-repeated': {
        'arguments': [
            'audios_source',
            'extensions',
            'recursive',
            'ignored_file',
            'output_file',
        ],
        'kwargs': {
            'description': '✋ List repeated audio files by artist and title',
            'help': 'list repeated',
            'usage': _render_usage('''
                ${cmd} list-repeated \\
                    --audios-source=${music} \\
                    --extensions=mp3,aac \\
                    --recursive \\
                    --ignored-file=${local}/ignored.txt \\
                    --output-file=""
            '''),
        },
    },
    'derive-artworks': {
        'arguments': [
            'audios_source',
            'extensions',
            'recursive',
            'ignored_file',
            'artwork_path',
        ],
        'kwargs': {
            'description': '✋ Derive artworks',
            'help': 'derive artworks',
            'usage': _render_usage('''
                ${cmd} derive-artworks \\
                    --audios-source=${music} \\
                    --extensions=mp3,aac \\
                    --recursive \\
                    --ignored-file=${local}/ignored.txt \\
                    --artwork-path=${music}/artworks
            '''),
        },
    },
    'display': {
        'arguments': [
            'audios_source',
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
            'output_file',
        ],
        'kwargs': {
            'description': '✋ Display audios',
            'help': 'display audios',
            'usage': _render_usage('''
                ${cmd} display \\
                    --audios-source=${music} \\
                    --extensions=mp3,aac \\
                    --recursive \\
                    --ignored-file=${local}/ignored.txt \\
                    --fields=core \\
                    --page-number=1 \\
                    --page-size=10 \\
                    --sort='[["title,artist", true], ["genre", false]]' \\
                    --filter='\\{ \\
                        "_options": \\{ \\
                            "relation": "and" #(note: and/or) \\
                        \\}, \\
                        "title,core": \\{ \\
                            "function": "search", #(note: equal/search/empty) \\
                            "parameters": ["a", true, false] \\
                        \\} \\
                    \\}' \\
                    --align='\\{ \\
                        "title,artist": "l:m" #(note: align=l/c/r, valign=t/m/b) \\
                    \\}' \\
                    --style=tabled \\
                    --data-format=outputted \\
                    --field-type=cn \\
                    --numbered \\
                    --output-file=""
            '''),
        },
    },
    'export': {
        'arguments': [
            'audios_source',
            'extensions',
            'recursive',
            'ignored_file',
            'fields',
            'field_type',
            'output_format',
            'output_file',
            'itunes_version_plist',
            'itunes_media_folder',
            'track_initial_id',
            'playlist_initial_id',
        ],
        'kwargs': {
            'description': '✋ Export details to file',
            'help': 'export details to file',
            'usage': _render_usage('''
                ${cmd} export \\
                    --audios-source=${music} \\
                    --extensions=mp3,aac \\
                    --recursive \\
                    --ignored-file=${local}/ignored.txt \\
                    --fields=ituned \\
                    --field-type=cn \\
                    --output-format=plist \\
                    --output-file=${local}/songs.xml \\
                    --itunes-version-plist=/System/Applications/Music.app/Contents/version.plist \\
                    --itunes-media-folder=${music}/iTunes/iTunes\\ Media \\
                    --track-initial-id=601 \\
                    --playlist-initial-id=3001
            '''),
        },
    },
    'convert': {
        'arguments': [
            'audios_source',
            'extensions',
            'recursive',
            'ignored_file',
        ],
        'kwargs': {
            'description': '✋ Convert audios',
            'help': 'convert audios',
            'usage': _render_usage('''
                ${cmd} convert \\
                    --audios-source=${music} \\
                    --extensions=mp3,aac \\
                    --recursive \\
                    --ignored-file=${local}/ignored.txt
            '''),
        },
    },
}


def _add_arguments(parser, arguments=[]) -> None:
    parser.add_argument(
        '--log-level', '-l',
        type=str,
        choices=[
            'NOTSET',
            'DEBUG',
            'INFO',
            'WARN',
            'WARNING',
            'ERROR',
            'FATAL',
            'CRITICAL',
        ],
        required=False,
        default=ARGUMENTS['log_level'],
        dest='log_level',
        help='level of logger',
    )

    if 'source_file' in arguments:
        parser.add_argument(
            '--source-file', '-s',
            type=str,
            required=False,
            default=ARGUMENTS['source_file'],
            dest='source_file',
            help='source file to match',
        )
    
    if 'ignored_file' in arguments:
        parser.add_argument(
            '--ignored-file', '-i',
            type=str,
            required=False,
            default=ARGUMENTS['ignored_file'],
            dest='ignored_file',
            help='ignored files',
        )
    
    if 'audios_source' in arguments:
        parser.add_argument(
            '--audios-source', '-c',
            type=str,
            required=False,
            default=ARGUMENTS['audios_source'],
            dest='audios_source',
            help='audio file or directory you want to process',
        )
    
    if 'audios_root' in arguments:
        parser.add_argument(
            '--audios-root', '-d',
            type=str,
            required=False,
            default=ARGUMENTS['audios_root'],
            dest='audios_root',
            help='root directory of audios',
        )
    
    if 'properties' in arguments:
        parser.add_argument(
            '--properties', '-p',
            type=str,
            required=False,
            default=ARGUMENTS['properties'],
            dest='properties',
            help='properties for audios',
        )
    
    if 'recursive' in arguments:
        parser.add_argument(
            '--recursive', '-r',
            action='store_true',
            dest='recursive',
            help='if recursive when traverse the audios directory',
        )
    
    if 'extensions' in arguments:
        parser.add_argument(
            '--extensions', '-e',
            type=str,
            required=False,
            default=ARGUMENTS['extensions'],
            dest='extensions',
            help='valid extensions of audios',
        )
    
    if 'fields' in arguments:
        parser.add_argument(
            '--fields', '-f',
            type=str,
            required=False,
            default=ARGUMENTS['fields'],
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
            default=ARGUMENTS['page_number'],
            dest='page_number',
            help='page number for audios display',
        )
    
    if 'page_size' in arguments:
        parser.add_argument(
            '--page-size', '-j',
            type=int,
            required=False,
            default=ARGUMENTS['page_size'],
            dest='page_size',
            help='page size for audios display',
        )
    
    if 'sort' in arguments:
        parser.add_argument(
            '--sort', '-q',
            type=str,
            required=False,
            default=ARGUMENTS['sort'],
            dest='sort',
            help='sort options for audios display',
        )
    
    if 'filter' in arguments:
        parser.add_argument(
            '--filter', '-b',
            type=str,
            required=False,
            default=ARGUMENTS['filter'],
            dest='filter',
            help='filter options for audios display',
        )
    
    if 'align' in arguments:
        parser.add_argument(
            '--align', '-w',
            type=str,
            required=False,
            default=ARGUMENTS['align'],
            dest='align',
            help='align options for audios display',
        )
    
    if 'numbered' in arguments:
        parser.add_argument(
            '--numbered', '-n',
            action='store_true',
            dest='numbered',
            help='if show number for audios display',
        )
    
    if 'style' in arguments:
        parser.add_argument(
            '--style', '-y',
            type=str,
            choices=AudioGod.DisplayStyle.members(),
            required=False,
            default=ARGUMENTS['style'],
            dest='style',
            help='display style for audios',
        )
    
    if 'data_format' in arguments:
        parser.add_argument(
            '--data-format', '-x',
            type=str,
            choices=AudioGod.DataFormat.members(),
            required=False,
            default=ARGUMENTS['data_format'],
            dest='data_format',
            help='the data format for audios to display',
        )
    
    if 'field_type' in arguments:
        parser.add_argument(
            '--field-type', '-8',
            type=str,
            choices=AudioGod.FieldType.members(),
            required=False,
            default=ARGUMENTS['field_type'],
            dest='field_type',
            help='type of field name',
        )
    
    if 'output_format' in arguments:
        parser.add_argument(
            '--output-format', '-9',
            type=str,
            choices=AudioGod.FileFormat.members(),
            required=False,
            default=ARGUMENTS['output_format'],
            dest='output_format',
            help='format of output content',
        )
    
    if 'output_file' in arguments:
        parser.add_argument(
            '--output-file', '-o',
            type=str,
            required=False,
            default=ARGUMENTS['output_file'],
            dest='output_file',
            help='output file',
        )
    
    if 'artwork_path' in arguments:
        parser.add_argument(
            '--artwork-path', '-k',
            type=str,
            required=False,
            default=ARGUMENTS['artwork_path'],
            dest='artwork_path',
            help='path to export artworks',
        )
    
    if 'filename_pattern' in arguments:
        parser.add_argument(
            '--filename-pattern', '-t',
            type=str,
            required=False,
            default=ARGUMENTS['filename_pattern'],
            dest='filename_pattern',
            help='filename pattern to rename audios',
        )
    
    if 'organize_type' in arguments:
        parser.add_argument(
            '--organize-type', '-g',
            type=str,
            choices=AudioGod.OrganizeType.members(),
            required=False,
            default=ARGUMENTS['organize_type'],
            dest='organize_type',
            help='type of file organization',
        )
    
    if 'itunes_version_plist' in arguments:
        parser.add_argument(
            '--itunes-version-plist', '-1',
            type=str,
            required=False,
            default=ARGUMENTS['itunes_version_plist'],
            dest='itunes_version_plist',
            help='the version plist file of itunes or apple music',
        )
    
    if 'itunes_media_folder' in arguments:
        parser.add_argument(
            '--itunes-media-folder', '-2',
            type=str,
            required=False,
            default=ARGUMENTS['itunes_media_folder'],
            dest='itunes_media_folder',
            help='the media folder of itunes or apple music',
        )
    
    if 'track_initial_id' in arguments:
        parser.add_argument(
            '--track-initial-id', '-3',
            type=int,
            required=False,
            default=ARGUMENTS['track_initial_id'],
            dest='track_initial_id',
            help='initial id of tracks for itunes or apple music plist file',
        )
    
    if 'playlist_initial_id' in arguments:
        parser.add_argument(
            '--playlist-initial-id', '-4',
            type=int,
            required=False,
            default=ARGUMENTS['playlist_initial_id'],
            dest='playlist_initial_id',
            help='initial id of playlists for itunes or apple music plist file',
        )


def _handle_subcmd(args) -> None:
    _arguments = copy.deepcopy(ARGUMENTS)

    for _argument in _arguments:
        if hasattr(args, _argument):
            _arguments[_argument] = getattr(args, _argument)

    god = AudioGod(
        source_file=_arguments['source_file'],
        ignored_file=_arguments['ignored_file'],
        audios_root=_arguments['audios_root'],
        audios_source=_arguments['audios_source'],
        recursive=_arguments['recursive'],
        properties=json.loads(_arguments['properties']) if _arguments['properties'] else {},
        extensions=AudioGod.split(_arguments['extensions'], ','),
        fields=_arguments['fields'],
        data_format=_arguments['data_format'],
        display_options=[
            _arguments['page_number'],
            _arguments['page_size'],
            json.loads(_arguments['sort']) if _arguments['sort'] else [],
            json.loads(_arguments['filter']) if _arguments['filter'] else {},
            _arguments['fields'],
            json.loads(_arguments['align']) if _arguments['align'] else {},
            _arguments['numbered'],
            _arguments['style'],
        ],
        itunes_options=[
            _arguments['itunes_version_plist'],
            _arguments['itunes_media_folder'],
            _arguments['track_initial_id'],
            _arguments['playlist_initial_id'],
        ],
        artwork_path=_arguments['artwork_path'],
        filename_pattern=_arguments['filename_pattern'],
        field_type=_arguments['field_type'],
        output_format=_arguments['output_format'],
        output_file=_arguments['output_file'],
        organize_type=_arguments['organize_type'],
        log_level=_arguments['log_level'],
    )

    getattr(god, args.subcmd.replace('-', '_'))()

################################################################################
#                                                                              #
#                                MAIN FUNCTION                                 #
#                                                                              #
################################################################################

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
            help_text += f'\nSubcommand "{name}" help info:\n\n'
            help_text += subparser.format_help()
        return help_text

    def print_help(self):
        pydoc.pager(self.format_help())
        self.exit(0)

    def error(self, message):
        #if re.search(r'(required: \w+|需要以下参数: \w+)', message):
        #    self.print_help()
        super().error(message)


def main():
    parser = GreatArgumentParser(
        prog=sys.argv[0],
        usage=_render_usage(__USAGE__),
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
    
    parser.add_argument(
        '--version', '-v',
        action='version',
        version=__VERSION__,
    )

    subparsers = parser.add_subparsers(
        prog=sys.argv[0],
        title='Subcommands',
        description='the available subcommands show below:',
        dest='subcmd',
        required=False,
        metavar='subcommand name:   ',
        help='subcommand statement:',
    )

    for _action in ACTIONS:
        _kwargs = {
            'description': '',
            'help': '',
            'usage': '',
            'epilog': '😴 Sleeping ...',
            'formatter_class': argparse.ArgumentDefaultsHelpFormatter,
            #'prog': None,
            #'aliases': (),
            #'prefix_chars': '-',
            #'fromfile_prefix_chars': None,
            #'argument_default': None,
            #'conflict_handler': 'error',
            #'add_help': True,
            #'allow_abbrev': True,
            #'exit_on_error': True,
        }
        _kwargs.update(ACTIONS[_action].get('kwargs', {}))
        _subparser = subparsers.add_parser(_action, **_kwargs)
        _add_arguments(
            _subparser,
            ACTIONS[_action].get('arguments', []),
        )
        _subparser.set_defaults(execute=_handle_subcmd)
        parser.add_subparser((_action, _subparser))

    args = parser.parse_args()
    # only for subparsers, error for main parser
    args.execute(args)

################################################################################
#                                                                              #
#                               SCRIPT ENTRANCE                                #
#                                                                              #
################################################################################

if __name__ == '__main__':
    main()
