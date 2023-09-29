from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QTextCursor, QAction
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPlainTextEdit, QListWidget, QMenu, \
    QMenuBar, QPushButton, QDialog, QLabel, QLineEdit, QSplitter, QHBoxLayout

from ttpbuilder.Library.util import show_ttp_help, name_selection, generate_template, highlight_text, \
    show_about_dialog, open_basics_dialog, restrict_to_single_line


from PyQt6.QtGui import QMouseEvent

class ClickablePlainTextEdit(QPlainTextEdit):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setMouseTracking(True)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover)

    def mousePressEvent(self, event: QMouseEvent):
        super().mousePressEvent(event)
        cursor = self.textCursor()
        position = cursor.position()

        # Check if clicked text corresponds to a named selection
        for unique_id, data in self.parent.named_selections.items():
            if data['start'] <= position <= data['end']:
                self.parent.customize_ttp_entry(data['list_widget_item'])
                break


class TTPGuiUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initialize_theme("dark")
        self.named_selections = {}
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
        basics_action.triggered.connect(lambda: open_basics_dialog(self))
        help_menu.addAction(basics_action)

        # Add TTP Help action
        ttp_help_action = QAction("TTP Help", self)
        ttp_help_action.triggered.connect(lambda: show_ttp_help(self))
        help_menu.addAction(ttp_help_action)

        # Add About action
        about_action = QAction("About", self)
        about_action.triggered.connect(lambda: show_about_dialog(self))
        help_menu.addAction(about_action)

        # Add Reset action
        reset_action = QAction("Reset", self)
        reset_action.triggered.connect(self.reset_app)
        file_menu.addAction(reset_action)

        main_layout.addWidget(menubar)

        # Create QPlainTextEdit and make it read-only after initial text is entered
        # self.text_edit = QPlainTextEdit()
        self.text_edit = ClickablePlainTextEdit(self)
        self.text_edit.installEventFilter(self)

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
        self.text_edit.selectionChanged.connect(lambda: restrict_to_single_line(self))

        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.show_list_context_menu)

    def eventFilter(self, obj, event):
        if obj == self.text_edit and event.type() == QEvent.Type.HoverMove:
            # Directly get cursor position during hover event
            hover_cursor = self.text_edit.cursorForPosition(event.position().toPoint())
            position = hover_cursor.position()

            is_clickable = False

            # Check if hovered text corresponds to a named selection
            for unique_id, data in self.named_selections.items():
                if position >= data['start'] and position <= data['end']:
                    is_clickable = True
                    break

            if is_clickable:
                QApplication.setOverrideCursor(Qt.CursorShape.PointingHandCursor)
            else:
                QApplication.restoreOverrideCursor()

            return True  # Return True if you want to stop event propagation
        return False  # Continue event propagation otherwise
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


    def customize_ttp_entry(self, item):
        QApplication.restoreOverrideCursor()
        dialog = QDialog(self)
        dialog.setWindowTitle('Customize TTP Entry')
        dialog.setMinimumWidth(400)
        layout = QHBoxLayout()
        layout.addWidget(QLabel("{{"))
        input_text = QLineEdit()
        current_entry = item.ttp_text
        if len(current_entry)>4:
            current_entry = current_entry.replace("{{","")
            current_entry = current_entry.replace("}}", "")
        input_text.setText(current_entry)
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