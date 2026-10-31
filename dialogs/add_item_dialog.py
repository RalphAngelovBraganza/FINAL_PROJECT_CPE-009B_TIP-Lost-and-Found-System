from PyQt6.QtCore import QDate, Qt
from PyQt6.QtWidgets import (QComboBox, QDateEdit, QDialog, QDialogButtonBox, QFileDialog,
                             QGridLayout, QHBoxLayout, QLabel, QLineEdit, QMessageBox,
                             QPushButton, QTextEdit, QVBoxLayout, QWidget)

from data.store import CATEGORIES, copy_image_to_images


class AddItemDialog(QDialog):  # One dialog for both adding and editing: pass item=None to add, or an item to edit.
    def __init__(self, parent=None, item=None):  # The parent is the page that opened this window.
        super().__init__(parent)
        self.setWindowTitle("Edit Item" if item else "Add Found Item")  # Title changes with the mode.
        self.setMinimumSize(900, 620)
        self.resize(1000, 680)

        self.name_input = QLineEdit()  # Item Name.
        self.name_input.setFixedHeight(36)
        self.name_input.setMaxLength(100)
        self.category_input = QComboBox()  # Category dropdown; starts blank ("All" is for the filter, not the form).
        self.category_input.setFixedHeight(36)
        self.category_input.addItem("")
        self.category_input.addItems(CATEGORIES)  # The 10 categories from data/store.py.
        self.subcategory_input = QLineEdit()  # Optional narrower type, e.g. "Smartphone".
        self.subcategory_input.setFixedHeight(36)
        self.subcategory_input.setMaxLength(100)

        self.description_input = QTextEdit()  # The description box has its own click-through limit below.
        self.description_input.setFixedHeight(80)
        self.description_input.textChanged.connect(self.limit_description)

        self.color_input = QLineEdit()
        self.color_input.setFixedHeight(36)
        self.color_input.setMaxLength(50)
        self.brand_input = QLineEdit()
        self.brand_input.setFixedHeight(36)
        self.brand_input.setMaxLength(50)
        self.size_input = QLineEdit()
        self.size_input.setFixedHeight(36)
        self.size_input.setMaxLength(50)

        self.date_input = QDateEdit()  # The Date Found field.
        self.date_input.setFixedHeight(36)
        self.date_input.setCalendarPopup(True)  # Clicking the arrow opens a real calendar.
        self.date_input.setDisplayFormat("MM/dd/yyyy")  # What the user sees; get_item_data() stores yyyy-MM-dd.
        self.date_input.setMinimumDate(QDate(2020, 1, 1))
        self.date_input.setMaximumDate(QDate.currentDate())  # An item cannot be found in the future.
        self.date_input.setDate(QDate.currentDate())  # Defaults to today.

        self.location_input = QLineEdit()  # Where the item was found; both required below.
        self.location_input.setFixedHeight(36)
        self.location_input.setMaxLength(150)
        self.finder_input = QLineEdit()  # Who found the item.
        self.finder_input.setFixedHeight(36)
        self.finder_input.setMaxLength(100)

        self.photo_input = QLineEdit()  # Photo path row: a read-only path box plus a Browse button.
        self.photo_input.setFixedHeight(36)
        self.photo_input.setReadOnly(True)  # The user only picks a file; nobody types a path by hand.
        self.photo_input.setMaxLength(250)
        self.browse_button = QPushButton("Browse...")
        self.browse_button.setObjectName("browseButton")  # Styled by dialogs.qss.
        photo_row = QHBoxLayout()
        photo_row.setContentsMargins(0, 0, 0, 0)
        photo_row.setSpacing(8)
        photo_row.addWidget(self.photo_input, 1)  # 1 = the path box stretches, the button stays its size.
        photo_row.addWidget(self.browse_button)

        root = QVBoxLayout(self)  # The dialog's outer layout.
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)
        title = QLabel("Found Item Details")
        title.setObjectName("formTitle")  # Styled by dialogs.qss.
        subtitle = QLabel("Enter the item's identifying details and where it was found.")
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

        left.addWidget(self.field("Item Name", self.name_input, True))  # True = required, shown with a red asterisk.
        left.addLayout(self.field_row(("Category", self.category_input, True), ("Subcategory", self.subcategory_input)))
        left.addWidget(self.field("Item Description", self.description_input))
        left.addLayout(self.field_row(("Primary Color", self.color_input), ("Brand", self.brand_input)))

        right.addLayout(self.field_row(("Item Size", self.size_input), ("Date Found", self.date_input, True)))
        right.addWidget(self.field("Location Found", self.location_input, True))
        right.addWidget(self.field("Finder Name", self.finder_input, True))
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
        if item:  # Edit mode: show what the status currently is before the user saves.
            status = QLabel(f"Current Status: {item['status']}")
            status.setObjectName("currentStatusLabel")
            status.setStyleSheet("font-weight: bold;")
            root.addWidget(status)  # The status itself is not editable here; update_item() keeps it.
        root.addLayout(self.action_bar())  # The Cancel / Save row at the bottom.

        self.browse_button.clicked.connect(self.choose_photo)
        if item:
            self.fill_form(item)  # Passing an item fills every field with its saved values.

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
        text = self.description_input.toPlainText()
        if len(text) > 1000:  # The description is capped at 1000 characters.
            position = min(self.description_input.textCursor().position(), 1000)  # The cursor never jumps; keep it where the user was.
            self.description_input.blockSignals(True)  # setPlainText would fire textChanged again; block it so this runs once per keystroke.
            self.description_input.setPlainText(text[:1000])
            cursor = self.description_input.textCursor()
            cursor.setPosition(position)
            self.description_input.setTextCursor(cursor)
            self.description_input.blockSignals(False)

    def fill_form(self, item):  # Copy every saved value into the inputs (edit mode only).
        self.name_input.setText(item["item_name"] or "")
        index = self.category_input.findText(item["category"] or "")
        if index == -1:  # The saved category is not in the dropdown (an old record): add it instead of losing it.
            self.category_input.addItem(item["category"] or "")
            index = self.category_input.count() - 1
        self.category_input.setCurrentIndex(index)
        self.subcategory_input.setText(item["subcategory"] or "")
        self.description_input.setPlainText(item["description"] or "")
        self.color_input.setText(item["color"] or "")
        self.size_input.setText(item["size"] or "")
        self.brand_input.setText(item["brand"] or "")
        saved_date = QDate.fromString(item["date_found"] or "", "yyyy-MM-dd")  # Records store yyyy-MM-dd; QDateEdit shows MM/dd/yyyy.
        if saved_date.isValid():
            self.date_input.setDate(saved_date)
        self.location_input.setText(item["location_found"] or "")
        self.finder_input.setText(item["finder_name"] or "")
        self.photo_input.setText(item["photo_path"] or "")

    def choose_photo(self):  # Opens the file picker and shows the chosen file's path.
        file_path, _ = QFileDialog.getOpenFileName(self, "Choose Photo", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if file_path:
            self.photo_input.setText(file_path)  # The actual copying happens in check_and_accept() when the user saves.

    def check_and_accept(self):  # Refuses to close until every required field passes.
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Missing Information", "Please enter the item name.")
            return
        if not self.category_input.currentText().strip():
            QMessageBox.warning(self, "Missing Information", "Please select the item's category.")
            return
        if not self.location_input.text().strip():
            QMessageBox.warning(self, "Missing Information", "Please enter the location found.")
            return
        if not self.finder_input.text().strip():
            QMessageBox.warning(self, "Missing Information", "Please enter the finder's name.")
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

    def get_item_data(self):  # get_data() in the reference; renamed to get_item_data() so the group's items page calls match.
        return {
            "item_name": self.name_input.text().strip(),
            "category": self.category_input.currentText(),
            "subcategory": self.subcategory_input.text().strip(),
            "description": self.description_input.toPlainText().strip(),
            "color": self.color_input.text().strip(),
            "size": self.size_input.text().strip(),
            "brand": self.brand_input.text().strip(),
            "date_found": self.date_input.date().toString("yyyy-MM-dd"),  # Stored in the ISO format the records use.
            "location_found": self.location_input.text().strip(),
            "finder_name": self.finder_input.text().strip(),
            "photo_path": self.photo_input.text().strip(),
        }
