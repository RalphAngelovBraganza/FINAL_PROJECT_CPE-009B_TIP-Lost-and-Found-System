from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (QComboBox, QDialog, QFormLayout, QDateEdit, QDialogButtonBox,
                             QFileDialog, QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QVBoxLayout)

from data.store import CATEGORIES, copy_image_to_images


class AddItemDialog(QDialog):
    # Initializes the Add Item window, creates the input fields for item details, and arranges them into a form.
    # It also adds Save and Cancel buttons and a label for displaying error messages.
    # in simple terms this is basically the pop up window when you click the add item button in the main window.
    # The same window is reused for editing: when an existing item is passed in, every field is filled
    # with that item's current values and the Save button updates the record instead of creating one.
    def __init__(self, parent=None, item=None):
        super().__init__(parent)
        self.item = item  # None when adding, the record being edited when editing.
        self.setWindowTitle("Edit Found Item" if item else "Add Found Item")
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
        self.date_input.setDate(QDate.currentDate())  # Defaults to today.
        self.date_input.setMaximumDate(QDate.currentDate())  # An item cannot be found in the future.
        self.location_input = QLineEdit()
        self.finder_input = QLineEdit()

        # The photo row is a read-only textbox plus a Browse button. The user never types a path by hand,
        # and the chosen file is copied into the project's images folder when the form is saved.
        self.photo_input = QLineEdit()
        self.photo_input.setReadOnly(True)
        self.browse_button = QPushButton("Browse...")
        photo_row = QHBoxLayout()
        photo_row.setContentsMargins(0, 0, 0, 0)
        photo_row.setSpacing(8)
        photo_row.addWidget(self.photo_input, 1)
        photo_row.addWidget(self.browse_button)

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
        form.addRow(QLabel("Photo"), photo_row)

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

        self.browse_button.clicked.connect(self.choose_photo)  # Opens the file picker.

        if item:  # Editing, so show the item's saved values.
            self.fill_form(item)

    # Opens a file picker limited to image files and puts the chosen path in the read-only textbox.
    def choose_photo(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Choose Photo", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if file_path:
            self.photo_input.setText(file_path)

    # Copies the item's current values into the form fields.
    def fill_form(self, item):
        self.name_input.setText(item.get("item_name", ""))
        index = self.category_input.findText(item.get("category", ""))  # Finds the category in the dropdown.
        if index >= 0:
            self.category_input.setCurrentIndex(index)
        self.subcategory_input.setText(item.get("subcategory", ""))
        self.color_input.setText(item.get("color", ""))
        self.size_input.setText(item.get("size", ""))
        self.brand_input.setText(item.get("brand", ""))
        self.description_input.setText(item.get("description", ""))
        saved_date = QDate.fromString(item.get("date_found", ""), "yyyy-MM-dd")  # The JSON stores dates as text.
        if saved_date.isValid():
            self.date_input.setDate(saved_date)
        self.location_input.setText(item.get("location_found", ""))
        self.finder_input.setText(item.get("finder_name", ""))
        self.photo_input.setText(item.get("photo_path", ""))

    # Checks the form for errors before allowing the user to save and close the dialog.
    def save(self):
        error = self.validate()
        if error:
            self.status_label.setText(error)
            return

        # Photos picked from another folder are copied into the images folder so the record keeps
        # working even if the original file is moved or deleted. A photo that already lives inside
        # that folder, like when the user edits an item without changing the photo, is left alone.
        photo_path = self.photo_input.text().strip()
        if photo_path and not photo_path.replace("\\", "/").startswith("images/"):
            try:
                photo_path = copy_image_to_images(photo_path)  # Returns the new path inside images/.
            except OSError:
                self.status_label.setText("The photo could not be copied.")
                return
            self.photo_input.setText(photo_path)

        self.accept()

    # Collects the information entered into the form and returns it as a dictionary for saving.
    def get_item_data(self):
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
            "photo_path": self.photo_input.text().strip(),
        }

    # Checks that the item name, location, and finder name are filled in and that the date found is not in the future.
    def validate(self):
        if not self.name_input.text().strip():
            return "Item name is required."
        if not self.location_input.text().strip():
            return "Location found is required."
        if not self.finder_input.text().strip():
            return "Finder name is required."
        if self.date_input.date() > QDate.currentDate():
            return "Date found cannot be in the future."
        return ""
