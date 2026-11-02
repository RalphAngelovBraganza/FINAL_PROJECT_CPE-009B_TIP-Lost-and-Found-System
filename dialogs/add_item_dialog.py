from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (QComboBox, QDateEdit, QDialog, QDialogButtonBox, QFileDialog,
                             QGridLayout, QHBoxLayout, QLabel, QLineEdit, QMessageBox,
                             QPushButton, QTextEdit, QVBoxLayout, QWidget)

from data.store import CATEGORIES, copy_image_to_images, window_icon_path


# Collects and validates found item details.
class AddItemDialog(QDialog):

    # Builds the form and connects its controls.
    def __init__(self, parent=None, item=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Item" if item else "Add Found Item")
        self.setWindowIcon(QIcon(window_icon_path("item_form.png")))
        self.setMinimumSize(900, 620)
        self.resize(1000, 680)

        self.name_input = QLineEdit()
        self.name_input.setFixedHeight(36)
        self.name_input.setMaxLength(100)
        self.category_input = QComboBox()
        self.category_input.setFixedHeight(36)
        self.category_input.addItem("")
        self.category_input.addItems(CATEGORIES)
        self.subcategory_input = QLineEdit()
        self.subcategory_input.setFixedHeight(36)
        self.subcategory_input.setMaxLength(100)

        self.description_input = QTextEdit()
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

        self.date_input = QDateEdit()
        self.date_input.setFixedHeight(36)
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("MM/dd/yyyy")
        self.date_input.setMinimumDate(QDate(2020, 1, 1))
        self.date_input.setMaximumDate(QDate.currentDate())
        self.date_input.setDate(QDate.currentDate())

        self.location_input = QLineEdit()
        self.location_input.setFixedHeight(36)
        self.location_input.setMaxLength(150)
        self.finder_input = QLineEdit()
        self.finder_input.setFixedHeight(36)
        self.finder_input.setMaxLength(100)

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
        title = QLabel("Found Item Details")
        title.setObjectName("formTitle")
        subtitle = QLabel("Enter the item's identifying details and where it was found.")
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

        left.addWidget(self.field("Item Name", self.name_input, True))
        left.addLayout(self.field_row(("Category", self.category_input, True), ("Subcategory", self.subcategory_input)))
        left.addWidget(self.field("Item Description", self.description_input))
        left.addLayout(self.field_row(("Primary Color", self.color_input), ("Brand", self.brand_input)))

        right.addLayout(self.field_row(("Item Size", self.size_input), ("Date Found", self.date_input, True)))
        right.addWidget(self.field("Location Found", self.location_input, True))
        right.addWidget(self.field("Finder Name", self.finder_input, True))
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
        if item:
            status = QLabel(f"Current Status: {item['status']}")
            status.setObjectName("currentStatusLabel")
            status.setStyleSheet("font-weight: bold;")
            root.addWidget(status)
        root.addLayout(self.action_bar())

        self.browse_button.clicked.connect(self.choose_photo)
        if item:
            self.fill_form(item)


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
        text = self.description_input.toPlainText()
        if len(text) > 1000:
            position = min(self.description_input.textCursor().position(), 1000)
            self.description_input.blockSignals(True)
            self.description_input.setPlainText(text[:1000])
            cursor = self.description_input.textCursor()
            cursor.setPosition(position)
            self.description_input.setTextCursor(cursor)
            self.description_input.blockSignals(False)


    # Fills the form with a saved record.
    def fill_form(self, item):
        self.name_input.setText(item["item_name"] or "")
        index = self.category_input.findText(item["category"] or "")
        if index == -1:
            self.category_input.addItem(item["category"] or "")
            index = self.category_input.count() - 1
        self.category_input.setCurrentIndex(index)
        self.subcategory_input.setText(item["subcategory"] or "")
        self.description_input.setPlainText(item["description"] or "")
        self.color_input.setText(item["color"] or "")
        self.size_input.setText(item["size"] or "")
        self.brand_input.setText(item["brand"] or "")
        saved_date = QDate.fromString(item["date_found"] or "", "yyyy-MM-dd")
        if saved_date.isValid():
            self.date_input.setDate(saved_date)
        self.location_input.setText(item["location_found"] or "")
        self.finder_input.setText(item["finder_name"] or "")
        self.photo_input.setText(item["photo_path"] or "")


    # Lets the user choose a photo.
    def choose_photo(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Choose Photo", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if file_path:
            self.photo_input.setText(file_path)


    # Validates the form before accepting it.
    def check_and_accept(self):
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
                photo_path = copy_image_to_images(photo_path)
            except OSError as error:
                QMessageBox.warning(self, "Photo Error", f"The photo could not be copied.\n\n{error}")
                return
            self.photo_input.setText(photo_path)
        self.accept()


    # Returns the item details entered in the form.
    def get_item_data(self):
        return {
            "item_name": self.name_input.text().strip(),
            "category": self.category_input.currentText(),
            "subcategory": self.subcategory_input.text().strip(),
            "description": self.description_input.toPlainText().strip(),
            "color": self.color_input.text().strip(),
            "size": self.size_input.text().strip(),
            "brand": self.brand_input.text().strip(),
            "date_found": self.date_input.date().toString("yyyy-MM-dd"),
            "location_found": self.location_input.text().strip(),
            "finder_name": self.finder_input.text().strip(),
            "photo_path": self.photo_input.text().strip(),
        }
