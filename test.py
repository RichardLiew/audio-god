
def tree(data):
    def _build(_data, lines, indent=0, prefix='', is_last=True, is_root=True, current_key='', show_count=True):
        if isinstance(_data, dict):
            def _count_leaves(node):
                if isinstance(node, list):
                    return len(node)
                elif isinstance(node, dict):
                    return sum(_count_leaves(v) for v in node.values())
                return 0

            def _count_children(node):
                if isinstance(node, dict):
                    return len(node)
                return 0

            total_leaves = _count_leaves(_data)
            direct_children = _count_children(_data)

            if is_root:
                key = list(_data.keys())[0] if len(_data) == 1 else 'Root'
                lines.append(
                    f'{key}' + f' (leaves: {total_leaves}, children: {direct_children})' if show_count else '',
                )
                new_prefix = prefix + '    '
                items = _data[key].items() if len(_data) == 1 else _data.items()
            else:
                connector = '└── ' if is_last else '├── '
                current_prefix = prefix + connector
                key = current_key if current_key else 'Node'
                lines.append(
                    f'{current_prefix}{key}' + f' (leaves: {total_leaves}, children: {direct_children})' if show_count else '',
                )
                new_prefix = prefix + ('    ' if is_last else '│   ')
                items = _data.items()

            for i, (key, value) in enumerate(items):
                child_is_last = i == len(items) - 1
                if isinstance(value, dict):
                    _build(value, lines, indent+1, new_prefix, child_is_last, False, key)
                elif isinstance(value, list):
                    lines.append(
                        f'{new_prefix}{"└── " if child_is_last else "├── "}{key} ' + f'(leaves: {len(value)}, children: 0)' if show_count else '',
                    )
        elif isinstance(_data, list):
            lines.append(
                f'{prefix}└── ' + f'(leaves: {len(_data)}, children: 0)' if show_count else '',
            )
        else:
            raise Exception('Data must be a dict!')

    lines = []
    _build(data, lines, show_count=True)
    return '\n'.join(lines)



print(tree({
    'RRRott': {
        'Branch1': ['a', 'b'],
        'Branch2': {
            'Sub1': ['c'],
            'Sub2': ['d', 'e', 'f'],
            'Sub3': {
                'Leaf1': ['g'],
                'Leaf2': ['h', 'i']
            }
        },
        'aaa': [],
        #'bbb': None,
    }
}))