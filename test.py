#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
import os

from enum import Enum


class DemoEnum(Enum):
    #Mem1 = ('a', '1')
    #Mem2 = ('b', '2')

    #def __new__(*agrs, **kwargs):
    #    print('KKKKKKKKKKKKKKKKKKK')
    #    return super().__new__(*agrs, **kwargs)

    def _create_(*agrs, **kwargs):
        print('CCCCCCCCCCCCCCCCCC')
        return super()._create_(*agrs, **kwargs)

    def __setattr__(self, key, value):
        print('EEEEEEE', key, value)

        super().__setattr__(key, value)

        print('AAAAAAA', self._member_map_)
        print('BBBBBBB', self._member_names_)


print(DemoEnum.__members__)

