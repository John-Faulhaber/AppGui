'''
Module containing class to handle the application's GUI and operation.
'''
# Built-in
import sys
import time
from datetime import datetime
from pathlib import Path
# PyQt5
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QRegExp
from PyQt5.QtCore import QThread
from PyQt5 import QtWidgets
from PyQt5 import QtGui
# Encryption
import base64
import hashlib
from cryptography.fernet import Fernet
# Modules
from functionality_module import FunctionalityClass
from threading_table_data_wrangler import ThreadingTableDataWrangler
from popup_dialogs import PopupDialogs


# Class to manage the GUI
# Make child class of QDialog
class ApplicationUi(QtWidgets.QDialog):
    '''
    Class containing functions to handle the application's GUI and operation.
    '''

    # Subclass __init__ to inject calls to methods to build GUI
    def __init__(self):
        '''
        "Initialize" GUI window and run the functions that create the GUI.

        Parameters
        ----------
        self: Represents the instance of the Class

        Returns
        -------
        None
        '''
        # Inherit back rest of QDialog. super.__init vs parent.__init similar. Do not need multiple inheritance. Using parent.__init__ for cleanliness
        QtWidgets.QDialog.__init__(self)  # QtWidgets.QDialog (class "PyQt5.QtWidgets.QDialog", "sip.wrappertype")

        # Immediately connect PyQt signals to slots for communication between threads
        # FunctionalityClass class must be instantiated to use .connect on its methods as per PyQt requirements
        # These non-static methods use self, so instantiating the class properly also removes the need to pass something to fill the "self" argument manually, a non-problem with static methods
        # For an instantiated class, the methods are called by the object variable the class is set to, self.foo.method(), as opposed to directly with class.method(args) like with static methods
        # When the methods these signals emit from are called, they must be called by using the same instantiated class variable object (below) used to make the signal slot connection (also below)
        # Else the object ID of self in self.foo_signal.emit() and the ID of the instance of the class used when making the signal slot connection (the instance the connection lives in) will differ
        self.functionality_class = FunctionalityClass()
        self.functionality_class.fancy_unexpected_exception_signal.connect(PopupDialogs.fancy_unexpected_exception)
        self.functionality_class.update_status_callback.connect(self.update_status_callback)  # Would be same syntax if connecting to a popup dialog method in PopupDialogs module

        # Build the GUI
        self.__create_components()  # create the GUI component objects
        self.__configure_components()  # Adjust GUI component object appearance and behavior
        self.__construct_gui()  # assemble all GUI component objects together


    def __create_components(self):
        '''
        Create GUI component objects: widgets, group-boxes, and layout objects.

        Parameters
        ----------
        self: Represents the instance of the Class

        Returns
        -------
        None
        '''
        # "#" represents reverse nested level
        #### Top-level window
        self.main_layout = QtWidgets.QGridLayout()

        ### General group-box
        self.main_box = QtWidgets.QGroupBox('General Functionality', alignment = Qt.AlignCenter)
        self.main_box_layout = QtWidgets.QGridLayout()

        ## set_text group-box
        self.set_text_group_box = QtWidgets.QGroupBox('Set Text')
        self.set_text_group_box_layout = QtWidgets.QGridLayout()
        # Widgets
        self.set_text = QtWidgets.QLineEdit()

        ## configure group-box
        self.configure_group_box = QtWidgets.QGroupBox('Configure Text')
        self.configure_group_box_layout = QtWidgets.QGridLayout()
        # Widgets
        self.radio_button_regular = QtWidgets.QRadioButton('Regular')
        self.radio_button_mirrored = QtWidgets.QRadioButton('Mirrored')

        ## threading_table group-box
        self.threading_table_group_box = QtWidgets.QGroupBox('Threading Table')
        self.threading_table_group_box_layout = QtWidgets.QGridLayout()
        # Widgets
        self.use_threading_table = QtWidgets.QCheckBox('Use threading table?')
        self.save_threading_data = QtWidgets.QCheckBox('Save to .txt file?')
        self.threading_table = QtWidgets.QTableWidget()
        self.threading_table_text_widgets = [QtWidgets.QLineEdit() for _ in range(5)]
        self.threading_table_time_widgets = [QtWidgets.QLineEdit() for _ in range(5)]

        ## status group-box
        self.status_group_box = QtWidgets.QGroupBox('Status')
        self.status_group_box_layout = QtWidgets.QGridLayout()
        # Widgets
        self.status = QtWidgets.QPlainTextEdit()

        ## go_row - distinct organization
        self.go_row_layout = QtWidgets.QHBoxLayout()
        # Widgets
        self.clear = QtWidgets.QPushButton('Clear')
        self.always_clear = QtWidgets.QCheckBox('Always clear on "Go!"')
        self.go_button = QtWidgets.QPushButton('Go!')

        ### Bonus group-box
        self.bonus_box = QtWidgets.QGroupBox('Bonus Features', alignment = Qt.AlignCenter)
        self.bonus_box_layout = QtWidgets.QGridLayout()

        ## Demonstrations group-box
        self.demonstration_group_box = QtWidgets.QGroupBox()
        self.demonstration_group_box_layout = QtWidgets.QGridLayout()
        # Widgets
        self.popup_test_button = QtWidgets.QPushButton('Pop-Up Demonstration')
        self.settings_button = QtWidgets.QPushButton('Saveable Settings Demonstration')
        self.mutex_test_button = QtWidgets.QPushButton('MUTEX Demonstration')  # FOR THREAD SAFETY!
        self.autofill_test_button = QtWidgets.QPushButton('Autofill Demonstration')

        ## Progress Bar group-box
        self.progress_bar_group_box = QtWidgets.QGroupBox('~Progress Bar~', alignment = Qt.AlignCenter)
        self.progress_bar_group_box_layout = QtWidgets.QGridLayout()
        # Widgets
        self.progress_bar = QtWidgets.QProgressBar()
        self.values_lassoed = QtWidgets.QLabel('Pointless items completed: 0/0 (0%)')
        self.pointless_task_button = QtWidgets.QPushButton('Pointless Task')
        self.reset_button = QtWidgets.QPushButton('Reset')

        ### version_row - distinct organization
        self.version_row_layout = QtWidgets.QHBoxLayout()
        # Create decrypted "version value" object for display in bottom of GUI. Version number is YYYYMMDD format
        version_decrypted = self.__version_decryption()
        self.version = QtWidgets.QLabel(f'Version {version_decrypted}')

        #### Create additional functional objects
        # Set Text entry validator
        self.set_text_validator = QtGui.QRegExpValidator(QRegExp(r'^[a-zA-Z0-9]{1,6}$'))  # REGEX One to six alphanumeric characters
        # Threading Table time value entry validator
        self.timing_validator = QtGui.QRegExpValidator(QRegExp(r'^[0-9]{1,2}$'))  # REGEX One to two digits. Limits on actual numerical value performed outside REGEX


    def __configure_components(self):
        '''
        Configure GUI component objects.
        Connect GUI component objects to methods.
        Assign/set entry validators.
        Assign/configure signals
        Add demonstration, such as "ToolTips" to specific component objects.

        Parameters
        ----------
        self: Represents the instance of the Class

        Returns
        -------
        None
        '''
        # "#" represents reverse nested level
        #### Top-level window attributes
        self.setLayout(self.main_layout)
        self.setWindowTitle('Application Graphical User Interface 3000')
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowMinimizeButtonHint)

        ### General group-box attributes
        self.main_box.setLayout(self.main_box_layout)
        self.main_box.setStyleSheet('QGroupBox { font-size: 11px; }')

        ## Set Text group-box attributes
        self.set_text_group_box.setLayout(self.set_text_group_box_layout)
        self.set_text_group_box.setStyleSheet('QGroupBox { font-size: 11px; }')
        self.set_text_group_box.setMinimumWidth(173)  # Minimum on this group-box still allows the set_text widget to expand horizontally with the group box itself
        # Widget attributes
        self.set_text.setFixedHeight(30)
        self.set_text.setReadOnly(False)
        self.set_text.setPlaceholderText('Text | Hover over me for help')
        self.set_text.setValidator(self.set_text_validator)
        self.set_text.textChanged.connect(self.check_state)
        self.set_text.textChanged.emit(self.set_text.text())
        self.set_text.textChanged.emit(self.set_text.text())
        self.set_text.setToolTip('Set Text text restricted to 1-6 alphanumeric characters.\n\nExamples:\nAny combination of letters and numbers, without spaces. See below:\n\nabc  |  123  |  abc123')

        ## configure group-box attributes
        self.configure_group_box.setLayout(self.configure_group_box_layout)
        self.configure_group_box.setStyleSheet('QGroupBox { font-size: 11px; }')
        # Widget attributes
        self.radio_button_regular.setFont(QtGui.QFont('Cascadia Mono', 10))
        self.radio_button_regular.setToolTip('Text will print normally.')
        self.radio_button_mirrored.setFont(QtGui.QFont('Cascadia Mono', 10))
        self.radio_button_mirrored.setToolTip("Text will print with character order reversed.")

        ## Threading Table group-box attributes
        self.threading_table_group_box.setLayout(self.threading_table_group_box_layout)
        self.threading_table_group_box.setStyleSheet('QGroupBox { font-size: 11px; }')
        # Widget attributes
        self.save_threading_data.setToolTip('Saves printed text to .txt file.')
        self.threading_table.setRowCount(5)
        self.threading_table.setColumnCount(2)
        self.threading_table.setHorizontalHeaderLabels(['Text', 'Time'])
        self.threading_table.setFixedHeight(171)  # Precise height to remove vertical scroll bar
        self.threading_table.setFixedWidth(213)  # Precise width to remove horizontal scroll bar

        for i in range(5):
            self.threading_table.setCellWidget(i,0, self.threading_table_text_widgets[i])
            self.threading_table_text_widgets[i].setPlaceholderText('Text')
            self.threading_table_text_widgets[i].setValidator(self.set_text_validator)
            self.threading_table_text_widgets[i].textChanged.connect(self.check_state)
            self.threading_table_text_widgets[i].textChanged.emit(self.threading_table_text_widgets[i].text())
            self.threading_table.setCellWidget(i,1, self.threading_table_time_widgets[i])
            self.threading_table_time_widgets[i].setPlaceholderText('Time (s)')
            self.threading_table_time_widgets[i].setValidator(self.timing_validator)
            self.threading_table_time_widgets[i].textChanged.connect(self.check_state)
            self.threading_table_time_widgets[i].textChanged.emit(self.threading_table_time_widgets[i].text())

        ## Status group-box attributes
        self.status_group_box.setLayout(self.status_group_box_layout)
        self.status_group_box.setStyleSheet('QGroupBox { font-size: 11px; }')
        # Widget attributes
        self.status.setStyleSheet('QPlainTextEdit {background-color: rgb(0, 0, 0);}')
        self.status.setReadOnly(True)
        self.status.setPlaceholderText('AGUI 3000 status log will print in this box')

        ## go_row attributes
        # Widget attributes
        # Make "Go!" the default button in focus. Enter key selects focused elements
        self.go_button.setDefault(True)
        self.go_button.clicked.connect(self.click_go)
        self.clear.clicked.connect(self.clear_status)

        ### Bonus group-box attributes
        self.bonus_box.setLayout(self.bonus_box_layout)
        self.bonus_box.setStyleSheet('QGroupBox { font-size: 11px; }')

        ## Demonstrations group-box attributes
        self.demonstration_group_box.setLayout(self.demonstration_group_box_layout)
        # Widget attributes
        self.popup_test_button.clicked.connect(self.popup_demonstration)
        self.mutex_test_button.clicked.connect(self.functionality_class.mutex_test)
        self.settings_button.clicked.connect(self.settings_dialog_window)
        self.autofill_test_button.clicked.connect(self.autofill_demonstration_window)

        ## Progress Bar group-box + component objects attributes
        self.progress_bar_group_box.setLayout(self.progress_bar_group_box_layout)
        self.progress_bar_group_box.setStyleSheet('QGroupBox { font-size: 11px; }')
        # Widget attributes
        self.progress_bar.setOrientation(Qt.Vertical)
        self.pointless_task_button.clicked.connect(self.pointless_task)
        self.reset_button.clicked.connect(lambda: self.update_progress_bar_callback(iteration = -1, list = ['foo'], reset = True))

        ### version_row component attributes
        self.version.setStyleSheet('QLabel { background-color : ; color : #6b6b6b; }')


    def __construct_gui(self):
        '''
        Assemble GUI component objects into GUI.

        Parameters
        ----------
        self: Represents the instance of the Class

        Returns
        -------
        None
        '''
        # "#" represents reverse nested level
        # (QGridLayout: row, column, rowSpan, columnSpan)
        #### Top-level window
        self.main_layout.addWidget(self.main_box, 0, 0, 1, 1)
        self.main_layout.addWidget(self.bonus_box, 0, 1, 1, 1)
        self.main_layout.addLayout(self.version_row_layout, 1, 0, 1, 2)

        ### General group-box
        self.main_box_layout.addWidget(self.set_text_group_box, 0, 0, 1, 1)
        self.main_box_layout.addWidget(self.configure_group_box, 0, 1, 1, 1)
        self.main_box_layout.addWidget(self.status_group_box, 1, 0, 1, 2)
        self.main_box_layout.addWidget(self.threading_table_group_box, 0, 2, 2, 1)

        ## Set Text group-box
        self.set_text_group_box_layout.addWidget(self.set_text)

        ## configure group-box
        self.configure_group_box_layout.addWidget(self.radio_button_regular)
        self.configure_group_box_layout.addWidget(self.radio_button_mirrored)

        ## Threading Table group-box
        self.threading_table_group_box_layout.addWidget(self.use_threading_table, 0, 0, 1, 1)
        self.threading_table_group_box_layout.addWidget(self.save_threading_data, 0, 1, 1, 1)
        self.threading_table_group_box_layout.addWidget(self.threading_table, 1, 0, 1, 2, alignment=Qt.AlignCenter)

        ## Status group-box
        self.status_group_box_layout.addWidget(self.status)

        ## go_row
        self.main_box_layout.addLayout(self.go_row_layout, 2, 0, 1, 4)
        # Order of code is significant, and determines visual order of components in GUI
        self.go_row_layout.addWidget(self.clear)
        self.go_row_layout.addWidget(self.always_clear)
        self.go_row_layout.addWidget(self.go_button)
        # Splay go_row widgets apart, stretch gaps to maximum size
        self.go_row_layout.insertStretch(2) # Adds a stretch in "spot 3"

        ### Bonus group-box
        self.bonus_box_layout.addWidget(self.demonstration_group_box, 0, 3, 1, 1)
        self.bonus_box_layout.addWidget(self.progress_bar_group_box, 1, 3, 1, 1)

        ## Demonstrations group-box
        self.demonstration_group_box_layout.addWidget(self.popup_test_button, 0, 0, 1, 1)
        self.demonstration_group_box_layout.addWidget(self.settings_button, 0, 1, 1, 1)
        self.demonstration_group_box_layout.addWidget(self.mutex_test_button, 1, 0, 1, 1)
        self.demonstration_group_box_layout.addWidget(self.autofill_test_button, 1, 1, 1, 1)

        ## Progress Bar group-box
        self.progress_bar_group_box_layout.addWidget(self.values_lassoed, 0, 0, 1, 1, alignment=Qt.AlignCenter)
        self.progress_bar_group_box_layout.addWidget(self.progress_bar, 1, 0, 1, 1, alignment=Qt.AlignHCenter)  # This AlignHCenter makes it such that the bar expands vertically with the GUI, and the above group box stays squished at top
        self.progress_bar_group_box_layout.addWidget(self.pointless_task_button, 2, 0, 1, 1, alignment=Qt.AlignCenter)
        self.progress_bar_group_box_layout.addWidget(self.reset_button, 3, 0, 1, 1, alignment=Qt.AlignCenter)

        ### version_row
        self.version_row_layout.addWidget(self.version, alignment = Qt.AlignCenter)


    # SUPPLEMENTARY FUNCTIONS
    def check_state(self):
        '''
        Change color of QLineEdit border to reflect validator status.

        Parameters
        ----------
        self: Represents the instance of the Class

        Returns
        -------
        None
        '''
        sender = self.sender()
        state = sender.validator().validate(sender.text(), 0)[0]

        if state == QtGui.QValidator.Acceptable:
            color = '#2bb359'  # A nice green
        elif state == QtGui.QValidator.Intermediate:
            color = '#87b7e3'  # A nice blue
        else:
            color = '#911e2e'  # A nice red

        # Perform the actual color change
        sender.setStyleSheet('QLineEdit { border: 1px solid' + f'{color}' + '; border-radius: 2px; margin-top: 0px;}')


    @staticmethod
    def __version_decryption():
        '''
        Performs decryption of version number.
        A version number is generated and encrypted into a data file when this application is compiled. Only an application from the same build as the mentioned data file can decrypt the version number.
        This is done so it is immediately apparent if the runtime files are the correct ones for the GUI being run.
        This is primarily relevant if end-users are overwriting old versions of individual files of the application on their system with files from new versions.

        Possible version values:
        00000001: The application .exe file is not located. This would be because a standalone GUI was run via a direct command-line call (a known action), or post-compile directory structure was lost
        00000000: The application .exe file exists, but the encrypted version.dat file is missing, was not successfully decrypted, or there was an error reading it
        YYYYMMDD: The application is running normally

        Parameters
        ----------
        N/A

        Returns
        -------
        String object containing appropriate version number
        '''
        # If standalone GUI run via direct command
        if not Path('RemoteControl.exe').is_file():
            return '00000001'

        # Grab encrypted version number from version.dat (try to)
        try:
            with open ('version.dat', 'rb') as myfile:
                version_encrypted = myfile.read()

            # Decryption. See make_version.py in scripts\helpers for fuller explanation comments
            exe_remote_control = 'RemoteControl.exe'

            # Generate 32-bit byte-type from CONTENTS of .exe file
            key = hashlib.blake2s(open(exe_remote_control, 'rb').read(), digest_size=32).digest()

            # Encodes to base64
            key_64 = base64.urlsafe_b64encode(key)

            # Actual decryption, is being fed appropriately structured objects
            version_decrypted = Fernet(key_64).decrypt(version_encrypted).decode()
            return version_decrypted

        except:
            # .exe exists, version.dat missing/not successfully decrypted/error reading
            return '00000000'


    @staticmethod
    def exception_catcher(exception, description, trace):
        '''
        Prints exception output with customized formatting.
        Replaces default exception catcher with "sys.excepthook = ApplicationUi.exception_catcher".

        Parameters
        ----------
        exception (exception class (Ags: "type")): Automatically passed in by system
        description (exception instance (Args: "value")): Automatically passed in by system
        trace (traceback object (Args: "traceback")): Automatically passed in by system. Not used

        Returns
        -------
        None
        '''
        # Design format of "custom" exception statement
        traceback_str = ''
        traceback_str += f'{description}: {type(exception).__name__} due to "{exception}"\n'
        tb_curr = description.__traceback__
        while tb_curr is not None:
            traceback_str += f'    File "{tb_curr.tb_frame.f_code.co_filename}", line {tb_curr.tb_lineno} in {tb_curr.tb_frame.f_code.co_name}\n'
            tb_curr = tb_curr.tb_next

        # Print and space traceback away for readability
        print(f'\n{traceback_str}\n\n')


    @staticmethod
    def dark_palette():
        '''
        General GUI components and component attributes color scheme configuration.

        Parameters
        ----------
        N/A

        Returns
        -------
        dark_palette: PyQt5.QtGui.QPalette object
        '''
        dark_palette = QtGui.QPalette()
        dark_palette.setColor(QtGui.QPalette.Window,          QtGui.QColor(43,   43,  48))  # Main dialog background color - deep gray-blue                                                                                  Colorize  rgb(43, 43, 48)
        dark_palette.setColor(QtGui.QPalette.Button,          QtGui.QColor(43,   43,  48))  # Button background color  - deep gray-blue - set to match main dialog background color                                          Colorize  rgb(43, 43, 48)
        dark_palette.setColor(QtGui.QPalette.Base,            QtGui.QColor(25,   25,  25))  # Background color of radio buttons, text fields, checkbox, etc. - Dark gray                                                     Colorize  rgb(25, 25, 25)
        dark_palette.setColor(QtGui.QPalette.WindowText,      QtGui.QColor(212, 212, 212))  # Widget text - Radio button text, check box text, label text - off-white                                                        Colorize  rgb(212, 212, 212)
        dark_palette.setColor(QtGui.QPalette.ButtonText,      QtGui.QColor(212, 212, 212))  # Push Button text - off-white - match to widget text                                                                            Colorize  rgb(212, 212, 212)
        dark_palette.setColor(QtGui.QPalette.Text,            QtGui.QColor(215, 215, 215))  # Special widget text - group box titles, text field default text, user-input text - bright off-white                            Colorize  rgb(215, 215, 215)
        dark_palette.setColor(QtGui.QPalette.Highlight,       QtGui.QColor(135, 183, 227))  # Text highlighting, and widget focus highlights                                                                                 Colorize  rgb(135, 183, 227)
        dark_palette.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor(215, 215, 215))  # Color of text while highlighted - Same as Special widget text, or adjusted to be legible under chosen text highlighting color  Colorize  rgb(215, 215, 215)
        return dark_palette


    # FUNCTIONAL METHODS
    # [General group-box]
    def update_status_callback(self, text):
        '''
        Display text in status widget in GUI.
        Updates/refreshes GUI.
        Can be passed as a function argument to get to other modules, allowing other modules to update the GUI
        without needing to import this module (offloads non-GUI work from GUI module + avoids circular imports).

        Parameters
        ----------
        self: Represents the instance of the Class
        text (string): Text to print in status text box

        Returns
        -------
        None
        '''
        self.status.appendHtml(text)
        QtWidgets.QApplication.processEvents()


    def clear_status(self):
        '''
        Clear text in status widget in GUI.
        Updates/refreshes GUI.

        Parameters
        ----------
        self: Represents the instance of the Class

        Returns
        -------
        None
        '''
        self.status.clear()
        QtWidgets.QApplication.processEvents()


    def click_go(self):
        '''
        Make clicking the 'Go!' button execute the primary functionality from among the following:
        --> Print text from Set Text widget to status widget
        --> Configure text according to Configure Text widget
        --> Use Threading Table widget option
        --> Save printed text to an output .txt file
        These are demonstrations of output capabilities, example organization and syntax, logging, etc.

        Parameters
        ----------
        self: Represents the instance of the Class

        Returns
        -------
        None
        '''
        # Check for user-defined GUI settings
        # Check for empty user input
        if self.always_clear.isChecked():
            self.clear_status()

        # Threading table not selected
        if not self.use_threading_table.isChecked():

            if self.set_text.text() == '':
                self.update_status_callback('<p style="font-size:11px; color:#DADADA;">' + 'No text specified!<br>' + '</p>')
                return

            text = self.set_text.text()

            regular = True if self.radio_button_regular.isChecked() else False
            mirrored = True if self.radio_button_mirrored.isChecked() else False

            # Catch missing user input
            if not regular and not mirrored:
                self.update_status_callback('<p style="font-size:11px; color:#DADADA;">' + 'No text configuration selected!<br>' + '</p>')
                return

            if self.set_text.text() == '':
                self.update_status_callback('<p style="font-size:11px; color:#DADADA;">' + 'No set value specified!<br>' + '</p>')
                return

            # Apply mirroring, if selected
            if mirrored:
                text = text[::-1]

            # Proceed with operations
            self.update_status_callback('<p style="font-size:11px; color:#DADADA;">' + '+++++++++++++++++++++++++++++<br>+++ JACKING INTO CENTRAL COMMAND +++<br>+++++++++++++++++++++++++++++<br><br>' + '</p>')
            start_time = datetime.now()

            # Perform the printing - using a separate module for demonstrative purposes, even though a pure GUI task
            self.functionality_class.print_text(text)  # Separate module method not required for pure GUI actions

            self.update_status_callback('<p style="font-size:11px; color:#DADADA;">' + f'<br><br>+++++++++++++++++<br>+++ TASK COMPLETE +++<br>+++++++++++++++++<br><br>Time taken: {datetime.now() - start_time}<br><br><br><br><br><br>' + '</p>')

        # "Use threading table?" is selected
        elif not self.save_threading_data.isChecked():
            # Grab and curate user-input Threading Table data
            threading_table_text_list, threading_table_times_list = ThreadingTableDataWrangler.threading_table_data_wrangler(self.update_status_callback, self.threading_table_text_widgets, self.threading_table_time_widgets)
            # Catch data curation error messages thrown from within threading_table_data_wrangler module. Only checking bool of one returned variable for efficiency
            if threading_table_text_list == True:
                return

            self.update_status_callback('<p style="font-size:11px; color:#DADADA;">' + '+++++++++++++++++++++++++++++<br>+++ JACKING INTO CENTRAL COMMAND +++<br>+++++++++++++++++++++++++++++<br><br>' + '</p>')
            start_time = datetime.now()

            # Create QThread object
            self.threading_table_thread = QThread()

            # Adjust QThread .run() function
            # Using lambda as a workaround to entirely subclassing the run() method that .start() calls
            # lambda grabs a snapshot of what the argument provided is, at the time of calling. The passed objects become static
            # This can be problematic if the passed object needs to be changed later, for example. To prevent this if relevant, pass start_time=start_time, number = number, etc. which passes the full object
            self.threading_table_thread.run = lambda: self.functionality_class.threading_table_handler(start_time, threading_table_text_list, threading_table_times_list)

            # Disable specific widgets for safety
            # Buttons
            self.go_button.setEnabled(False)
            self.use_threading_table.setEnabled(False)
            self.save_threading_data.setEnabled(False)
            # Toggling threading table QLineEdit cells instead of entire QTableWidget to preserve threading table scrolling functionality in the instance of too many rows
            for widget in self.threading_table_text_widgets: widget.setEnabled(False)
            for widget in self.threading_table_time_widgets: widget.setEnabled(False)

            # Re-enable widgets when threaded method completes
            # Buttons
            self.threading_table_thread.finished.connect(lambda: self.go_button.setEnabled(True))
            self.threading_table_thread.finished.connect(lambda: self.use_threading_table.setEnabled(True))
            self.threading_table_thread.finished.connect(lambda: self.save_threading_data.setEnabled(True))
            # Toggling threading table QLineEdit cells instead of entire QTableWidget to preserve threading table scrolling functionality
            for widget in self.threading_table_text_widgets: self.threading_table_thread.finished.connect(lambda widget=widget: widget.setEnabled(True))  # widget=widget captures iterable into the lambda
            for widget in self.threading_table_time_widgets: self.threading_table_thread.finished.connect(lambda widget=widget: widget.setEnabled(True))

            # Execute the thread
            self.threading_table_thread.start()

        # "Use threading table?" AND "Save to .txt file?" are selected
        else:
            # Grab and curate user-input Threading Table data
            threading_table_text_list, threading_table_times_list = ThreadingTableDataWrangler.threading_table_data_wrangler(self.update_status_callback, self.threading_table_text_widgets, self.threading_table_time_widgets)

            # Catch data curation error messages thrown from within threading_table_dat_wrangler module. Only checking bool of one returned variable for efficiency
            if threading_table_text_list == True:
                return

            self.update_status_callback('<p style="font-size:11px; color:#DADADA;">' + '+++++++++++++++++++++++++++++<br>+++ JACKING INTO CENTRAL COMMAND +++<br>+++++++++++++++++++++++++++++<br><br>' + '</p>')
            start_time = datetime.now()

            # Create QThread object
            self.threading_table_thread = QThread()

            # Adjust QThread .run() function
            # Using lambda as a workaround to entirely subclassing the run() method that .start() calls
            # lambda grabs a snapshot of what the argument provided is, at the time of calling. The passed objects become static
            # This can be problematic if the passed object needs to be changed later, for example. To prevent this if relevant, pass start_time=start_time, number = number, etc. which passes the full object
            self.threading_table_thread.run = lambda: self.functionality_class.fancy_threading_table_handler(start_time, threading_table_text_list, threading_table_times_list)

            # Disable specific widgets for safety
            # Buttons
            self.go_button.setEnabled(False)
            self.use_threading_table.setEnabled(False)
            self.save_threading_data.setEnabled(False)
            # Toggling threading table QLineEdit cells instead of entire QTableWidget to preserve threading table scrolling functionality in the instance of too many rows
            for widget in self.threading_table_text_widgets: widget.setEnabled(False)
            for widget in self.threading_table_time_widgets: widget.setEnabled(False)

            # Re-enable widgets when threaded method completes
            # Buttons
            self.threading_table_thread.finished.connect(lambda: self.go_button.setEnabled(True))
            self.threading_table_thread.finished.connect(lambda: self.use_threading_table.setEnabled(True))
            self.threading_table_thread.finished.connect(lambda: self.save_threading_data.setEnabled(True))
            # Toggling threading table QLineEdit cells instead of entire QTableWidget to preserve threading table scrolling functionality
            for widget in self.threading_table_text_widgets: self.threading_table_thread.finished.connect(lambda widget=widget: widget.setEnabled(True))  # widget=widget captures iterable into the lambda
            for widget in self.threading_table_time_widgets: self.threading_table_thread.finished.connect(lambda widget=widget: widget.setEnabled(True))

            # Execute the thread
            self.threading_table_thread.start()


    # [Bonus group-box]
    def popup_demonstration(self):
        '''
        Call self.popup_demonstration_window().
        Performing under a separate method in order to take advantage of PyQt5 dialog .exec() blocking for print timing purposes.

        Parameters
        ----------
        self: Represents the instance of the Class

        Returns
        -------
        None
        '''
        self.update_status_callback('<p style="font-size:11px; color:#DADADA;">' + 'Pop-Up Demonstration<br>---------------------------<br>' + '</p>')
        self.popup_demonstration_window()  # .exec() used, so blocks until closed
        self.update_status_callback('<p style="font-size:11px; color:#DADADA;">' + 'Complete<br><br>---------------------------<br><br>' + '</p>')


    def popup_demonstration_window(self):
        '''
        Dialog window with interactive behavior to demonstrate exception pop-up user experience.

        Parameters
        ----------
        self: Represents the instance of the Class

        Returns
        -------
        None
        '''
        # "#" represents reverse nested level
        ## Dialog Window
        self.popup_demonstration_dialog = QtWidgets.QDialog(self)
        self.popup_demonstration_dialog.setWindowTitle('Pop-Up Demonstration')
        self.popup_demonstration_dialog.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        self.popup_demonstration_dialog_layout = QtWidgets.QGridLayout()
        self.popup_demonstration_dialog.setLayout(self.popup_demonstration_dialog_layout)

        # Widgets
        self.popup_label = QtWidgets.QLabel(
            'The application is performing a task.\n'
            'If the task is successful, the status log will be updated accordingly.\n'
            'If the task fails, a visually engaging pop-up dialog will open in addition to the status log being updated accordingly.\n'
            '\n'
            'Does the task succeed or fail?\n', alignment = Qt.AlignCenter
        )
        self.popup_label.setStyleSheet('QLabel { background-color : ; color : #6b6b6b; }')
        self.task_succeeds_button = QtWidgets.QPushButton('<Task succeeds>')
        self.task_fails_button = QtWidgets.QPushButton('<Task fails>')
        self.task_succeeds_button.clicked.connect(lambda: self.functionality_class.popup_demonstration(True))
        self.task_fails_button.clicked.connect(lambda: self.functionality_class.popup_demonstration(False))

        # Construct dialog window
        self.popup_demonstration_dialog_layout.addWidget(self.popup_label, 0, 0, 1, 2, alignment=Qt.AlignCenter)
        self.popup_demonstration_dialog_layout.addWidget(self.task_succeeds_button, 1, 0, 1, 1, alignment=Qt.AlignCenter)
        self.popup_demonstration_dialog_layout.addWidget(self.task_fails_button, 1, 1, 1, 1, alignment=Qt.AlignCenter)

        # Using exec to block main window so "Complete" prints only after closed
        self.popup_demonstration_dialog.exec()


    def settings_dialog_window(self):
        '''
        Dialog window demonstrating "memory" functionality.
        Retrieves and displays current GUI settings upon opening.
        Settings chosen will be reflected in GUI, and preserved when settings dialog is closed.

        Parameters
        ----------
        self: Represents the instance of the Class

        Returns
        -------
        None
        '''
        # "#" represents reverse nested level
        ### Dialog Window
        self.settings_dialog = QtWidgets.QDialog(self)
        self.settings_dialog.setWindowTitle('Saveable Settings')
        self.settings_dialog.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        self.settings_dialog_layout = QtWidgets.QGridLayout()
        self.settings_dialog.setLayout(self.settings_dialog_layout)

        ## "Use threading table?" group-box
        self.settings_1_group_box = QtWidgets.QGroupBox('"Use threading table?"', alignment=Qt.AlignCenter)  # Centers group box title
        self.settings_1_group_box.setStyleSheet('QGroupBox { font-size: 11px; }')
        self.settings_1_group_box.setFixedSize(114, 109)
        self.settings_1_group_box_layout = QtWidgets.QVBoxLayout()
        self.settings_1_group_box.setLayout(self.settings_1_group_box_layout)
        # Widgets
        self.radio_button_unchecked = QtWidgets.QRadioButton('Unchecked')
        self.radio_button_checked = QtWidgets.QRadioButton('Checked')
        self.settings_1_group_box_layout.addWidget(self.radio_button_unchecked)
        self.settings_1_group_box_layout.addWidget(self.radio_button_checked)
        self.radio_button_unchecked.clicked.connect(lambda: self.radio_button_click())  # 'clicked' emits only on user-interaction, unlike "toggled"
        self.radio_button_checked.clicked.connect(lambda: self.radio_button_click())

        # "Save to .txt file?" group-box
        self.settings_2_group_box = QtWidgets.QGroupBox('"Save to .txt file?"', alignment=Qt.AlignCenter)
        self.settings_2_group_box.setStyleSheet('QGroupBox { font-size: 11px; }')
        self.settings_2_group_box.setFixedSize(133, 109)
        self.settings_2_group_box_layout = QtWidgets.QVBoxLayout()
        self.settings_2_group_box.setLayout(self.settings_2_group_box_layout)
        # Widgets
        self.settings_dropdown = QtWidgets.QComboBox()
        self.settings_dropdown.addItem('Unchecked')
        self.settings_dropdown.addItem('Checked')
        self.settings_2_group_box_layout.addWidget(self.settings_dropdown)
        self.settings_dropdown.activated.connect(lambda: self.drop_down_click())  # 'activated' emits only on user-interaction. Not programmatic selection

        ## Settings Status group-box
        self.settings_status_group_box = QtWidgets.QGroupBox('Settings Status', alignment=Qt.AlignCenter)
        self.settings_status_group_box.setStyleSheet('QGroupBox { font-size: 11px; }')
        self.settings_status_group_box.setFixedSize(203, 109)
        self.settings_status_group_box_layout = QtWidgets.QVBoxLayout()
        self.settings_status_group_box.setLayout(self.settings_status_group_box_layout)
        # Widgets
        self.settings_status = QtWidgets.QPlainTextEdit()
        self.settings_status.setStyleSheet('QPlainTextEdit {background-color: rgb(0, 0, 0); }')
        self.settings_status.setReadOnly(True)
        self.settings_status.setPlaceholderText('Settings change log will display in this box')
        self.settings_status_group_box_layout.addWidget(self.settings_status)

        ## Settings Label
        self.settings_label = QtWidgets.QLabel('☆   Options selected in this window will be reflected in the main window.\n☆   Accurate live settings will always be reflected upon opening this window.')
        self.settings_label.setStyleSheet('QLabel { background-color : ; color : #6b6b6b; }')

        # Construct dialog window
        self.settings_dialog_layout.addWidget(self.settings_1_group_box, 0, 0, 1, 1, alignment=Qt.AlignLeft)
        self.settings_dialog_layout.addWidget(self.settings_2_group_box, 0, 1, 1, 1, alignment=Qt.AlignLeft)
        self.settings_dialog_layout.addWidget(self.settings_status_group_box, 0, 2, 1, 1, alignment=Qt.AlignLeft)
        self.settings_dialog_layout.addWidget(self.settings_label, 1, 0, 1, 3, alignment=Qt.AlignLeft)

        # Functionality
        # Retrieve live settings
        use = True if self.use_threading_table.isChecked() else False
        save = True if self.save_threading_data.isChecked() else False

        # Display live settings
        if not use:
            self.radio_button_unchecked.setChecked(True)
        else:
            self.radio_button_checked.setChecked(True)

        if not save:
            self.settings_dropdown.setCurrentText('Unchecked')
        else:
            self.settings_dropdown.setCurrentText('Checked')

        # Using .open() to directly engage setWindowModality(), making it a modal window --> other windows will not be accessible until this window is closed
        self.settings_dialog.open()


    def radio_button_click(self):
        '''
        Interface with top-level GUI window when radio buttons are clicked.

        Parameters
        ----------
        self: Represents the instance of the Class

        Returns
        -------
        None
        '''
        if self.radio_button_unchecked.isChecked():
            # Send checkbox change
            self.use_threading_table.setChecked(False)  # Would be method from separate module if not a pure GUI action
            self.update_settings_status('<p style="font-size:10px; color:#00DF00;">' + '⤑ ' + '<span style="color:#DADADA">' + '"Use threading table?" unchecked' + '</p>')

        if self.radio_button_checked.isChecked():
            # Send checkbox change
            self.use_threading_table.setChecked(True)
            self.update_settings_status('<p style="font-size:10px; color:#00DF00;">' + '⤑ ' + '<span style="color:#DADADA">' + '"Use threading table?" checked' + '</p>')


    def drop_down_click(self):
        '''
        Interface with top-level GUI window when drop-down widget is used.

        Parameters
        ----------
        self: Represents the instance of the Class

        Returns
        -------
        None
        '''
        if self.settings_dropdown.currentText() == 'Unchecked':
            # Send combobox change
            self.save_threading_data.setChecked(False)
            self.update_settings_status('<p style="font-size:10px; color:#00DF00;">' + '⤑ ' + '<span style="color:#DADADA">' + '"Save to .txt file?" unchecked' + '</p>')

        if self.settings_dropdown.currentText() == 'Checked':
            # Send combobox change
            self.save_threading_data.setChecked(True)
            self.update_settings_status('<p style="font-size:10px; color:#00DF00;">' + '⤑ ' + '<span style="color:#DADADA">' + '"Save to .txt file?" checked' + '</p>')


    def update_settings_status(self, text):
        '''
        Display text in settings status widget in settings dialog window.
        Updates/refreshes GUI.

        Parameters
        ----------
        self: Represents the instance of the Class
        text (string): Text to print in settings status text box

        Returns
        -------
        None
        '''
        self.settings_status.appendHtml(text)
        QtWidgets.QApplication.processEvents()


    def autofill_demonstration_window(self):
        '''
        Dialog window with interactive behavior to demonstrate autofill functionality.

        Parameters
        ----------
        self: Represents the instance of the Class

        Returns
        -------
        None
        '''
        # Dialog Window
        self.autofill_demonstration_dialog = QtWidgets.QDialog(self)
        self.autofill_demonstration_dialog.setWindowTitle('Autofill Demonstration')
        self.autofill_demonstration_dialog.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        self.autofill_demonstration_dialog_layout = QtWidgets.QGridLayout()
        self.autofill_demonstration_dialog.setLayout(self.autofill_demonstration_dialog_layout)

        # Widgets
        self.autofill_label = QtWidgets.QLabel(
            'Below is a text box. The text box know five words:\n'
            '\n'
            'Apple, Tennis, Hiking, Pencil, Book\n'
            '\n'
            'The autofill functionality matches exact results, only.'
            '\n'
            'Try entering some characters!\n', alignment = Qt.AlignCenter
        )
        self.autofill_label.setStyleSheet('QLabel { background-color : ; color : #6b6b6b; }')
        self.autofill_text_box = QtWidgets.QLineEdit()
        self.words = ['Apple', 'Tennis', 'Hiking', 'Pencil', 'Book']
        self.completer = QtWidgets.QCompleter(self.words)
        self.autofill_text_box.setCompleter(self.completer)

        # Construct dialog window
        self.autofill_demonstration_dialog_layout.addWidget(self.autofill_label, 0, 0, 1, 1, alignment=Qt.AlignCenter)
        self.autofill_demonstration_dialog_layout.addWidget(self.autofill_text_box, 1, 0, 1, 1, alignment=Qt.AlignCenter)

        # Using .open() to directly engage setWindowModality(), making it a modal window --> other windows will not be accessible until this window is closed
        self.autofill_demonstration_dialog.open()


    def update_progress_bar_callback(self, iteration, list, reset = False):
        '''
        Manages progress bar in GUI. Based on simple iteration through a list.
        Updates/refreshes GUI.
        Can be passed as a function argument to get to other modules, allowing other modules to update the progress bar
        without needing to import this module (offloads non-GUI work from GUI module + avoids circular imports).

        Parameters
        ----------
        self: Represents the instance of the Class
        iteration (integer): Current iterative step. i = zero is accommodated
        list (list): List being looped over. Determines total iteration count

        Returns
        -------
        None
        '''
        if reset:
            self.progress_bar.setValue(0)
            self.values_lassoed.setText(f'Pointless items completed: 0/0 (0%)')
            return

        # Normalize progress to be out of 100 steps
        # Integer percentages may jump >+1 depending on divisibility
        # Will always perceive 100% with the final iteration
        self.progress_bar.setValue(int((100*(iteration+1))/(len(list))))
        self.values_lassoed.setText(f'Pointless items completed: {iteration+1}/{len(list)} ({int((100*(iteration+1))/(len(list)))}%)')
        QtWidgets.QApplication.processEvents()


    def pointless_task(self):
        '''
        Arbitrary looping through a list for demonstrating the use of update_progress_bar_callback method, and progress_bar object.

        Parameters
        ----------
        self: Represents the instance of the Class

        Returns
        -------
        None
        '''
        self.pointless_task_button.setEnabled(False)
        self.reset_button.setEnabled(False)
        pointless_list = [item for item in range(4)]
        for i in range(len(pointless_list)):
            time.sleep(0.5)
            self.update_progress_bar_callback(i, pointless_list)

        self.reset_button.setEnabled(True)
        self.pointless_task_button.setEnabled(True)


# Initialize the GUI
if __name__ == '__main__':
    # Create an instance of QApplication
    application = QtWidgets.QApplication(sys.argv)
    application.setStyle('Fusion')
    application.setPalette(ApplicationUi.dark_palette())

    # Setting icon here applies to all windows (as opposed to setting within each window's code)
    application.setWindowIcon(QtGui.QIcon('planet_icon.ico'))

    # Override built-in exception handler and print function
    # Connect custom ApplicationUi.exception_catcher function to built-in exception handler
    sys.excepthook = ApplicationUi.exception_catcher

    # Show the application's GUI
    view = ApplicationUi()
#    view.resize(1001, 635)
    view.show()

    # Execute the application's main loop
    sys.exit(application.exec())  # .exec() blocks until app quits (event loop is terminated) - then returns and sys.exit can execute
