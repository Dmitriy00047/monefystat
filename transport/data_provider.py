import dropbox
import re
from datetime import datetime


class DataProvider(object):
    '''
    This is DataProvider class
    Methods:
        get_files_list
        get_file_by_name
        get_newest_monefy_data
    '''
    def __init__(self,
                 access_token: str,
                 download_path='',
                 working_directory='/',
                 mode='auto'):
        '''
        :param str access_token: dropbox API token.
        :param str download_path: path to folder for providing data (sould include file name).
        :param str working_directory: path to working directory on dropbox where monefy data should be placed.
        :param str mode: using for switching workflow, can take only two values:
            'auto' - when dropbox working directory refreshing automatically,
            'manual' - when user refreshing dropbox working directory manually.

        Warning: 'download_path' are relative to module where method calls.

        :raises: AssertionError, TypeError.
        '''
        assert isinstance(download_path, str), 'path should be str type.'
        assert working_directory.startswith('/'), 'working directory should starts with \'/\''
        assert mode == 'auto' or mode == 'manual', 'mode should be \'auto\' or \'manual\''

        self.dbx = dropbox.Dropbox(access_token)
        self._download_path = download_path
        self._working_directory = working_directory
        self._mode = mode

    @property
    def download_path(self):
        return self._download_path

    @download_path.setter
    def download_path(self, value):
        if isinstance(value, str):
            self._download_path = value
        else:
            raise TypeError()

    @property
    def working_directory(self):
        return self._working_directory

    @working_directory.setter
    def working_directory(self, value):
        if not isinstance(value, str):
            raise TypeError()
        else:
            if value.startswith('/'):
                self._working_directory = value
            else:
                raise ValueError('Working directory should starts with \'/\'')

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        if not isinstance(value, str):
            raise TypeError()
        elif value != 'auto' and value != 'manual':
            raise ValueError('Value should be \'auto\' or \'manual\'.')
        else:
            self._mode = value

    def __get_newest_monefy_data_name_manual(self, list_of_files: list) -> str or None:
        list_of_elements = []

        for element in list_of_files:
            if element.startswith('Monefy.Data'):
                current_file_date = re.search(r'(\d{1,2}(\-|\.)\d{1,2}(\-|\.)\d{2})', element).group()
                # parsing american date format
                if current_file_date.find('-') > 0:
                    current_file_date = datetime.strptime(current_file_date, '%m-%d-%y')
                    # parsing european date format
                elif current_file_date.find('.') > 0:
                    current_file_date = datetime.strptime(current_file_date, '%d.%m.%y')

                list_of_elements.append((current_file_date, element))

        list_of_elements.sort(key=lambda tup: tup[0], reverse=True)

        if list_of_elements:
            return list_of_elements[0][1]

    def __get_newest_monefy_data_name_auto(self) -> str or None:
        if self._working_directory != '/':
            directory = self._working_directory
        else:
            directory = ''

        list_of_files = self.dbx.files_list_folder(directory).entries
        list_of_files.reverse()

        for entry in list_of_files:
            if entry.name.startswith('Monefy.Data'):
                return entry.name

    def get_files_list(self) -> list:
        '''
        This method returns list of file and folder names which contains in app folder.

        :returns list: list of names of files.
        :raises: dropbox.exceptions.ApiError.
        '''
        result = []

        if self._working_directory == '/':
            directory = ''
        else:
            directory = self._working_directory

        for entry in self.dbx.files_list_folder(directory).entries:
            result.append(entry.name)
        return result

    def get_file_by_name(self, file_name: str) -> None:
        '''
        This method download file with 'file_name' to 'self.download_path'.

        :param str file_name: name of file to download.
        :rtype: None
        :raises: dropbox.exceptions.ApiError.
        '''
        path_to_file = self._working_directory + '/' + file_name
        self.dbx.files_download_to_file(self.download_path, path_to_file)

    def get_newest_monefy_data(self) -> None:
        '''
        This method download newest monefy.data file to 'self.download_path'.

        :rtype: None
        :raises: dropbox.exceptions.ApiError.
        '''
        newest_file_name = None

        if self._mode == 'manual':
            newest_file_name = self.__get_newest_monefy_data_name_manual(self.get_files_list())
        elif self._mode == 'auto':
            newest_file_name = self.__get_newest_monefy_data_name_auto()

        if newest_file_name:
            if self._working_directory == '/':
                path_to_file = self.working_directory + newest_file_name
            else:
                path_to_file = self._working_directory + '/' + newest_file_name
            self.dbx.files_download_to_file(self.download_path, path_to_file)
