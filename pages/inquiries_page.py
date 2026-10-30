from PyQt6.QtWidgets import (QComboBox, QDialog, QHBoxLayout, QHeaderView, QLabel,
                             QLineEdit, QPushButton)

from data.inquiries import (add_inquiry, get_inquiries, update_inquiry,
                            update_inquiry_status)
from data.store import INQUIRY_STATUSES, format_record_id
from dialogs.add_inquiry_dialog import AddInquiryDialog
from dialogs.inquiry_details_dialog import InquiryDetailsDialog
from pages.base_page import BasePage


class InquiriesPage(BasePage):
    def __init__(self):
        super().__init__("Lost-Item Inquiries")

        self.inquiries = []  # All inquiries that match the current search and status filter.
        self.current_inquiries = []  # Remember which inquiries are on the table rows right now.
        self.page_size = 100  # How many rows the table shows at once.
        self.current_page = 0  # The page number the user is looking at (starts at 0).

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

        # The Actions column is added last because the view and edit buttons sit there, one set per row.
        headers = ["ID", "Student Name", "T.I.P. Email", "Item Name", "Category",
                   "Date Lost", "Date Reported", "Status", "Actions"]  # The column titles.
        self.table = self.create_table(headers)  # Builds the table using the shared BasePage helper.
        self.table.horizontalHeader().setStretchLastSection(False)  # The Actions column should keep its own small width.
        self.table.horizontalHeader().setSectionResizeMode(8, QHeaderView.ResizeMode.ResizeToContents)  # Fits the two icon buttons.
        self.main_layout.addWidget(self.table, 1)  # 1 = the table stretches to fill the page.

        # Paging row: the user moves between pages here instead of loading every inquiry at once.
        self.previous_button = QPushButton("Previous")  # Goes one page back.
        self.next_button = QPushButton("Next")  # Goes one page forward.
        self.page_label = QLabel("")  # Shows something like "Page 2 of 5".
        pager = QHBoxLayout()
        pager.addWidget(self.previous_button)
        pager.addWidget(self.page_label)
        pager.addWidget(self.next_button)
        pager.addStretch()  # Pushes the paging controls to the left side.
        self.main_layout.addLayout(pager)

        self.status_label = QLabel("")  # Shows the count or an error message later on.
        self.main_layout.addWidget(self.status_label)  # Places the label below the table.

        self.add_button.clicked.connect(self.add_inquiry)  # Opens the Add Inquiry form.
        self.resolve_button.clicked.connect(lambda: self.change_status("Resolved"))  # Selected row -> Resolved.
        self.reopen_button.clicked.connect(lambda: self.change_status("Open"))  # Selected row -> Open.
        self.search_input.textChanged.connect(self.start_search)  # Back to page 1 and reload whenever the search text changes.
        self.status_filter.currentIndexChanged.connect(self.start_search)  # Same thing for the status dropdown.
        self.previous_button.clicked.connect(self.previous_page)  # Moves the table to the previous page.
        self.next_button.clicked.connect(self.next_page)  # Moves the table to the next page.
        self.table.doubleClicked.connect(lambda index: self.view_inquiry(index.row()))  # Double-clicking a row opens its details.

        self.refresh()  # Loads the inquiries when the page is first opened.

    def start_search(self, _value=None):  # Called when the search text or the status changes.
        self.current_page = 0  # A new search always starts from the first page.
        self.refresh()  # Reloads the table.

    def add_inquiry(self):  # Opens the Add Inquiry dialog.
        dialog = AddInquiryDialog(self)  # Creates the Add Inquiry window.
        if dialog.exec() == QDialog.DialogCode.Accepted:  # Checks if the user confirms (Save) the dialog.
            add_inquiry(dialog.get_data())  # Saves the new inquiry through the data layer.
            self.refresh()  # Updates the table to show the new inquiry.

    def refresh(self):  # Reloads the table from the JSON file.
        search = self.search_input.text()  # Gets the current text entered in the search field.
        status = self.status_filter.currentText()  # Gets the currently selected status.

        try:  # Tries to load the inquiries.
            self.inquiries = get_inquiries(search, status)  # Gets inquiries matching the search and status.
        except (OSError, ValueError, TypeError, KeyError):  # Handles these errors if reading fails.
            self.status_label.setText("Could not load inquiries.")  # Shows an error message.
            return  # Stops the method if an error occurs.

        self.show_page()  # Shows the rows of the current page.

    def show_page(self):  # Displays only the inquiries that belong to the current page.
        total = len(self.inquiries)  # How many inquiries matched the search and status.
        page_count = (total + self.page_size - 1) // self.page_size  # Rounds up so a partial last page still counts.
        self.current_page = min(self.current_page, max(page_count - 1, 0))  # Keeps the page number inside the available pages.

        start = self.current_page * self.page_size  # The position of the first row on this page.
        self.current_inquiries = self.inquiries[start:start + self.page_size]  # The slice of inquiries this page shows.

        # Each inquiry becomes one row: the ID is formatted (INQ-YYMM-nnn) and the last column is left
        # empty because the BasePage helper fills it with the view and edit buttons afterwards.
        rows = [[
            format_record_id("INQ", inquiry.get("date_reported"), inquiry["inquiry_id"]),  # Formatted ID.
            inquiry.get("student_name", ""),  # Student Name.
            inquiry.get("tip_email", ""),  # T.I.P. Email.
            inquiry.get("item_name", ""),  # Item Name.
            inquiry.get("category", ""),  # Category.
            inquiry.get("date_lost", ""),  # Date Lost.
            inquiry.get("date_reported", ""),  # Date Reported.
            inquiry.get("status", ""),  # Status.
            "",  # Actions column, filled below.
        ] for inquiry in self.current_inquiries]
        self.fill_table(self.table, rows)  # Writes all of the rows into the table.

        # Adds the view and edit buttons to every row. The row number is passed along so each button
        # knows which record it belongs to.
        for row in range(len(self.current_inquiries)):
            self.add_action_buttons(self.table, row, [
                ("view.png", self.view_inquiry, "View inquiry details"),
                ("edit.png", self.edit_inquiry, "Edit inquiry"),
            ])

        # Updates the paging controls and the count message.
        self.page_label.setText(f"Page {self.current_page + 1} of {page_count}" if page_count else "Page 0 of 0")
        self.previous_button.setEnabled(self.current_page > 0)  # No previous page while on the first page.
        self.next_button.setEnabled(self.current_page + 1 < page_count)  # No next page on the last page.

        visible_end = start + len(self.current_inquiries)
        self.status_label.setText(f"Showing {start + 1 if self.current_inquiries else 0}-{visible_end} of {total} inquiry(ies)")

    def previous_page(self):  # Moves one page back.
        if self.current_page > 0:
            self.current_page -= 1
            self.show_page()

    def next_page(self):  # Moves one page forward.
        if (self.current_page + 1) * self.page_size < len(self.inquiries):
            self.current_page += 1
            self.show_page()

    def selected_inquiry(self, row=None):  # Returns the full record behind a table row.
        if row is None:  # No row was passed in, so use the highlighted one.
            row = self.table.currentRow()
        if row < 0 or row >= len(self.current_inquiries):  # Nothing selected (or beyond this page).
            return None  # Tells the caller that no row was selected.
        return self.current_inquiries[row]  # Table rows match this list 1 to 1.

    def view_inquiry(self, row=None):  # Opens the read-only details window.
        inquiry = self.selected_inquiry(row)  # Finds the record the user picked.
        if inquiry is None:  # No row is selected.
            self.status_label.setText("Select an inquiry first.")  # Tells the user to pick a row.
            return
        InquiryDetailsDialog(inquiry, self).exec()  # Shows the details, including the photo if there is one.

    def edit_inquiry(self, row=None):  # Opens the same inquiry form, but already filled in.
        inquiry = self.selected_inquiry(row)  # Finds the record the user picked.
        if inquiry is None:  # No row is selected.
            self.status_label.setText("Select an inquiry first.")  # Tells the user to pick a row.
            return
        dialog = AddInquiryDialog(self, inquiry)  # Passing the inquiry switches the dialog to edit mode.
        if dialog.exec() == QDialog.DialogCode.Accepted:  # Checks if the user saves the changes.
            try:  # Tries to save the edited inquiry.
                update_inquiry(inquiry["inquiry_id"], dialog.get_data())  # Writes the new values to the JSON file.
                self.status_label.setText("")  # Clears any previous message.
            except (ValueError, OSError):  # The record is missing or the file cannot be written.
                self.status_label.setText("Could not update that inquiry.")  # Shows an error message.
            self.refresh()  # Reloads the table so the changes are visible.

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
