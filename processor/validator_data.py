import csv
from datetime import date, datetime


class ValidationError(Exception):
    pass


def validate_data(file_csv) -> list:
    '''
    This method validate Monefy_data.csv and typing data from Monefy_data.csv
    The file that is called by this function is stored in the following way:
    '/downloads/Monefy_data.csv'
    :param .csv file_csv: path to file Monefy_data.csv
    '''
    result = []
    rows = read_from_file(file_csv)
    for row in rows:
        result.append(convert_type(row))
    return result


def convert_type(row: list) -> list:
    '''
    This method convert each element of the csv row into
    specific type.
    :param row: the line of the csv file
    '''
    types = [date, str, str, float, str, float, str, str]
    row[0] = datetime.strptime(row[0], '%d/%m/%Y').date()
    for i in range(1, len(types)):
        if i in (3, 5):
            row[i] = replace_symbol_from_amount(row[i])
        row[i] = types[i](row[i])
    return row


def replace_symbol_from_amount(column: str) -> str:
    '''
    This method replace special symbols to empty string.
    :param column: the string that should be checked
    '''
    column = column.replace('"', '')
    parts = column.split(',')
    if len(parts[-1]) < 3:
        return str().join(parts[:-1]) + '.' + parts[-1]
    return str().join(parts)


def read_from_file(file_csv) -> list:
    '''
    This method read data from the csv file.
    :param .csv file_csv: path to file Monefy_data.csv
    :raises: ValidationError
    '''
    title_file = [
        'date',
        'account',
        'category',
        'amount',
        'currency',
        'converted amount',
        'currency',
        'description'
    ]
    result = []
    with open(file_csv, 'r', encoding='utf8') as csvfile:
        header = csvfile.readline()
        delimiter = ',' if header.count(',') else ';'

        if header == delimiter.join(title_file):
            raise ValidationError('The content of the file is incorrect')

        rows = csv.reader(csvfile, delimiter=delimiter)
        for row in rows:
            result.append(convert_row(row))
    return result


def convert_row(row: list) -> list:
    '''
    This method remove space and '\xa0' from the each element
    of the csv row.
    :param row: the line of the csv file
    '''
    row = list(map(lambda x: x.replace(' ', ''), row))
    row = list(map(lambda x: x.replace('\xa0', ''), row))
    return row
