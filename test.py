import os
from pathlib import Path

def count_files(directory):
    """递归统计目录下所有非目录文件数量"""
    return sum(1 for f in Path(directory).rglob('*') if f.is_file())

def print_tree(directory, prefix=''):
    """打印带文件计数的目录树"""
    contents = sorted(os.listdir(directory))
    pointers = ['├──'] * (len(contents)-1) + ['└──']
    
    for pointer, item in zip(pointers, contents):
        path = os.path.join(directory, item)
        if os.path.isdir(path):
            file_count = count_files(path)
            print(f"{prefix}{pointer} {item}/ [文件数: {file_count}]")
            new_prefix = prefix + ("│   " if pointer == '├──' else "    ")
            print_tree(path, new_prefix)

print_tree('~/Music/Source')