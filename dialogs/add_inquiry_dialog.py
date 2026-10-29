from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (QComboBox, QDateEdit, QDialog, QDialogButtonBox,
                             QFormLayout, QLabel, QLineEdit, QPlainTextEdit,
                             QVBoxLayout)

from data.store import CATEGORIES


class AddInquiryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Lost-Item Inquiry") 
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

    # Python Methods:
    # strip() - Removes whitespace from the beginning and end of a string.
    # lower() - Converts all letters in a string to lowercase.

    # Custom Methods:
    # validate() - Checks whether the required fields are filled in.
    # save() - Validates the form and accepts the dialog if validation passes.
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
        self.details_input = QPlainTextEdit()  
        self.details_input.setFixedHeight(64) 

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

    def save(self):  # Runs when the Save button is clicked.
        error = self.validate()  # Checks the required fields.
        if error:  # If something is missing or wrong...
            self.status_label.setText(error)  # ...show the message in red and keep the dialog open.
            return
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
            "photo_path": "",  # Photo support is a later stage.
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
