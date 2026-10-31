import inspect
import os
from functools import wraps

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (QAbstractItemView, QHBoxLayout, QHeaderView, QLabel, QMessageBox,
                             QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

from data.store import BASE_DIR


# This decorator catches common errors so they can be displayed instead of unexpectedly closing the window.
# Examples of errors include trying to open a photo that was deleted
# This took me quite a a while
def guarded(message="An error occurred."):  # display a custom error message if the decorated function fails.
    def decorator(func):  # Receives the function that will be protected by the decorator. This could be any function, but in our case it will be the methods that handle button clicks.
        params = [p for p in inspect.signature(func).parameters.values()  # Gets the parameters defined in the original function.
                  if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)]  # Keeps only parameters that can be passed normally by position or keyword.
        max_extra = max(0, len(params) - 1)  # Subtracts self because it is automatically passed to class methods; the remaining number is the allowed extra arguments.

        @wraps(func)  # Preserves the original function's name, documentation, and other identifying information.
        def wrapper(self, *args, **kwargs):  # Replaces the original function call and accepts its instance, extra positional arguments, and keyword arguments.
            try:  # Starts a protected section where errors from the original function can be caught.
                return func(self, *args[:max_extra], **kwargs)  # Calls the original function, passing only the number of positional arguments it accepts.
            except (OSError, ValueError, TypeError):  # Catches common errors related to files, invalid values, or incorrect data types.
                if hasattr(self, "show_error"):  # Checks whether the current page has a show_error() method available.
                    self.show_error(message)  # Uses the page's own method to display the error message.
                else:  # Runs if the page does not have its own show_error() method.
                    QMessageBox.critical(None, "Error", message)  # Displays a standard critical error message box instead.
                return None  # Stops the function and returns None instead of allowing the caught error to interrupt the application.
        return wrapper  # Returns the protected version of the original function.
    return decorator  # Returns the decorator so it can be applied to other functions.


# Pages are responsible for the content of the main window, not the navigation bar or header bar.
# Those are handled by the main window.
class BasePage(QWidget):
    def __init__(self, title, show_title=True):
        super().__init__()
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(25, 20, 25, 20)
        self.main_layout.setSpacing(12)

        if show_title:
            title_label = QLabel(title)
            title_label.setObjectName("pageTitle")
            self.main_layout.addWidget(title_label)

    # Refreshes the page when needed. Individual pages can override this method to perform their own updates.
    def refresh(self):
        pass

    # Creates an empty table with the given column titles. The table only allows row selection,
    # the user cannot type inside the cells, and every column stretches to fill the page width.
    def create_table(self, headers):
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)  # the cells are read only
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)  # clicking a cell selects the whole row
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)  # only one row at a time
        table.setAlternatingRowColors(True)  # gives every other row a different color
        table.verticalHeader().setVisible(False)  # hides the default row numbers on the left
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)  # columns share the available space
        return table

    # Fills the table with the given rows. Each row is a list of values that map to the columns
    # in order, and None is shown as an empty cell instead of the word "None".
    def fill_table(self, table, rows):
        table.setRowCount(len(rows))
        for row_number, row in enumerate(rows):
            for column_number, value in enumerate(row):
                text = "" if value is None else str(value)
                table.setItem(row_number, column_number, QTableWidgetItem(text))

    # Gets the ID of the currently selected record from the first column of the table.
    # If no row is selected, it displays a warning instead.
    def get_selected_id(self, table):
        selected_rows = table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a row in the table first.")
            return None
        return int(table.item(selected_rows[0].row(), 0).text().split("-")[-1])

    # Displays an error message.
    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)

    # Displays an informational message.
    def show_info(self, message):
        QMessageBox.information(self, "Information", message)

    # Asks the user to confirm an action and returns True if they choose Yes.
    def confirm(self, title, message):
        answer = QMessageBox.question(
            self, title, message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        return answer == QMessageBox.StandardButton.Yes

    # Puts small icon buttons in a table row. The actions argument is a list of
    # (icon file name, method to call, tooltip) triples, and each method receives the row number
    # so the page knows which record the button belongs to.
    def add_action_buttons(self, table, row, actions, height=50, column=None):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(5)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        for filename, callback, tooltip in actions:
            button = QPushButton()  # Creates an empty button.
            button.setObjectName("itemActionButton")  # Gives the button a name so we can style it using our stylesheet.
            button.setFixedSize(30, 30)  # Makes the button 30x30 so all action buttons have the same size.
            button.setIconSize(QSize(20, 20))  # Sets the icon size inside the button.
            button.setIcon(QIcon(os.path.join(BASE_DIR, "images", "icons", filename)))  # Loads the correct icon from our icons folder.
            button.setToolTip(tooltip)  # Shows a small description when the mouse hovers over the button.
            button.setAccessibleName(tooltip)  # Gives the button a name that screen readers can recognize.
            button.clicked.connect(lambda checked=False, r=row, action=callback: action(r))  # When clicked, it runs the assigned function for that specific row.
            layout.addWidget(button)  # Adds the button to the layout.
        container.setMinimumHeight(height)
        if column is None:
            column = max(0, table.columnCount() - 1)
        table.setCellWidget(row, column, container)  # Places the whole button container in the specified column of the current row.
        return container