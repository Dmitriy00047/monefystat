from datetime import date


class ValidationError(Exception):
    pass


def validate_data(file_csv) -> list:
    """
    This method validate Monefy_data.csv and typing data from Monefy_data.csv
    The file that is called by this function is stored in the following way:
    '/downloads/Monefy_data.csv'

    :param .csv file_csv: path to file Monefy_data.csv

    :raises: ValidationError
    """
    types = [date, str, str, float, str, float, str, str]
    result = []
    # validate data
    with open(file_csv, 'r', encoding='utf8') as inf:
        title_file = inf.readline().strip()
        if title_file != 'date,account,category,amount,currency,converted amount,currency,description':
            raise ValidationError("The content of the file is incorrect")

        # convert all the fields in a row by type
        for line in inf:
            if line != '\n':
                current_string = line.strip().split(',')
                description = current_string[7] if len(current_string) == 8 else ''

                # the following two lines to that the fields don't have spaces except the description field
                current_string = list(map(lambda x: x.replace(" ", ""), current_string[:7]))
                current_string = list(map(lambda x: x.replace("\xa0", ""), current_string[:7]))
                current_string.append(description)

                # the following two lines convert str with date into datetime.date
                current_string[0] = current_string[0].split('/')[::-1]
                if current_string[0] != ['']:
                    current_string[0] = date(int(current_string[0][0]), int(current_string[0][1]), int(current_string[0][2]))

                # convert the rest of the fields
                for i in range(1, len(types)):
                    if len(current_string) == 8:
                        current_string[i] = types[i](current_string[i])
                result.append(current_string)
    return result
