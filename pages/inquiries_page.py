from PyQt6.QtWidgets import (QComboBox, QHBoxLayout, QHeaderView, QLabel,
                             QLineEdit, QPushButton, QTableWidget,
                             QTableWidgetItem, QVBoxLayout)

from data.inquiries import add_inquiry, get_inquiries, update_inquiry_status
from data.store import INQUIRY_STATUSES, format_record_id
from dialogs.add_inquiry_dialog import AddInquiryDialog
from pages.base_page import BasePage


class InquiriesPage(BasePage):
    def __init__(self):
        super().__init__("Lost-Item Inquiries")

        self.current_inquiries = []  # Remembers which inquiries are on the table rows right now.

        controls = QHBoxLayout()  # Layout for the search field, status dropdown, and add button.
        self.search_input = QLineEdit()  # Textbox where the user can search.
        self.search_input.setPlaceholderText("Search")  # Displays "Search" in the text box.
        self.search_input.setFixedHeight(32)  # Size of the textbox.

        self.status_filter = QComboBox()  # Dropdown for filtering by status.
        self.status_filter.setFixedHeight(32)  # Size.
        self.status_filter.setMinimumWidth(180)  # Width of the dropdown.
        self.status_filter.addItem("All")  # "All" shows everything.
        self.status_filter.addItems(INQUIRY_STATUSES)  # Adds "Open" and "Resolved" from data/store.py.

        self.add_button = QPushButton("Add Inquiry")  # Button for opening the inquiry form.
        self.add_button.setFixedHeight(32)  # Size.

        self.resolve_button = QPushButton("Mark as Resolved")  # Marks the selected inquiry as resolved.
        self.reopen_button = QPushButton("Reopen")  # Puts the selected inquiry back to Open.

        controls.addWidget(self.search_input, 1)  # 1 is how much extra space the search field gets.
        controls.addWidget(QLabel("Status:"))  # Label beside the status dropdown.
        controls.addWidget(self.status_filter)  # Adds the status dropdown to the row.
        controls.addWidget(self.add_button)  # Adds the Add Inquiry button (left to right).
        self.main_layout.addLayout(controls)  # Puts the controls row inside the main layout.

        actions = QHBoxLayout()  # Second row for the Open/Resolved buttons.
        actions.addWidget(self.resolve_button)  # Left button.
        actions.addWidget(self.reopen_button)  # Right button.
        actions.addStretch()  # Pushes both buttons to the left side.
        self.main_layout.addLayout(actions)  # Puts the actions row inside the main layout.

        self.table = QTableWidget()  # Table to display the inquiries.
        headers = ["ID", "Student Name", "T.I.P. Email", "Item Name", "Category",
                   "Date Lost", "Date Reported", "Status"]  # The column titles.
        self.table.setColumnCount(len(headers))  # Creates one column per title (8 columns).
        self.table.setHorizontalHeaderLabels(headers)  # Displays the titles at the top of the table.
        self.table.verticalHeader().setVisible(False)  # Hides the default row numbers.
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)  # Clicking selects the whole row.
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)  # Cells cannot be edited directly.
        self.table.horizontalHeader().setStretchLastSection(True)  # The last column fills the leftover space.
        # This is basically self.table.setColumnWidth(column_number, width_in_pixels) for each column.
        self.table.setColumnWidth(0, 100)  # ID.
        self.table.setColumnWidth(1, 115)  # Student Name.
        self.table.setColumnWidth(2, 155)  # T.I.P. Email.
        self.table.setColumnWidth(3, 120)  # Item Name.
        self.table.setColumnWidth(4, 110)  # Category.
        self.table.setColumnWidth(5, 90)   # Date Lost.
        self.table.setColumnWidth(6, 100)  # Date Reported.
        self.main_layout.addWidget(self.table, 1)  # 1 = the table stretches to fill the page.

        self.status_label = QLabel("")  # Shows the count or an error message later on.
        self.main_layout.addWidget(self.status_label)  # Places the label below the table.

        self.add_button.clicked.connect(self.add_inquiry)  # Opens the Add Inquiry form.
        self.resolve_button.clicked.connect(lambda: self.change_status("Resolved"))  # Selected row -> Resolved.
        self.reopen_button.clicked.connect(lambda: self.change_status("Open"))  # Selected row -> Open.
        self.search_input.textChanged.connect(self.refresh)  # Refreshes whenever the search text changes.
        self.status_filter.currentIndexChanged.connect(self.refresh)  # Refreshes when the dropdown changes.

        self.refresh()  # Loads the inquiries when the page is first opened.

    def add_inquiry(self):  # Opens the Add Inquiry dialog.
        dialog = AddInquiryDialog(self)  # Creates the Add Inquiry window.
        if dialog.exec():  # Checks if the user confirms (Save) the dialog.
            add_inquiry(dialog.get_data())  # Saves the new inquiry through the data layer.
            self.refresh()  # Updates the table to show the new inquiry.

    def selected_inquiry(self):  # Returns the full record behind the currently selected row.
        row = self.table.currentRow()  # Gets the highlighted row number (starts at 0).
        if row < 0 or row >= len(self.current_inquiries):  # Nothing selected (or beyond the list).
            return None  # Tells the caller that no row was selected.
        return self.current_inquiries[row]  # Table rows match this list 1 to 1.

    def change_status(self, new_status):  # Used by both the Resolve and Reopen buttons.
        inquiry = self.selected_inquiry()  # Finds the record the user selected.
        if inquiry is None:  # No row is selected.
            self.status_label.setText("Select an inquiry first.")  # Tells the user to pick a row.
            return  # Stops here, no change is made.
        try:  # Tries to save the new status.
            update_inquiry_status(inquiry["inquiry_id"], new_status)  # Writes the new status to the JSON file.
            self.status_label.setText("")  # Clears any previous message.
        except (ValueError, OSError):  # The record is missing or the file cannot be written.
            self.status_label.setText("Could not update that inquiry.")  # Shows an error message.
        self.refresh()  # Reloads the table so the changed Status column is visible.

    def refresh(self):  # Reloads the table from the JSON file.
        search = self.search_input.text()  # Gets the current text entered in the search field.
        status = self.status_filter.currentText()  # Gets the currently selected status.

        try:  # Tries to load the inquiries.
            inquiries = get_inquiries(search, status)  # Gets inquiries matching the search and status.
        except (OSError, ValueError, TypeError, KeyError):  # Handles these errors if reading fails.
            self.status_label.setText("Could not load inquiries.")  # Shows an error message.
            return  # Stops the method if an error occurs.

        self.current_inquiries = inquiries  # Remembers this list so buttons know which row is which.
        self.table.setRowCount(0)  # Removes all existing rows before displaying the refreshed results.
        for row, inquiry in enumerate(inquiries):  # Loops through the inquiries, numbering rows from 0.
            self.table.insertRow(row)  # Creates a new table row at the current position.
            # setItem() places each detail into its column, turning it into a table cell.
            self.table.setItem(row, 0, QTableWidgetItem(format_record_id("INQ", inquiry.get("date_reported"), inquiry["inquiry_id"])))  # Formatted ID (INQ-YYMM-nnn).
            self.table.setItem(row, 1, QTableWidgetItem(inquiry.get("student_name", "")))
            self.table.setItem(row, 2, QTableWidgetItem(inquiry.get("tip_email", "")))
            self.table.setItem(row, 3, QTableWidgetItem(inquiry.get("item_name", "")))
            self.table.setItem(row, 4, QTableWidgetItem(inquiry.get("category", "")))
            self.table.setItem(row, 5, QTableWidgetItem(inquiry.get("date_lost", "")))
            self.table.setItem(row, 6, QTableWidgetItem(inquiry.get("date_reported", "")))
            self.table.setItem(row, 7, QTableWidgetItem(inquiry.get("status", "")))

        self.status_label.setText(f"{len(inquiries)} inquiry(ies)")  # Shows the total, e.g. "3 inquiry(ies)".
