import dropbox
from datetime import datetime


class DataProvider:
    '''
    This is DataProvider class
    Methods:
        get_files_list
        get_file_by_name
        get_newest_monefy_data
    '''
    def __init__(self, access_token):
        self.dbx = dropbox.Dropbox(access_token)

    def __get_newest_monefy_data_name(self, list_of_files):
        newest_file_index = -1
        newest_file_date = datetime(1, 1, 1)
        for i in range(len(list_of_files)):
            file_name_parts = list_of_files[i].split('.')
            if (file_name_parts[0] == 'Monefy' and
                    file_name_parts[1] == 'Data'):
                if datetime.strptime(
                        file_name_parts[2], "%m-%d-%y") > newest_file_date:
                    newest_file_date == datetime.strptime(
                        file_name_parts[2], "%m-%d-%y")
                    newest_file_index = i

        if newest_file_index > 0:
            return list_of_files[newest_file_index]

    def get_files_list(self):
        '''
        This method returns list of file and folder names which
        contains in app folder.
        '''
        result = []
        for entry in self.dbx.files_list_folder('').entries:
            result.append(entry.name)
        return result

    def get_file_by_name(self, download_path, file_name):
        '''
        This method download file with 'file_name' to 'download_path'.

        Warning: 'download_path' are relative to module where its called.

        :param download_path: path to download (should include file name).
        :param file_name: name of file to download.
        :return:
        '''
        self.dbx.files_download_to_file(download_path, '/' + file_name)

    def get_newest_monefy_data(self, download_path):
        '''
        This method download newest monefy.data file to 'download_path'.

        Warning: 'download_path' are relative to module where its called.

        :param download_path: path to download (should include file name).
        :return:
        '''
        newest_file_name = \
            self.__get_newest_monefy_data_name(self.get_files_list())
        self.dbx.files_download_to_file(download_path, '/' + newest_file_name)
