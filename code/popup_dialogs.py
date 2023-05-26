'''
Module to handle exception-catch pop-up dialog boxes.
'''
# PyQt5
from PyQt5.QtWidgets import QMessageBox


class PopupDialogs():
    '''
    Class containing functions to handle exception-catch pop-up dialog boxes.
    '''

    # Design exception-catch pop-up dialog boxes
    # Purpose of each is listed within each
    @staticmethod
    def fancy_unexpected_exception(output_crash_log_file_path, output_crash_data_file_path):
        '''
        Notifies user of unexpected exception.
        Informs user of crash exception log and crash data file PATHs.

        Parameters
        ----------
        output_log_file_path (string): Output crash log file path
        output_crash_data_file_path (string): Output crash data file path

        Returns
        -------
        A Boolean value of True is returned when the dialog box is exited.
        '''
        pop_up = QMessageBox()
        pop_up.setIcon(QMessageBox.Warning)
        pop_up.setWindowTitle('Unexpected Exception!')
        pop_up.setText('<p style="font-size:11px;">' + f'An unexpected exception occurred. Please see:<br><br>"{output_crash_log_file_path}"<br><br>and<br><br>"{output_crash_data_file_path}"' + '</p>')
        pop_up.setStandardButtons(QMessageBox.Ok)

        # Returns the evaluation of pop_up.exec() == QMessageBox.Ok
        # i.e. popup appears, background blocks, "OK" or "X" selected, bool of True is returned, the return below returns that bool out
        return pop_up.exec() == QMessageBox.Ok


    @staticmethod
    def popup_demonstration():
        '''
        Notifies user of task result.
        Informs user of crash exception log and crash data file PATHS.

        Parameters
        ----------
        N/A

        Returns
        -------
        A Boolean value of True is returned when the dialog box is exited.
        '''
        pop_up = QMessageBox()
        pop_up.setIcon(QMessageBox.Warning)
        pop_up.setWindowTitle('Task Failed!')
        pop_up.setText('<p style="font-size:11px;">' + f'The task failed!' + '</p>')
        pop_up.setStandardButtons(QMessageBox.Ok)

        # Returns the evaluation of pop_up.exec() == QMessageBox.Ok
        # i.e. popup appears, background blocks, "OK" or "X" selected, bool of True is returned, the return below returns that bool out
        return pop_up.exec() == QMessageBox.Ok
