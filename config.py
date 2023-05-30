# -*- coding: utf-8 -*-

from enum import Enum

token = "6242184601:AAHxe-6qimbqmQ8cctHI7b_fgH2ZX0Caji8" 
db_file = "database.vdb"
database_name = 'shoes.db'  
shelve_name = 'shelve.db'  



class States(Enum):
    """
    We use the Vedis database, in which the stored values ​​are always strings, so we will use strings here too
 (str)
    """
    S_START = "0"   
    S_ENTER_NAME = "1"
    S_ENTER_AGE = "2"
    S_SEND_PIC = "3"
    S_PICK_GOODS = "4"
    S_PICK_SHOES = "5"
    S_MAKE_ORDER_NAME = "6"
    S_MAKE_ORDER_PHONE = "7"
    S_MAKE_ORDER_ADDR = "8"
    S_ORDER_DETAILS = "9"
