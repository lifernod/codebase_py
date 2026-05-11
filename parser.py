import sys

from tabulate import tabulate

from core.parsers.file_parser import process_dir


def main():
    if len(sys.argv) < 2:
        raise RuntimeError('Не указан путь до директории')

    input_dir = sys.argv[1]
    results = process_dir(input_dir)

    rows = []
    for result in results:
        rows.append([result.name, len(result.classes), len(result.functions)])

    print(tabulate(rows, headers=["Имя файла", "Классы", "Функции"], tablefmt="fancy_grid"))

if __name__ == '__main__':
    main()