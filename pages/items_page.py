from PyQt6.QtWidgets import (QComboBox, QHBoxLayout, QHeaderView, QLabel,
                             QLineEdit, QPushButton, QTableWidget,
                             QTableWidgetItem, QVBoxLayout)

from data.items import add_item, get_items
from data.store import CATEGORIES, format_record_id
from dialogs.add_item_dialog import AddItemDialog
from pages.base_page import BasePage


class ItemsPage(BasePage):
    def __init__(self):
        super().__init__("Found Items")

        controls = QHBoxLayout()  #layout for the search field, category dropdown, and add button.
        self.search_input = QLineEdit()  # Textbox where the user can search stuff 
        self.search_input.setPlaceholderText("Search")  # Displays "Search" in the text box
        self.search_input.setFixedHeight(32)  # Size of the textbox

        self.category_filter = QComboBox()  # This is the drop down
        self.category_filter.setFixedHeight(32)  # size
        self.category_filter.setMinimumWidth(180)  # the wdith of the drop down
        self.category_filter.addItem("All")  # Adds "All" option for the drop down
        self.category_filter.addItems(CATEGORIES)  # Calls all the categories from the CATEGORIES list and adds them to the drop down.

        self.add_button = QPushButton("Add Item")  # button for adding an item
        self.add_button.setFixedHeight(32)  # size

        controls.addWidget(self.search_input, 1)  # Adds the search field then 1 is basically how much space it gets
        controls.addWidget(QLabel("Category:"))  # basically a label beside the category drop down
        controls.addWidget(self.category_filter)  # Adds the category dropdown to the horizontal layout (that is called control btw go back up) 
        controls.addWidget(self.add_button)  # Adds the the add button (REMEMBER ADDING BUTTONS GOES FROM LEFT TO RIGHT)
        self.main_layout.addLayout(controls)  # Places the horizontal controls layout inside the main layout (putting a square inside a square basically)

        self.table = QTableWidget()  # TABLE TO DISPLAY THE ITEMS
        headers = ["ID", "Item Name", "Category", "Date Found", "Location", "Finder", "Status"]  # The column titles
        self.table.setColumnCount(len(headers))  # Sets the number of columns to match the number of titles (we have 7 columns so basically it will create 7 columns).
        self.table.setHorizontalHeaderLabels(headers)  # Displays the titles at the top of the table.
        self.table.verticalHeader().setVisible(False)  # this will basically hide the default numbers so you will only see the ID
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)  # when you click on anything on the table it will highlight
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)  # the user wont be able to edit the table directly
        self.table.horizontalHeader().setStretchLastSection(True)  # fills whatever space there is left in the colum
        # this is basically self.table.setColumnWidth(column_number, width_in_pixels) (hope this helps)
        self.table.setColumnWidth(0, 110) 
        self.table.setColumnWidth(1, 140)  
        self.table.setColumnWidth(2, 140)  
        self.table.setColumnWidth(3, 110)  
        self.table.setColumnWidth(4, 160)  
        self.table.setColumnWidth(5, 160)
        self.table.setColumnWidth(6, 100)
        self.main_layout.addWidget(self.table, 1)  # Adds the table 

        self.status_label = QLabel("")  # this is basically a status label and it will set it to blank and then we will set it to something later on
        self.main_layout.addWidget(self.status_label)  # Places the status label below the table.

        self.add_button.clicked.connect(self.add_item)  # Calls add_item() from the add_item_dialog.py 
        self.search_input.textChanged.connect(self.refresh)  # Calls refresh() whenever the search text changes.
        self.category_filter.currentIndexChanged.connect(self.refresh)  # Calls refresh() (same thing)

        self.refresh() # Loads the items when the page is first opened.

    def add_item(self):  # Defines the method for adding an item.
            dialog = AddItemDialog(self)  # Creates the Add Item window.
            if dialog.exec():  # Checks if the user confirms the dialog.
                data = dialog.get_item_data()  # Gets the item details entered by the user.
                add_item(data)  # Saves the new item.
                self.refresh()  # Updates the table to show the new item.

    def refresh(self): # reloads the table 
        search = self.search_input.text()  # Gets the current text entered in the search field.
        category = self.category_filter.currentText()  # Gets the currently selected category from the dropdown.

        try:  # Tries to load the items.
            items = get_items(search, category)  # Gets items matching the search and category.
        except (OSError, ValueError, TypeError):  # Handles these errors if something goes wrong.
            self.status_label.setText("Could not load items.")  # Shows an error message.
            return  # Stops the method if an error occurs.

        self.table.setRowCount(0)  # Removes all existing table rows before displaying the refreshed results.
        for row, item in enumerate(items):  # Loops through the retrieved items and gives each one a row index starting at 0.



        #These lines use insertRow() to create a new table row and setItem() to place each item's details, such as
        #its ID, name, category, date, location, finder, and status, into the correct columns. The code also uses
        #QTableWidgetItem() to turn each value into a table cell and format_record_id() to format the item's ID,
        #while item.get() retrieves details or uses an empty string if a value is missing.
            self.table.insertRow(row)  # Creates a new table row at the current row
            self.table.setItem(row, 0, QTableWidgetItem(format_record_id("ITM", item.get("date_found"), item["item_id"])))  # Formats the item's ID using "ITM", its date, and its item ID, then displays it in column 0.
            self.table.setItem(row, 1, QTableWidgetItem(item.get("item_name", ""))) 
            self.table.setItem(row, 2, QTableWidgetItem(item.get("category", "")))  
            self.table.setItem(row, 3, QTableWidgetItem(item.get("date_found", ""))) 
            self.table.setItem(row, 4, QTableWidgetItem(item.get("location_found", ""))) 
            self.table.setItem(row, 5, QTableWidgetItem(item.get("finder_name", "")))  
            self.table.setItem(row, 6, QTableWidgetItem(item.get("status", ""))) 

        self.status_label.setText(f"{len(items)} item(s)")  # Displays the total number of items retrieved, such as "5 item(s)".
