import os
import argparse
from pathlib import Path

IGNORE_DIRS = {
    '__pycache__', 'node_modules', '.git', '.vscode', 
    'dist', 'build', 'venv', 'env', '.idea', 'tmp'
}

IGNORE_FILES = {
    '.DS_Store', '*.log', '*.md', 'package-lock.json',
    '*.config.js', '*.pyc', '*.swp', '*.tmp', '*.bak'
}

def should_ignore(path):
    if any(part.startswith('.') and part not in ('.', '..') 
           for part in path.parts):
        return True
    
    if any(part in IGNORE_DIRS for part in path.parts):
        return True
    
    if path.is_file():
        return any(path.match(pattern) for pattern in IGNORE_FILES)
    
    return False

def generate_tree(directory, prefix='', is_last=True):
    directory = Path(directory)
    if should_ignore(directory):
        return ''
    
    lines = []
    parts = list(directory.iterdir())
    
    parts.sort(key=lambda p: (not p.is_dir(), p.name.lower()))
    
    connector = '└── ' if is_last else '├── '
    lines.append(f"{prefix}{connector}{directory.name}/" if directory != Path('.') else "")
    
    new_prefix = prefix + ('    ' if is_last else '│   ')
    
    for i, path in enumerate(parts):
        if should_ignore(path):
            continue
            
        is_last_item = i == len(parts) - 1
        
        if path.is_dir():
            lines.append(generate_tree(
                path, new_prefix, is_last_item
            ))
        else:
            connector = '└── ' if is_last_item else '├── '
            lines.append(f"{new_prefix}{connector}{path.name}")
    
    return '\n'.join(line for line in lines if line)

def main():
    parser = argparse.ArgumentParser(description='Generate a clean directory tree')
    parser.add_argument('root', nargs='?', default='.', help='Root directory')
    parser.add_argument('-o', '--output', help='Output file (optional)')
    args = parser.parse_args()
    
    tree = generate_tree(args.root)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(tree)
        print(f"Tree saved to {args.output}")
    else:
        print(tree)

if __name__ == '__main__':
    main()