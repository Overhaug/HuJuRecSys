#!/usr/bin/env python


# last-index-of
def rindex(iterable, value):
    try:
        return len(iterable) - next(i for i, val in enumerate(reversed(iterable)) if val == value) - 1
    except StopIteration:
        raise ValueError


# Length of a file
def file_len(fname, encoding='utf-8'):
    empty_lines = 0
    with open(fname, 'r', encoding=encoding) as f:
        for i, l in enumerate(f):
            if l == '' or l is None:
                empty_lines += 1
            pass
    return i + 1 - empty_lines


# Options menu when filepath exists
def options(path):
    alternatives = ('Overwrite', 'Generate new path (current path: '+path+')')
    for i, v in enumerate(alternatives):
        print(i, v)
    try:
        choice = int(input())
    except ValueError:
        print('Must be digit')
        return options(path)
    if choice == 0:
        return path
    if choice == 1:
        i = path.rfind('.')
        try:
            if int(path[i-1]):
                new_no = int(path[i-1]) + 1
                new_path = path[:i-1] + str(new_no) + '.csv'
                path = new_path
        except ValueError:
            path = path[:i] + path[i:-4] + '2' + '.csv'
        return path
