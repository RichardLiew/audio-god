from enumx import StringEnum, IntegerEnum
import os, sys


class AAA(object):
    V = 'vvv'

    @classmethod
    def ff(cls):
        cls.V = 'iii'


AAA.V = 'ooo'
AAA.ff()

a = AAA()
a.V = 'aaa'
a.ff()

print(AAA.V, a.V)