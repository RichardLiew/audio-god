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
#            pipenv run python audgod.py --help
#        ```;
#        3. 查看常用命令：```
#            pipenv run python audgod.py --usage
#        ```;
#        4. 查看版本：```
#            pipenv run python audgod.py --version
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
###############################################################################

import os
import re
import sys
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

from treelib import Tree

from prettytable import PrettyTable


__AVATAR__ = 'Audio God'
__VERSION__ = '1.0'
__USAGE__ = Template('''

General commands show below:

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
            --filename-pattern="@{artist} # @{title}" \\
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
    cmd='{}'.format(sys.argv[0]),
    music='~/Music',
    local='.',
))


class TreeX(Tree):
    def perfect_merge(self, nid, new_tree, deep=False) -> None:
        if not (isinstance(new_tree, Tree) or isinstance(new_tree, TreeX)):
            raise Exception('The new tree to merge is not a valid tree.')

        if new_tree is None:
            return

        if new_tree.root is None:
            return

        if nid is None:
            if self.root is None:
                self.add_node(new_tree[new_tree.root])
            nid = self.root

        if not self.contains(nid):
            raise Exception('Node <{}> is not in the tree!'.format(nid))

        current_node = self[nid]

        if current_node.tag != new_tree[new_tree.root].tag:
            raise Exception('Current node not same with root of new tree.')

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
    class FileType(Enum):
        NONE = 'none'
        JSON = 'json'
        MARKDOWN = 'markdown'
        PLIST = 'plist'
        NOTE = 'note'
        DISPLAY = 'display'


    @unique
    class PropertySource(Enum):
        COMMAND = 'command'
        FILE = 'file'
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


    @unique
    class AudiosTreeNodeType(Enum):
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

    AudioProperty = unique(Enum(
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

    ALL_FIELDS = [prop for prop in AudioProperty]

    FIELDS = {
        'default': DEFAULT_FIELDS,
        'zip': ZIP_FIELDS,
        'core': CORE_FIELDS,
        'ituned': ITUNED_FIELDS,
        'all': ALL_FIELDS,
    }


    DEFAULT_ITUNES_VERSION_PLIST = '/System/Applications/Music.app/Contents/version.plist'
    DEFAULT_ITUNES_FOLDER = '{}/Music/iTunes'.format(os.environ['HOME'])
    DEFAULT_ITUNES_MEDIA_FOLDER = '{}/iTunes Media'.format(DEFAULT_ITUNES_FOLDER)
    DEFAULT_ITUNES_LIBRARY_PLIST = '{}/Library.xml'.format(DEFAULT_ITUNES_MEDIA_FOLDER)


    AUDIOS_TREE_ROOT_TAG = '--root-tag--'
    AUDIOS_TREE_ROOT_NID = '--root-nid--'

    AUDIO_DEFAULT_GROUPING = 'Default'

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
        fields=[field.value for field in CORE_FIELDS],
        data_format=DataFormat.OUTPUTTED.value,
        display_options=[
            1, None, None, None, None, None, True,
            DisplayStyle.TABLED.value,
        ],
        itunes_options=[
            DEFAULT_ITUNES_VERSION_PLIST,
            DEFAULT_ITUNES_MEDIA_FOLDER,
            DEFAULT_TRACK_INITIAL_ID,
            DEFAULT_PLAYLIST_INITIAL_ID,
        ],
        artwork_path=None,
        filename_pattern='%{artist} ' + DIV_CHAR + ' %{title}',
        output_file=None,
        organize_type=OrganizeType.ITUNED.value,
        log_level=logging.DEBUG,
    ):
        self.__source_file = source_file
        self.__ignored_file = ignored_file
        self.__audios_root = audios_root
        self.__audios_source = audios_source
        self.__properties = properties
        self.__extensions = list(map(lambda x: x.lower(), filter(None, extensions)))
        self.__fields = [
            self.AudioProperty(x) for x in self.__resolve_fields(fields)
        ]
        self.__clauses = ([], {}, {})
        self.__audios = ([], [], [], [], set(), set())
        self.__audios_tree = TreeX(tree=None, deep=False, node_class=None, identifier=None)
        self.audios_tree.create_node(self.AUDIOS_TREE_ROOT_TAG, self.AUDIOS_TREE_ROOT_NID)
        self.__ignored_set = set()
        self.__format = {
            field.value: getattr(
                self, 'format_{}'.format(field.value), lambda x: x,
            )
            for field in self.ALL_FIELDS
        }
        self.__parse = {
            field.value: getattr(
                self, 'parse_{}'.format(field.value), lambda x: x,
            )
            for field in self.ALL_FIELDS
        }
        self.__output = {
            field.value: getattr(
                self,
                'output_{}'.format(field.value),
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
        self.__logger = logging.getLogger()
        self.__logger.setLevel(log_level)
        eyed3.log.setLevel(
            #log_level,
            logging.ERROR,
        )

    def __resolve_fields(self, fields):
        fields_ = list(filter(None, fields.split(',')))
        for key in self.FIELDS.keys():
            try:
                index = fields_.index(key)
                fields_ = fields_[0:index] + \
                        [x.value for x in self.FIELDS[key]] + \
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
                keyword = ','.join([x.value for x in self.FIELDS[key]])
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
    def source_audios(self):
        src, recursive = self.audios_source
        if not os.path.exists(src):
            self.logger.fatal('Source <{}> not exists!'.format(src))
        src = os.path.abspath(src)
        if os.path.isfile(src):
            if not self.__check_extension(src):
                self.logger.fatal('Source <{}> invalid extension!'.format(src))
            return [src]
        if not os.path.isdir(src):
            self.logger.fatal('Source <{}> not a directory!'.format(src))
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
        #ret = re.sub(r'[ \t]{0,}&[ \t]{0,}', r' & ', ret)
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
    def output_title(cls, title, output_type=FileType.NONE):
        if not title:
            return ''
        ret = title
        if output_type == cls.FileType.PLIST:
            ret = cls.escape_characters(ret)
        return ret

    @classmethod
    def output_album(cls, album, output_type=FileType.NONE):
        if not album:
            return ''
        ret = album
        if output_type == cls.FileType.PLIST:
            ret = cls.escape_characters(ret)
        return ret

    @classmethod
    def output_album_artist(cls, album_artist, output_type=FileType.NONE):
        if not album_artist:
            return ''
        ret = album_artist
        if output_type == cls.FileType.PLIST:
            ret = cls.escape_characters(ret)
        return ret

    @classmethod
    def output_artist(cls, artist, output_type=FileType.NONE):
        if not artist:
            return ''
        ret = artist
        if output_type == cls.FileType.PLIST:
            ret = cls.escape_characters(ret)
        return ret

    @classmethod
    def output_genre(cls, genre, output_type=FileType.NONE):
        if not genre:
            return ''
        ret = genre
        if isinstance(genre, Genre):
            ret = genre.name
        if output_type == cls.FileType.PLIST:
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
        return '{} kb/s'.format(bit_rate)

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
        if output_type == cls.FileType.NONE:
            return duration
        elif output_type == cls.FileType.PLIST:
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
        if output_type == cls.FileType.PLIST:
            return cls.format_utc(mtime)
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime))

    def __fetch_from_outside(self, audio, field):
        format_ = self.format[field.value]
        parse_ = self.parse[field.value]
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
            elif source == self.PropertySource.FILE:
                key = self.generate_key_by_audio(audio)
                _value = self.valid_clauses.get(key, {}).get(field.value, None)
                if _value is not None:
                    ret = _value
                    break
            elif source == self.PropertySource.DIRECTORY:
                _value = dirname = os.path.dirname(audio)
                if field == self.AudioProperty.GENRE:
                    _value = os.path.basename(dirname)
                elif field == self.AudioProperty.GROUPING:
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
            value = self.format[field.value](value)
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
                        self.logger.fatal(
                            'Audio <{}> has invalid artwork "{}"'.format(
                                audio_object.file_info.name, value,
                            ),
                        )
        else:
            setattr(audio_object.tag, field.value, value)
        audio_object.tag.save()

    # Use AudioProperty type field here, you won't to check field parameter.
    def fetch(self, audio_object, field):
        ret, filename = None, audio_object.tag.file_info.name
        if field == AudioGod.AudioProperty.GENRE:
            if audio_object.tag.genre is not None:
                ret = audio_object.tag.genre.name
        elif field == AudioGod.AudioProperty.TRACK_NUM:
            ret = audio_object.tag.track_num
        elif field == AudioGod.AudioProperty.DURATION:
            ret = audio_object.info.time_secs
        elif field == AudioGod.AudioProperty.MTIME:
            ret = audio_object.tag.file_info.mtime
        elif field == AudioGod.AudioProperty.SIZE:
            ret = audio_object.info.size_bytes
        elif field == AudioGod.AudioProperty.NAME:
            ret = os.path.basename(filename)
        elif field == AudioGod.AudioProperty.PATH:
            ret = os.path.dirname(filename)
        elif field == AudioGod.AudioProperty.COMMENTS:
            ret = audio_object.tag.comments
        elif field in self.ZIP_FIELDS:
            comments = audio_object.tag.comments
            if comments:
                comments = ''.join([comment.text for comment in comments])
                try:
                    ret = json.loads(comments).get(field.value, None)
                except:
                    pass
            if field == AudioGod.AudioProperty.ARTWORK:
                if len(audio_object.tag.images) == 0 and not ret:
                    ret = None
                else:
                    ret = (len(audio_object.tag.images), ret if ret else '')
            #elif field == AudioGod.AudioProperty.GROUPING:
            #    if not ret:
            #        ret = self.AUDIO_DEFAULT_GROUPING
        else:
            if hasattr(audio_object.tag, field.value):
                ret = getattr(audio_object.tag, field.value)
            elif hasattr(audio_object.info, field.value):
                ret = getattr(audio_object.info, field.value)
            elif hasattr(audio_object.tag.file_info, field.value):
                ret = getattr(audio_object.tag.file_info, field.value)
        return ret

    def fetchx(self, audio_object, field,
               formatted=False, output_type=FileType.NONE):
        ret = self.fetch(audio_object, field)
        if ret is None:
            return None
        if formatted:
            ret = self.format[field.value](ret)
        if output_type != self.FileType.NONE:
            ret = self.output[field.value](ret, output_type)
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
            self.logger.fatal('Invalid name of audio <{}>!'.format(audio))
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
        title = hashed_clause.get(self.AudioProperty.TITLE.value, None)
        if not title:
            self.invalid_clauses.append(plain_clause)
            return
        artist = hashed_clause.get(self.AudioProperty.ARTIST.value, None)
        if not artist:
            self.invalid_clauses.append(plain_clause)
            return
        key = self.generate_key(artist, title)
        if key in final_clauses:
            final_clauses[key].append(hashed_clause)
        else:
            final_clauses[key] = [hashed_clause]

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
        if filetype in [self.FileType.NONE, self.FileType.DISPLAY]:
            return
        elif filetype == self.FileType.JSON:
            self.__import_json()
        elif filetype == self.FileType.MARKDOWN:
            self.__import_markdown()
        elif filetype == self.FileType.PLIST:
            self.__import_plist()
        else:
            self.__import_note()


    def __load_properties_from_file(self):
        if not os.path.exists(self.source_file):
            self.logger.fatal('Source file <{}> not exists!'.format(self.source_file))
        self.import_()
        self.logger.warning('\n{}\n'.format('#' * 78))
        self.logger.warning(
            'Total Clauses: {}\n\n'
            'Valid Clauses: {}, '
            'Invalid Clauses: {}, '
            'Repeated Clauses: {}\n'.format(
                len(self.valid_clauses) \
                + len(self.invalid_clauses) \
                + len([
                    item
                    for value in self.repeated_clauses.values()
                    for item in value
                ]),
                len(self.valid_clauses),
                len(self.invalid_clauses),
                len([
                    item
                    for value in self.repeated_clauses.values()
                    for item in value
                ]),
            )
        )
        if len(self.invalid_clauses) > 0:
            self.logger.info('\nInvalid Clauses:')
            for item in self.invalid_clauses:
                self.logger.info('\t{}'.format(item))
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
        fields_pattern = '|'.join(
            list(self.AUDIO_CN_PROPERTIES.keys()) + \
            list(self.AUDIO_CN_PROPERTY_SYNONYMS.keys()),
        )
        prefix_pattern = r'^.*(({}))[:：]'.format(fields_pattern)
        entire_pattern = \
                r'^({0})[:：].*([,，][ \t]{{0,}}({0})[:：].*){{0,}}$'.format(
            fields_pattern,
        )

        _clauses = {}
        with open(self.source_file, 'r', encoding='utf-8') as f:
            for line in f:
                _line = re.sub(prefix_pattern, r'\1:', line, re.IGNORECASE)
                if re.match(entire_pattern, _line, re.IGNORECASE) is None:
                    self.invalid_clauses.append(line)
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
                    k = self.AUDIO_CN_PROPERTY_SYNONYMS.get(k, k).lower()
                    if k not in [field.value for field in self.ALL_FIELDS]:
                        self.invalid_clauses.append(line)
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
            if key in self.valid_clauses:
                self.matched_audios.add(audio)
                self.logger.debug(self.AudioType.MATCHED.value)
            else:
                self.notmatched_audios.add(audio)
                self.logger.debug(self.AudioType.NOTMATCHED.value)

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
                self.logger.info('\t{}'.format(audio))
        if len(self.invalid_name_audios) > 0:
            self.logger.info('\nInvalid Name Audios:')
            for audio in self.invalid_name_audios:
                self.logger.info('\t{}'.format(audio))
        if len(self.notmatched_audios) > 0:
            self.logger.info('\nNot Matched Audios:')
            for audio in self.notmatched_audios:
                self.logger.info('\t{}'.format(audio))

    def __fill_audios_tree(self) -> None:
        self.__load_audios()

        _, _, track_initial_id, playlist_initial_id = self.itunes_options
        track_id, audios = track_initial_id, self.concerned_audios

        for audio in audios:
            track_persistent_id = self.generate_persistent_id()
            audio_object = eyed3.load(audio)
            grouping = self.fetchx(audio_object, self.AudioProperty.GROUPING)
            if not grouping:
                grouping = self.AUDIO_DEFAULT_GROUPING
                self.logger.debug(
                    'Empty grouping of <{}>, use <{}> instead!'.format(audio, self.AUDIO_DEFAULT_GROUPING),
                )
            for group in grouping.split('|'):
                group = re.sub(r'\/+', r'/', group).rstrip('/')
                if not group:
                    continue
                tags = list(filter(lambda x: x, group.split('/')))
                if not tags:
                    continue
                tags = [self.AUDIOS_TREE_ROOT_TAG] + tags
                subtree = TreeX()
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
            if node_type == self.AudiosTreeNodeType.TRACK:
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
            if node_type == self.AudiosTreeNodeType.TRACK or node_type == self.AudiosTreeNodeType.ROOT:
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
                    self.save(audio_object, field, property_, True)
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
            self.logger.debug('Formatting <{}> ...'.format(audio))
            audio_object = eyed3.load(audio)
            for field in self.fields:
                property_ = self.fetchx(audio_object, field, True)
                if property_ is not None:
                    self.save(audio_object, field, property_, True)
        self.logger.warning(
            'Formatted Audios: {}\n'.format(len(audios)),
        )

    def rename_audios(self):
        class StringTemplate(Template):
            delimiter = '@'

        self.__load_audios()
        audios = self.concerned_audios
        for audio in audios:
            audio_object = eyed3.load(audio)
            _old = os.path.basename(audio)
            _, ext = os.path.splitext(_old)
            _new = StringTemplate(self.filename_pattern).safe_substitute({
                field.value: self.fetchx(
                    audio_object, field, True,
                ) for field in self.ALL_FIELDS
            }) + ext.lower()
            if _old == _new:
                continue
            _path = os.path.dirname(audio)
            os.rename('{}/{}'.format(_path, _old), '{}/{}'.format(_path, _new))

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
                image_file = '{}/{}'.format(_path, _name)
                if len(audio_object.tag.images) > 1:
                    image_file += '@{}'.format(i)
                image_file += '.jpg'
                with open(image_file, 'wb') as f:
                    f.write(image.image_data)

    def organize_files(self):
        if not self.audio_root:
            self.logger.fatal('Invalid audio root!')
        self.__load_audios()
        audios = self.concerned_audios
        for audio in audios:
            audio_object = eyed3.load(audio)
            if self.organize_type == self.OrganizeType.ITUNED:
                artist = self.fetchx(audio_object, self.AudioProperty.ARTIST)
                if not artist:
                    self.logger.fatal('Invalid artist of <{}>'.format(audio))
                album = self.fetchx(audio_object, self.AudioProperty.ALBUM)
                if not album:
                    self.logger.fatal('Invalid album of <{}>'.format(audio))
                dir_ = '{}/{}/{}'.format(self.audio_root, artist, album)
            else:
                grouping = self.fetchx(audio_object, self.AudioProperty.GROUPING)
                if not grouping:
                    self.logger.fatal('Invalid grouping of <{}>'.format(audio))
                dir_ = '{}/{}'.format(self.audio_root, grouping)
            os.makedirs(dir_, exist_ok=True)
            newname = '{}/{}'.format(dir_, os.path.basename(audio))
            os.rename(audio, newname)

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
            (field.value, self.AUDIO_CN_PROPERTIES[field.value])
            for field in self.ALL_FIELDS
        ]
        formatted, output_type = True, self.FileType.DISPLAY
        if self.data_format == self.DataFormat.ORIGINAL:
            formatted, output_type = False, self.FileType.NONE
        elif self.data_format == self.DataFormat.FORMATTED:
            formatted, output_type = True, self.FileType.NONE
        elif self.data_format == self.DataFormat.OUTPUTTED:
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
                    self.logger.fatal('Invalid field <{}>!'.format(field))
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
                            self.logger.fatal(
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
                            self.logger.fatal(
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

                if style != AudioGod.DisplayStyle.TABLED:
                    beg = result.find('|\n+', 0)
                    end = result.find('|\n+', beg+3)
                    result = result[:beg+2] + result[end+2:]
                    result = re.sub(r'\+[\+-]{0,}\n', r'', result)
                    result = re.sub(r'[ \t]{0,}\|[ \t]{0,}', r'|', result)
                    result = re.sub(r'^[ \t\n]{0,}\|', r'', result)
                    result = re.sub(r'\|[ \t\n]{0,}$', r'\n', result)
                    result = re.sub(r'\|\n\|', r'\n', result)

                if style == AudioGod.DisplayStyle.VERTICAL:
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
        if filetype == self.FileType.NONE:
            self.logger.fatal('Output file is empty when export!')
        self.__fill_audios_tree()
        if filetype == self.FileType.JSON:
            self.__export_json()
        elif filetype == self.FileType.MARKDOWN:
            self.__export_markdown()
        elif filetype == self.FileType.PLIST:
            self.__export_plist()
        elif filetype == self.FileType.NOTE:
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
        ret = 'file://{}'.format(cls.encode(location))
        if os.path.isfile(location):
            return ret
        return '{}/'.format(ret)

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
                        formatted_version += '.{}'.format(str(int(origin_version[pos:pos+3])))
                        pos += 3
                    return formatted_version.rstrip('.0')
            return '1.0'

        def _format_template(template) -> str:
            return template.strip().replace(' '*4, '\t') + '\n'

        def _repack_plist(content) -> str:
            result = '\n{}'.format(content).replace('\n', '\n\t\t')
            return result[:-1]

        def _pack_track(track) -> str:
            _, track_id, persistent_id, audio_object = track.data

            def _pack_properties() -> str:
                ret = ''
                for field in self.fields:
                    value = self.fetchx(audio_object, field)
                    value = self.output[field.value](
                        value, output_type=self.FileType.PLIST,
                    )
                    if (not isinstance(value, int)) and (not isinstance(value, float)) and (not value):
                        continue
                    ret += '\t'
                    ret += '<key>{key}</key>'.format(
                        key=self.AUDIO_EN_PROPERTIES[field.value],
                    )
                    type_ = self.AUDIO_PROPERTY_TYPES[field.value]
                    if type_ != 'boolean':
                        ret += '<{type}>{value}</{type}>'.format(
                            value=value,
                            type=self.AUDIO_PROPERTY_TYPES[field.value],
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
                if track.data[0] != self.AudiosTreeNodeType.TRACK:
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
                if track.data[0] != self.AudiosTreeNodeType.TRACK:
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
''' + ('' if node_type != self.AudiosTreeNodeType.FOLDER else '''\t<key>Folder</key><${is_folder}/>
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
                if node_type == self.AudiosTreeNodeType.TRACK:
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
                '({}: {})'.format(key, ','.join([f.value for f in fields]))
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
        choices=[x.value for x in AudioGod.DisplayStyle],
        required=False,
        default=AudioGod.DisplayStyle.TABLED.value,
        dest='style',
        help='display style for audios',
    )
    parser.add_argument(
        '--data-format', '-x',
        type=str,
        choices=[x.value for x in AudioGod.DataFormat],
        required=False,
        default=AudioGod.DataFormat.OUTPUTTED.value,
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
        default='%{artist} ' + AudioGod.DIV_CHAR + ' %{title}',
        dest='filename_pattern',
        help='filename pattern to rename audios',
    )
    parser.add_argument(
        '--organize-type', '-g',
        type=str,
        choices=[x.value for x in AudioGod.OrganizeType],
        required=False,
        default=AudioGod.OrganizeType.ITUNED.value,
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
        print(__USAGE__)
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


if __name__ == '__main__':
    main()
