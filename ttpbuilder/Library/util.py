# util.py
from PyQt6.QtWebEngineWidgets import QWebEngineView
from ttp import ttp
from PyQt6.QtGui import QTextCursor, QTextCharFormat, QColor
from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import QInputDialog, QListWidgetItem, QDialog, QVBoxLayout, QTextBrowser, QPushButton, \
    QPlainTextEdit
import json
from ttpbuilder.HighlighterTEWidget import SyntaxHighlighter
import uuid

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

def show_ttp_help(self):
    ttp_help_dialog = QDialog(self)
    ttp_help_dialog.setWindowTitle("TTP Help")

    layout = QVBoxLayout()

    web_view = QWebEngineView()
    web_view.setUrl(QUrl("https://ttp.readthedocs.io/en/latest/"))

    layout.addWidget(web_view)
    ttp_help_dialog.setLayout(layout)

    ttp_help_dialog.exec()

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

def show_about_dialog(self):
    about_dialog = QDialog(self)
    about_dialog.setWindowTitle("About")

    layout = QVBoxLayout()

    text_browser = QTextBrowser()
    text_browser.setHtml(
        "Author: Scott Peterman <br> Github: <a href='https://github.com/scottpeterman/ttpbuilder'>TTP Builder</a>")
    text_browser.setOpenExternalLinks(True)
    layout.addWidget(text_browser)
    about_dialog.setLayout(layout)

    about_dialog.exec()


def name_selection(parent):
    current_theme = parent.current_theme
    cursor = parent.text_edit.textCursor()
    selected_text = cursor.selectedText()

    if not selected_text:
        return None

    start = cursor.selectionStart()
    end = cursor.selectionEnd()

    cursor.setPosition(start, QTextCursor.MoveMode.MoveAnchor)
    start_line = cursor.blockNumber() + 1
    lines = parent.text_edit.toPlainText().splitlines()
    original_line_text = lines[start_line - 1]

    name, ok = QInputDialog.getText(parent, "Name the Selection", "Name:")

    if ok and name:
        new_item = QListWidgetItem(f"{name} {start}:{end} Line No.: {start_line}")
        new_item.selection_start = start
        new_item.selection_end = end
        new_item.selected_text = selected_text
        new_item.line_pos = start_line
        new_item.original_line_text = original_line_text
        new_item.ttp_text =  f"{{{{{name}}}}}"
        unique_id = str(uuid.uuid4())
        new_item.unique_id = unique_id
        parent.named_selections[unique_id] = {
            'start': start,
            'end': end,
            'list_widget_item': new_item
        }

        parent.list_widget.addItem(new_item)

        # Highlight text
        highlight_text(parent, start, end)

        return new_item

    return None

def highlight_text(self, start, end, default=False):
    if default:
        if self.current_theme == "dark":
            highlight_color = QColor("#2d2d2d")
        else:
            highlight_color = QColor("#ffffff")
    else:
        # Detect the current theme
        current_theme = self.current_theme  # Assume this function exists and returns either 'dark' or 'light'

        # Choose highlight color based on theme
        if current_theme == 'dark':
            highlight_color = QColor("green")  # Or any color suitable for dark mode
        else:
            highlight_color = QColor("yellow")  # Or any color suitable for light mode

    cursor = self.text_edit.textCursor()

    cursor.setPosition(start, QTextCursor.MoveMode.MoveAnchor)
    cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
    highlight_format = QTextCharFormat()
    highlight_format.setBackground(highlight_color)

    cursor.mergeCharFormat(highlight_format)


def generate_template(self):
    lines_dict = {}
    template_lines_ordered = []
    item_count = self.list_widget.count()
    items = [self.list_widget.item(i) for i in range(item_count)]

    sorted_items = sorted(items, key=lambda item: item.line_pos)

    for item in sorted_items:
        if hasattr(item, 'ttp_text'):
            original_line = item.original_line_text
            if original_line not in lines_dict:
                lines_dict[original_line] = []
                template_lines_ordered.append(original_line)
            lines_dict[original_line].append({
                'selected_text': item.selected_text,
                'ttp_text': item.ttp_text
            })

    template_lines = []
    for original_line in template_lines_ordered:
        template_line_temp = original_line
        for replacement in lines_dict[original_line]:
            template_line_temp = template_line_temp.replace(replacement['selected_text'], replacement['ttp_text'],
                                                            1)
        template_lines.append(template_line_temp)

    template_text = '\n'.join(template_lines)
    show_template_dialog(self, template_text)


def show_template_dialog(self, template):
    dialog = QDialog(self)
    dialog.setWindowTitle('Generated Template')

    layout = QVBoxLayout()

    # self.source_highlighter = SyntaxHighlighter(self.text_edit.document())
    # self.source_highlighter.set_syntax_type("jinja")
    template_browser = QPlainTextEdit()
    template_browser.setPlainText(template)
    template_browser.setMinimumWidth(600)
    self.source_highlighter = SyntaxHighlighter(template_browser.document())
    self.source_highlighter.set_syntax_type("jinja")
    layout.addWidget(template_browser)

    # Adding the Test Template button to the dialog
    test_button = QPushButton("Test Template")
    test_button.clicked.connect(lambda: test_template(self, template))
    layout.addWidget(test_button)

    dialog.setLayout(layout)
    dialog.exec()


def test_template(self, template):
    # Get the source text from QPlainTextEdit
    source_text = self.text_edit.toPlainText()

    # Use TTP to parse
    try:
        parser = ttp(data=source_text, template=template)
        parser.parse()
        results = parser.result(format="json")[0]
        try:
            results = json.loads(results)
            # results = json.dumps(results, indent=2)
        except:
            pass
        # Show the results in a custom dialog
    except Exception as e:
        print(f"TTP Error: {e}")
        results = [{"error":f"ttp parser failed: {e}"}]
    show_results_dialog(self, json.dumps(results, indent=4))

def show_results_dialog(self, results):
    dialog = QDialog(self)
    dialog.setWindowTitle('TTP Results')

    layout = QVBoxLayout()

    result_browser = QTextBrowser()
    result_browser.setMinimumWidth(500)
    result_browser.setPlainText(results)
    layout.addWidget(result_browser)

    dialog.setLayout(layout)
    dialog.exec()
