from PyQt6.QtCore import QDate, Qt
from PyQt6.QtWidgets import (QComboBox, QDateEdit, QDialog, QDialogButtonBox, QFileDialog,
                             QGridLayout, QHBoxLayout, QLabel, QLineEdit, QMessageBox,
                             QPushButton, QTextEdit, QVBoxLayout, QWidget)

from data.store import CATEGORIES, copy_image_to_images


class AddInquiryDialog(QDialog):  # One dialog for both adding and editing: pass inquiry=None to add, or an inquiry to edit.
    def __init__(self, parent=None, inquiry=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Lost-Item Inquiry" if inquiry else "Add Lost-Item Inquiry")  # Title changes with the mode.
        self.setMinimumSize(900, 640)
        self.resize(1000, 700)

        self.student_input = QLineEdit()  # Student Name.
        self.student_input.setFixedHeight(36)
        pass
        self.student_input.setMaxLength(100)
        self.email_input = QLineEdit()  # The student's T.I.P. email.
        self.email_input.setFixedHeight(36)
        pass
        self.email_input.setMaxLength(150)

        self.item_name_input = QLineEdit()  # The lost item's name.
        self.item_name_input.setFixedHeight(36)
        self.item_name_input.setMaxLength(150)

        self.description_input = QTextEdit()  # The description box has its own click-through limit below.
        self.description_input.setFixedHeight(80)
        self.description_input.textChanged.connect(self.limit_description)

        self.category_input = QComboBox()  # Category dropdown; starts blank.
        self.category_input.setFixedHeight(36)
        self.category_input.addItem("")
        self.category_input.addItems(CATEGORIES)  # The 10 categories from data/store.py.

        self.date_input = QDateEdit()  # The Date Lost field.
        self.date_input.setFixedHeight(36)
        self.date_input.setCalendarPopup(True)  # Clicking the arrow opens a real calendar.
        self.date_input.setDisplayFormat("MM/dd/yyyy")
        self.date_input.setMinimumDate(QDate(2020, 1, 1))
        self.date_input.setMaximumDate(QDate.currentDate())  # An inquiry cannot be dated in the future.
        self.date_input.setDate(QDate.currentDate())  # Defaults to today.

        self.color_input = QLineEdit()  # Optional identifying details.
        self.color_input.setFixedHeight(36)
        self.color_input.setMaxLength(50)
        self.brand_input = QLineEdit()
        self.brand_input.setFixedHeight(36)
        self.brand_input.setMaxLength(50)
        self.size_input = QLineEdit()
        self.size_input.setFixedHeight(36)
        self.size_input.setMaxLength(50)
        self.location_input = QLineEdit()  # Where the item was last seen; optional, so the box opens blank.
        self.location_input.setFixedHeight(36)
        self.location_input.setMaxLength(150)
        self.details_input = QTextEdit()
        self.details_input.setFixedHeight(80)
        self.details_input.textChanged.connect(self.limit_details)

        self.photo_input = QLineEdit()  # Photo path row: a read-only path box plus a Browse button.
        self.photo_input.setFixedHeight(36)
        self.photo_input.setReadOnly(True)
        self.photo_input.setMaxLength(250)
        self.browse_button = QPushButton("Browse...")
        self.browse_button.setObjectName("browseButton")  # Styled by dialogs.qss.
        photo_row = QHBoxLayout()
        photo_row.setContentsMargins(0, 0, 0, 0)
        photo_row.setSpacing(8)
        photo_row.addWidget(self.photo_input, 1)  # 1 = the path box stretches, the button keeps its size.
        photo_row.addWidget(self.browse_button)

        root = QVBoxLayout(self)  # The dialog's outer layout.
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)

        title = QLabel("Lost Item Inquiry & Details")
        title.setObjectName("formTitle")  # Styled by dialogs.qss.
        subtitle = QLabel("Update the student's contact and lost-item details." if inquiry else "Fill in the student's contact and lost-item details to submit a new inquiry.")
        subtitle.setObjectName("formSubtitle")
        root.addWidget(title)
        root.addWidget(subtitle)

        # The form is built as two vertical columns side by side; field() and field_row()
        # below pair each label with its input and lay two fields out in one row.
        columns = QGridLayout()
        columns.setHorizontalSpacing(24)
        columns.setVerticalSpacing(12)
        left = QVBoxLayout()  # Column 1.
        right = QVBoxLayout()  # Column 2.
        left.setSpacing(10)
        right.setSpacing(10)

        left.addWidget(self.field("Student Name", self.student_input, True))  # True = required, shown with a red asterisk.
        left.addLayout(self.field_row(
            ("Category", self.category_input, True), ("Email", self.email_input, True)))
        left.addWidget(self.field("Item Name", self.item_name_input, True))
        left.addWidget(self.field("Item Description", self.description_input, True))
        left.addLayout(self.field_row(("Color", self.color_input), ("Brand", self.brand_input)))

        right.addLayout(self.field_row(("Size", self.size_input), ("Date Lost", self.date_input, True)))
        right.addWidget(self.field("Last Seen Location", self.location_input))
        right.addWidget(self.field("Additional Details", self.details_input))
        right.addWidget(self.field("Photo Attachment", photo_row))  # A row layout can be passed to field() like a widget.
        left.addStretch(1)  # Keeps both columns aligned at the top when the window grows.
        right.addStretch(1)

        columns.addLayout(left, 0, 0)  # Column 0.
        columns.addLayout(right, 0, 1)  # Column 1.
        columns.setColumnStretch(0, 1)
        columns.setColumnStretch(1, 1)
        root.addLayout(columns)
        root.addStretch(1)

        required_note = QLabel("* Required")
        required_note.setObjectName("requiredNote")  # Styled by dialogs.qss.
        root.addWidget(required_note)
        root.addLayout(self.action_bar())  # The Cancel / Save row at the bottom.

        self.browse_button.clicked.connect(self.choose_photo)
        if inquiry:
            self.fill_form(inquiry)  # Passing an inquiry fills every field with its saved values.

    def field(self, label_text, widget, required=False):  # Pairs one label with one input; returns a container QWidget.
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        label = QLabel(f"{label_text} <span style='color:#d93025'>*</span>" if required else label_text)  # Required fields get a red asterisk after the label.
        label.setObjectName("formFieldLabel")  # Styled by dialogs.qss.
        label.setStyleSheet("font-weight: bold;")
        if required:
            label.setTextFormat(Qt.TextFormat.RichText)  # The asterisk is an HTML span, so the label must render rich text.
        if isinstance(widget, QTextEdit):  # Tall text boxes take their label at the top-left.
            label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        layout.addWidget(label)
        if isinstance(widget, QHBoxLayout):  # The photo row is a layout, not a widget.
            layout.addLayout(widget)
        else:
            layout.addWidget(widget)
        return container

    def field_row(self, *fields):  # Puts two (or more) fields side by side in one row; each field is a tuple for field().
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(12)
        for field_data in fields:
            row.addWidget(self.field(*field_data), 1)  # 1 = the two fields share the row width evenly.
        return row

    def action_bar(self):  # Builds the Cancel / Save button row.
        bar = QHBoxLayout()
        bar.addStretch()  # Pushes both buttons to the right edge.
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Save)
        buttons.button(QDialogButtonBox.StandardButton.Save).setObjectName("primaryFormButton")  # Yellow Save, styled by dialogs.qss.
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setObjectName("secondaryFormButton")  # Red Cancel.
        buttons.accepted.connect(self.check_and_accept)  # Save runs the validation first.
        buttons.rejected.connect(self.reject)  # Cancel closes without saving.
        bar.addWidget(buttons)
        return bar

    def limit_description(self):  # Runs on every keystroke in the description box.
        self.limit_text(self.description_input, 1000)

    def limit_details(self):  # Same cap for the additional details box.
        self.limit_text(self.details_input, 1000)

    def limit_text(self, field, limit):  # Shared worker: caps a QTextEdit at `limit` characters while typing.
        text = field.toPlainText()
        if len(text) > limit:
            position = min(field.textCursor().position(), limit)  # The cursor never jumps; keep it where the user was.
            field.blockSignals(True)  # setPlainText would fire textChanged again; block it so this runs once per keystroke.
            field.setPlainText(text[:limit])
            cursor = field.textCursor()
            cursor.setPosition(position)
            field.setTextCursor(cursor)
            field.blockSignals(False)

    def choose_photo(self):  # Opens the file picker and shows the chosen file's path.
        file_path, _ = QFileDialog.getOpenFileName(self, "Choose Photo", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if file_path:
            self.photo_input.setText(file_path)  # The actual copying happens in check_and_accept() when the user saves.

    def check_and_accept(self):  # Refuses to close until every required field passes.
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
                photo_path = copy_image_to_images(photo_path)  # Copies the photo into images/ so the record keeps working if the original is moved or deleted.
            except OSError as error:
                QMessageBox.warning(self, "Photo Error", f"The photo could not be copied.\n\n{error}")
                return  # Not accepted: the user can pick a different photo or save without one.
            self.photo_input.setText(photo_path)  # The stored path is the copy inside images/, not the original.
        self.accept()  # All checks passed: close with Accepted, which the page treats as "save".

    def fill_form(self, inquiry):  # Copy every saved value into the inputs (edit mode only).
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
        self.date_input.setDate(QDate.fromString(inquiry.get("date_lost", ""), "yyyy-MM-dd"))  # Records store yyyy-MM-dd; QDateEdit shows MM/dd/yyyy.
        self.location_input.setText(inquiry.get("location_last_seen", ""))
        self.details_input.setPlainText(inquiry.get("additional_details", ""))
        self.photo_input.setText(inquiry.get("photo_path", ""))

    def get_data(self):  # Called by the page after exec() returns Accepted.
        date_lost = self.date_input.date().toString("yyyy-MM-dd")  # Stored in the ISO format the records use.
        return {
            "student_name": self.student_input.text().strip(),
            "tip_email": self.email_input.text().strip().lower(),  # Emails are stored lowercase.
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
