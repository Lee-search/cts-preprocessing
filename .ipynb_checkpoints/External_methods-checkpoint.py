import os

# ---- External Methods ---- #
# pretty_print: XML 서식에 맞춰서 출력
# create_directory: 폴더 없으면 시스템 생성
def pretty_print(current, parent=None, index=-1, depth=0):
    for i, node in enumerate(current):
        pretty_print(node, current, i, depth + 1)
    if parent is not None:
        if index == 0:
            parent.text = '\n' + ('\t' * depth)
        else:
            parent[index - 1].tail = '\n' + ('\t' * depth)
        if index == len(parent) - 1:
            current.tail = '\n' + ('\t' * (depth - 1))
            
def create_directory(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print("Error: Failed to create the directory.")