from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (QComboBox, QDateEdit, QDialog, QDialogButtonBox, QFileDialog,
                             QFormLayout, QHBoxLayout, QLabel, QLineEdit, QPlainTextEdit,
                             QPushButton, QVBoxLayout)

from data.store import CATEGORIES, copy_image_to_images


class AddInquiryDialog(QDialog):
    # The same window is used for adding and editing. When an existing inquiry is passed in, the
    # fields are filled with its saved values and the Save button updates that record.
    def __init__(self, parent=None, inquiry=None):
        super().__init__(parent)
        self.inquiry = inquiry  # None when adding, the record being edited when editing.
        self.setWindowTitle("Edit Lost-Item Inquiry" if inquiry else "Add Lost-Item Inquiry")
        self.setMinimumWidth(480)

        form = QFormLayout()  # The form layout: one label beside one input, row by row.
        form.setSpacing(10)  # Space between rows.


    # PyQt6 Methods used for familiarization:
    # setWindowTitle() - Sets the window title.
    # setMinimumWidth() - Sets the minimum window width.
    # setSpacing() - Sets the spacing between layout rows.
    # addItem() / addItems() - Adds choices to a dropdown menu.
    # setCalendarPopup() - Enables the calendar popup.
    # setDate() / setMaximumDate() - Sets the initial date and restricts the latest selectable date.
    # addRow() / addWidget() / addLayout() - Arranges widgets and layouts.
    # connect() - Connects a signal or event to a method.
    # accept() / reject() - Accepts or rejects the dialog.
    # text() / toPlainText() - Retrieves text entered into input widgets.
    # currentText() / date() - Retrieves the selected dropdown text or date.
    # toString() - Converts a QDate into formatted text.
    # getOpenFileName() - Opens the file picker used for choosing a photo.

    # Python Methods:
    # strip() - Removes whitespace from the beginning and end of a string.
    # lower() - Converts all letters in a string to lowercase.

    # Custom Methods:
    # validate() - Checks whether the required fields are filled in.
    # save() - Validates the form, copies the chosen photo, and accepts the dialog if everything is fine.
    # choose_photo() - Opens the file picker and stores the chosen photo path.
    # fill_form() - Puts an existing inquiry's values back into the input fields when editing.
    # get_data() - Collects the form values and returns them as a dictionary.



        #highly referenced from Ralph's code in add_item_dialog.py, but I changed the input fields to match the lost item inquiry form.
        # This block of code is basically where the input fields are created for the add inquiry dialog, where students can enter information about their lost item.
        self.student_input = QLineEdit()  # added a textbox for the student's name.
        self.email_input = QLineEdit()  #  added a textbox for the student's T.I.P. email.
        self.item_name_input = QLineEdit()  # added a textbox for the lost item's name.
        self.category_input = QComboBox()  # Dropdown for the item's category.
        self.category_input.addItem("")  # Starts blank so the user must pick a category.
        self.category_input.addItems(CATEGORIES)  # Fills dropdown with the shared CATEGORIES list.
        self.description_input = QPlainTextEdit()  #
        self.description_input.setFixedHeight(64)  # Keeps the description box short.
        self.color_input = QLineEdit()  # added a textbox for the item's color.
        self.size_input = QLineEdit()  # added a textbox for the item's size.
        self.brand_input = QLineEdit()  # added a textbox for the item's brand.
        self.date_input = QDateEdit()  # Calendar input for the date the item was lost.
        self.date_input.setCalendarPopup(True)  # Shows the dropdown calendar.
        self.date_input.setDate(QDate.currentDate())  # I fixed the default date to today
         # I made sure the user can't pick a future date for when the item was lost (that wont make sense)
        self.date_input.setMaximumDate(QDate.currentDate())
        self.location_input = QLineEdit()  # Textbox for where the item was last seen.
        self.details_input = QPlainTextEdit()  #
        self.details_input.setFixedHeight(64)

        # The photo row works like the one in the Add Item form: a read-only textbox and a Browse button.
        # The student's photo is copied into the project's images folder when the inquiry is saved.
        self.photo_input = QLineEdit()
        self.photo_input.setReadOnly(True)
        self.browse_button = QPushButton("Browse...")
        photo_row = QHBoxLayout()
        photo_row.setContentsMargins(0, 0, 0, 0)
        photo_row.setSpacing(8)
        photo_row.addWidget(self.photo_input, 1)
        photo_row.addWidget(self.browse_button)

        # Adds each input field to the form, placing its label beside the corresponding input widget.
        form.addRow(QLabel("Student Name"), self.student_input)
        form.addRow(QLabel("T.I.P. Email"), self.email_input)
        form.addRow(QLabel("Item Name"), self.item_name_input)
        form.addRow(QLabel("Category"), self.category_input)
        form.addRow(QLabel("Item Description"), self.description_input)
        form.addRow(QLabel("Color"), self.color_input)
        form.addRow(QLabel("Size"), self.size_input)
        form.addRow(QLabel("Brand"), self.brand_input)
        form.addRow(QLabel("Date Lost"), self.date_input)
        form.addRow(QLabel("Last Seen Location"), self.location_input)
        form.addRow(QLabel("Additional Details"), self.details_input)
        form.addRow(QLabel("Photo"), photo_row)


        #I just copied the same logic from ralph
        # Creates Save and Cancel buttons and connects them to their respective actions.
        # Basically if you click either save or canel, it will either save the information you entered or close the window without saving.
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)

        self.status_label = QLabel("")  # Shows validation errors in red instead of closing the dialog.
        self.status_label.setStyleSheet("color: red;")

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(self.status_label)
        layout.addWidget(buttons)

        self.browse_button.clicked.connect(self.choose_photo)  # Opens the file picker.

        if inquiry:  # Editing, so show the inquiry's saved values.
            self.fill_form(inquiry)

    # Opens a file picker limited to image files and puts the chosen path in the read-only textbox.
    def choose_photo(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Choose Photo", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if file_path:
            self.photo_input.setText(file_path)

    # Copies an existing inquiry's values into the form fields when the user edits it.
    def fill_form(self, inquiry):
        self.student_input.setText(inquiry.get("student_name", ""))
        self.email_input.setText(inquiry.get("tip_email", ""))
        self.item_name_input.setText(inquiry.get("item_name", ""))
        self.description_input.setPlainText(inquiry.get("item_description", ""))
        index = self.category_input.findText(inquiry.get("category", ""))  # Finds the category in the dropdown.
        if index >= 0:
            self.category_input.setCurrentIndex(index)
        self.color_input.setText(inquiry.get("color", ""))
        self.size_input.setText(inquiry.get("size", ""))
        self.brand_input.setText(inquiry.get("brand", ""))
        saved_date = QDate.fromString(inquiry.get("date_lost", ""), "yyyy-MM-dd")  # The JSON stores dates as text.
        if saved_date.isValid():
            self.date_input.setDate(saved_date)
        self.location_input.setText(inquiry.get("location_last_seen", ""))
        self.details_input.setPlainText(inquiry.get("additional_details", ""))
        self.photo_input.setText(inquiry.get("photo_path", ""))

    def save(self):  # Runs when the Save button is clicked.
        error = self.validate()  # Checks the required fields.
        if error:  # If something is missing or wrong...
            self.status_label.setText(error)  # ...show the message in red and keep the dialog open.
            return

        # Photos chosen from another folder are copied into the images folder so the record keeps
        # working even if the original file is moved. A photo that is already inside that folder
        # (for example when editing without changing it) is left as is.
        photo_path = self.photo_input.text().strip()
        if photo_path and not photo_path.replace("\\", "/").startswith("images/"):
            try:
                photo_path = copy_image_to_images(photo_path)  # Returns the new path inside images/.
            except OSError:
                self.status_label.setText("The photo could not be copied.")
                return
            self.photo_input.setText(photo_path)

        self.accept()  # Everything is valid, so close and confirm.

    def get_data(self):  # Collects everything typed into the form as one dictionary.
        return {
            "student_name": self.student_input.text().strip(),
            "tip_email": self.email_input.text().strip().lower(),  # Emails are stored in lowercase so that searches are case-insensitive.
            "item_name": self.item_name_input.text().strip(),
            "item_description": self.description_input.toPlainText().strip(),
            "category": self.category_input.currentText(),
            "color": self.color_input.text().strip(),
            "size": self.size_input.text().strip(),
            "brand": self.brand_input.text().strip(),
            "date_lost": self.date_input.date().toString("yyyy-MM-dd"),
            "location_last_seen": self.location_input.text().strip(),
            "additional_details": self.details_input.toPlainText().strip(),
            "photo_path": self.photo_input.text().strip(),
        }

    def validate(self):  # Returns an error message, or "" when everything is filled in correctly.
        if not self.student_input.text().strip():
            return "Student name is required."
        if not self.email_input.text().strip():
            return "Email is required."
        if not self.item_name_input.text().strip():
            return "Item name is required."
        if not self.category_input.currentText().strip():
            return "Category is required."
        if not self.description_input.toPlainText().strip():
            return "Item description is required."
        return ""
