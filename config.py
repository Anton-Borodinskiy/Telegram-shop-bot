# -*- coding: utf-8 -*-

from enum import Enum

token = "" # Токен телеграм бота
db_file = "database.vdb"
database_name = 'shoes.db'  # Файл с базой данных
shelve_name = 'shelve.db'  # Файл с хранилищем



class States(Enum):
    """
    Мы используем БД Vedis, в которой хранимые значения всегда строки,
    поэтому и тут будем использовать тоже строки (str)
    """
    S_START = "0"  # Начало нового диалога
    S_ENTER_NAME = "1"
    S_ENTER_AGE = "2"
    S_SEND_PIC = "3"
    S_PICK_GOODS = "4"
    S_PICK_SHOES = "5"
    S_MAKE_ORDER_NAME = "6"
    S_MAKE_ORDER_PHONE = "7"
    S_MAKE_ORDER_ADDR = "8"
    S_ORDER_DETAILS = "9"
