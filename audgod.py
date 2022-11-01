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
#       3.9.1
#   ```];
#   2. pipenv: [Pipfile => ```
#       [[source]]
#       url = "https://pypi.org/simple"
#       verify_ssl = true
#       name = "pypi"
#
#       [packages]
#       eyed3 = "*"
#       prettytable = "*"
#       mdutils = "*"
#       treelib = "*"
#       enumx = "*"
#
#       [dev-packages]
#       pylint = "*"
#
#       [requires]
#       python_version = "3.10.6"
#   ```].
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
import pydoc
import urllib
import logging
import argparse
import plistlib
import datetime

from string import Template

import eyed3
from eyed3.id3 import Genre, frames
from eyed3.id3.tag import CommentsAccessor

from treelib import Tree

from enumx import StringEnum

from prettytable import PrettyTable

'''
    The god processor for audios.
'''

################################################################################
#                                                                              #
#                                SCRIPT MACROS                                 #
#                                                                              #
################################################################################

__AVATAR__ = 'Audio God'
__VERSION__ = '1.0'

################################################################################
#                                                                              #
#                            CLASSES AND FUNCTIONS                             #
#                                                                              #
################################################################################

class TreeX(Tree):
    def __init__(self, logger=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if logger is None:
            logger = logging.getLogger()
        self.logger = logger

    def perfect_merge(self, nid, new_tree, deep=False) -> None:
        if not (isinstance(new_tree, Tree) or isinstance(new_tree, TreeX)):
            self.logger.critical('The new tree to merge is not a valid tree.')
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
            self.logger.critical(f'Node <{nid}> is not in the tree!')
            return

        current_node = self[nid]

        if current_node.tag != new_tree[new_tree.root].tag:
            self.logger.critical('Current node not same with root of new tree.')
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


class AudioGod(object):
    ORI_DIV_CHAR = '-'
    DIV_CHAR = '#'
    GROUPING_SEPARATOR = '|'


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
    class FileType(StringEnum):
        NONE = 'none'
        JSON = 'json'
        MARKDOWN = 'markdown'
        PLIST = 'plist'
        NOTE = 'note'
        DISPLAY = 'display'


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


    AUDIO_PROPERTIES = {
        'title': (('歌曲名', 'Name'), 'string'),
        'artist': (('歌手名', 'Artist'), 'string'),
        'album': (('专辑名', 'Album'), 'string'),
        'album_artist': (('专辑出品人', 'Album Artist'), 'string'),
        'genre': (('流派', 'Genre'), 'string'),
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
        'grouping': (('分组', 'Grouping'), 'string'),
        'artwork': (('封面', 'Artwork'), 'string'),
    }

    AUDIO_CN_PROPERTIES = {
        key: value[0][0] for key, value in AUDIO_PROPERTIES.items()
    }

    AUDIO_CN_PROPERTY_SYNONYMS = {
        value: key for key, value in AUDIO_CN_PROPERTIES.items()
    }

    AUDIO_EN_PROPERTIES = {
        key: value[0][1] for key, value in AUDIO_PROPERTIES.items()
    }

    AUDIO_EN_PROPERTY_SYNONYMS = {
        value: key for key, value in AUDIO_EN_PROPERTIES.items()
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
        AudioProperty.ALBUM_ARTIST,
        AudioProperty.GENRE,
    ]

    ZIP_FIELDS = [
        AudioProperty.SELECTED,
        AudioProperty.LIKED,
        AudioProperty.RATING,
        AudioProperty.GROUPING,
        AudioProperty.ARTWORK,
    ]

    CORE_FIELDS = [
        AudioProperty.TITLE,
        AudioProperty.ARTIST,
        AudioProperty.ALBUM,
        AudioProperty.ALBUM_ARTIST,
        AudioProperty.GENRE,
        AudioProperty.GROUPING,
        AudioProperty.ARTWORK,
    ]

    ITUNED_FIELDS = [
        AudioProperty.TITLE,
        AudioProperty.ARTIST,
        AudioProperty.ALBUM,
        AudioProperty.ALBUM_ARTIST,
        AudioProperty.GENRE,
        AudioProperty.SIZE,
        AudioProperty.DURATION,
        AudioProperty.BIT_RATE,
        AudioProperty.SAMPLE_FREQ,
        AudioProperty.MTIME,
    ]

    ALL_FIELDS = AudioProperty.members()

    FIELDS = {
        'default': DEFAULT_FIELDS,
        'zip': ZIP_FIELDS,
        'core': CORE_FIELDS,
        'ituned': ITUNED_FIELDS,
        'all': ALL_FIELDS,
    }


    DEFAULT_ITUNES_VERSION_PLIST = '/System/Applications/Music.app/Contents/version.plist'
    DEFAULT_ITUNES_FOLDER = os.path.expandvars('${HOME}/Music/iTunes')
    DEFAULT_ITUNES_MEDIA_FOLDER = os.path.join(DEFAULT_ITUNES_FOLDER, 'iTunes Media')
    DEFAULT_ITUNES_LIBRARY_PLIST = os.path.join(DEFAULT_ITUNES_MEDIA_FOLDER, 'Library.xml')


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
        output_file=None,
        organize_type=OrganizeType.ITUNED,
        log_level=logging.DEBUG,
    ):
        self.__logger = logging.getLogger()
        self.__logger.setLevel(log_level)
        eyed3.log.setLevel(
            #log_level,
            logging.ERROR,
        )

        self.__source_file = source_file
        self.__ignored_file = ignored_file
        self.__audios_root = audios_root
        self.__audios_source = audios_source
        self.__properties = properties
        self.__extensions = list(map(lambda x: x.lower(), filter(None, extensions)))
        self.__fields = [
            self.AudioProperty(x) for x in self.__resolve_fields(fields)
        ]
        self.__clauses = ([], {}, {}, [])
        self.__clauses_counter = (0, 0, 0, 0, 0)
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
        self.__format = {
            field: getattr(
                self, f'format_{field}', lambda x: x,
            )
            for field in self.ALL_FIELDS
        }
        self.__parse = {
            field: getattr(
                self, f'parse_{field}', lambda x: x,
            )
            for field in self.ALL_FIELDS
        }
        self.__output = {
            field: getattr(
                self,
                f'output_{field}',
                lambda x, y=self.FileType.NONE: x,
            )
            for field in self.ALL_FIELDS
        }
        self.__data_format = self.DataFormat(data_format)
        self.__display_options = self.__rewrite_options(display_options)
        self.__itunes_options = itunes_options
        self.__artwork_path = artwork_path
        self.__organize_type = AudioGod.OrganizeType(organize_type)
        self.__filename_pattern = filename_pattern
        self.__output_file = output_file

    def __resolve_fields(self, fields):
        fields_ = list(filter(None, fields.split(',')))
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
    def total_clauses_counter(self):
        return self.__clauses_counter[0]

    @property
    def invalid_clauses_counter(self):
        return self.__clauses_counter[1]

    @property
    def valid_clauses_counter(self):
        return self.__clauses_counter[2]

    @property
    def repeated_clauses_counter(self):
        return self.__clauses_counter[3]

    @property
    def grouping_clauses_counter(self):
        return self.__clauses_counter[4]

    @property
    def source_audios(self):
        src, recursive = self.audios_source
        if not os.path.exists(src):
            self.logger.fatal(f'Source <{src}> not exists!')
            return
        src = os.path.abspath(src)
        if os.path.isfile(src):
            if not self.__check_extension(src):
                self.logger.fatal(f'Source <{src}> invalid extension!')
                return
            return [src]
        if not os.path.isdir(src):
            self.logger.fatal(f'Source <{src}> not a directory!')
            return
        ret = []
        if recursive:
            for _root, _dirs, _files in os.walk(src):
                for _dir in _dirs:
                    ret.append(os.path.join(_root, _dir))
                for _file in _files:
                    ret.append(os.path.join(_root, _file))
        else:
            ret.extend(
                [os.path.join(src, audio) for audio in os.listdir(src)]
            )
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

    @staticmethod
    def unify_format(content):
        if content is None:
            return None

        def _format_english(matched):
            return matched.group('english')
            #return matched.group('english').lower().capitalize()

        ret = re.sub(
            r'(?P<english>[a-zA-Z]+)', _format_english, content,
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
        ret = re.sub(r'[、，/,]', r'&', ret)
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
    def output_title(cls, title, output_type=FileType.NONE):
        if not title:
            return ''
        ret = title
        if cls.FileType.PLIST.eq(output_type):
            ret = cls.escape_characters(ret)
        return ret

    @classmethod
    def output_album(cls, album, output_type=FileType.NONE):
        if not album:
            return ''
        ret = album
        if cls.FileType.PLIST.eq(output_type):
            ret = cls.escape_characters(ret)
        return ret

    @classmethod
    def output_album_artist(cls, album_artist, output_type=FileType.NONE):
        if not album_artist:
            return ''
        ret = album_artist
        if cls.FileType.PLIST.eq(output_type):
            ret = cls.escape_characters(ret)
        return ret

    @classmethod
    def output_artist(cls, artist, output_type=FileType.NONE):
        if not artist:
            return ''
        ret = artist
        if cls.FileType.PLIST.eq(output_type):
            ret = cls.escape_characters(ret)
        return ret

    @classmethod
    def output_genre(cls, genre, output_type=FileType.NONE):
        if not genre:
            return ''
        ret = genre
        if isinstance(genre, Genre):
            ret = genre.name
        if cls.FileType.PLIST.eq(output_type):
            ret = cls.escape_characters(ret)
        return ret

    @classmethod
    def output_bit_rate(cls, bit_rate, output_type=FileType.NONE):
        if not bit_rate:
            return ''
        if isinstance(bit_rate, tuple):
            bit_rate = bit_rate[1]
        if output_type in [cls.FileType.NONE, cls.FileType.PLIST]:
            return bit_rate
        return f'{bit_rate} kb/s'

    @classmethod
    def output_sample_freq(cls, sample_freq, output_type=FileType.NONE):
        if not sample_freq:
            return ''
        return sample_freq

    @classmethod
    def output_comments(cls, comments, output_type=FileType.NONE):
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
    def output_track_num(cls, track_num, output_type=FileType.NONE):
        if not track_num:
            return ''
        if isinstance(track_num, tuple):
            return str(track_num)
        return track_num

    @classmethod
    def output_artwork(cls, artwork, output_type=FileType.NONE):
        if not artwork:
            return ''
        return artwork

    @classmethod
    def output_duration(cls, duration, output_type=FileType.NONE):
        if not duration:
            duration = 0.0
        match output_type:
            case cls.FileType.NONE:
                return duration
            case cls.FileType.PLIST:
                return int(round(duration, 3) * 1000)
        s = duration
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)
        return '{:02d}:{:02d}:{:02d}'.format(
            int(h), int(m), int(s),
        )

    @classmethod
    def output_size(cls, size, output_type=FileType.NONE):
        if not size:
            return '0'
        if output_type in [cls.FileType.NONE, cls.FileType.PLIST]:
            return size
        suffix='B'
        for unit in ['','K','M','G','T','P','E','Z']:
            if abs(size) < 1024.0:
                return "%3.1f%s%s" % (size, unit, suffix)
            size /= 1024.0
        return "%.1f%s%s" % (size, 'Y', suffix)

    @classmethod
    def output_mtime(cls, mtime, output_type=FileType.NONE):
        if not mtime:
            return ''
        if cls.FileType.PLIST.eq(output_type):
            return cls.format_utc(mtime)
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime))

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
                    key = self.generate_key_by_audio(audio)
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
                            _value = re.sub(r'/+$', r'', dirname)
                            _value = re.sub(
                                r'^%s/{1,}' % (
                                    re.escape(re.sub(r'/+$', r'', self.audios_root)),
                                ),
                                r'',
                                _value,
                            )
                    ret = _value
                    break
        return None if ret is None else format_(parse_(ret))

    @staticmethod
    def validate_url(url):
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

    # Use AudioProperty type field here, you won't to check field parameter.
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
                                        os.path.isfile(os.paht.join(
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
                                'Audio <{}> has invalid artwork "{}"'.format(
                                    audio_object.file_info.name, value,
                                ),
                            )
                            return
            case _:
                setattr(audio_object.tag, field, value)
        audio_object.tag.save()

    # Use AudioProperty type field here, you won't to check field parameter.
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
                    #case AudioGod.AudioProperty.GROUPING:
                    #    if not ret:
                    #        ret = self.DEFAULT_GROUPING
            case _:
                if hasattr(audio_object.tag, field):
                    ret = getattr(audio_object.tag, field)
                elif hasattr(audio_object.info, field):
                    ret = getattr(audio_object.info, field)
                elif hasattr(audio_object.tag.file_info, field):
                    ret = getattr(audio_object.tag.file_info, field)
        return ret

    def fetchx(self, audio_object, field,
               formatted=False, output_type=FileType.NONE):
        ret = self.fetch(audio_object, field)
        if ret is None:
            return None
        if formatted:
            ret = self.format[field](ret)
        if self.FileType.NONE.ne(output_type):
            ret = self.output[field](ret, output_type)
        return ret

    @classmethod
    def generate_key(cls, artist, title):
        return '{}{}{}'.format(
            cls.format_artist(artist.strip()),
            cls.DIV_CHAR,
            cls.format_title(title.strip()),
        ).upper()

    def generate_key_by_audio(self, audio):
        if not self.__check_name(audio):
            self.logger.fatal(f'Invalid name of audio <{audio}>!')
            return
        name, _ = os.path.splitext(os.path.basename(audio))
        name = name.strip()
        if name.count(self.DIV_CHAR) == 1:
            return self.generate_key(*name.split(self.DIV_CHAR))
        return self.generate_key(*name.split(self.ORI_DIV_CHAR))

    def __load_ignored(self):
        if not self.ignored_file:
            return
        if not os.path.exists(self.ignored_file):
            if self.ignored_file in ['ignored.txt', './ignored.txt']:
                return
        with open(self.ignored_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    self.ignored_set.add(os.path.abspath(line))

    def process_clause(self, plain_clause, hashed_clause, final_clauses):
        title = hashed_clause.get(self.AudioProperty.TITLE, None)
        if not title:
            self.invalid_clauses.append(plain_clause)
            self.invalid_clauses_counter += 1
            return
        artist = hashed_clause.get(self.AudioProperty.ARTIST, None)
        if not artist:
            self.invalid_clauses.append(plain_clause)
            self.invalid_clauses_counter += 1
            return
        key = self.generate_key(artist, title)
        if key not in final_clauses:
            final_clauses[key] = [hashed_clause]
            self.valid_clauses_counter += 1
            return
        if len(final_clauses[key] > 1):
            final_clauses[key].append(hashed_clause)
            self.repeated_clauses_counter += 1
            return
        grouping = hashed_clause.get(
            self.AudioProperty.GROUPING, None,
        )
        if not grouping:
            grouping = self.DEFAULT_GROUPING
        final_grouping = final_clauses[key][0].get(
            self.AudioProperty.GROUPING, None,
        )
        if not final_grouping:
            final_clauses[key][0][self.AudioProperty.GROUPING] = grouping
            self.valid_clauses_counter += 1
            return
        groups = grouping.split(self.GROUPING_SEPARATOR)
        final_groups = final_grouping.split(self.GROUPING_SEPARATOR)
        if len(list(set(groups) & set(final_groups))) > 0:
            final_clauses[key].append(hashed_clause)
            self.valid_clauses_counter -= 1
            self.repeated_clauses_counter += 2
            return
        final_clauses[key][0][self.AudioProperty.GROUPING] = '{}{}{}'.format(
            final_grouping, self.GROUPING_SEPARATOR, grouping,
        )
        self.valid_clauses_counter += 1
        return

    @classmethod
    def recognize_filetype(cls, file):
        if not file:
            return cls.FileType.NONE
        _, ext = os.path.splitext(os.path.basename(file))
        ext = ext[1:].lower()
        if ext in ['json']:
            return cls.FileType.JSON
        if ext in ['md', 'markdown']:
            return cls.FileType.MARKDOWN
        if ext in ['xml', 'plist']:
            return cls.FileType.PLIST
        return cls.FileType.NOTE

    def import_(self):
        filetype = self.recognize_filetype(self.source_file)
        match filetype:
            case self.FileType.NONE | self.FileType.DISPLAY:
                return
            case self.FileType.JSON:
                self.__import_json()
            case self.FileType.MARKDOWN:
                self.__import_markdown()
            case self.FileType.PLIST:
                self.__import_plist()
            case _:
                self.__import_note()

    def __load_properties_from_file(self):
        if not os.path.exists(self.source_file):
            self.logger.fatal(f'Source file <{self.source_file}> not exists!')
            return
        self.import_()
        self.logger.warning('\n{}\n'.format('#' * 78))
        self.logger.warning(
            'Total Clauses: {}\n\n'
            'Valid Clauses: {}, '
            'Grouping Clauses: {}, '
            'Invalid Clauses: {}, '
            'Repeated Clauses: {}\n'.format(
                self.total_clauses_counter,
                self.valid_clauses_counter,
                self.grouping_clauses_counter,
                self.invalid_clauses_counter,
                self.repeated_clauses_counter,
            )
        )
        if len(self.invalid_clauses) > 0:
            self.logger.info('\nInvalid Clauses:')
            for item in self.invalid_clauses:
                self.logger.info(f'\t{item}')
        if len(self.repeated_clauses) > 0:
            self.logger.info('\nRepeated Clauses:')
            for key in self.repeated_clauses:
                self.logger.info('\t{}: [{}]'.format(
                    key, '｜'.join(self.repeated_clauses[key]),
                ))

    def __import_json(self):
        pass

    def __import_markdown(self):
        pass

    def __import_plist(self):
        pass

    def __import_note(self):
        grouping_pattern = r'^\s*#\s*\[\s*(\S+)\s*\]\s*(\S+)\s*$'
        fields_pattern = '|'.join(
            list(self.AUDIO_CN_PROPERTIES.keys()) + \
            list(self.AUDIO_CN_PROPERTY_SYNONYMS.keys()),
        )
        prefix_pattern = r'^.*(({}))[:：]'.format(fields_pattern)
        entire_pattern = \
                r'^({0})[:：].*([,，]\s*({0})[:：].*){{0,}}$'.format(
            fields_pattern,
        )

        _clauses = {}
        with open(self.source_file, 'r', encoding='utf-8') as f:
            genre, grouping = self.DEFAULT_GENRE, self.DEFAULT_GROUPING
            for line in f:
                self.total_clauses_counter += 1
                # grouping line
                if re.match(grouping_pattern, line, re.IGNORECASE) is not None:
                    _line = re.sub(grouping_pattern, r'\1====\2', line, re.IGNORECASE)
                    genre, grouping = _line.split('====')
                    self.grouping_clauses.append(line)
                    self.grouping_clauses_counter += 1
                    continue
                # audio information line 
                _line = re.sub(prefix_pattern, r'\1:', line, re.IGNORECASE)
                if re.match(entire_pattern, _line, re.IGNORECASE) is None:
                    self.invalid_clauses.append(line)
                    self.invalid_clauses_counter += 1
                    continue
                _line = re.sub(
                    r'^\s*(({}))[:：]'.format(fields_pattern),
                    r'\1:',
                    _line,
                    re.IGNORECASE,
                )
                _line = re.sub(
                    r'[,，]\s*(({}))[:：]'.format(fields_pattern),
                    r'====\1:',
                    _line,
                    re.IGNORECASE,
                )
                result = {
                    self.AudioProperty.GENRE: genre,
                    self.AudioProperty.GROUPING: grouping,
                }
                for kv in _line.split('===='):
                    k, v = [item.strip() for item in kv.split(':')]
                    k = self.AUDIO_CN_PROPERTY_SYNONYMS.get(k, k).lower()
                    if k not in self.ALL_FIELDS:
                        self.invalid_clauses.append(line)
                        self.invalid_clauses_counter += 1
                        continue
                    result[k] = v
                self.process_clause(line, result, _clauses)

        self.valid_clauses.update({
            key: _clauses[key][0]
            for key in _clauses
            if len(_clauses[key]) == 1
        })

        self.repeated_clauses.update({
            key: _clauses[key]
            for key in _clauses
            if len(_clauses[key]) > 1
        })

    def __load_audios(self):
        self.__load_ignored()

        audios = self.source_audios
        for audio in audios:
            self.logger.debug(f'Loading <{audio}> ...')
            _type = self.__check_audio(audio)
            if self.AudioType.INVALID_EXT.eq(_type):
                self.invalid_ext_audios.append(audio)
                self.logger.debug(self.AudioType.INVALID_EXT)
                continue
            if self.AudioType.INVALID_NAME.eq(_type):
                self.invalid_name_audios.append(audio)
                self.logger.debug(self.AudioType.INVALID_NAME)
                continue
            if self.AudioType.OMITTED.eq(_type):
                self.omitted_audios.append(audio)
                self.logger.debug(self.AudioType.OMITTED)
                continue
            if self.AudioType.IGNORED.eq(_type):
                self.ignored_audios.append(audio)
                self.logger.debug(self.AudioType.IGNORED)
                continue
            key = self.generate_key_by_audio(audio)
            if key in self.valid_clauses:
                self.matched_audios.add(audio)
                self.logger.debug(self.AudioType.MATCHED)
            else:
                self.notmatched_audios.add(audio)
                self.logger.debug(self.AudioType.NOTMATCHED)

        self.logger.warning('\n{}\n'.format('#' * 78))

        self.logger.warning(
            'Total Audios: {}\n\n'
            'Invalid Audios: {} '
            '(Invalid Extension Audios: {}, Invalid Name Audios: {})\n'
            'Omitted Audios: {}\n'
            'Ignored Audios: {}\n'
            'Valid Audios: {} '
            '(Matched: {}, NotMatched: {})\n'.format(
                len(self.invalid_ext_audios) \
                    + len(self.invalid_name_audios) \
                    + len(self.omitted_audios) \
                    + len(self.ignored_audios) \
                    + len(self.matched_audios) \
                    + len(self.notmatched_audios),
                len(self.invalid_ext_audios) + len(self.invalid_name_audios),
                len(self.invalid_ext_audios),
                len(self.invalid_name_audios),
                len(self.omitted_audios),
                len(self.ignored_audios),
                len(self.matched_audios) + len(self.notmatched_audios),
                len(self.matched_audios),
                len(self.notmatched_audios),
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

    def __fill_audios_tree(self) -> None:
        self.__load_audios()

        _, _, track_initial_id, playlist_initial_id = self.itunes_options
        track_id, audios = track_initial_id, self.concerned_audios

        for audio in audios:
            track_persistent_id = self.generate_persistent_id()
            audio_object = eyed3.load(audio)
            grouping = self.fetchx(audio_object, self.AudioProperty.GROUPING)
            if not grouping:
                grouping = self.DEFAULT_GROUPING
                self.logger.debug(
                    f'Empty grouping of <{audio}>, use <{self.DEFAULT_GROUPING}> instead!',
                )
            for group in grouping.split(self.GROUPING_SEPARATOR):
                group = re.sub(r'\/+', r'/', group).rstrip('/')
                if not group:
                    continue
                tags = list(filter(lambda x: x, group.split('/')))
                if not tags:
                    continue
                tags = [self.AUDIOS_TREE_ROOT_TAG] + tags
                subtree = TreeX(logger=self.logger)
                last_nid = self.AUDIOS_TREE_ROOT_NID
                for i in range(len(tags)):
                    tag, nid = tags[i], self.generate_persistent_id()
                    parent, node_type = last_nid, self.AudiosTreeNodeType.FOLDER
                    if i == 0:
                        nid = self.AUDIOS_TREE_ROOT_NID
                        parent, node_type = None, self.AudiosTreeNodeType.ROOT
                    elif i == len(tags) - 1:
                        node_type = self.AudiosTreeNodeType.PLAYLIST
                    subtree.create_node(
                        tag, nid, parent=parent,
                        data=[node_type, -1, nid, ''],
                    )
                    last_nid = nid
                subtree.create_node(
                    audio,
                    self.generate_persistent_id(),
                    parent=last_nid,
                    data=[self.AudiosTreeNodeType.TRACK, track_id, track_persistent_id, audio_object],
                )
                self.audios_tree.perfect_merge(self.AUDIOS_TREE_ROOT_NID, subtree, deep=False)
            track_id += 1

        playlist_id = playlist_initial_id
        for node in self.audios_tree.all_nodes():
            if node.is_root():
                continue
            node_type, _, _, _ = node.data
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
            node_type, _, _, _ = node.data
            if node_type in [self.AudiosTreeNodeType.TRACK, self.AudiosTreeNodeType.ROOT]:
                continue
            node.data[3] = parent.identifier

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
            if re.match('^/{0,}$', _audio) is not None:
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
        self.logger.warning('\n{}\n'.format('#' * 78))
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
            'Audios To Fill: {}, Filled Audios: {}\n'.format(
                len(audios), filled_count,
            )
        )

    def format_notes(self):
        lines = []
        with open(self.source_file, 'r', encoding='utf-8') as f:
            for line in f:
                pos = line.find('歌曲名：')
                if pos < 0:
                    pos = line.find('歌曲名:')
                    if pos < 0:
                        continue
                lines.append(line[pos:].strip())
        tmp_file = self.source_file + '.tmp'
        with open(tmp_file, 'w', encoding='utf-8') as f:
            for i in range(len(lines)):
                f.write(lines[i])
                if i < len(lines) - 1:
                    f.write('\n')
        os.remove(self.source_file)
        os.rename(tmp_file, self.source_file)

    def fill_properties(self):
        self.__load_properties_from_file()
        self.__load_audios()
        self.__fill_audio_properties()

    def format_properties(self):
        self.__load_audios()
        audios = self.concerned_audios
        self.logger.warning('\n{}\n'.format('#' * 78))
        for audio in audios:
            self.logger.debug(f'Formatting <{audio}> ...')
            audio_object = eyed3.load(audio)
            for field in self.fields:
                property_ = self.fetchx(audio_object, field, True)
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
                    audio_object, field, True,
                ) for field in self.ALL_FIELDS
            }) + ext.lower()
            if _old == _new:
                continue
            _path = os.path.dirname(audio)
            os.rename(os.paht.join(_path, _old), os.path.join(_path, _new))

    def derive_artworks(self):
        self.__load_audios()
        audios = self.concerned_audios
        for audio in audios:
            _name, _ = os.path.splitext(os.path.basename(audio))
            _path = os.path.dirname(audio)
            if self.artwork_path:
                _path = self.artwork_path
            audio_object = eyed3.load(audio)
            for i, image in enumerate(audio_object.tag.images):
                image_file = os.path.join(_path, _name)
                if len(audio_object.tag.images) > 1:
                    image_file += f'@{i}'
                image_file += '.jpg'
                with open(image_file, 'wb') as f:
                    f.write(image.image_data)

    def organize_files(self):
        if not self.audio_root:
            self.logger.fatal('Invalid audio root!')
            return
        self.__load_audios()
        audios = self.concerned_audios
        for audio in audios:
            audio_object = eyed3.load(audio)
            if self.OrganizeType.ITUNED.eq(self.organize_type):
                artist = self.fetchx(audio_object, self.AudioProperty.ARTIST)
                if not artist:
                    self.logger.fatal(f'Invalid artist of <{audio}>')
                    return
                album = self.fetchx(audio_object, self.AudioProperty.ALBUM)
                if not album:
                    self.logger.fatal(f'Invalid album of <{audio}>')
                    return
                dir_ = os.path.join(self.audio_root, artist, album)
                os.makedirs(dir_, exist_ok=True)
                newname = os.path.join(dir_, os.path.basename(audio))
                os.rename(audio, newname)
            else:
                grouping = self.fetchx(audio_object, self.AudioProperty.GROUPING)
                if not grouping:
                    self.logger.fatal(f'Invalid grouping of <{audio}>')
                    return
                groups = grouping.split(self.GROUPING_SEPARATOR)
                target = os.path.join(self.audio_root, groups[0])
                os.makedirs(target, exist_ok=True)
                target = os.path.join(target, os.path.basename(audio))
                os.rename(audio, target)
                links = [os.path.join(self.audio_root, group) for group in groups[1:]]
                for link in links:
                    os.makedirs(link, exist_ok=True)
                links = list(map(
                    lambda x: os.path.join(self.audio_root, x), links,
                ))
                for link in links:
                    if os.path.exists(link):
                        if os.path.islink(link):
                            os.remove(link)
                        else:
                            self.logger.fatal(f'<{link}> not a link!')
                            return
                    #os.link(target, link)  # 创建硬链接
                    os.symlink(target, link)  # 创建软链接

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
            (field, self.AUDIO_CN_PROPERTIES[field])
            for field in self.ALL_FIELDS
        ]
        formatted, output_type = True, self.FileType.DISPLAY
        match self.data_format:
            case self.DataFormat.ORIGINAL:
                formatted, output_type = False, self.FileType.NONE
            case self.DataFormat.FORMATTED:
                formatted, output_type = True, self.FileType.NONE
            case self.DataFormat.OUTPUTTED:
                formatted, output_type = True, self.FileType.DISPLAY
        for audio in audios:
            audio_object = eyed3.load(audio)
            results.append([
                self.fetchx(
                    audio_object, self.AudioProperty(x[0]), formatted, output_type,
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

            cn_fields_to_show = [dict(pair_fields)[x] for x in fields_to_show]
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

            cn_fields = [dict(pair_fields)[x] for x in fields]

            table = PrettyTable()
            table.field_names = cn_fields

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

            total_rows, show_page, start = len(rows), False, 0
            if total_rows > 0:
                show_page = True
                if page_size is None or page_size < 1:
                    page_size = total_rows
                else:
                    show_page = True
                total_pages = math.ceil(total_rows / page_size)
                page_number = min(max(page_number, 1), total_pages)
                start = (min(page_number, total_pages) - 1) * page_size + 1
                end = min(page_number * page_size, total_rows)
                for row in rows[start-1:end]:
                    table.add_row(row)

            table_title = f'Total Audios: {total_rows}'
            if show_page:
                table_title += f', Page Size: {page_size}'
                table_title += f', Page Number: {page_number} / {total_pages}'

            table_string = table.get_string(
                title=table_title,
                fields=cn_fields_to_show,
            )

            def _wrap_table(table_string, start=1, numbered=True,
                            style=AudioGod.DisplayStyle.TABLED):

                def _xlen_(s):
                    length = len(s)
                    utf8_length = len(s.encode('utf-8'))
                    length = (utf8_length - length) / 2 + length
                    return int(length)

                cn_number = '序号'

                _total = table_string.count('\n') - 6
                offset = 0
                if numbered:
                    offset = max(len(str(start+_total-1)), _xlen_(cn_number)) + 3
                result = re.sub(r'\n\+[\+-]{1,}\+$', r'\n', table_string)

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
                _offset -= len(re.compile(r'[\u4E00-\u9FA5]').findall(cn_number))

                result= '{}{}{}'.format(
                    result[:pos+2],
                    # 这里 offset-2-2
                    ('|{0:>%s} ' % (_offset)).format(cn_number) \
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
                    result = re.sub(r'\+[\+-]{0,}\n', r'', result)
                    result = re.sub(r'\s*\|\s*', r'|', result)
                    result = re.sub(r'^[ \t\n]{0,}\|', r'', result)
                    result = re.sub(r'\|[ \t\n]{0,}$', r'\n', result)
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
                    field_width = 2 + max(*([_xlen_(cn_number) if numbered else 0]+[
                        _xlen_(field) for field in cn_fields_to_show
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
                                        ([cn_number] if numbered \
                                        else []) + cn_fields_to_show
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
                    result = re.sub(r'[ \t\n]{1,}$', r'\n', result)
                return result

            content = _wrap_table(
                table_string, start=start, numbered=numbered, style=style,
            )
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(content)
            else:
                print(content)
            return content

        _ = _charting(
            results,
            all_fields,
            self.display_options,
            self.output_file,
        )

    @staticmethod
    def generate_persistent_id() -> str:
        return str(uuid.uuid4()).replace('-', '')[:16].upper()

    def export(self):
        filetype = self.recognize_filetype(self.output_file) 
        if self.FileType.NONE.eq(filetype):
            self.logger.fatal('Output file is empty when export!')
            return
        self.__fill_audios_tree()
        match filetype:
            case self.FileType.JSON:
                self.__export_json()
            case self.FileType.MARKDOWN:
                self.__export_markdown()
            case self.FileType.PLIST:
                self.__export_plist()
            case self.FileType.NOTE:
                self.__export_note()

    def __export_json(self):
        pass

    def __export_markdown(self):
        pass

    def __export_note(self):
        pass

    @staticmethod
    def format_utc(timestamp) -> str:
        return datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%dT%H:%M:%SZ')

    @classmethod
    def current_time(cls) -> str:
        return cls.format_utc(time.time())

    @staticmethod
    def encode(src) -> str:
        return urllib.parse.quote(src, safe='/', encoding='utf-8', errors=None)

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
            _, track_id, persistent_id, audio_object = track.data

            def _pack_properties() -> str:
                ret = ''
                for field in self.fields:
                    value = self.fetchx(audio_object, field)
                    value = self.output[field](
                        value, output_type=self.FileType.PLIST,
                    )
                    if (not isinstance(value, int)) and (not isinstance(value, float)) and (not value):
                        continue
                    ret += '\t'
                    ret += '<key>{key}</key>'.format(
                        key=self.AUDIO_EN_PROPERTIES[field],
                    )
                    type_ = self.AUDIO_PROPERTY_TYPES[field]
                    if type_ != 'boolean':
                        ret += '<{type}>{value}</{type}>'.format(
                            value=value,
                            type=self.AUDIO_PROPERTY_TYPES[field],
                        )
                    elif value == 'true':
                        ret += '<true/>'
                    ret += '\n'
                return ret.strip()

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
                properties=_pack_properties(),
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
                if self.AudiosTreeNodeType.TRACK.ne(track.data[0]):
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
                if self.AudiosTreeNodeType.TRACK.ne(track.data[0]):
                    continue
                _, track_id, _, _ = track.data
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
            node_type, id, pid, ppid = node.data
            result = Template(_format_template('''
<dict>
	<key>Name</key><string>${name}</string>
	<key>Description</key><string>${description}</string>
	<key>Playlist ID</key><integer>${playlist_id}</integer>
	<key>Playlist Persistent ID</key><string>${playlist_persistent_id}</string>
''' + ('' if (not ppid) or (ppid == self.AUDIOS_TREE_ROOT_NID) else \
'''\t<key>Parent Persistent ID</key><string>${parent_persistent_id}</string>
''') + '''\t<key>All Items</key><${show_all_items}/>
''' + ('' if self.AudiosTreeNodeType.FOLDER.ne(node_type) else '''\t<key>Folder</key><${is_folder}/>
''') + '''\t<key>Playlist Items</key>
	<array>${tracks}</array>
</dict>
            ''')).safe_substitute(dict(
                name=self.escape_characters(node.tag),
                description=self.escape_characters(''),
                playlist_id=id,
                playlist_persistent_id=pid,
                parent_persistent_id=ppid,
                show_all_items='true',
                is_folder='true',
                tracks=_pack_simple_tracks(node),
            ))
            return result

        def _pack_playlists() -> str:
            result = _pack_library()
            for node in self.audios_tree.all_nodes():
                if node.is_root():
                    continue
                node_type, _, _, _ = node.data
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

        with open(self.output_file, mode='w', encoding='utf-8') as f:
            f.write(_pack_plist())
            f.flush()

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

__USAGE__ = Template('''
All fields:
${audio_properties}

Special characters:
${special_characters}

General commands:
    1. Show help information:
        ${cmd} -h/--help

    2. Show version of program:
        ${cmd} -v/--version

    3. Format the notes file:
        ${cmd} \\
            --action=format-notes \\
            --source-file=${local}/notes.txt \\
            --log-level=DEBUG

    4. Fill properties of audios:
        ${cmd} \\
            --action=fill-properties \\
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
            \\}' \\
            --log-level=DEBUG

    5. Format properties of audios:
        ${cmd} \\
            --action=format-properties \\
            --audios-source=${music} \\
            --extensions=mp3,aac \\
            --recursive \\
            --ignored-file=${local}/ignored.txt \\
            --log-level=DEBUG

    6. Rename audios:
        ${cmd} \\
            --action=rename-audios \\
            --audios-source=${music} \\
            --extensions=mp3,aac \\
            --recursive \\
            --ignored-file=${local}/ignored.txt \\
            --filename-pattern="${delimiter}{artist} ${div_char} ${delimiter}{title}" \\
            --log-level=DEBUG

    7. Organize files:
        ${cmd} \\
            --action=organize-files \\
            --audios-source=${music} \\
            --extensions=mp3,aac \\
            --recursive \\
            --ignored-file=${local}/ignored.txt \\
            --organize-type=grouped \\
            --log-level=DEBUG

    8. Derive artworks:
        ${cmd} \\
            --action=derive-artworks \\
            --audios-source=${music} \\
            --extensions=mp3,aac \\
            --recursive \\
            --ignored-file=${local}/ignored.txt \\
            --artwork-path=${music}/artworks \\
            --log-level=DEBUG

    9. Display audios:
        ${cmd} \\
            --action=display \\
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
            --numbered \\
            --output-file="" \\
            --log-level=ERROR

    10. Export plist file for itunes or apple music:
        ${cmd} \\
            --action=export \\
            --audios-source=${music} \\
            --extensions=mp3,aac \\
            --recursive \\
            --ignored-file=${local}/ignored.txt \\
            --fields=ituned \\
            --output-file=${local}/songs.xml \\
            --itunes-version-plist=/System/Applications/Music.app/Contents/version.plist \\
            --itunes-media-folder=${music}/iTunes/iTunes\\ Media \\
            --track-initial-id=601 \\
            --playlist-initial-id=3001 \\
            --log-level=DEBUG

    11. Export markdown (or json/note) file of properties for audios:
        ${cmd} \\
            --action=export \\
            --audios-source=${music} \\
            --extensions=mp3,aac \\
            --recursive \\
            --ignored-file=${local}/ignored.txt \\
            --fields=all \\
            --output-file=${local}/songs.md \\
            --log-level=DEBUG

    12. Convert audios:
        ${cmd} \\
            --action=convert \\
            --audios-source=${music} \\
            --extensions=mp3,aac \\
            --recursive \\
            --ignored-file=${local}/ignored.txt \\
            --log-level=DEBUG

------------------------------------------------------------------------------

Sample of audio file name:

Original  audio file name: "傅梦彤-潮汐 (Natural).mp3"
Formatted audio file name: "傅梦彤 # 潮汐 (Natural).mp3"

------------------------------------------------------------------------------

Sample in note to import:

#[Pop] Vocals/Explosive/English
歌曲名：Rise And Fall (DJ版), 歌手名：Camelot, 专辑名：Rise And Fall
[]歌曲名：Drag Me Down, artist：One Direction, 专辑名：Drag Me Down, genre：Electronic
#[Pop] Vocals/ppp/qqq
1. []title：Star Sky, artist：Two Steps From Hell/Thomas Bergersen, album：Battlecry
2.[]歌曲名：Horizon, 歌手名：Janji, 专辑名：Horizon, 分组：a/b/c|d/e/f|g/h/k

------------------------------------------------------------------------------

General steps:
    No.1: Download songs, and make sure that file named with "artist-title";
    No.2: Add detail of songs to notes, then grouped;
    No.3: Format notes;
    No.4: Fill properties;
    No.5: Format properties;
    No.6: Rename audios;
    No.7: Organize files;
    No.8: Export plist, json, markdown and note file.

------------------------------------------------------------------------------
''').safe_substitute(dict(
    audio_properties=audio_properties(),
    special_characters=special_characters(),
    cmd=f'pipenv run python {sys.argv[0]}',
    music='~/Music',
    local='.',
    delimiter=AudioGod.FilenamePatternTemplate.delimiter,
    div_char=AudioGod.DIV_CHAR,
))

################################################################################
#                                                                              #
#                                MAIN FUNCTION                                 #
#                                                                              #
################################################################################

def main():
    parser = argparse.ArgumentParser(
        prog=sys.argv[0],
        usage='Use "--usage/-u" option to see details.',
        description='🎻 God of audios 🎸',
        epilog='🤔 Thinking ...',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        '--version', '-v',
        action='version',
        version='{avatar} {version}'.format(
            avatar=__AVATAR__,
            version=__VERSION__,
        ),
    )
    parser.add_argument(
        '--usage', '-u',
        action='store_true',
        dest='usage',
        help='details of usage',
    )
    parser.add_argument(
        '--action', '-a',
        type=str,
        choices=[
            'format-notes',
            'fill-properties',
            'format-properties',
            'rename-audios',
            'derive-artworks',
            'organize-files',
            'display',
            'export',
            'convert',
        ],
        required=False,
        default=None,
        dest='action',
        help='actions you want to process',
    )
    parser.add_argument(
        '--source-file', '-s',
        type=str,
        required=False,
        default='./source.txt',
        dest='source_file',
        help='source file to match',
    )
    parser.add_argument(
        '--ignored-file', '-i',
        type=str,
        required=False,
        default='./ignored.txt',
        dest='ignored_file',
        help='ignored files',
    )
    parser.add_argument(
        '--audios-source', '-c',
        type=str,
        required=False,
        default='{}/Music/Temp'.format(os.environ['HOME']),
        dest='audios_source',
        help='audio file or directory you want to process',
    )
    parser.add_argument(
        '--audios-root', '-d',
        type=str,
        required=False,
        default='{}/Music/Temp'.format(os.environ['HOME']),
        dest='audios_root',
        help='root directory of audios',
    )
    parser.add_argument(
        '--properties', '-p',
        type=str,
        required=False,
        default=None,
        dest='properties',
        help='properties for audios',
    )
    parser.add_argument(
        '--recursive', '-r',
        action='store_true',
        dest='recursive',
        help='if recursive when traverse the audios directory',
    )
    parser.add_argument(
        '--extensions', '-e',
        type=str,
        required=False,
        default=','.join(AudioGod.DEFAULT_EXTENSIONS),
        dest='extensions',
        help='valid extensions of audios',
    )
    parser.add_argument(
        '--fields', '-f',
        type=str,
        required=False,
        default='core',
        dest='fields',
        help='fields of audio to process: {}'.format(
            '; '.join([
                '({}: {})'.format(key, ','.join([f for f in fields]))
                for key, fields in AudioGod.FIELDS.items()
            ]),
        ),
    )
    parser.add_argument(
        '--page-number', '-m',
        type=int,
        required=False,
        default=1,
        dest='page_number',
        help='page number for audios display',
    )
    parser.add_argument(
        '--page-size', '-j',
        type=int,
        required=False,
        default=None,
        dest='page_size',
        help='page size for audios display',
    )
    parser.add_argument(
        '--sort', '-q',
        type=str,
        required=False,
        default=None,
        dest='sort',
        help='sort options for audios display',
    )
    parser.add_argument(
        '--filter', '-b',
        type=str,
        required=False,
        default=None,
        dest='filter',
        help='filter options for audios display',
    )
    parser.add_argument(
        '--align', '-w',
        type=str,
        required=False,
        default=None,
        dest='align',
        help='align options for audios display',
    )
    parser.add_argument(
        '--numbered', '-n',
        action='store_true',
        dest='numbered',
        help='if show number for audios display',
    )
    parser.add_argument(
        '--style', '-y',
        type=str,
        choices=AudioGod.DisplayStyle.members(),
        required=False,
        default=AudioGod.DisplayStyle.TABLED,
        dest='style',
        help='display style for audios',
    )
    parser.add_argument(
        '--data-format', '-x',
        type=str,
        choices=AudioGod.DataFormat.members(),
        required=False,
        default=AudioGod.DataFormat.OUTPUTTED,
        dest='data_format',
        help='the data format for audios to display',
    )
    parser.add_argument(
        '--output-file', '-o',
        type=str,
        required=False,
        default=None,
        dest='output_file',
        help='output file',
    )
    parser.add_argument(
        '--artwork-path', '-k',
        type=str,
        required=False,
        default=None,
        dest='artwork_path',
        help='path to export artworks',
    )
    parser.add_argument(
        '--filename-pattern', '-t',
        type=str,
        required=False,
        default='{delimiter}{{artist}} {div_char} {delimiter}{{title}}'.format(
            delimiter=AudioGod.FilenamePatternTemplate.delimiter,
            div_char=AudioGod.DIV_CHAR,
        ),
        dest='filename_pattern',
        help='filename pattern to rename audios',
    )
    parser.add_argument(
        '--organize-type', '-g',
        type=str,
        choices=AudioGod.OrganizeType.members(),
        required=False,
        default=AudioGod.OrganizeType.ITUNED,
        dest='organize_type',
        help='type of file organization',
    )
    parser.add_argument(
        '--itunes-version-plist', '-1',
        type=str,
        required=False,
        default=AudioGod.DEFAULT_ITUNES_VERSION_PLIST,
        dest='itunes_version_plist',
        help='the version plist file of itunes or apple music',
    )
    parser.add_argument(
        '--itunes-media-folder', '-2',
        type=str,
        required=False,
        default=AudioGod.DEFAULT_ITUNES_MEDIA_FOLDER,
        dest='itunes_media_folder',
        help='the media folder of itunes or apple music',
    )
    parser.add_argument(
        '--track-initial-id', '-3',
        type=int,
        required=False,
        default=AudioGod.DEFAULT_TRACK_INITIAL_ID,
        dest='track_initial_id',
        help='initial id of tracks for itunes or apple music plist file',
    )
    parser.add_argument(
        '--playlist-initial-id', '-4',
        type=int,
        required=False,
        default=AudioGod.DEFAULT_PLAYLIST_INITIAL_ID,
        dest='playlist_initial_id',
        help='initial id of playlists for itunes or apple music plist file',
    )
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
        default='DEBUG',
        dest='log_level',
        help='level of logger',
    )

    args = parser.parse_args()

    if args.usage:
        #print(__USAGE__)
        pydoc.pager(__USAGE__)
    else:
        if not args.action:
            raise Exception('Missing "action" option!')
        god = AudioGod(
            source_file=args.source_file,
            ignored_file=args.ignored_file,
            audios_root=args.audios_root,
            audios_source=(args.audios_source, args.recursive),
            properties=json.loads(args.properties) if args.properties else {},
            extensions=list(filter(None, args.extensions.split(','))),
            fields=args.fields,
            data_format=args.data_format,
            display_options=[
                args.page_number,
                args.page_size,
                json.loads(args.sort) if args.sort else [],
                json.loads(args.filter) if args.filter else {},
                args.fields,
                json.loads(args.align) if args.align else {},
                args.numbered,
                args.style,
            ],
            itunes_options=[
                args.itunes_version_plist,
                args.itunes_media_folder,
                args.track_initial_id,
                args.playlist_initial_id,
            ],
            artwork_path=args.artwork_path,
            filename_pattern=args.filename_pattern,
            output_file=args.output_file,
            organize_type=args.organize_type,
            log_level=args.log_level,
        )

        getattr(god, args.action.replace('-', '_'))()

################################################################################
#                                                                              #
#                               SCRIPT ENTRANCE                                #
#                                                                              #
################################################################################

if __name__ == '__main__':
    main()
