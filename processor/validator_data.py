import csv
from datetime import date, datetime


class ValidationError(Exception):
    pass


def validate_data(file_csv) -> list:
    '''
    This method validate Monefy_data.csv and typing data from Monefy_data.csv
    The file that is called by this function is stored in the following way:
    /downloads/Monefy_data.csv'

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
        row[i] = types[i](row[i])
    return row


def read_from_file(file_csv) -> list:
    '''
    This method read data fron the csv file.

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
        rows = csv.reader(csvfile, delimiter=',')
        if title_file not in rows:
            raise ValidationError('The content of the file is incorrect')
        for row in rows:
            if row and row != title_file:
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
