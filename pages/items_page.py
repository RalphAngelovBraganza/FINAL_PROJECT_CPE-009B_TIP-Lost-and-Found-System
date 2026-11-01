from PyQt6.QtWidgets import (QComboBox, QDialog, QHBoxLayout, QHeaderView, QLabel,
                             QLineEdit, QPushButton)

from data.items import add_item, get_items, update_item
from data.store import CATEGORIES, format_record_id
from dialogs.add_item_dialog import AddItemDialog
from dialogs.item_details_dialog import ItemDetailsDialog
from pages.base_page import BasePage


# Lists, filters, and edits found items.
class ItemsPage(BasePage):

    # Builds the page controls and connects their signals.
    def __init__(self, show_title=True):
        super().__init__("Found Items", show_title)

        self.items = []
        self.current_items = []
        self.page_size = 100
        self.current_page = 0

        controls = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search")
        self.search_input.setFixedHeight(32)

        self.category_filter = QComboBox()
        self.category_filter.setFixedHeight(32)
        self.category_filter.setMinimumWidth(180)
        self.category_filter.addItem("All")
        self.category_filter.addItems(CATEGORIES)

        self.add_button = QPushButton("Add Item")
        self.add_button.setFixedHeight(32)

        controls.addWidget(self.search_input, 1)
        controls.addWidget(QLabel("Category:"))
        controls.addWidget(self.category_filter)
        controls.addWidget(self.add_button)
        self.main_layout.addLayout(controls)


        headers = ["ID", "Item Name", "Category", "Date Found", "Location", "Finder", "Status", "Actions"]
        self.table = self.create_table(headers)
        self.table.verticalHeader().setDefaultSectionSize(54)
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)
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

        self.add_button.clicked.connect(self.add_item)
        self.search_input.textChanged.connect(self.start_search)
        self.category_filter.currentIndexChanged.connect(self.start_search)
        self.previous_button.clicked.connect(self.previous_page)
        self.next_button.clicked.connect(self.next_page)
        self.table.doubleClicked.connect(lambda index: self.view_item(index.row()))

        self.refresh()


    # Saves a new found item.
    def add_item(self):
        dialog = AddItemDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            add_item(dialog.get_item_data())
            self.refresh()


    # Applies the current search and filters.
    def start_search(self, _value=None):
        self.current_page = 0
        self.refresh()


    # Reloads the displayed data.
    def refresh(self):
        search = self.search_input.text()
        category = self.category_filter.currentText()

        try:
            self.items = get_items(search, category)
        except (OSError, ValueError, TypeError):
            self.status_label.setText("Could not load items.")
            return

        self.show_page()


    # Displays the current page of results.
    def show_page(self):
        total = len(self.items)
        page_count = (total + self.page_size - 1) // self.page_size
        self.current_page = min(self.current_page, max(page_count - 1, 0))

        start = self.current_page * self.page_size
        self.current_items = self.items[start:start + self.page_size]


        rows = [[
            format_record_id("ITM", item.get("date_found"), item["item_id"]),
            item.get("item_name", ""),
            item.get("category", ""),
            item.get("date_found", ""),
            item.get("location_found", ""),
            item.get("finder_name", ""),
            item.get("status", ""),
            "",
        ] for item in self.current_items]
        self.fill_table(self.table, rows)


        for row in range(len(self.current_items)):
            self.add_action_buttons(self.table, row, [
                ("view.png", self.view_item, "View item details"),
                ("edit.png", self.edit_item, "Edit item"),
            ])


        self.page_label.setText(f"Page {self.current_page + 1} of {page_count}" if page_count else "Page 0 of 0")
        self.previous_button.setEnabled(self.current_page > 0)
        self.next_button.setEnabled(self.current_page + 1 < page_count)

        visible_end = start + len(self.current_items)
        self.status_label.setText(f"Showing {start + 1 if self.current_items else 0}-{visible_end} of {total} item(s)")


    # Displays the previous page of results.
    def previous_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.show_page()


    # Displays the next page of results.
    def next_page(self):
        if (self.current_page + 1) * self.page_size < len(self.items):
            self.current_page += 1
            self.show_page()


    # Returns the selected item, if any.
    def selected_item(self, row=None):
        if row is None:
            row = self.table.currentRow()
        if row < 0 or row >= len(self.current_items):
            return None
        return self.current_items[row]


    # Displays details for the selected item.
    def view_item(self, row=None):
        item = self.selected_item(row)
        if item is None:
            self.status_label.setText("Select an item first.")
            return
        ItemDetailsDialog(item, self).exec()


    # Opens the form for the selected item.
    def edit_item(self, row=None):
        item = self.selected_item(row)
        if item is None:
            self.status_label.setText("Select an item first.")
            return
        dialog = AddItemDialog(self, item)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                update_item(item["item_id"], dialog.get_item_data())
                self.status_label.setText("")
            except (ValueError, OSError):
                self.status_label.setText("Could not update that item.")
            self.refresh()
