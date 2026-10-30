from PyQt6.QtWidgets import (QComboBox, QDialog, QHBoxLayout, QHeaderView, QLabel,
                             QLineEdit, QPushButton)

from data.items import add_item, get_items, update_item
from data.store import CATEGORIES, format_record_id
from dialogs.add_item_dialog import AddItemDialog
from dialogs.item_details_dialog import ItemDetailsDialog
from pages.base_page import BasePage


class ItemsPage(BasePage):
    def __init__(self):
        super().__init__("Found Items")

        self.items = []  # All items that match the current search and category filter.
        self.current_items = []  # Only the items shown on the table rows right now.
        self.page_size = 100  # How many rows the table shows at once.
        self.current_page = 0  # The page number the user is looking at (starts at 0).

        controls = QHBoxLayout()  # layout for the search field, category dropdown, and add button.
        self.search_input = QLineEdit()  # Textbox where the user can search stuff
        self.search_input.setPlaceholderText("Search")  # Displays "Search" in the text box
        self.search_input.setFixedHeight(32)  # Size of the textbox

        self.category_filter = QComboBox()  # This is the drop down
        self.category_filter.setFixedHeight(32)  # size
        self.category_filter.setMinimumWidth(180)  # the width of the drop down
        self.category_filter.addItem("All")  # Adds "All" option for the drop down
        self.category_filter.addItems(CATEGORIES)  # Calls all the categories from the CATEGORIES list and adds them to the drop down.

        self.add_button = QPushButton("Add Item")  # button for adding an item
        self.add_button.setFixedHeight(32)  # size

        controls.addWidget(self.search_input, 1)  # Adds the search field then 1 is basically how much space it gets
        controls.addWidget(QLabel("Category:"))  # basically a label beside the category drop down
        controls.addWidget(self.category_filter)  # Adds the category dropdown to the horizontal layout (that is called control btw go back up)
        controls.addWidget(self.add_button)  # Adds the the add button (REMEMBER ADDING BUTTONS GOES FROM LEFT TO RIGHT)
        self.main_layout.addLayout(controls)  # Places the horizontal controls layout inside the main layout (putting a square inside a square basically)

        # The Actions column is added last because the view and edit buttons sit there, one set per row.
        headers = ["ID", "Item Name", "Category", "Date Found", "Location", "Finder", "Status", "Actions"]  # The column titles
        self.table = self.create_table(headers)  # Builds the table using the shared BasePage helper.
        self.table.horizontalHeader().setStretchLastSection(False)  # The Actions column should keep its own small width.
        self.table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)  # Fits the two icon buttons.
        self.main_layout.addWidget(self.table, 1)  # Adds the table, and 1 makes it stretch to fill the page.

        # Paging row: the user moves between pages here instead of scrolling through every record at once.
        self.previous_button = QPushButton("Previous")  # Goes one page back.
        self.next_button = QPushButton("Next")  # Goes one page forward.
        self.page_label = QLabel("")  # Shows something like "Page 2 of 5".
        pager = QHBoxLayout()
        pager.addWidget(self.previous_button)
        pager.addWidget(self.page_label)
        pager.addWidget(self.next_button)
        pager.addStretch()  # Pushes the paging controls to the left side.
        self.main_layout.addLayout(pager)

        self.status_label = QLabel("")  # this is basically a status label and it will set it to blank and then we will set it to something later on
        self.main_layout.addWidget(self.status_label)  # Places the status label below the table.

        self.add_button.clicked.connect(self.add_item)  # Opens the Add Item form.
        self.search_input.textChanged.connect(self.start_search)  # Back to page 1 and reload whenever the search text changes.
        self.category_filter.currentIndexChanged.connect(self.start_search)  # Same thing for the category dropdown.
        self.previous_button.clicked.connect(self.previous_page)  # Moves the table to the previous page.
        self.next_button.clicked.connect(self.next_page)  # Moves the table to the next page.
        self.table.doubleClicked.connect(lambda index: self.view_item(index.row()))  # Double-clicking a row opens its details.

        self.refresh()  # Loads the items when the page is first opened.

    def add_item(self):  # Defines the method for adding an item.
        dialog = AddItemDialog(self)  # Creates the Add Item window.
        if dialog.exec() == QDialog.DialogCode.Accepted:  # Checks if the user confirms the dialog.
            add_item(dialog.get_item_data())  # Saves the new item.
            self.refresh()  # Updates the table to show the new item.

    def start_search(self, _value=None):  # Called when the search text or the category changes.
        self.current_page = 0  # A new search always starts from the first page.
        self.refresh()  # Reloads the table.

    def refresh(self):  # reloads the table
        search = self.search_input.text()  # Gets the current text entered in the search field.
        category = self.category_filter.currentText()  # Gets the currently selected category from the dropdown.

        try:  # Tries to load the items.
            self.items = get_items(search, category)  # Gets items matching the search and category.
        except (OSError, ValueError, TypeError):  # Handles these errors if something goes wrong.
            self.status_label.setText("Could not load items.")  # Shows an error message.
            return  # Stops the method if an error occurs.

        self.show_page()  # Shows the rows of the current page.

    def show_page(self):  # Displays only the items that belong to the current page.
        total = len(self.items)  # How many items matched the search and category.
        page_count = (total + self.page_size - 1) // self.page_size  # Rounds up so a partial last page still counts.
        self.current_page = min(self.current_page, max(page_count - 1, 0))  # Keeps the page number inside the available pages.

        start = self.current_page * self.page_size  # The position of the first row on this page.
        self.current_items = self.items[start:start + self.page_size]  # The slice of items this page shows.

        # Each item becomes one row: the ID is formatted (ITM-YYMM-nnn) and the last column is left
        # empty because the BasePage helper fills it with the view and edit buttons afterwards.
        rows = [[
            format_record_id("ITM", item.get("date_found"), item["item_id"]),  # Formatted record ID.
            item.get("item_name", ""),  # Item Name.
            item.get("category", ""),  # Category.
            item.get("date_found", ""),  # Date Found.
            item.get("location_found", ""),  # Location.
            item.get("finder_name", ""),  # Finder.
            item.get("status", ""),  # Status.
            "",  # Actions column, filled below.
        ] for item in self.current_items]
        self.fill_table(self.table, rows)  # Writes all of the rows into the table.

        # Adds the view and edit buttons to every row. The row number is passed along so each button
        # knows which record it belongs to.
        for row in range(len(self.current_items)):
            self.add_action_buttons(self.table, row, [
                ("view.png", self.view_item, "View item details"),
                ("edit.png", self.edit_item, "Edit item"),
            ])

        # Updates the paging controls and the count message.
        self.page_label.setText(f"Page {self.current_page + 1} of {page_count}" if page_count else "Page 0 of 0")
        self.previous_button.setEnabled(self.current_page > 0)  # No previous page while on the first page.
        self.next_button.setEnabled(self.current_page + 1 < page_count)  # No next page on the last page.

        visible_end = start + len(self.current_items)
        self.status_label.setText(f"Showing {start + 1 if self.current_items else 0}-{visible_end} of {total} item(s)")

    def previous_page(self):  # Moves one page back.
        if self.current_page > 0:
            self.current_page -= 1
            self.show_page()

    def next_page(self):  # Moves one page forward.
        if (self.current_page + 1) * self.page_size < len(self.items):
            self.current_page += 1
            self.show_page()

    def selected_item(self, row=None):  # Returns the full record behind a table row.
        if row is None:  # No row was passed in, so use the highlighted one.
            row = self.table.currentRow()
        if row < 0 or row >= len(self.current_items):  # Nothing selected (or beyond this page).
            return None
        return self.current_items[row]  # Table rows match this list 1 to 1.

    def view_item(self, row=None):  # Opens the read-only details window.
        item = self.selected_item(row)  # Finds the record the user picked.
        if item is None:
            self.status_label.setText("Select an item first.")  # Tells the user to pick a row.
            return
        ItemDetailsDialog(item, self).exec()  # Shows the details, including the photo if there is one.

    def edit_item(self, row=None):  # Opens the same item form, but already filled in.
        item = self.selected_item(row)  # Finds the record the user picked.
        if item is None:
            self.status_label.setText("Select an item first.")  # Tells the user to pick a row.
            return
        dialog = AddItemDialog(self, item)  # Passing the item switches the dialog to edit mode.
        if dialog.exec() == QDialog.DialogCode.Accepted:  # Checks if the user saves the changes.
            try:  # Tries to save the edited item.
                update_item(item["item_id"], dialog.get_item_data())  # Writes the new values to the JSON file.
                self.status_label.setText("")  # Clears any old message.
            except (ValueError, OSError):  # The record is missing or the file cannot be written.
                self.status_label.setText("Could not update that item.")  # Shows an error message.
            self.refresh()  # Reloads the table so the changes are visible.
