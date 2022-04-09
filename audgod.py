#!/usr/bin/env python
# -*- coding: UTF-8 -*-

###############################################################################
#
#    TODOS:
#        1. 增加qmc0转mp3的功能;
#        2. 增加kmx转mp4的功能;
#        3. 增加mp4转mp3的功能;
#
#    COMMANDS:
#        1. 查看音频信息：```
#            ffmpeg -i ~/Music/Demo.mp3
#        ```;
#        2. 查看帮助：```
#            pipenv run python main.py --help
#        ```;
#        3. 查看版本：```
#            pipenv run python main.py --version
#        ```;
#        4. 预处理 Notes 文件：```
#            pipenv run python main.py \
#                    -a format-notes \
#                    -n ./notes.txt \
#                    -l DEBUG
#        ```;
#        5. 填充音频文件属性：```
#            pipenv run python main.py \
#                    -a fill-properties \
#                    -n ./notes.txt \
#                    -i ./ignored.txt \
#                    -o ${HOME}/Music/Temp \
#                    -r \
#                    -g Pop \
#                    -s notefile \
#                    -e mp3 \
#                    -l DEBUG
#        ```;
#        6. 统一音频文件属性：```
#            pipenv run python main.py \
#                    -a format-properties \
#                    -n ./notes.txt \
#                    -i ./ignored.txt \
#                    -o ${HOME}/Music/Temp \
#                    -r \
#                    -g Pop \
#                    -s notefile \
#                    -e mp3 \
#                    -l DEBUG
#        ```;
#        7. 根据音频属性重命名文件：```
#            pipenv run python main.py \
#                    -a rename-audios \
#                    -n ./notes.txt \
#                    -i ./ignored.txt \
#                    -o ${HOME}/Music/Temp \
#                    -r \
#                    -g Pop \
#                    -s notefile \
#                    -e mp3 \
#                    -l DEBUG
#        ```;
#
#    FILES:
#        1. pyenv: [.python-version => ```
#            3.9.1
#        ```];
#        2. pipenv: [Pipfile => ```
#            [[source]]
#            url = "https://pypi.org/simple"
#            verify_ssl = true
#            name = "pypi"
#
#            [packages]
#            eyed3 = "*"
#
#            [dev-packages]
#
#            [requires]
#            python_version = "3.9.1"
#        ```]
#
#
###############################################################################

import os
import re
import math
import time
import uuid
import json
import urllib
import logging
import argparse
import plistlib
import datetime

from string import Template
from enum import Enum, unique

import eyed3
from eyed3.id3 import Genre, frames
from eyed3.id3.tag import CommentsAccessor

from treelib import Tree, Node

from prettytable import PrettyTable


