import os

def print_tree(path, indent=''):
    print(indent + os.path.basename(path) + '/')
    if os.path.isdir(path):
        for filename in os.listdir(path):
            print_tree(os.path.join(path, filename), indent + '  ')

print_tree('.')