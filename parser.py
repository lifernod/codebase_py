import sys

from tabulate import tabulate

from core.parsers.file_parser import process_dir
from database.write_database import WriteDatabase


def main():
    if len(sys.argv) < 2:
        raise RuntimeError('Не указан путь до директории')

    input_dir = sys.argv[1]
    results = process_dir(input_dir)
    if results:
        wdb = WriteDatabase("data/codebase.db")

        rows = []
        for result in results:
            wdb.save_file(result)
            rows.append([result.name, len(result.classes), len(result.functions)])

        wdb.close()

        print(tabulate(rows, headers=["Имя файла", "Классы", "Функции"], tablefmt="fancy_grid"))
    else:
        print("Ничего не удалось прочитать")

if __name__ == '__main__':
    main()