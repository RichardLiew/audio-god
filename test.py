from enumx import StringEnum, IntegerEnum
import os

@StringEnum.unique
class ABC(StringEnum):
    A = 'a'
    B = 'b'
    C = 'c'

@IntegerEnum.unique
class DEF(IntegerEnum):
    D = 1
    E = 2
    F = 3


lse = [ABC.A, ABC.B]
lss = ['a', 'b']
dse = {ABC.A: 'aa', ABC.B: 'bb'}
dss = {'a': 'aa', 'b': 'bb'}

print(ABC.A == ABC.A, ABC.B == ABC.A)
print(ABC.A == 'a', ABC.B == 'a')

print(ABC.A in lse, ABC.C in lse)
print(ABC.A in lss, ABC.C in lss)

print('a' in lse, 'c' in lse)
print('a' in lss, 'c' in lss)

print(ABC.A in dse, ABC.C in dse)
print(ABC.A in dss, ABC.C in dss)

print('a' in dse, 'c' in dse)
print('a' in dss, 'c' in dss)

print(dse['a'], dse[ABC.A])
print(dss['a'], dss[ABC.A])

print(ABC.A.upper())




p = '/aa/bb/cc'
print(os.path.dirname(p))