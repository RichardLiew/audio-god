#import os
#from pathlib import Path
#
#def count_files(directory):
#    """递归统计目录下所有非目录文件数量"""
#    return sum(1 for f in Path(directory).rglob('*') if f.is_file())
#
#def print_tree(directory, prefix=''):
#    """打印带文件计数的目录树"""
#    contents = sorted(os.listdir(directory))
#    pointers = ['├──'] * (len(contents)-1) + ['└──']
#    
#    for pointer, item in zip(pointers, contents):
#        path = os.path.join(directory, item)
#        if os.path.isdir(path):
#            file_count = count_files(path)
#            print(f"{prefix}{pointer} {item}/ [文件数: {file_count}]")
#            new_prefix = prefix + ("│   " if pointer == '├──' else "    ")
#            print_tree(path, new_prefix)





#import os
#from pathlib import Path
#
#def count_non_dir_files(directory):
#    """精确统计当前目录下的非目录文件数量（不递归子目录）"""
#    return sum(1 for item in Path(directory).iterdir() if item.is_file())
#
#def print_dir_tree(directory, prefix='', is_last=True):
#    """优化后的目录树打印函数"""
#    path = Path(directory)
#    file_count = count_non_dir_files(path)
#    
#    # 当前节点连接线
#    connector = '└── ' if is_last else '├── '
#    print(f"{prefix}{connector}{path.name}/ [文件数: {file_count}]")
#    
#    # 子目录处理
#    dirs = [d for d in path.iterdir() if d.is_dir()]
#    new_prefix = prefix + ('    ' if is_last else '│   ')
#    
#    for i, child in enumerate(sorted(dirs)):
#        print_dir_tree(child, new_prefix, i == len(dirs)-1)








#import os
#from pathlib import Path
#
#def count_files_recursive(directory):
#    """递归统计目录下所有非隐藏的非目录文件数量"""
#    return sum(1 for f in directory.rglob('*') 
#              if f.is_file() and not f.name.startswith('.'))
#
#def print_dir_tree(directory, prefix='', is_last=True):
#    """打印带递归文件计数的目录树"""
#    path = Path(directory)
#    file_count = count_files_recursive(path)
#    
#    # 当前节点显示
#    connector = '└── ' if is_last else '├── '
#    print(f"{prefix}{connector}{path.name}/ [总文件数: {file_count}]")
#    
#    # 处理子目录
#    dirs = [d for d in path.iterdir() 
#            if d.is_dir() and not d.name.startswith('.')]
#    new_prefix = prefix + ('    ' if is_last else '│   ')
#    
#    for i, child in enumerate(sorted(dirs)):
#        print_dir_tree(child, new_prefix, i == len(dirs)-1)







import os
#from pathlib import Path
#
#def count_files_recursive(directory):
#    """递归统计非隐藏的非目录文件数量"""
#    return sum(1 for f in directory.rglob('*') 
#              if f.is_file() and not f.name.startswith('.'))
#
#def print_dir_tree(directory, prefix='', is_root=True):
#    """优化连接线显示的目录树打印"""
#    path = Path(directory)
#    file_count = count_files_recursive(path)
#    
#    # 根目录特殊处理
#    if is_root:
#        print(f"{path.name}/ [总文件数: {file_count}]")
#    else:
#        connector = '└── ' if prefix.endswith('    ') else '├── '
#        print(f"{prefix}{connector}{path.name}/ [总文件数: {file_count}]")
#    
#    # 处理子目录
#    dirs = [d for d in path.iterdir() 
#            if d.is_dir() and not d.name.startswith('.')]
#    new_prefix = prefix + ('    ' if is_root or prefix.endswith('    ') else '│   ')
#    
#    for i, child in enumerate(sorted(dirs)):
#        print_dir_tree(child, new_prefix, False)



from pathlib import Path

#def count_files_recursive(directory):
#    """递归统计非隐藏的非目录文件数量"""
#    return sum(1 for f in directory.rglob('*') 
#              if f.is_file() and not f.name.startswith('.'))
#
#def print_dir_tree(directory, prefix='', is_last=True, is_root=True):
#    """优化后的目录树打印函数"""
#    path = Path(directory)
#    file_count = count_files_recursive(path)
#    
#    # 根目录特殊处理
#    if is_root:
#        print(f"{path.name}/ [总文件数: {file_count}]")
#    else:
#        connector = '└── ' if is_last else '├── '
#        print(f"{prefix}{connector}{path.name}/ [总文件数: {file_count}]")
#    
#    # 处理子目录
#    dirs = [d for d in path.iterdir() 
#            if d.is_dir() and not d.name.startswith('.')]
#    new_prefix = prefix + ('    ' if is_last else '│   ')
#    
#    for i, child in enumerate(sorted(dirs)):
#        print_dir_tree(child, new_prefix, i == len(dirs)-1, False)
#
#
#
#
#
#
#
#from pathlib import Path

def count_files_recursive(directory):
    """递归统计非隐藏的非目录文件数量"""
    return sum(1 for f in directory.rglob('*') 
              if f.is_file() and not f.name.startswith('.'))

def print_dir_tree(directory, prefix='', is_last=True, is_root=True):
    """带行间距优化的目录树打印"""
    path = Path(directory)
    file_count = count_files_recursive(path)
    
    # 根目录特殊处理
    if is_root:
        print(f"\n{path.name}/ [总文件数: {file_count}]\n")
    else:
        connector = '└── ' if is_last else '├── '
        print(f"\n{prefix}{connector}{path.name}/ [总文件数: {file_count}]\n")
    
    # 处理子目录
    dirs = [d for d in path.iterdir() 
            if d.is_dir() and not d.name.startswith('.')]
    new_prefix = prefix + ('    ' if is_last else '│   ')
    
    for i, child in enumerate(sorted(dirs)):
        print_dir_tree(child, new_prefix, i == len(dirs)-1, False)





print_dir_tree(os.path.expanduser('~/Music'))