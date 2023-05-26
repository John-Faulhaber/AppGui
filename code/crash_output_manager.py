'''
Module to handle crash log and data dump directory checks and creation, and file relocation.
'''
# Built-in
import os
import shutil
import logging
import traceback


class CrashOutputManager():
    '''
    Class containing functions to handle crash log and data dump directory checks and creation, and file relocation.
    '''

    @staticmethod
    def crash_log_manager(output_file_name, optional_bool = False):
        '''
        Manage crash log and crash log directory creation and location.

        Parameters
        ----------
        output_file_name (string): File name of regular output file, based on hard-coded name in functionality_module module.
        optional_bool (bool): If True, custom log error will be printed, instead of traceback.format_exc()

        Returns
        -------
        PATH string of output crash log file
        '''
        # Check for and make if required "Crash Logs" directory
        output_crash_log_folder = 'Crash Logs'
        output_crash_log_folder_path = f'{os.path.dirname(os.getcwd())}\\{output_crash_log_folder}'

        if not os.path.isdir(f'{output_crash_log_folder_path}'):
            os.mkdir(f'{output_crash_log_folder_path}')

        # Carve out original output file name, add ".log" filetype
        output_crash_log_file_name = f'{output_file_name.split(".")[0]}_CRASHLOG.log'
        output_crash_log_file_path = f'{output_crash_log_folder_path}\\{output_crash_log_file_name}'

        # Perform the logging
        # logger.error(msg) - "logs" what it's fed (msg), marks it as an "error"-level issue. As opposed to info-level, warning-level, critical level, etc.
        # force=True - Any existing handlers attached to the root logger are removed and closed, before carrying out the configuration as specified by the other arguments.
        # --> This will allow for logging to a NEW log file with the updated name, as opposed to using the first name it gets from any first exception when application is run, and locking that file in as the one to write to
        # Using defaults for all other logger configuration keywords
        logging.basicConfig(filename=output_crash_log_file_path, force=True)
        if not optional_bool:
            logging.error(traceback.format_exc())
        else:
            logging.error(
                f'\n'
                f'\n'
                f'[This is a custom logging.error message]\n'
                f'\n'
                f'| Here is a sentence!\n'
                f'| \n'
                f'| \n'
                f'| Here is another sentence!\n'
                f'| \n'
                f'|'
            )

        return output_crash_log_file_path


    @staticmethod
    def crash_data_manager(output_file_name, output_file_path):
        '''
        Manage crash data output and crash data directory creation and location.
        Relocates original output file to crash directory, and renames to include crash descriptors.

        Parameters
        ----------
        output_file_name (string): File name of regular output file, based on user-chosen voltage list .txt file
        output_file_path (string): PATH of regular output file, based on user-chosen voltage list .txt file

        Returns
        -------
        PATH string of output crash data file
        '''
        # Check for and make if required "Crash Data" directory
        output_crash_data_folder = 'Crash Data'
        output_crash_data_folder_path = f'{os.path.dirname(os.getcwd())}\\{output_crash_data_folder}'

        if not os.path.isdir(f'{output_crash_data_folder_path}'):
            os.mkdir(f'{output_crash_data_folder_path}')

        # Carve out original output file name, add ".txt" filetype
        output_crash_data_file_name = f'{output_file_name.split(".")[0]}_CRASHDUMP.txt'
        output_crash_data_file_path = f'{output_crash_data_folder_path}\\{output_crash_data_file_name}'

        # Move original output file to crash specific directory
        # Performs the above-specified re-naming
        shutil.move(output_file_path, output_crash_data_file_path)

        return output_crash_data_file_path
