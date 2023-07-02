import sys
if sys.version_info < (3, 10):
    print('You need a Python version >= 3.10')
    exit(1)
import os
import subprocess
from PySide6.QtCore import QSize
from PySide6.QtGui import QAction, QIcon, QKeySequence,  QTextCursor, QColor
from PySide6.QtWidgets import (QApplication, QWidget, QMainWindow, QFileDialog, QMessageBox,
                               QDialog, QTextBrowser,
                               QVBoxLayout, QHBoxLayout,
                               QPushButton, QLabel, QLineEdit, QListWidget, QListWidgetItem, QDialogButtonBox,
                               QToolBar, QStatusBar)

basedir = os.path.dirname(__file__)

try:
    from ctypes import windll  # Only exists on Windows.
    myappid = 'mycompany.myproduct.subproduct.version'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

# Docs
MANUAL = os.path.join(basedir, "docs", 'manual.html')
LICENSE = os.path.join(basedir, "docs", 'license.html')
ABOUT = os.path.join(basedir, "docs", 'about.html')

# Icons
APP_ICON = os.path.join(basedir, "icons", 'pysigvi.ico')
OPEN_FILE_ICON = os.path.join(basedir, "icons", 'blue-folder-open-document.png')
OPEN_FOLDER_ICON = os.path.join(basedir, "icons", 'blue-folder-open-document-text.png')
CHECK_ICON = os.path.join(basedir, "icons", 'ui-check-box.png')
EXIT_ICON = os.path.join(basedir, "icons", 'door-open-out.png')


class ManualDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("PySigViManual")
        self.setMinimumSize(QSize(648, 648))

        button_ok = QDialogButtonBox.StandardButton.Ok
        self.buttonBox = QDialogButtonBox(button_ok)
        self.buttonBox.accepted.connect(self.accept)
        self.manual = QTextBrowser()
        self.manual.setOpenExternalLinks(True)
        try:
            with open(MANUAL) as _:
                self.manual.append(_.read())
        except FileNotFoundError:
            self.manual.append('Try to use it...')
        cursor = self.manual.textCursor()
        cursor.movePosition(QTextCursor.Start)
        self.manual.setTextCursor(cursor)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.manual)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Signatures Verify')  # Main Window
        self.setMinimumSize(QSize(640, 480))
        # Labels
        file_label = QLabel('File to verify: ')  # File to verify
        sign_label = QLabel('Signatures')  # Signatures to verify
        check_label = QLabel('Check')  # Result

        # Actions
        self.action_add_file = QAction(QIcon(OPEN_FILE_ICON), '&Open File', self)
        self.action_add_file.setShortcut(QKeySequence("Ctrl+F"))
        self.action_add_file.setStatusTip('Open the file to verify')
        self.action_add_file.triggered.connect(self.add_file)
        self.action_add_signatures = QAction(QIcon(OPEN_FOLDER_ICON), '&Add Signatures', self)
        self.action_add_signatures.setShortcut(QKeySequence("Ctrl+S"))
        self.action_add_signatures.setStatusTip('Add signatures to verify the file')
        self.action_add_signatures.triggered.connect(self.add_signature)
        self.action_remove_signatures = QAction('Clear S&ignatures', self)
        self.action_remove_signatures.setStatusTip('Remove all the signatures')
        self.action_remove_signatures.triggered.connect(self.remove_signature)
        self.action_remove_signatures.setEnabled(False)
        self.action_check_signatures = QAction(QIcon(CHECK_ICON), '&Check Signatures', self)
        self.action_check_signatures.setShortcut(QKeySequence("Ctrl+K"))
        self.action_check_signatures.setStatusTip('Check all the signatures')
        self.action_check_signatures.triggered.connect(self.check_signatures)
        self.action_check_signatures.setEnabled(False)
        self.action_check_clear = QAction('Clear C&heck', self)
        self.action_check_clear.setStatusTip('Clear the Check panel')
        self.action_check_clear.triggered.connect(self.check_clear)
        self.action_check_clear.setEnabled(False)
        self.action_open_manual = QAction('&Manual', self)
        self.action_open_manual.setStatusTip('Manual and instructions')
        self.action_open_manual.setShortcut(QKeySequence("F1"))
        self.action_open_manual.triggered.connect(self.open_manual)
        self.action_open_license = QAction('&License', self)
        self.action_open_license.setStatusTip('license')
        self.action_open_license.triggered.connect(self.open_license)
        self.action_open_about = QAction('&About', self)
        self.action_open_about.setStatusTip('About this software')
        self.action_open_about.triggered.connect(self.open_about)
        self.action_exit_program = QAction(QIcon(EXIT_ICON), '&Exit', self)
        self.action_exit_program.setShortcut(QKeySequence("Ctrl+Q"))
        self.action_exit_program.setStatusTip('Close the application')
        self.action_exit_program.triggered.connect(self.exit_program)
        # Widgets
        self.file_lineedit = QLineEdit()
        self.file_lineedit.setPlaceholderText("Enter file name with url.")
        self.sign_list = QListWidget()
        self.check_list = QListWidget()
        # Buttons
        self.button_add_file = QPushButton('...')
        self.button_add_file.clicked.connect(self.action_add_file.trigger)
        self.button_add_signatures = QPushButton('Add Signatures')
        self.button_add_signatures.clicked.connect(self.action_add_signatures.trigger)
        self.button_remove_signatures = QPushButton('Remove Signatures')
        self.button_remove_signatures.clicked.connect(self.action_remove_signatures.trigger)
        self.button_remove_signatures.setEnabled(False)
        self.action_remove_signatures.enabledChanged.connect(self.button_remove_signatures.setEnabled)
        self.button_check_signatures = QPushButton('Check Signatures')
        self.button_check_signatures.clicked.connect(self.action_check_signatures.trigger)
        self.button_check_signatures.setEnabled(False)
        self.action_check_signatures.enabledChanged.connect(self.button_check_signatures.setEnabled)
        self.button_check_clear = QPushButton('Clear Check')
        self.button_check_clear.clicked.connect(self.action_check_clear.trigger)
        self.button_check_clear.setEnabled(False)
        self.action_check_clear.enabledChanged.connect(self.button_check_clear.setEnabled)
        # Menu
        menu = self.menuBar()
        menu_file = menu.addMenu("&File")
        menu_file.addAction(self.action_add_file)
        menu_file.addSeparator()
        menu_file.addAction(self.action_exit_program)
        menu_tools = menu.addMenu("&Tools")
        menu_tools.addAction(self.action_add_signatures)
        menu_tools.addAction(self.action_remove_signatures)
        menu_tools.addSeparator()
        menu_tools.addAction(self.action_check_signatures)
        menu_tools.addAction(self.action_check_clear)
        menu_help = menu.addMenu("&Help")
        menu_help.addAction(self.action_open_manual)
        menu_help.addAction(self.action_open_license)
        menu_help.addAction(self.action_open_about)
        # Toolbar
        toolbar = QToolBar('Main Toolbar')  # Tool Bar
        toolbar.addAction(self.action_add_file)
        toolbar.addAction(self.action_add_signatures)
        toolbar.addAction(self.action_check_signatures)
        self.addToolBar(toolbar)
        # Layout
        layout_file = QHBoxLayout()  # File layout
        layout_file.addWidget(file_label)
        layout_file.addWidget(self.file_lineedit)
        layout_file.addWidget(self.button_add_file)
        layout_signatures = QVBoxLayout()  # Signatures layout
        layout_signatures.addWidget(sign_label)
        layout_signatures.addWidget(self.sign_list)
        layout_check = QVBoxLayout()  # Check layout
        layout_check.addWidget(check_label)
        layout_check.addWidget(self.check_list)
        layout_button_signatures = QHBoxLayout()  # Signatures layout
        layout_button_signatures.addWidget(self.button_add_signatures)
        layout_button_signatures.addWidget(self.button_remove_signatures)
        layout_button_signatures.insertStretch(0)
        layout_button_check = QHBoxLayout()  # Check layout
        layout_button_check.addWidget(self.button_check_signatures)
        layout_button_check.addWidget(self.button_check_clear)
        layout_button_check.insertStretch(0)
        layout = QVBoxLayout()  # Main layout
        layout.addLayout(layout_file)
        layout.addLayout(layout_signatures)
        layout.addLayout(layout_button_signatures)
        layout.addLayout(layout_check)
        layout.addLayout(layout_button_check)
        # Status bar
        self.setStatusBar(QStatusBar(self))
        # Central Widget
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def add_file(self):
        self.file_lineedit.setText(QFileDialog.getOpenFileName(self, 'Select file')[0])
        if self.file_lineedit.text() and self.sign_list.count():
            self.action_check_signatures.setEnabled(True)

    def add_signature(self):
        for signature in QFileDialog.getOpenFileNames(self, 'Select signatures')[0]:
            self.sign_list.addItem(signature)
        if self.sign_list.count():
            self.action_remove_signatures.setEnabled(True)
            if self.file_lineedit.text():
                self.action_check_signatures.setEnabled(True)

    def remove_signature(self):
        self.sign_list.clear()
        self.action_remove_signatures.setEnabled(False)
        self.action_check_signatures.setEnabled(False)

    def check_signatures(self):
        self.check_clear()
        signatures_number = self.sign_list.count()
        failed_signatures_count = 0
        for index in range(signatures_number):
            result = subprocess.run(['gpg', '--verify',
                                     self.sign_list.item(index).text(),
                                     self.file_lineedit.text()],
                                    stderr=subprocess.PIPE, text=True)
            check_list_item = QListWidgetItem(result.stderr, self.check_list)
            if result.returncode == 0:
                check_list_item.setBackground(QColor('green'))
            else:
                failed_signatures_count += 1
                check_list_item.setBackground(QColor('red'))
        if failed_signatures_count > 0:
            QMessageBox.critical(self, 'Signature Failed',
                                 f'{failed_signatures_count} / {signatures_number} not verified!')
        if signatures_number:
            self.action_check_clear.setEnabled(True)

    def check_clear(self):
        self.check_list.clear()
        self.action_check_clear.setEnabled(False)

    def open_manual(self):
        man = ManualDialog(self)
        man.exec()

    def open_license(self):
        try:
            with open(LICENSE) as _:
                QMessageBox.about(self, 'License', _.read())
        except FileNotFoundError:
            QMessageBox.about(self, 'License', 'GPL v3.0')
    
    def open_about(self):
        try:
            with open(ABOUT) as _:
                QMessageBox.about(self, 'About', _.read())
        except FileNotFoundError:
            QMessageBox.about(self, 'About', 'About PySigVi...\nabout.html\nFile Not Found!')

    @staticmethod
    def exit_program():
        app.quit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(APP_ICON))
    window = MainWindow()
    window.show()
    app.exec()
