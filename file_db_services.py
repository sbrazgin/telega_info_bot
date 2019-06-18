from os import walk
import os
import io


class File_DB_helper:

    # ------------------------------------------------------------------
    def __init__(self, data_dir: str, data_drop_dir: str, g_logger):
        self._data_dir = data_dir
        self._data_drop_dir = data_drop_dir
        self._g_logger = g_logger


    # ------------------------------------------------------------------
    def get_files(self):
        f = []
        for (dirpath, dirnames, filenames) in walk(self._data_dir):
            f.extend(filenames)
            break
        return f

    # ------------------------------------------------------------------
    def drop_file(self, file_name: str):
        try:
            os.rename(self._data_dir + file_name, self._data_drop_dir + file_name)
        except OSError as err:
            self._g_logger.error("OS error: {0}".format(err))

        try:
            os.remove(self._data_dir + file_name)
        except OSError as err:
            self._g_logger.error("OS error: {0}".format(err))

    # ------------------------------------------------------------------
    def get_file_cont(self, file_name: str):
        with io.open(self._data_dir + file_name, "r", encoding='utf8') as myfile:
            data = myfile.read()
            return data

