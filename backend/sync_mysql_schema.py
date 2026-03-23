# -*- coding: utf-8 -*-
from modules.mysql_runtime import init_mysql_schema


def main() -> None:
    init_mysql_schema()
    print('MySQL schema synchronized.')


if __name__ == '__main__':
    main()
