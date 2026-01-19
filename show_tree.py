import os

# Папки, которые не нужно включать в дерево
IGNORED_DIRS = {
    "__pycache__",
    ".venv",
    "venv",
    "migrations",
    "staticfiles",
    "media",
    "node_modules",
    ".git",
    ".idea",
    ".vscode",
}

# Файлы, которые не нужно показывать
IGNORED_FILES = {
    "tree_filtered.txt",
    "show_tree.py",
    "output.html",
    "render_template.py",
}

def print_tree(start_path=".", prefix="", file=None, max_depth=4, level=0):
    """
    Печатает дерево директорий (с ограничением глубины и фильтрацией).
    """
    if level > max_depth:
        return

    try:
        items = sorted(os.listdir(start_path))
    except PermissionError:
        return

    for i, name in enumerate(items):
        path = os.path.join(start_path, name)

        # Пропуск игнорируемых папок и файлов
        if name in IGNORED_DIRS or name in IGNORED_FILES:
            continue

        connector = "└── " if i == len(items) - 1 else "├── "
        print(prefix + connector + name, file=file)

        # Рекурсивный спуск в подпапку
        if os.path.isdir(path):
            extension = "    " if i == len(items) - 1 else "│   "
            print_tree(path, prefix + extension, file=file, max_depth=max_depth, level=level + 1)


if __name__ == "__main__":
    with open("tree_filtered.txt", "w", encoding="utf-8") as f:
        print_tree(".", file=f)
    print("✅ Дерево сохранено в tree_filtered.txt")




# python show_tree.py