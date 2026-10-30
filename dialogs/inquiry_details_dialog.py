import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (QDialog, QDialogButtonBox, QFormLayout, QFrame, QHBoxLayout,
                             QLabel, QLineEdit, QPlainTextEdit, QScrollArea, QVBoxLayout,
                             QWidget)

from data.store import BASE_DIR, format_record_id


class InquiryDetailsDialog(QDialog):
    # A read-only window that shows one lost-item inquiry in full: the student's photo on the left
    # and every saved detail on the right. Status changes and edits are done on the inquiries page.
    def __init__(self, inquiry, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Inquiry Details")
        self.setMinimumSize(900, 620)

        content = QHBoxLayout()
        content.setContentsMargins(16, 16, 16, 12)
        content.setSpacing(24)

        # The photo area keeps a fixed size so the window does not jump around when there is no photo.
        self.photo_label = QLabel()
        self.photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.photo_label.setFixedSize(320, 400)
        self.photo_label.setStyleSheet("background-color: white; border: 1px solid #dddddd;")
        self.show_photo(inquiry.get("photo_path", ""))

        photo_box = QVBoxLayout()
        photo_box.setContentsMargins(0, 0, 0, 0)
        photo_box.addStretch()
        photo_box.addWidget(self.photo_label, 0, Qt.AlignmentFlag.AlignCenter)
        photo_box.addStretch()
        content.addLayout(photo_box)

        # Every row is a label plus a read-only box, so the values look like a form the user can read but not type in.
        form = QFormLayout()
        form.setSpacing(10)
        fields = [
            ("Inquiry ID", format_record_id("INQ", inquiry.get("date_reported"), inquiry.get("inquiry_id"))),
            ("Student Name", inquiry.get("student_name", "")),
            ("T.I.P. Email", inquiry.get("tip_email", "")),
            ("Item Name", inquiry.get("item_name", "")),
            ("Category", inquiry.get("category", "")),
            ("Color", inquiry.get("color", "")),
            ("Size", inquiry.get("size", "")),
            ("Brand", inquiry.get("brand", "")),
            ("Date Lost", inquiry.get("date_lost", "")),
            ("Last Seen Location", inquiry.get("location_last_seen", "")),
            ("Date Reported", inquiry.get("date_reported", "")),
            ("Status", inquiry.get("status", "")),
        ]

        for label_text, value_text in fields:
            value = QLineEdit()  # Read-only textbox for a single line of detail.
            value.setReadOnly(True)
            value.setText(str(value_text or ""))
            value.setFixedHeight(32)
            form.addRow(QLabel(label_text + ":"), value)

        # The two long text fields get taller boxes because they can hold whole paragraphs.
        self.description_input = QPlainTextEdit()
        self.description_input.setReadOnly(True)
        self.description_input.setPlainText(inquiry.get("item_description", ""))
        self.description_input.setFixedHeight(90)
        form.addRow(QLabel("Item Description:"), self.description_input)

        self.details_input = QPlainTextEdit()
        self.details_input.setReadOnly(True)
        self.details_input.setPlainText(inquiry.get("additional_details", ""))
        self.details_input.setFixedHeight(90)
        form.addRow(QLabel("Additional Details:"), self.details_input)

        details = QVBoxLayout()
        details.setContentsMargins(0, 0, 0, 0)
        details.setSpacing(14)
        heading = QLabel("Inquiry Details")
        heading.setObjectName("pageTitle")
        details.addWidget(heading)
        details.addLayout(form)
        details.addStretch()

        # The details column is placed inside a scroll area so a small window can still show every field.
        details_widget = QWidget()
        details_widget.setLayout(details)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidget(details_widget)
        content.addWidget(scroll, 1)

        # Only a Close button is needed because this window never saves anything.
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.addLayout(content, 1)
        layout.addWidget(buttons, 0, Qt.AlignmentFlag.AlignRight)

    # Loads the saved photo into the photo area, or shows a plain message when there is none.
    def show_photo(self, photo_path):
        if not photo_path:
            self.photo_label.setText("No photo available")
            return

        # Saved photos are relative to the project folder (images/...), so the full path is built here.
        full_path = photo_path if os.path.isabs(photo_path) else os.path.join(BASE_DIR, photo_path)
        pixmap = QPixmap(full_path)
        if pixmap.isNull():
            self.photo_label.setText("Photo file not found")
            return

        # Keeps the photo's proportions and shrinks it to fit inside the label.
        self.photo_label.setPixmap(pixmap.scaled(
            self.photo_label.width() - 8,
            self.photo_label.height() - 8,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        ))
