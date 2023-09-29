import json

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QTextCursor, QColor, QTextCharFormat, QAction
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPlainTextEdit, QListWidget, QInputDialog, QMenu, \
    QMenuBar, QListWidgetItem, QPushButton, QDialog, QLabel, QLineEdit, QTextBrowser, QHBoxLayout, QSplitter


from ttp import ttp
from ttpbuilder.Library.util import name_selection, generate_template, highlight_text


class TTPGuiUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initialize_theme("dark")
        self.initUI()

    def initUI(self):
        # Create QVBoxLayout
        main_layout = QVBoxLayout()
        self.setWindowTitle("TTP Builder")

        # Create Menu Bar
        menubar = QMenuBar(self)
        file_menu = menubar.addMenu("File")
        # Create Help Menu
        help_menu = menubar.addMenu("Help")

        # Add Basics action
        basics_action = QAction("Basics", self)
        basics_action.triggered.connect(self.open_basics_dialog)
        help_menu.addAction(basics_action)

        # Add TTP Help action
        ttp_help_action = QAction("TTP Help", self)
        ttp_help_action.triggered.connect(self.show_ttp_help)
        help_menu.addAction(ttp_help_action)

        # Add About action
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

        # Add Reset action
        reset_action = QAction("Reset", self)
        reset_action.triggered.connect(self.reset_app)
        file_menu.addAction(reset_action)

        main_layout.addWidget(menubar)

        # Create QHBoxLayout
        control_layout = QHBoxLayout()

        # Create QPlainTextEdit and make it read-only after initial text is entered
        self.text_edit = QPlainTextEdit()
        self.text_edit.textChanged.connect(self.make_readonly)
        self.text_edit.setMinimumHeight(600)

        # Create QListWidget
        self.list_widget = QListWidget()
        # Event to detect QListWidget item clicked
        self.list_widget.itemClicked.connect(self.customize_ttp_entry)

        # Create and add Labels and Widgets to the splitter
        text_area = QWidget()
        text_layout = QVBoxLayout()
        text_layout.addWidget(QLabel('Paste text here (Do Not Type):'))
        text_layout.addWidget(self.text_edit)
        text_area.setLayout(text_layout)

        list_area = QWidget()
        list_layout = QVBoxLayout()
        list_layout.addWidget(QLabel('Variables:'))
        list_layout.addWidget(self.list_widget)
        list_area.setLayout(list_layout)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(text_area)
        splitter.addWidget(list_area)

        # Set the initial proportions; the numbers are the 'stretch factors'
        splitter.setSizes([300, 100])

        main_layout.addWidget(splitter)

        # Generate Template Button
        self.generate_button = QPushButton('Generate Template', self)
        self.generate_button.clicked.connect(lambda: generate_template(self))

        main_layout.addWidget(self.generate_button)

        # Set layout
        self.setLayout(main_layout)

        # Context menu
        self.text_edit.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.text_edit.customContextMenuRequested.connect(self.show_context_menu)
        self.text_edit.selectionChanged.connect(self.restrict_to_single_line)

        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.show_list_context_menu)

    def open_basics_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('Basics - How to Use')
        layout = QVBoxLayout()

        text_browser = QTextBrowser()
        text_browser.setMinimumWidth(500)

        how_to_text = '''
<ol>
        <li><strong>Paste Sample Data:</strong> Open the app and paste your sample text data into the text editor on the left-hand side.</li>
        <li><strong>Reset:</strong> Once you past data in the text area, you cannot edit it. Use File/Reset to start over</li>
        <li><strong>Named Selections:</strong> After pasting text data, highlight a section of the text that you want to be a variable in the TTP template. Right-click and choose "Create Named Selection".</li>
        <li><strong>Variable List:</strong> This will populate the ListWidget on the right with your identified variables. You can edit or remove these as necessary.</li>
        <li><strong>Generate Template:</strong> Once you've highlighted all variables of interest, click on the 'Generate Template' button at the bottom to create the TTP template.</li>
    </ol>
            '''
        text_browser.setMarkdown(how_to_text)

        layout.addWidget(text_browser)

        dialog.setLayout(layout)
        dialog.exec()


    def show_ttp_help(self):
        ttp_help_dialog = QDialog(self)
        ttp_help_dialog.setWindowTitle("TTP Help")

        layout = QVBoxLayout()

        web_view = QWebEngineView()
        web_view.setUrl(QUrl("https://ttp.readthedocs.io/en/latest/"))

        layout.addWidget(web_view)
        ttp_help_dialog.setLayout(layout)

        ttp_help_dialog.exec()

    def show_about_dialog(self):
        about_dialog = QDialog(self)
        about_dialog.setWindowTitle("About")

        layout = QVBoxLayout()

        text_browser = QTextBrowser()
        text_browser.setHtml("Author: Scott Peterman <br> Github: <a href='https://github.com/scottpeterman'>Github Link</a>")
        text_browser.setOpenExternalLinks(True)
        layout.addWidget(text_browser)
        about_dialog.setLayout(layout)

        about_dialog.exec()

    def initialize_theme(self, theme="light"):
        # Load the theme from a config file, or database, etc.
        # This is just a dummy example; your actual loading logic will vary.
        self.current_theme = theme

    def show_list_context_menu(self, pos):
        item = self.list_widget.itemAt(pos)
        if item:
            context_menu = QMenu(self)
            delete_action = QAction("Delete", self)
            delete_action.triggered.connect(lambda: self.delete_item(item))
            context_menu.addAction(delete_action)
            context_menu.exec(self.list_widget.mapToGlobal(pos))

    def delete_item(self, item):
        # Unhighlight source text
        start = item.selection_start
        end = item.selection_end

        cursor = self.text_edit.textCursor()
        cursor.setPosition(start, QTextCursor.MoveMode.MoveAnchor)
        cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)

        self.text_edit.setReadOnly(False)
        highlight_text(self, start, end, default=True)
        self.text_edit.setReadOnly(True)

        # Remove item from QListWidget
        row = self.list_widget.row(item)
        self.list_widget.takeItem(row)

    def restrict_to_single_line(self):
        cursor = self.text_edit.textCursor()
        start = cursor.selectionStart()
        end = cursor.selectionEnd()

        cursor.setPosition(start, QTextCursor.MoveMode.MoveAnchor)
        start_line = cursor.blockNumber()

        cursor.setPosition(end, QTextCursor.MoveMode.MoveAnchor)
        end_line = cursor.blockNumber()

        if start_line != end_line:
            # If the selection is across multiple lines, restrict it to the start line
            cursor.setPosition(start, QTextCursor.MoveMode.MoveAnchor)
            cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor, 1)
            self.text_edit.setTextCursor(cursor)

    def customize_ttp_entry(self, item):
        dialog = QDialog(self)
        dialog.setWindowTitle('Customize TTP Entry')

        layout = QVBoxLayout()
        layout.addWidget(QLabel("{{"))

        input_text = QLineEdit()
        layout.addWidget(input_text)

        layout.addWidget(QLabel("}}"))

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(dialog.accept)
        layout.addWidget(ok_button)

        dialog.setLayout(layout)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            item.ttp_text = f"{{{{{input_text.text()}}}}}"
        print(item.ttp_text)


    def make_readonly(self):
        if self.text_edit.toPlainText():
            self.text_edit.setReadOnly(True)

    def show_context_menu(self, pos):
        context_menu = QMenu(self)
        create_action = QAction("Create Named Selection", self)
        create_action.triggered.connect(lambda: name_selection(self))
        context_menu.addAction(create_action)
        context_menu.exec(self.text_edit.mapToGlobal(pos))


    def reset_app(self):
        self.text_edit.setPlainText("")
        self.text_edit.setReadOnly(False)
        self.list_widget.clear()

def main():
    import sys
    # Your existing code that kicks off the app
    app = QApplication(sys.argv)
    app.setStyle("fusion")
    app_widget = TTPGuiUI()
    app_widget.resize(800, 600)
    app_widget.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()