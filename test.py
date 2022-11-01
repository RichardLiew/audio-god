#!/usr/bin/python
# -*- coding: utf-8 -*-

x = 1

l = [0, 1, 2]

match x:
    case [*l]:
        print('a')
    case _:
        print('others')


