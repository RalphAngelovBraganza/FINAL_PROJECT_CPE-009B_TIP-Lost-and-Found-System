from PyQt6.QtCore import QDate, Qt
from PyQt6.QtWidgets import (QComboBox, QDateEdit, QDialog, QDialogButtonBox, QFileDialog,
                             QGridLayout, QHBoxLayout, QLabel, QLineEdit, QMessageBox,
                             QPushButton, QTextEdit, QVBoxLayout, QWidget)

from data.store import CATEGORIES, copy_image_to_images


# Collects and validates lost item inquiry details.
class AddInquiryDialog(QDialog):

    # Builds the form and connects its controls.
    def __init__(self, parent=None, inquiry=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Lost-Item Inquiry" if inquiry else "Add Lost-Item Inquiry")
        self.setMinimumSize(900, 640)
        self.resize(1000, 700)

        self.student_input = QLineEdit()
        self.student_input.setFixedHeight(36)
        pass
        self.student_input.setMaxLength(100)
        self.email_input = QLineEdit()
        self.email_input.setFixedHeight(36)
        pass
        self.email_input.setMaxLength(150)

        self.item_name_input = QLineEdit()
        self.item_name_input.setFixedHeight(36)
        self.item_name_input.setMaxLength(150)

        self.description_input = QTextEdit()
        self.description_input.setFixedHeight(80)
        self.description_input.textChanged.connect(self.limit_description)

        self.category_input = QComboBox()
        self.category_input.setFixedHeight(36)
        self.category_input.addItem("")
        self.category_input.addItems(CATEGORIES)

        self.date_input = QDateEdit()
        self.date_input.setFixedHeight(36)
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("MM/dd/yyyy")
        self.date_input.setMinimumDate(QDate(2020, 1, 1))
        self.date_input.setMaximumDate(QDate.currentDate())
        self.date_input.setDate(QDate.currentDate())

        self.color_input = QLineEdit()
        self.color_input.setFixedHeight(36)
        self.color_input.setMaxLength(50)
        self.brand_input = QLineEdit()
        self.brand_input.setFixedHeight(36)
        self.brand_input.setMaxLength(50)
        self.size_input = QLineEdit()
        self.size_input.setFixedHeight(36)
        self.size_input.setMaxLength(50)
        self.location_input = QLineEdit()
        self.location_input.setFixedHeight(36)
        self.location_input.setMaxLength(150)
        self.details_input = QTextEdit()
        self.details_input.setFixedHeight(80)
        self.details_input.textChanged.connect(self.limit_details)

        self.photo_input = QLineEdit()
        self.photo_input.setFixedHeight(36)
        self.photo_input.setReadOnly(True)
        self.photo_input.setMaxLength(250)
        self.browse_button = QPushButton("Browse...")
        self.browse_button.setObjectName("browseButton")
        photo_row = QHBoxLayout()
        photo_row.setContentsMargins(0, 0, 0, 0)
        photo_row.setSpacing(8)
        photo_row.addWidget(self.photo_input, 1)
        photo_row.addWidget(self.browse_button)

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)

        title = QLabel("Lost Item Inquiry & Details")
        title.setObjectName("formTitle")
        subtitle = QLabel("Update the student's contact and lost-item details." if inquiry else "Fill in the student's contact and lost-item details to submit a new inquiry.")
        subtitle.setObjectName("formSubtitle")
        root.addWidget(title)
        root.addWidget(subtitle)


        columns = QGridLayout()
        columns.setHorizontalSpacing(24)
        columns.setVerticalSpacing(12)
        left = QVBoxLayout()
        right = QVBoxLayout()
        left.setSpacing(10)
        right.setSpacing(10)

        left.addWidget(self.field("Student Name", self.student_input, True))
        left.addLayout(self.field_row(
            ("Category", self.category_input, True), ("Email", self.email_input, True)))
        left.addWidget(self.field("Item Name", self.item_name_input, True))
        left.addWidget(self.field("Item Description", self.description_input, True))
        left.addLayout(self.field_row(("Color", self.color_input), ("Brand", self.brand_input)))

        right.addLayout(self.field_row(("Size", self.size_input), ("Date Lost", self.date_input, True)))
        right.addWidget(self.field("Last Seen Location", self.location_input))
        right.addWidget(self.field("Additional Details", self.details_input))
        right.addWidget(self.field("Photo Attachment", photo_row))
        left.addStretch(1)
        right.addStretch(1)

        columns.addLayout(left, 0, 0)
        columns.addLayout(right, 0, 1)
        columns.setColumnStretch(0, 1)
        columns.setColumnStretch(1, 1)
        root.addLayout(columns)
        root.addStretch(1)

        required_note = QLabel("* Required")
        required_note.setObjectName("requiredNote")
        root.addWidget(required_note)
        root.addLayout(self.action_bar())

        self.browse_button.clicked.connect(self.choose_photo)
        if inquiry:
            self.fill_form(inquiry)


    # Pairs a form label with its input.
    def field(self, label_text, widget, required=False):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        label = QLabel(f"{label_text} <span style='color:#d93025'>*</span>" if required else label_text)
        label.setObjectName("formFieldLabel")
        label.setStyleSheet("font-weight: bold;")
        if required:
            label.setTextFormat(Qt.TextFormat.RichText)
        if isinstance(widget, QTextEdit):
            label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        layout.addWidget(label)
        if isinstance(widget, QHBoxLayout):
            layout.addLayout(widget)
        else:
            layout.addWidget(widget)
        return container


    # Places related form fields side by side.
    def field_row(self, *fields):
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(12)
        for field_data in fields:
            row.addWidget(self.field(*field_data), 1)
        return row


    # Builds the dialog action buttons.
    def action_bar(self):
        bar = QHBoxLayout()
        bar.addStretch()
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Save)
        buttons.button(QDialogButtonBox.StandardButton.Save).setObjectName("primaryFormButton")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setObjectName("secondaryFormButton")
        buttons.accepted.connect(self.check_and_accept)
        buttons.rejected.connect(self.reject)
        bar.addWidget(buttons)
        return bar


    # Keeps the description within its length limit.
    def limit_description(self):
        self.limit_text(self.description_input, 1000)


    # Keeps details within their length limit.
    def limit_details(self):
        self.limit_text(self.details_input, 1000)


    # Keeps text within the allowed length.
    def limit_text(self, field, limit):
        text = field.toPlainText()
        if len(text) > limit:
            position = min(field.textCursor().position(), limit)
            field.blockSignals(True)
            field.setPlainText(text[:limit])
            cursor = field.textCursor()
            cursor.setPosition(position)
            field.setTextCursor(cursor)
            field.blockSignals(False)


    # Lets the user choose a photo.
    def choose_photo(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Choose Photo", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if file_path:
            self.photo_input.setText(file_path)


    # Validates the form before accepting it.
    def check_and_accept(self):
        if not self.student_input.text().strip():
            QMessageBox.warning(self, "Missing Information", "Please enter the student's name.")
            return
        if not self.item_name_input.text().strip():
            QMessageBox.warning(self, "Missing Information", "Please provide the item name.")
            self.item_name_input.setFocus()
            return
        email = self.email_input.text().strip()
        if not email:
            QMessageBox.warning(self, "Invalid Email", "Please enter an email address.")
            return
        if not self.description_input.toPlainText().strip():
            QMessageBox.warning(self, "Missing Information", "Please describe the lost item.")
            return
        if not self.category_input.currentText().strip():
            QMessageBox.warning(self, "Missing Information", "Please select the item's category.")
            return
        photo_path = self.photo_input.text().strip()
        if photo_path:
            try:
                photo_path = copy_image_to_images(photo_path)
            except OSError as error:
                QMessageBox.warning(self, "Photo Error", f"The photo could not be copied.\n\n{error}")
                return
            self.photo_input.setText(photo_path)
        self.accept()


    # Fills the form with a saved record.
    def fill_form(self, inquiry):
        self.student_input.setText(inquiry.get("student_name", ""))
        self.email_input.setText(inquiry.get("tip_email", ""))
        self.item_name_input.setText(inquiry.get("item_name", ""))
        self.description_input.setPlainText(inquiry.get("item_description", ""))
        index = self.category_input.findText(inquiry.get("category", ""))
        if index >= 0:
            self.category_input.setCurrentIndex(index)
        self.color_input.setText(inquiry.get("color", ""))
        self.brand_input.setText(inquiry.get("brand", ""))
        self.size_input.setText(inquiry.get("size", ""))
        self.date_input.setDate(QDate.fromString(inquiry.get("date_lost", ""), "yyyy-MM-dd"))
        self.location_input.setText(inquiry.get("location_last_seen", ""))
        self.details_input.setPlainText(inquiry.get("additional_details", ""))
        self.photo_input.setText(inquiry.get("photo_path", ""))


    # Returns the values entered in the form.
    def get_data(self):
        date_lost = self.date_input.date().toString("yyyy-MM-dd")
        return {
            "student_name": self.student_input.text().strip(),
            "tip_email": self.email_input.text().strip().lower(),
            "item_name": self.item_name_input.text().strip(),
            "item_description": self.description_input.toPlainText().strip(),
            "category": self.category_input.currentText(),
            "color": self.color_input.text().strip(),
            "size": self.size_input.text().strip(),
            "brand": self.brand_input.text().strip(),
            "date_lost": date_lost,
            "location_last_seen": self.location_input.text().strip(),
            "additional_details": self.details_input.toPlainText().strip(),
            "photo_path": self.photo_input.text().strip(),
        }
