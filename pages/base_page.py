import inspect
import os
from functools import wraps

from PyQt6.QtCore import QDate, QSize, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (QAbstractItemView, QCheckBox, QDateEdit, QHBoxLayout,
                             QHeaderView, QLabel, QMessageBox, QPushButton,
                             QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

from data.store import BASE_DIR


# Catches common errors in page actions.
def guarded(message="An error occurred."):

    # Wraps page actions with error handling.
    def decorator(func):
        params = [p for p in inspect.signature(func).parameters.values()
                  if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)]
        max_extra = max(0, len(params) - 1)


        # Shows an error when a page action fails.
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args[:max_extra], **kwargs)
            except (OSError, ValueError, TypeError):
                if hasattr(self, "show_error"):
                    self.show_error(message)
                else:
                    QMessageBox.critical(None, "Error", message)
                return None
        return wrapper
    return decorator


# Provides shared page and table helpers.
class BasePage(QWidget):

    # Builds the page controls and connects their signals.
    def __init__(self, title, show_title=True):
        super().__init__()
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(25, 20, 25, 20)
        self.main_layout.setSpacing(12)

        if show_title:
            title_label = QLabel(title)
            title_label.setObjectName("pageTitle")
            self.main_layout.addWidget(title_label)


    # Reloads the displayed data.
    def refresh(self):
        raise NotImplementedError("This page must define its own refresh() method.")


    # Builds a read-only table with the given columns.
    def create_table(self, headers):
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        return table


    # Builds a disabled-until-selected exact-date filter.
    def create_date_filter(self):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        checkbox = QCheckBox("Filter by date")
        checkbox.setObjectName("dateFilterCheckBox")
        date_input = QDateEdit(QDate.currentDate())
        date_input.setCalendarPopup(True)
        date_input.setDisplayFormat("yyyy-MM-dd")
        date_input.setFixedHeight(32)
        date_input.setEnabled(False)
        date_input.setToolTip("Choose a date to match the dates shown in this table.")
        checkbox.toggled.connect(date_input.setEnabled)

        layout.addWidget(checkbox)
        layout.addWidget(date_input)
        return container, checkbox, date_input


    # Fills a table with the supplied rows.
    def fill_table(self, table, rows):
        table.setRowCount(len(rows))
        for row_number, row in enumerate(rows):
            for column_number, value in enumerate(row):
                text = "" if value is None else str(value)
                table.setItem(row_number, column_number, QTableWidgetItem(text))


    # Returns the ID of the selected table row.
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


    # Asks the user to confirm an action.
    def confirm(self, title, message):
        answer = QMessageBox.question(
            self, title, message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        return answer == QMessageBox.StandardButton.Yes


    # Adds action buttons to a table row.
    def add_action_buttons(self, table, row, actions, height=50, column=None):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(5)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        for filename, callback, tooltip in actions:
            button = QPushButton()
            button.setObjectName("itemActionButton")
            button.setFixedSize(30, 30)
            button.setIconSize(QSize(20, 20))
            button.setIcon(QIcon(os.path.join(BASE_DIR, "images", "icons", filename)))
            button.setToolTip(tooltip)
            button.setAccessibleName(tooltip)
            button.clicked.connect(lambda checked=False, r=row, action=callback: action(r))
            layout.addWidget(button)
        container.setMinimumHeight(height)
        if column is None:
            column = max(0, table.columnCount() - 1)
        table.setCellWidget(row, column, container)
        return container
