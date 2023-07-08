import os

def run(action, directory=None, contents=None):
    if directory:
        root = os.getcwd()
        filename_or_directory = os.path.join('workspace', directory)
    else:
        filename_or_directory = 'workspace'
    if action == 'read_file':
        with open(filename_or_directory) as f:
            return f.read()
    elif action == 'write_file':
        with open(filename_or_directory, 'w') as f:
            f.write(contents)
        return f'Written file!'
    elif action == 'create_directory':
        os.mkdir(filename_or_directory)
        return f'Created directory {filename_or_directory}'
    elif action == 'delete_directory':
        for root, dirs, files in os.walk(filename_or_directory):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        os.rmdir(filename_or_directory)
        return f'Deleted directory successfully!'
    elif action == 'delete_file':
        os.remove(filename_or_directory)
        return 'Deleted file successfully!'
    elif action == 'list_files':
        return os.listdir(filename_or_directory)
