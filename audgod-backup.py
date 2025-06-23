class AudioGod(object):
    def __init__(self, *args, **kwargs):
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

        self.__parse_funcs = {
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
        self.__parse_funcs = {
            field: __parse_func(self.__parse_funcs[field])
            for field in self.ALL_FIELDS
        }

        self.__format_funcs = {
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
        self.__format_funcs = {
            field: __format_func(self.__format_funcs[field])
            for field in self.ALL_FIELDS
        }

        self.__output_funcs = {
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
        self.__output_funcs = {
            field: __output_func(self.__output_funcs[field])
            for field in self.ALL_FIELDS
        }

    #---------------------------------------------------------------------------

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
    def format_funcs(self):
        return self.__format_funcs

    @property
    def parse_funcs(self):
        return self.__parse_funcs

    @property
    def output_funcs(self):
        return self.__output_funcs

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

    def __prime_audio(self, audio):
        audio_object = eyed3.load(audio)
        if audio_object is None:
            self.logger.fatal(f'Invalid audio <{audio}>!')
            return None
        if audio_object.tag is None:
            audio_object.initTag()
            audio_object.tag.save() # type: ignore
        return audio_object

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