class AudioProcessor(object):
    DIV_CHAR = '#'
    ORI_DIV_CHAR = '-'


    @unique
    class AudioType(Enum):
       VALID = 'valid'
       MATCHED = 'matched'
       NOTMATCHED = 'notmatched'
       OMITTED = 'omitted'
       IGNORED = 'ignored'
       INVALID_EXT = 'invalid-ext'
       INVALID_NAME = 'invalid-name'


    @unique
    class PropertySource(Enum):
       COMMAND = 'command'
       NOTEFILE = 'notefile'
       FILENAME = 'filename'
       DIRECTORY = 'directory'

    DEFAULT_SOURCES = [source for source in PropertySource]


    @unique
    class DisplayStyle(Enum):
       TABLED = 'tabled'
       COMPACT = 'compact'
       VERTICAL = 'vertical'


    @unique
    class DataFormat(Enum):
       ORIGINAL = 'original'
       FORMATTED = 'formatted'
       OUTPUTTED = 'outputted'


    @unique
    class OrganizeType(Enum):
       ITUNED = 'ituned'
       GROUPED = 'grouped'


    AUDIO_PROPERTIES = {
        'title': '歌曲名',
        'artist': '歌手名',
        'album': '专辑名',
        'album_artist': '专辑出品人',
        'genre': '流派',
        'comments': '备注',
        'track_num': '音轨号',
        'composer': '作曲人',
        'publisher': '出版公司',
        'mtime': '修改时间',
        'duration': '时长',
        'bit_rate_str': '比特率',
        'sample_freq': '采样率',
        'mode': '模式',
        'size': '文件大小',
        'name': '文件名',
        'path': '文件路径',
        'selected': '已选择',
        'liked': '喜欢',
        'rating': '评分',
        'grouping': '分组',
        'artwork': '封面',
    }

    AUDIO_PROPERTY_SYNONYMS = {
        value: key for key, value in AUDIO_PROPERTIES.items()
    }

    AudioProperty = unique(Enum(
        'AudioProperty', {
            prop.upper(): prop for prop in AUDIO_PROPERTIES.keys()
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

    ALL_FIELDS = [prop for prop in AudioProperty]


    DEFAULT_ITUNES_VERSION_PLIST = '/System/Applications/Music.app/Contents/version.plist'
    DEFAULT_ITUNES_FOLDER = '{}/Music/iTunes'.format(os.environ['HOME'])
    DEFAULT_ITUNES_MEDIA_FOLDER = '{}/iTunes Media'.format(DEFAULT_ITUNES_FOLDER)
    DEFAULT_ITUNES_LIBRARY_PLIST = '{}/Library.xml'.format(DEFAULT_ITUNES_MEDIA_FOLDER)


    def __init__(
        self,
        notes_file,
        ignored_file,
        audios_root,
        audios_source,
        properties={},
        extensions=['mp3'],
        fields=[field.value for field in CORE_FIELDS],
        data_format=DataFormat.OUTPUTTED.value,
        display_options=[
            1, None, None, None, None, None, True,
            DisplayStyle.TABLED.value,
        ],
        itunes_options=[
            DEFAULT_ITUNES_VERSION_PLIST,
            DEFAULT_ITUNES_MEDIA_FOLDER,
            DEFAULT_ITUNES_LIBRARY_PLIST,
        ],
        artwork_path=None,
        filename_pattern='%{artist} ' + DIV_CHAR + ' %{title}',
        output_file=None,
        organize_type=OrganizeType.ITUNED.value,
        log_level=logging.DEBUG,
    ):
        self.__notes_file = notes_file
        self.__ignored_file = ignored_file
        self.__audios_root = audios_root
        self.__audios_source = audios_source
        self.__properties = properties
        self.__extensions = list(map(lambda x: x.lower(), filter(None, extensions)))
        self.__fields = [
            self.AudioProperty(x) for x in self.__resolve_fields(fields)
        ]
        self.__notes = ([], {}, {})
        self.__audios = ([], [], [], [], set(), set())
        self.__grouped_audios = Tree(tree=None, deep=False, node_class=None, identifier=None)
        self.__ignored_set = set()
        self.__format_functions = {
            field.value: getattr(
                self, 'format_{}'.format(field.value), lambda x: x,
            )
            for field in self.ALL_FIELDS
        }
        self.__parse_functions = {
            field.value: getattr(
                self, 'parse_{}'.format(field.value), lambda x: x,
            )
            for field in self.ALL_FIELDS
        }
        self.__output_functions = {
            field.value: getattr(
                self, 'output_{}'.format(field.value), lambda x: x,
            )
            for field in self.ALL_FIELDS
        }
        self.__data_format = self.DataFormat(data_format)
        self.__display_options = self.__rewrite_options(display_options)
        self.__itunes_options = itunes_options
        self.__artwork_path = artwork_path
        self.__organize_type = AudioProcessor.OrganizeType(organize_type)
        self.__filename_pattern = filename_pattern
        self.__output_file = output_file
        self.__logger = logging.getLogger()
        self.__logger.setLevel(log_level)
        eyed3.log.setLevel(log_level)

    def __resolve_fields(self, fields):
        ret = list(filter(None, fields.split(',')))
        try:
            index = ret.index('cores')
            ret = ret[0:index] + \
                    [x.value for x in self.CORE_FIELDS] + \
                    ret[index+1:]
        except:
            pass
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

        if 'cores' in filter_.keys():
            key = ','.join([x.value for x in self.CORE_FIELDS])
            filter_[key] = filter_.pop('cores')

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
    def format_functions(self):
        return self.__format_functions

    @property
    def parse_functions(self):
        return self.__parse_functions

    @property
    def output_functions(self):
        return self.__output_functions

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
    def notes_file(self):
        return self.__notes_file

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
    def grouped_audios(self):
        return self.__grouped_audios

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
    def invalid_notes(self):
        return self.__notes[0]

    @property
    def valid_notes(self):
        return self.__notes[1]

    @property
    def repeated_notes(self):
        return self.__notes[2]

    @property
    def source_audios(self):
        src, recursive = self.audios_source
        if not os.path.exists(src):
            raise Exception('Source <{}> not exists!'.format(src))
        src = os.path.abspath(src)
        if os.path.isfile(src):
            if not self.__check_extension(src):
                raise Exception('Source <{}> invalid extension!'.format(src))
            return [src]
        if not os.path.isdir(src):
            raise Exception('Source <{}> not a directory!'.format(src))
        ret = []
        if recursive:
            for _root, _dirs, _files in os.walk(src):
                for _dir in _dirs:
                    ret.append(os.path.join(_root, _dir))
                for _file in _files:
                    ret.append(os.path.join(_root, _file))
        else:
            ret.extend(
                ['{}/{}'.format(src, audio) for audio in os.listdir(src)]
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
    def unify_format(property_content):
        if property_content is None:
            return None

        def _format_english(matched):
            return matched.group('english')
            #return matched.group('english').lower().capitalize()

        ret = re.sub(
            r'(?P<english>[a-zA-Z]+)', _format_english, property_content,
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
        ret = re.sub(r'[ \t]+', r' ', ret).strip()
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
        ret = re.sub(r'[ \t]{0,}&[ \t]{0,}', r' & ', ret)
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
    def output_genre(cls, genre):
        if genre is None:
            return None
        if isinstance(genre, str):
            return genre
        return genre.name

    @classmethod
    def output_comments(cls, comments):
        if comments is None:
            return None
        if isinstance(comments, str):
            return comments
        ret = ''
        for i in range(len(comments)):
            ret += comments[i].text
            if i < len(comments) - 1:
                ret += '\n'
        return ret

    @classmethod
    def output_track_num(cls, track_num):
        if track_num is None:
            return None
        if isinstance(track_num, str):
            return track_num
        return str(track_num)

    @classmethod
    def output_artwork(cls, artwork):
        if artwork is None:
            return None
        return artwork

    @classmethod
    def output_duration(cls, duration):
        if duration is None:
            return None
        s = duration
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)
        return '{:02d}:{:02d}:{:02d}'.format(
            int(h), int(m), int(s),
        )

    @classmethod
    def output_size(cls, size, suffix='B'):
        if size is None:
            return None
        for unit in ['','K','M','G','T','P','E','Z']:
            if abs(size) < 1024.0:
                return "%3.1f%s%s" % (size, unit, suffix)
            size /= 1024.0
        return "%.1f%s%s" % (size, 'Y', suffix)

    @classmethod
    def output_mtime(cls, mtime):
        if mtime is None:
            return None
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime))

    def __fetch_from_outside(self, audio, field):
        format_ = self.format_functions[field.value]
        parse_ = self.parse_functions[field.value]
        sources = self.properties.get('default', {}).get(
            'sources', [
                source.value for source in self.DEFAULT_SOURCES
            ],
        )
        if field.value in self.properties.keys():
            sources = self.properties[field.value].get('sources', sources)
        sources = [
            self.PropertySource(source) for source in sources
        ]
        ret = self.properties.get('default', {}).get('value', None)
        for source in sources:
            if source == self.PropertySource.COMMAND:
                if field.value in self.properties.keys():
                    _value = self.properties[field.value].get('value', None)
                    if _value is not None:
                        ret = _value
                        break
            elif source == self.PropertySource.NOTEFILE:
                key = self.generate_key_by_audio(audio)
                _value = self.valid_notes.get(key, {}).get(field.value, None)
                if _value is not None:
                    ret = _value
                    break
            elif source == self.PropertySource.DIRECTORY:
                _value = dirname = os.path.dirname(audio)
                if field == self.AudioProperty.GENRE:
                    _value = os.path.basename(dirname)
                elif field == self.AudioProperty.COMMENTS:
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
    def __assign_to_audio(self, audio_object, field, value, formatted=False):
        if value is None:
            return
        if formatted:
            value = self.format_functions[field.value](value)
        if field == self.AudioProperty.COMMENTS:
            audio_object.tag.comments.set(value)
        elif field in self.ZIP_FIELDS:
            comments = audio_object.tag.comments
            if comments is None:
                comments = '{}'
            else:
                comments = ''.join([comment.text for comment in comments])
            try:
                comments = json.loads(comments)
            except:
                comments = {}
            comments[field.value] = value
            audio_object.tag.comments.set(json.dumps(comments))
            if field == self.AudioProperty.ARTWORK:
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
                                    os.path.isfile('{}/{}'.format(
                                        self.artwork_path, value,
                                    ))
                                )
                            )
                    if valid:
                        _, ext = os.path.splitext(os.path.basename(value))
                        audio_object.tag.images.set(
                            type_=3,
                            img_data=open(value, 'rb').read(),
                            mime_type='image/{}'.format(ext[1:].lower()),
                        )
                    else:
                        raise Exception(
                            'Audio <{}> has invalid artwork "{}"'.format(
                                audio_object.file_info.name, value,
                            ),
                        )
        else:
            setattr(audio_object.tag, field.value, value)
        audio_object.tag.save()

    # Use AudioProperty type field here, you won't to check field parameter.
    def __fetch_from_audio(self, audio_object, field,
                           formatted=False, outputted=False):
        ret, filename = None, audio_object.tag.file_info.name
        if field == AudioProcessor.AudioProperty.GENRE:
            ret = audio_object.tag.genre.name
        elif field == AudioProcessor.AudioProperty.TRACK_NUM:
            ret = audio_object.tag.track_num
        elif field == AudioProcessor.AudioProperty.DURATION:
            ret = audio_object.info.time_secs
        elif field == AudioProcessor.AudioProperty.MTIME:
            ret = audio_object.tag.file_info.mtime
        elif field == AudioProcessor.AudioProperty.SIZE:
            ret = audio_object.info.size_bytes
        elif field == AudioProcessor.AudioProperty.NAME:
            ret = os.path.basename(filename)
        elif field == AudioProcessor.AudioProperty.PATH:
            ret = os.path.dirname(filename)
        elif field == AudioProcessor.AudioProperty.COMMENTS:
            ret = audio_object.tag.comments
        elif field in self.ZIP_FIELDS:
            comments = audio_object.tag.comments
            if comments:
                comments = ''.join([comment.text for comment in comments])
                try:
                    ret = json.loads(comments).get(field.value, None)
                except:
                    pass
            if field == AudioProcessor.AudioProperty.ARTWORK:
                if len(audio_object.tag.images) == 0 and not ret:
                    ret = None
                else:
                    ret = (len(audio_object.tag.images), ret if ret else '')
        else:
            if hasattr(audio_object.tag, field.value):
                ret = getattr(audio_object.tag, field.value)
            elif hasattr(audio_object.info, field.value):
                ret = getattr(audio_object.info, field.value)
            elif hasattr(audio_object.tag.file_info, field.value):
                ret = getattr(audio_object.tag.file_info, field.value)
        if ret is None:
            return None
        if formatted:
            ret = self.format_functions[field.value](ret)
        if outputted:
            ret = self.output_functions[field.value](ret)
        return ret

    @classmethod
    def generate_key(cls, artist, title):
        return '{}{}{}'.format(
            cls.format_artist(artist.strip()),
            cls.DIV_CHAR,
            cls.format_title(title.strip()),
        ).upper()

    @classmethod
    def generate_key_by_audio(cls, audio):
        if not cls.__check_name(audio):
            raise Exception('Invalid name of audio <{}>!'.format(audio))
        name, _ = os.path.splitext(os.path.basename(audio))
        name = name.strip()
        if name.count(cls.DIV_CHAR) == 1:
            return cls.generate_key(*name.split(cls.DIV_CHAR))
        return cls.generate_key(*name.split(cls.ORI_DIV_CHAR))

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

    def __load_notes(self):
        if not self.notes_file:
            return
        if not os.path.exists(self.notes_file):
            if self.notes_file in ['notes.txt', './notes.txt']:
                return
        fields_pattern = '|'.join(
            list(self.AUDIO_PROPERTIES.keys()) + \
            list(self.AUDIO_PROPERTY_SYNONYMS.keys()),
        )
        prefix_pattern = r'^.*(({}))[:：]'.format(fields_pattern)
        entire_pattern = \
                r'^({0})[:：].*([,，][ \t]{{0,}}({0})[:：].*){{0,}}$'.format(
            fields_pattern,
        )

        _notes = {}
        with open(self.notes_file, 'r', encoding='utf-8') as f:
            for line in f:
                _line = re.sub(prefix_pattern, r'\1:', line, re.IGNORECASE)
                if re.match(entire_pattern, _line, re.IGNORECASE) is None:
                    self.invalid_notes.append(line)
                    continue
                _line = re.sub(
                    r'^[ \t]{{0,}}(({}))[:：]'.format(fields_pattern),
                    r'\1:',
                    _line,
                    re.IGNORECASE,
                )
                _line = re.sub(
                    r'[,，][ \t]{{0,}}(({}))[:：]'.format(fields_pattern),
                    r'|\1:',
                    _line,
                    re.IGNORECASE,
                )
                result = {}
                for kv in _line.split('|'):
                    k, v = [item.strip() for item in kv.split(':')]
                    k = self.AUDIO_PROPERTY_SYNONYMS.get(k, k).lower()
                    if k not in [field.value for field in self.ALL_FIELDS]:
                        self.invalid_notes.append(line)
                        continue
                    result[k] = v
                title = result.get(self.AudioProperty.TITLE.value, None)
                if not title:
                    self.invalid_notes.append(line)
                    continue
                artist = result.get(self.AudioProperty.ARTIST.value, None)
                if not artist:
                    self.invalid_notes.append(line)
                    continue
                key = self.generate_key(artist, title)
                if key in _notes:
                    _notes[key].append(result)
                else:
                    _notes[key] = [result]

        self.valid_notes.update({
            key: _notes[key][0]
            for key in _notes
            if len(_notes[key]) == 1
        })

        self.repeated_notes.update({
            key: _notes[key]
            for key in _notes
            if len(_notes[key]) > 1
        })

        self.logger.warning('\n{}\n'.format('#' * 78))

        self.logger.warning(
            'Total Notes: {}\n\n'
            'Valid Notes: {}, '
            'Invalid Notes: {}, '
            'Repeated Notes: {}\n'.format(
                len(self.valid_notes) \
                + len(self.invalid_notes) \
                + len([
                    item
                    for value in self.repeated_notes.values()
                    for item in value
                ]),
                len(self.valid_notes),
                len(self.invalid_notes),
                len([
                    item
                    for value in self.repeated_notes.values()
                    for item in value
                ]),
            )
        )
        if len(self.invalid_notes) > 0:
            self.logger.info('\nInvalid Notes:')
            for item in self.invalid_notes:
                self.logger.info('\t{}'.format(item))
        if len(self.repeated_notes) > 0:
            self.logger.info('\nRepeated Notes:')
            for key in self.repeated_notes:
                self.logger.info('\t{}: [{}]'.format(
                    key, '｜'.join(self.repeated_notes[key]),
                ))

    def __load_audios(self):
        for audio in self.source_audios:
            self.logger.debug('Loading <{}> ...'.format(audio))
            _type = self.__check_audio(audio)
            if _type == self.AudioType.INVALID_EXT:
                self.invalid_ext_audios.append(audio)
                self.logger.debug(self.AudioType.INVALID_EXT.value)
                continue
            if _type == self.AudioType.INVALID_NAME:
                self.invalid_name_audios.append(audio)
                self.logger.debug(self.AudioType.INVALID_NAME.value)
                continue
            if _type == self.AudioType.OMITTED:
                self.omitted_audios.append(audio)
                self.logger.debug(self.AudioType.OMITTED.value)
                continue
            if _type == self.AudioType.IGNORED:
                self.ignored_audios.append(audio)
                self.logger.debug(self.AudioType.IGNORED.value)
                continue
            key = self.generate_key_by_audio(audio)
            if key in self.valid_notes:
                self.matched_audios.add(audio)
                self.logger.debug(self.AudioType.MATCHED.value)
            else:
                self.notmatched_audios.add(audio)
                self.logger.debug(self.AudioType.NOTMATCHED.value)

        self.logger.warning('\n{}\n'.format('#' * 78))

        self.logger.warning(
            'Total Audios: {}\n\n'
            'Invalid Audios: {}, '
            'Invalid Extension Audios: {}, '
            'Invalid Name Audios: {}\n'
            'Omitted Audios: {}\n'
            'Ignored Audios: {}\n'
            'Valid Audios: {}, '
            'Matched: {}, '
            'NotMatched: {}\n'.format(
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
                self.logger.info('\t{}'.format(audio))
        if len(self.invalid_name_audios) > 0:
            self.logger.info('\nInvalid Name Audios:')
            for audio in self.invalid_name_audios:
                self.logger.info('\t{}'.format(audio))
        if len(self.notmatched_audios) > 0:
            self.logger.info('\nNot Matched Audios:')
            for audio in self.notmatched_audios:
                self.logger.info('\t{}'.format(audio))

    def __check_extension(self, audio):
        _, ext = os.path.splitext(os.path.basename(audio))
        return ext[1:].lower() in self.extensions

    @staticmethod
    def __check_name(audio):
        name, _ = os.path.splitext(os.path.basename(audio))
        name = name.strip()
        if not name:
            return False
        if name.count(AudioProcessor.DIV_CHAR) > 1 or not name:
            return False
        if name.count(AudioProcessor.DIV_CHAR) == 1 and (name[0] == AudioProcessor.DIV_CHAR or name[-1] == AudioProcessor.DIV_CHAR):
            return False
        if name.count(AudioProcessor.DIV_CHAR) == 0:
            if name.count(AudioProcessor.ORI_DIV_CHAR) != 1:
                return False
            if name[0] == AudioProcessor.ORI_DIV_CHAR or name[-1] == AudioProcessor.ORI_DIV_CHAR:
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
            self.logger.debug('Filling <{}> ...'.format(audio))
            filled, audio_object = False, eyed3.load(audio)
            for field in self.fields:
                property_ = self.__fetch_from_outside(audio, field)
                if property_ is not None:
                    filled = True
                    self.__assign_to_audio(audio_object, field, property_, True)
                    self.logger.debug('Field <{}> assigned!'.format(field.value))
            if filled:
                filled_count += 1
                self.logger.debug('Audio <{}> filled!'.format(audio))
        self.logger.warning(
            'Audios To Fill: {}, Filled Audios: {}\n'.format(
                len(audios), filled_count,
            )
        )

    def format_notes(self):
        lines = []
        with open(self.notes_file, 'r', encoding='utf-8') as f:
            for line in f:
                pos = line.find('歌曲名：')
                if pos < 0:
                    pos = line.find('歌曲名:')
                    if pos < 0:
                        continue
                lines.append(line[pos:].strip())
        tmp_file = self.notes_file + '.tmp'
        with open(tmp_file, 'w', encoding='utf-8') as f:
            for i in range(len(lines)):
                f.write(lines[i])
                if i < len(lines) - 1:
                    f.write('\n')
        os.remove(self.notes_file)
        os.rename(tmp_file, self.notes_file)

    def fill_properties(self):
        self.__load_notes()
        self.__load_ignored()
        self.__load_audios()
        self.__fill_audio_properties()

    def format_properties(self):
        self.__load_ignored()
        self.__load_audios()
        audios = self.concerned_audios
        self.logger.warning('\n{}\n'.format('#' * 78))
        for audio in audios:
            self.logger.debug('Formatting <{}> ...'.format(audio))
            audio_object = eyed3.load(audio)
            for field in self.fields:
                property_ = self.__fetch_from_audio(
                    audio_object, field, True, False,
                )
                if property_ is not None:
                    self.__assign_to_audio(audio_object, field, property_, True)
        self.logger.warning(
            'Formatted Audios: {}\n'.format(len(audios)),
        )

    def rename_audios(self):
        class StringTemplate(Template):
            delimiter = '%'

        self.__load_ignored()
        self.__load_audios()
        audios = self.concerned_audios
        for audio in audios:
            audio_object = eyed3.load(audio)
            _old = os.path.basename(audio)
            _, ext = os.path.splitext(_old)
            _new = StringTemplate(self.filename_pattern).safe_substitute({
                field.value: self.__fetch_from_audio(
                    audio_object, field, True, False
                ) for field in self.ALL_FIELDS
            }) + ext.lower()
            if _old == _new:
                continue
            _path = os.path.dirname(audio)
            os.rename('{}/{}'.format(_path, _old), '{}/{}'.format(_path, _new))

    def export_artworks(self):
        self.__load_ignored()
        self.__load_audios()
        audios = self.concerned_audios
        for audio in audios:
            _name, _ = os.path.splitext(os.path.basename(audio))
            _path = os.path.dirname(audio)
            if self.artwork_path:
                _path = self.artwork_path
            audio_object = eyed3.load(audio)
            for i, image in enumerate(audio_object.tag.images):
                image_file = '{}/{}'.format(_path, _name)
                if len(audio_object.tag.images) > 1:
                    image_file += '@{}'.format(i)
                image_file += '.jpg'
                with open(image_file, 'wb') as f:
                    f.write(image.image_data)

    def organize_files(self):
        if not self.audio_root:
            raise Exception('Invalid audio root!')
        self.__load_ignored()
        self.__load_audios()
        audios = self.concerned_audios
        for audio in audios:
            audio_object = eyed3.load(audio)
            if self.organize_type == self.OrganizeType.ITUNED:
                artist = self.__fetch_from_audio(
                    audio_object, self.AudioProperty.ARTIST, False, False,
                )
                if not artist:
                    raise Exception('Invalid artist of <{}>'.format(audio))
                album = self.__fetch_from_audio(
                    audio_object, self.AudioProperty.ALBUM, False, False,
                )
                if not album:
                    raise Exception('Invalid album of <{}>'.format(audio))
                dir_ = '{}/{}/{}'.format(self.audio_root, artist, album)
            else:
                grouping = self.__fetch_from_audio(
                    audio_object, self.AudioProperty.GROUPING, False, False,
                )
                if not grouping:
                    raise Exception('Invalid grouping of <{}>'.format(audio))
                dir_ = '{}/{}'.format(self.audio_root, grouping)
            os.makedirs(dir_, exist_ok=True)
            newname = '{}/{}'.format(dir_, os.path.basename(audio))
            os.rename(audio, newname)

    def display_audios(self):
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

        self.__load_ignored()
        self.__load_audios()

        results, audios = [], self.concerned_audios
        all_fields = [
            (field.value, self.AUDIO_PROPERTIES[field.value])
            for field in self.ALL_FIELDS
        ]
        formatted, outputted = True, True
        if self.data_format == self.DataFormat.ORIGINAL:
            formatted, outputted = False, False
        elif self.data_format == self.DataFormat.FORMATTED:
            formatted, outputted = True, False
        elif self.data_format == self.DataFormat.OUTPUTTED:
            formatted, outputted = True, True
        for audio in audios:
            audio_object = eyed3.load(audio)
            results.append([
                self.__fetch_from_audio(
                    audio_object, self.AudioProperty(x[0]), formatted, outputted,
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
            style = AudioProcessor.DisplayStyle(options[7])

            cn_fields_to_show = [dict(pair_fields)[x] for x in fields_to_show]
            fields = [x[0] for x in pair_fields]

            if align_:
                _keys = [k for k in align_.keys()]
                for _fields in _keys:
                    h, v = align_[_fields].split(':')
                    h, v = h.strip(), v.strip()
                    for _field in filter(None, _fields.split(',')):
                        _field = _field.strip()
                        if _field:
                            align_[_field] = (h if h else 'l', v if v else 'c')

            swaps = []
            for i, field in enumerate(fields_to_show):
                index = fields.index(field)
                if index < 0:
                    raise Exception('Invalid field <{}>!'.format(field))
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
                table.valign[field] = 'c'
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
                                    raise Exception(
                                        'Invalid field <%s> when filter!' % (
                                            _field,
                                        ),
                                    )
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
                                'Invalid function <{}>!'.format(function),
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
                    for _field in reversed(list(filter(None, _fields.split(',')))):
                        index = fields.index(_field.strip())
                        if index < 0:
                            raise Exception(
                                'Invalid field <{}> when sort!'.format(_field),
                            )
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

            table_title = 'Total Audios: {}'.format(total_rows)
            if show_page:
                table_title += ', Page Size: {}'.format(page_size)
                table_title += ', Page Number: {} / {}'.format(
                    page_number, total_pages,
                )

            table_string = table.get_string(
                title=table_title,
                fields=cn_fields_to_show,
            )

            def _wrap_table(table_string, start=1, numbered=True,
                            style=AudioProcessor.DisplayStyle.TABLED):

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

                if style != AudioProcessor.DisplayStyle.TABLED:
                    beg = result.find('|\n+', 0)
                    end = result.find('|\n+', beg+3)
                    result = result[:beg+2] + result[end+2:]
                    result = re.sub(r'\+[\+-]{0,}\n', r'', result)
                    result = re.sub(r'[ \t]{0,}\|[ \t]{0,}', r'|', result)
                    result = re.sub(r'^[ \t\n]{0,}\|', r'', result)
                    result = re.sub(r'\|[ \t\n]{0,}$', r'\n', result)
                    result = re.sub(r'\|\n\|', r'\n', result)

                if style == AudioProcessor.DisplayStyle.VERTICAL:
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

    def export_markdown(self):
        self.__load_ignored()
        self.__load_audios()

        results = {}
        for audio in audios:
            audio_object = eyed3.load(audio)
            grouping = self.__fetch_from_audio(
                audio_object, self.AudioProperty.GROUPING, False, False,
            )
            if not grouping:
                raise Exception('Invalid grouping of <{}>'.format(audio))
            for group in grouping.split('/'):
                if group not in results.keys():
                    results[group]
                else:
                    pass

    def export_itunes_plist(self):
        itunes_version_plist, itunes_media_folder, itunes_library_plist = self.itunes_options

        def _format_time(timestamp) -> str:
            return datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%dT%H:%M:%SZ')

        def _current_time() -> str:
            return _format_time(time.time())

        def _generate_persistent_id() -> str:
            return str(uuid.uuid4()).replace('-', '')[:16].upper()

        def _encode(src) -> str:
            return urllib.parse.quote(src, safe='/', encoding='utf-8', errors=None)

        def _encode_location(location) -> str:
            return 'file://{}'.format(_encode(location))

        def _encode_folder(folder) -> str:
            return '{}/'.format(_encode_location(folder))

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
                        formatted_version += '.{}'.format(str(int(origin_version[pos:pos+3])))
                        pos += 3
                    return formatted_version.rstrip('.0')
            return '1.0'

        def _pack_tracks() -> str:
            return Template('''
<key>536</key>
<dict>
	<key>Track ID</key><integer>536</integer>
	<key>Name</key><string>bboy danny</string>
	<key>Artist</key><string>新旭</string>
	<key>Album</key><string>Holy Bgm</string>
	<key>Genre</key><string>Explosive</string>
	<key>Kind</key><string>MPEG audio file</string>
	<key>Size</key><integer>6797692</integer>
	<key>Total Time</key><integer>169691</integer>
	<key>Date Modified</key><date>2021-04-22T09:47:27Z</date>
	<key>Date Added</key><date>2021-04-15T17:16:05Z</date>
	<key>Bit Rate</key><integer>320</integer>
	<key>Sample Rate</key><integer>44100</integer>
	<key>Persistent ID</key><string>2004BAD0A3E3CA9A</string>
	<key>Track Type</key><string>File</string>
	<key>Location</key><string>file:///Users/Zichoole/Music/iTunes/iTunes%20Media/Music/%E6%96%B0%E6%97%AD/Holy%20Bgm/bboy%20danny.mp3</string>
	<key>File Folder Count</key><integer>5</integer>
	<key>Library Folder Count</key><integer>1</integer>
</dict>
            '''.strip().replace(' '*4, '\t')).safe_substitute(dict(
            ))

        def _pack_playlists() -> str:
            return Template('''
<dict>
	<key>Name</key><string>Chinese</string>
	<key>Description</key><string></string>
	<key>Playlist ID</key><integer>4323</integer>
	<key>Playlist Persistent ID</key><string>5FDC1EDE16DE9643</string>
	<key>Parent Persistent ID</key><string>20A3545EE4358FFB</string>
	<key>All Items</key><true/>
	<key>Playlist Items</key>
	<array>
		<dict>
			<key>Track ID</key><integer>1184</integer>
		</dict>
		<dict>
			<key>Track ID</key><integer>1178</integer>
		</dict>
		<dict>
			<key>Track ID</key><integer>1172</integer>
		</dict>
		<dict>
			<key>Track ID</key><integer>1169</integer>
		</dict>
		<dict>
			<key>Track ID</key><integer>1181</integer>
		</dict>
		<dict>
			<key>Track ID</key><integer>1175</integer>
		</dict>
	</array>
</dict>
            '''.strip().replace(' '*4, '\t')).safe_substitute(dict(
            ))

        def _pack_plist() -> str:
            return Template('''
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
            '''.strip().replace(' '*4, '\t') + '\n').safe_substitute(dict(
                xml_version = '1.0',
                xml_encoding = 'UTF-8',
                plist_version = '1.0',
                major_version = '1',
                minor_version = '1',
                created_date = _current_time(),
                itunes_version = _get_itunes_version(itunes_version_plist),
                features = '5',
                show_content_ratings = 'true',
                itunes_media_folder = _encode_folder(itunes_media_folder),
                library_persistent_id = _generate_persistent_id(),
                tracks = '\n{}'.format(_pack_tracks()).replace('\n', '\n\t\t')+'\n\t',
                playlists = '\n{}'.format(_pack_playlists()).replace('\n', '\n\t\t')+'\n\t',
            ))

        with open(itunes_library_plist, mode='w', encoding='utf-8') as f:
            f.write(_pack_plist())
            f.flush()


def main():
    parser = argparse.ArgumentParser(
        description='🎻 Processor for audios 🎸',
        epilog='🤔 Thinking ...',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        '--version', '-v',
        action='version',
        version='Audio Processor 1.0',
    )
    parser.add_argument(
        '--action', '-a',
        type=str,
        choices=[
            'format-notes',
            'fill-properties',
            'format-properties',
            'rename-audios',
            'display-audios',
            'export-artworks',
            'organize-files',
            'export-markdown',
            'export-itunes-plist',
            'convert-qmc0',
            'convert-kmx',
            'convert-mp4',
        ],
        required=True,
        dest='action',
        help='actions you want to process',
    )
    parser.add_argument(
        '--notes-file', '-f',
        type=str,
        required=False,
        default='./notes.txt',
        dest='notes_file',
        help='notes file to match',
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
        '--audios-source', '-o',
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
        default='mp3',
        dest='extensions',
        help='valid extensions of audios',
    )
    parser.add_argument(
        '--fields', '-u',
        type=str,
        required=False,
        default='cores',
        dest='fields',
        help='fields of audio to process, all fields: [{}], cores: [{}]'.format(
            ' '.join([x.value for x in AudioProcessor.ALL_FIELDS]),
            ' '.join([x.value for x in AudioProcessor.CORE_FIELDS]),
        ),
    )
    parser.add_argument(
        '--page-number', '-n',
        type=int,
        required=False,
        default=1,
        dest='page_number',
        help='page number for audios display',
    )
    parser.add_argument(
        '--page-size', '-z',
        type=int,
        required=False,
        default=None,
        dest='page_size',
        help='page size for audios display',
    )
    parser.add_argument(
        '--sort', '-b',
        type=str,
        required=False,
        default=None,
        dest='sort',
        help='sort options for audios display',
    )
    parser.add_argument(
        '--filter', '-x',
        type=str,
        required=False,
        default=None,
        dest='filter',
        help='filter options for audios display',
    )
    parser.add_argument(
        '--align', '-y',
        type=str,
        required=False,
        default=None,
        dest='align',
        help='align options for audios display',
    )
    parser.add_argument(
        '--numbered', '-k',
        action='store_true',
        dest='numbered',
        help='if show number for audios display',
    )
    parser.add_argument(
        '--style', '-w',
        type=str,
        choices=[x.value for x in AudioProcessor.DisplayStyle],
        required=False,
        default=AudioProcessor.DisplayStyle.TABLED.value,
        dest='style',
        help='display style for audios',
    )
    parser.add_argument(
        '--data-format', '-t',
        type=str,
        choices=[x.value for x in AudioProcessor.DataFormat],
        required=False,
        default=AudioProcessor.DataFormat.OUTPUTTED.value,
        dest='data_format',
        help='the data format for audios to display',
    )
    parser.add_argument(
        '--output-file', '-j',
        type=str,
        required=False,
        default=None,
        dest='output_file',
        help='output file',
    )
    parser.add_argument(
        '--artwork-path', '-c',
        type=str,
        required=False,
        default=None,
        dest='artwork_path',
        help='path to export artworks',
    )
    parser.add_argument(
        '--filename-pattern', '-m',
        type=str,
        required=False,
        default='%{artist} ' + AudioProcessor.DIV_CHAR + ' %{title}',
        dest='filename_pattern',
        help='filename pattern to rename audios',
    )
    parser.add_argument(
        '--organize-type', '-g',
        type=str,
        choices=[x.value for x in AudioProcessor.OrganizeType],
        required=False,
        default=AudioProcessor.OrganizeType.ITUNED.value,
        dest='organize_type',
        help='type of file organization',
    )
    parser.add_argument(
        '--log-level', '-l',
        type=str,
        required=False,
        default='DEBUG',
        dest='log_level',
        help='level of logger',
    )

    parser.add_argument(
        '--itunes-version-plist', '-q',
        type=str,
        required=False,
        default=AudioProcessor.DEFAULT_ITUNES_VERSION_PLIST,
        dest='itunes_version_plist',
        help='the version plist file of itunes or apple music',
    )

    parser.add_argument(
        '--itunes-media-folder', '-s',
        type=str,
        required=False,
        default=AudioProcessor.DEFAULT_ITUNES_MEDIA_FOLDER,
        dest='itunes_media_folder',
        help='the media folder of itunes or apple music',
    )

    parser.add_argument(
        '--itunes-library-plist', '-2',
        type=str,
        required=False,
        default=AudioProcessor.DEFAULT_ITUNES_LIBRARY_PLIST,
        dest='itunes_library_plist',
        help='the library plist file of itunes or apple music',
    )

    args = parser.parse_args()

    processor = AudioProcessor(
        notes_file=args.notes_file,
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
            args.itunes_library_plist,
        ],
        artwork_path=args.artwork_path,
        filename_pattern=args.filename_pattern,
        output_file=args.output_file,
        organize_type=args.organize_type,
        log_level=args.log_level,
    )

    if args.action == 'format-notes':
        processor.format_notes()
    elif args.action == 'fill-properties':
        processor.fill_properties()
    elif args.action == 'format-properties':
        processor.format_properties()
    elif args.action == 'rename-audios':
        processor.rename_audios()
    elif args.action == 'display-audios':
        processor.display_audios()
    elif args.action == 'export-artworks':
        processor.export_artworks()
    elif args.action == 'organize-files':
        processor.organize_files()
    elif args.action == 'export-markdown':
        processor.export_markdown()
    elif args.action == 'export-itunes-plist':
        processor.export_itunes_plist()
    elif args.action == 'convert-qmc0':
        pass
    elif args.action == 'convert-kmx':
        pass
    elif args.action == 'convert-mp4':
        pass
    else:
        print('Nothing to do!')


if __name__ == '__main__':
    main()
