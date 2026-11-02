from PyQt6.QtWidgets import (QComboBox, QDialog, QHBoxLayout, QHeaderView, QLabel,
                             QLineEdit, QPushButton)

from data.inquiries import (add_inquiry, get_inquiries, update_inquiry,
                            update_inquiry_status)
from data.store import INQUIRY_STATUSES, format_record_id
from dialogs.add_inquiry_dialog import AddInquiryDialog
from dialogs.inquiry_details_dialog import InquiryDetailsDialog
from pages.base_page import BasePage


# Lists, filters, and resolves inquiries.
class InquiriesPage(BasePage):

    # Builds the page controls and connects their signals.
    def __init__(self):
        super().__init__("Lost-Item Inquiries")

        self.inquiries = []
        self.current_inquiries = []
        self.page_size = 100
        self.current_page = 0

        controls = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search")
        self.search_input.setFixedHeight(32)

        date_filter_widget, self.date_filter, self.date_input = self.create_date_filter()

        self.status_filter = QComboBox()
        self.status_filter.setFixedHeight(32)
        self.status_filter.setMinimumWidth(180)
        self.status_filter.addItem("All")
        self.status_filter.addItems(INQUIRY_STATUSES)

        self.add_button = QPushButton("Add Inquiry")
        self.add_button.setFixedHeight(32)

        self.resolve_button = QPushButton("Mark as Resolved")
        self.reopen_button = QPushButton("Reopen")

        controls.addWidget(self.search_input, 1)
        controls.addWidget(date_filter_widget)
        controls.addWidget(QLabel("Status:"))
        controls.addWidget(self.status_filter)
        controls.addWidget(self.add_button)
        self.main_layout.addLayout(controls)

        actions = QHBoxLayout()
        actions.addWidget(self.resolve_button)
        actions.addWidget(self.reopen_button)
        actions.addStretch()
        self.main_layout.addLayout(actions)


        headers = ["ID", "Student Name", "T.I.P. Email", "Item Name", "Category",
                   "Date Lost", "Date Reported", "Status", "Actions"]
        self.table = self.create_table(headers)
        self.table.verticalHeader().setDefaultSectionSize(54)
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(8, QHeaderView.ResizeMode.ResizeToContents)
        self.main_layout.addWidget(self.table, 1)


        self.previous_button = QPushButton("Previous")
        self.next_button = QPushButton("Next")
        self.page_label = QLabel("")
        pager = QHBoxLayout()
        pager.addWidget(self.previous_button)
        pager.addWidget(self.page_label)
        pager.addWidget(self.next_button)
        pager.addStretch()
        self.main_layout.addLayout(pager)

        self.status_label = QLabel("")
        self.main_layout.addWidget(self.status_label)

        self.add_button.clicked.connect(self.add_inquiry)
        self.resolve_button.clicked.connect(lambda: self.change_status("Resolved"))
        self.reopen_button.clicked.connect(lambda: self.change_status("Open"))
        self.search_input.textChanged.connect(self.start_search)
        self.date_filter.toggled.connect(self.start_search)
        self.date_input.dateChanged.connect(self.start_search)
        self.status_filter.currentIndexChanged.connect(self.start_search)
        self.previous_button.clicked.connect(self.previous_page)
        self.next_button.clicked.connect(self.next_page)
        self.table.doubleClicked.connect(lambda index: self.view_inquiry(index.row()))

        self.refresh()


    # Applies the current search and filters.
    def start_search(self, _value=None):
        self.current_page = 0
        self.refresh()


    # Saves a new lost item inquiry.
    def add_inquiry(self):
        dialog = AddInquiryDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            add_inquiry(dialog.get_data())
            self.refresh()


    # Reloads the displayed data.
    def refresh(self):
        search = self.search_input.text()
        status = self.status_filter.currentText()
        date_filter = self.date_input.date().toString("yyyy-MM-dd") if self.date_filter.isChecked() else ""

        try:
            self.inquiries = get_inquiries(search, status, date_filter)
        except (OSError, ValueError, TypeError, KeyError):
            self.status_label.setText("Could not load inquiries.")
            return

        self.show_page()


    # Displays the current page of results.
    def show_page(self):
        total = len(self.inquiries)
        page_count = (total + self.page_size - 1) // self.page_size
        self.current_page = min(self.current_page, max(page_count - 1, 0))

        start = self.current_page * self.page_size
        self.current_inquiries = self.inquiries[start:start + self.page_size]


        rows = [[
            format_record_id("INQ", inquiry.get("date_reported"), inquiry["inquiry_id"]),
            inquiry.get("student_name", ""),
            inquiry.get("tip_email", ""),
            inquiry.get("item_name", ""),
            inquiry.get("category", ""),
            inquiry.get("date_lost", ""),
            inquiry.get("date_reported", ""),
            inquiry.get("status", ""),
            "",
        ] for inquiry in self.current_inquiries]
        self.fill_table(self.table, rows)


        for row in range(len(self.current_inquiries)):
            self.add_action_buttons(self.table, row, [
                ("view.png", self.view_inquiry, "View inquiry details"),
                ("edit.png", self.edit_inquiry, "Edit inquiry"),
            ])


        self.page_label.setText(f"Page {self.current_page + 1} of {page_count}" if page_count else "Page 0 of 0")
        self.previous_button.setEnabled(self.current_page > 0)
        self.next_button.setEnabled(self.current_page + 1 < page_count)

        visible_end = start + len(self.current_inquiries)
        self.status_label.setText(f"Showing {start + 1 if self.current_inquiries else 0}-{visible_end} of {total} inquiry(ies)")


    # Displays the previous page of results.
    def previous_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.show_page()


    # Displays the next page of results.
    def next_page(self):
        if (self.current_page + 1) * self.page_size < len(self.inquiries):
            self.current_page += 1
            self.show_page()


    # Returns the selected inquiry, if any.
    def selected_inquiry(self, row=None):
        if row is None:
            row = self.table.currentRow()
        if row < 0 or row >= len(self.current_inquiries):
            return None
        return self.current_inquiries[row]


    # Displays details for the selected inquiry.
    def view_inquiry(self, row=None):
        inquiry = self.selected_inquiry(row)
        if inquiry is None:
            self.status_label.setText("Select an inquiry first.")
            return
        InquiryDetailsDialog(inquiry, self).exec()


    # Opens the form for the selected inquiry.
    def edit_inquiry(self, row=None):
        inquiry = self.selected_inquiry(row)
        if inquiry is None:
            self.status_label.setText("Select an inquiry first.")
            return
        dialog = AddInquiryDialog(self, inquiry)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                update_inquiry(inquiry["inquiry_id"], dialog.get_data())
                self.status_label.setText("")
            except (ValueError, OSError):
                self.status_label.setText("Could not update that inquiry.")
            self.refresh()


    # Updates the selected record status.
    def change_status(self, new_status):
        inquiry = self.selected_inquiry()
        if inquiry is None:
            self.status_label.setText("Select an inquiry first.")
            return
        try:
            update_inquiry_status(inquiry["inquiry_id"], new_status)
            self.status_label.setText("")
        except (ValueError, OSError):
            self.status_label.setText("Could not update that inquiry.")
        self.refresh()
