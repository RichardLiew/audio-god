import os
import re
import sys


qmc_dir = '~/Library/Containers/com.tencent.QQMusicMac/Data/Library/Application Support/QQMusicMac/iQmc/'

mgg_dir = '~/Music/Source/Primary/Mgg/Sad'



work_dir = '~/Music/Output/Temp'

def absdir(dir_):
    return os.path.normpath(os.path.abspath(os.path.expanduser(dir_)))

qmc_dir = absdir(qmc_dir)
mgg_dir = absdir(mgg_dir)
work_dir = absdir(work_dir)


mgg_set = {}
with open('./mgg.txt', 'r', encoding='utf-8') as f1:
    for line in f1:
        line = line.strip()
        origin = line
        line = re.sub(r'_(L|H).mgg$', '', line)
        line = re.sub(r'\s*-\s*', ' - ', line)
        line = re.sub(r'\s+_\s+', ' & ', line)
        mgg_set[line] = origin


qmc_set = {}
with open('./aaa.txt', 'r', encoding='utf-8') as f2:
    for line in f2:
        line = line.strip()
        origin = line
        line = re.sub(r'\.\S+$', '', line)
        line = re.sub(r'\s*-\s*', ' - ', line)
        line = re.sub(r'\s*,\s*', ' & ', line)
        qmc_set[line] = origin



temp_set = set(set(mgg_set.keys()) - set(qmc_set.keys()))
happy_set = set(mgg_set.keys()) - temp_set







big_string = '|'.join(list(qmc_set.keys()))
invalid_set = set()

for item in temp_set:
    units = item.split('-')
    #if len(units) != 2:
    #    print('0     AAAAAAAAAAAAAAA', item)
    #    continue
    invalid = True
    for unit in units:
        unit = unit.strip()
        if not unit in big_string:
            continue
        invalid = False

    if invalid:
        invalid_set.add(item)

part_set = temp_set - invalid_set

for key in happy_set:
    os.rename(
        os.path.join(qmc_dir, qmc_set[key]),
        os.path.join(work_dir, 'happy/qmc', qmc_set[key])
    )
    os.rename(
        os.path.join(mgg_dir, mgg_set[key]),
        os.path.join(work_dir, 'happy/mgg', mgg_set[key])
    )

for key in part_set:
    os.rename(
        os.path.join(mgg_dir, mgg_set[key]),
        os.path.join(work_dir, 'part/mgg', mgg_set[key])
    )
    units = key.split('-')
    #if len(units) != 2:
    #    print('0     AAAAAAAAAAAAAAA', item)
    #    continue
    selected = False
    for unit in units[1:]:
        unit = unit.strip()
        for qmc_k in qmc_set:
            if unit in qmc_k:
                selected = True
                if os.path.exists(qmc_set[qmc_k]):
                    os.rename(
                        os.path.join(qmc_dir, qmc_set[qmc_k]),
                        os.path.join(work_dir, 'part/qmc', qmc_set[qmc_k])
                    )
                else:
                    print(key, mgg_set[key], qmc_set[qmc_k])
                break
        if selected:
            break

#for key in sad_set:
#    os.rename(
#        os.path.join(qmc_dir, qmc_set[key]),
#        os.path.join(work_dir, 'sad/qmc', qmc_set[key])
#    )
#    os.rename(
#        os.path.join(mgg_dir, mgg_set[key]),
#        os.path.join(work_dir, 'sad/mgg', mgg_set[key])
#    )


