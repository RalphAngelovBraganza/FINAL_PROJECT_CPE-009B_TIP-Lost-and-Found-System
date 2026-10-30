import os

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (QAbstractItemView, QHBoxLayout, QHeaderView, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QVBoxLayout, QWidget)

from data.store import BASE_DIR

# okay pages are responsible for the content of the main window, they are not responsible for the navigation
#  bar or the header bar, those are handled by the main window
class BasePage(QWidget):
    def __init__(self, title):
        super().__init__()
        self.page_title = title

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)

        title_label = QLabel(title)
        title_label.setObjectName("pageTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(title_label)

        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(12)
        layout.addLayout(self.main_layout)

    def refresh(self):
        pass

    # The three helpers below are shared by every page that shows a table.
    # They live here so the pages do not repeat the same table setup, row filling, and icon button code.

    # Creates an empty table with the given column titles. The table only allows row selection,
    # the user cannot type inside the cells, and every column stretches to fill the page width.
    def create_table(self, headers):
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.verticalHeader().setVisible(False)  # hides the default row numbers on the left
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)  # clicking a cell selects the whole row
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)  # only one row at a time
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)  # the cells are read only
        table.setAlternatingRowColors(True)  # gives every other row a different color
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)  # columns share the available space
        table.verticalHeader().setDefaultSectionSize(44)  # row height, tall enough for the 30x30 action buttons
        return table

    # Fills the table with the given rows. Each row is a list of values that map to the columns
    # in order, and None is shown as an empty cell instead of the word "None".
    def fill_table(self, table, rows):
        table.setRowCount(len(rows))
        for row_number, row in enumerate(rows):
            for column_number, value in enumerate(row):
                table.setItem(row_number, column_number, QTableWidgetItem("" if value is None else str(value)))

    # Puts small icon buttons at the end of a table row. The actions argument is a list of
    # (icon file name, method to call, tooltip) triples, and each method receives the row number
    # so the page knows which record the button belongs to.
    def add_action_buttons(self, table, row, actions):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        for icon_name, callback, tooltip in actions:
            # This loop goes through each action we want to put in the table, like edit, delete, or view.
            button = QPushButton()  # Creates an empty button.
            button.setObjectName("itemActionButton")  # Gives the button a name so we can style it using our stylesheet.
            button.setFixedSize(30, 30)  # Makes the button 30x30 so all action buttons have the same size.
            button.setIconSize(QSize(18, 18))  # Sets the icon size inside the button.
            button.setIcon(QIcon(os.path.join(BASE_DIR, "images", "icons", icon_name)))  # Loads the correct icon from our icons folder.
            button.setToolTip(tooltip)  # Shows a small description when the mouse hovers over the button.
            button.clicked.connect(lambda checked=False, current_row=row, method=callback: method(current_row))  # When clicked, it runs the assigned function for that specific row.
            layout.addWidget(button)  # Adds the button to the layout.

        table.setCellWidget(row, table.columnCount() - 1, container)  # Places the whole button container in the last column of the current row.