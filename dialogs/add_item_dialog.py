from PyQt6.QtWidgets import (QComboBox, QDialog, QFormLayout, QDateEdit, QDialogButtonBox,
                             QLineEdit, QLabel, QVBoxLayout)
from data.store import CATEGORIES
from data.items import add_item


class AddItemDialog(QDialog):
    # Initializes the Add Item window, creates the input fields for item details, and arranges them into a form.
    # It also adds Save and Cancel buttons and a label for displaying error messages.
    # in simple terms this is basically the pop up window when you click the add item button in the main window.
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Found Item")
        self.setMinimumWidth(420)

        form = QFormLayout()
        form.setSpacing(10)

        #these are the input fields for the add item dialog, where staff can enter information about the found item.
        self.name_input = QLineEdit()
        self.category_input = QComboBox()
        self.category_input.addItems(CATEGORIES)
        self.subcategory_input = QLineEdit()
        self.color_input = QLineEdit()
        self.size_input = QLineEdit()
        self.brand_input = QLineEdit()
        self.description_input = QLineEdit()
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.location_input = QLineEdit()
        self.finder_input = QLineEdit()

        # Then this basically Adds labels beside each input field so staff know what information to enter.
        form.addRow(QLabel("Item Name"), self.name_input)
        form.addRow(QLabel("Category"), self.category_input)
        form.addRow(QLabel("Subcategory"), self.subcategory_input)
        form.addRow(QLabel("Color"), self.color_input)
        form.addRow(QLabel("Size"), self.size_input)
        form.addRow(QLabel("Brand"), self.brand_input)
        form.addRow(QLabel("Description"), self.description_input)
        form.addRow(QLabel("Date Found"), self.date_input)
        form.addRow(QLabel("Location Found"), self.location_input)
        form.addRow(QLabel("Finder Name"), self.finder_input)

        # Creates Save and Cancel buttons and connects them to their respective actions.
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: red;")

        # Arranges the form, error message, and buttons vertically inside the window.
        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(self.status_label)
        layout.addWidget(buttons)

    # Checks the form for errors before allowing the user to save and close the dialog.
    def save(self):
        error = self.validate()
        if error:
            self.status_label.setText(error)
            return
        self.accept()

    # Collects the information entered into the form and returns it as a dictionary for saving.
    def get_item_data(self):
        from PyQt6.QtCore import QDate

        return {
            "item_name": self.name_input.text().strip(),
            "category": self.category_input.currentText(),
            "subcategory": self.subcategory_input.text().strip(),
            "description": self.description_input.text().strip(),
            "color": self.color_input.text().strip(),
            "size": self.size_input.text().strip(),
            "brand": self.brand_input.text().strip(),
            "date_found": self.date_input.date().toString("yyyy-MM-dd"),
            "location_found": self.location_input.text().strip(),
            "finder_name": self.finder_input.text().strip(),
            "photo_path": "",
        }

    # Checks that the item name, location, and finder name are filled in and that the date found is not in the future.
    def validate(self):
        from PyQt6.QtCore import QDate

        if not self.name_input.text().strip():
            return "Item name is required."
        if not self.location_input.text().strip():
            return "Location found is required."
        if not self.finder_input.text().strip():
            return "Finder name is required."
        if self.date_input.date() > QDate.currentDate():
            return "Date found cannot be in the future."
        return ""