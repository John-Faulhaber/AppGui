'''
Module to handle grabbing user-input data from the threading table in the GUI.
'''


class ThreadingTableDataWrangler():
    '''
    Class containing a function to handle grabbing user-input data from the threading table in the GUI.
    '''

    @staticmethod
    def threading_table_data_wrangler(update_status_callback, threading_table_text_widgets, threading_table_time_widgets):
        '''
        Grabs user-input values directly from GUI Threading Table widgets. Curates grabbed data.

        Parameters
        ----------
        update_status_callback (function object): Defined in run.py, prints fed string to GUI status box + refreshes GUI
        threading_table_text_widgets (list): List of 'PyQt5.QtWidgets.QLineEdit' class objects that take the text value user-input for Threading Table in the GUI
        threading_table_time_widgets (list): List of 'PyQt5.QtWidgets.QLineEdit' class objects that take the time value user-input for Threading Table in the GUI

        Returns
        -------
        A tuple containing two boolean values of True is returned if failure occurs at a known potential failure point.
        Otherwise returns a tuple containing:
        threading_table_text_list (list): List of str-type user-input text values from GUI Threading Table
        threading_table_times_list (list): List of str-type user-input time values from GUI Threading Table
        '''
        threading_table_text_list = []
        threading_table_times_list = []

        for i in range(5):  # Threading table has 5 rows
            threading_table_text_list.append(threading_table_text_widgets[i].text())
            threading_table_times_list.append(threading_table_time_widgets[i].text())

        # Remove rows with both empty text and empty time columns from end of GUI threading table. Detect if entire threading table is empty
        while threading_table_text_list[-1] == '' and threading_table_times_list[-1] == '':
            if len(threading_table_text_list) == 1 and len(threading_table_times_list) == 1:
                update_status_callback('<p style="font-size:11px; color:#DADADA;">' + 'Empty Threading Table!<br>' + '</p>')
                return (True, True)

            threading_table_text_list.pop()
            threading_table_times_list.pop()

        # Check for empty text or empty time column cells in remaining, trimmed threading table data
        if '' in threading_table_text_list or '' in threading_table_times_list:
            update_status_callback('<p style="font-size:11px; color:#DADADA;">' + 'Missing Threading Table data!<br>' + '</p>')
            return (True, True)

        # Avoid sleep time overflow
        for value in threading_table_times_list:
            if not 60 >= float(value) >= 0:  # Set limit to 60 seconds
                update_status_callback('<p style="font-size:11px; color:#DADADA;">' + 'Threading Table time values too large: 60 ≥ t ≥ 0<br>' + '</p>')
                return (True, True)

        return (threading_table_text_list, threading_table_times_list)
