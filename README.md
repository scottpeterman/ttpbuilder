# TTP Builder GUI Application

## Introduction

TTP Builder is a Python-based GUI application built using PyQt6 that facilitates the creation and management of Text-based Template Parsing (TTP) templates. TTP Builder offers a seamless user experience for network engineers familiar with TTP, TextFSM, and Genie. 

## Features

- **Text Editor**: A primary text editor to paste sample text data.
- **Named Selections**: A ListWidget displays identified variables parsed from the sample text data.
- **Template Generator**: A 'Generate Template' button for automated TTP template creation.
- **Help System**: In-app help documentation linking directly to TTP's official documentation and an "About" section.
  
## Pre-requisites

- Python 3.x
- PyQt6
- PyQt6-WebEngine (For Help menu)
- TTP

## Install and Run
### From an activated venv environment

`pip install ttpbuilder`

Execute: `ttpbuilder`

```bash
git clone https://github.com/scottpeterman/ttpbuilder.git
cd ttp_builder
```

Install the required packages.

```bash
pip install -r requirements.txt
```

Run the application.

```bash
python main.py
```

## How to Use

1. **Paste Sample Data**: Open the app and paste your sample text data into the text editor on the left-hand side.
2. **Named Selections**: After pasting text data, highlight a section of the text that you want to be a variable in the TTP template. Right-click and choose "Create Named Selection".
3. **ListWidget**: This will populate the ListWidget on the right with your identified variables. You can edit or remove these as necessary.
4. **Generate Template**: Once you've highlighted all variables of interest, click on the 'Generate Template' button at the bottom to create the TTP template.
5. **Help Menu**: Use the Help menu for additional resources and documentation on TTP.

## Technologies and Libraries Used

- **PyQt6**: For the GUI.
- **QWebEngineView**: For embedded web browser support.
- **TTP**: For template generation logic.


---
