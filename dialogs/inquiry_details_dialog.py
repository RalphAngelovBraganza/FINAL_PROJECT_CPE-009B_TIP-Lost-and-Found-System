import os  # Resolves relative photo paths against the project folder.

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtWidgets import (QDialog, QDialogButtonBox, QFrame, QHBoxLayout,
                             QLabel, QScrollArea, QSizePolicy, QTextEdit, QVBoxLayout, QWidget, QLineEdit)

from data.store import BASE_DIR, format_record_id


class InquiryDetailsDialog(QDialog):  # A read-only window that shows one inquiry in full: the photo on the left and every saved field on the right.
    def __init__(self, inquiry, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Inquiry Details")
        self.setMinimumSize(1100, 700)
        self.resize(1200, 800)

        content = QHBoxLayout()  # Photo on one side, the scrollable details on the other.
        content.setContentsMargins(16, 16, 16, 12)
        content.setSpacing(48)
        photo_box = QVBoxLayout()  # The photo column is centred vertically.
        photo = QLabel()
        photo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        photo.setFixedSize(420, 520)  # The photo area keeps a fixed size so the window does not jump around when an inquiry has no photo.
        photo.setStyleSheet("background-color: white; color: #222222; border: 1px solid #dddddd; border-radius: 4px;")
        photo_path = inquiry.get("photo_path", "")
        if photo_path:
            full_path = photo_path if os.path.isabs(photo_path) else os.path.join(BASE_DIR, photo_path)  # Records store paths relative to the project folder.
            pixmap = QPixmap(full_path)
            if not pixmap.isNull():
                photo.setPixmap(pixmap.scaled(404, 504, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))  # Fit inside the fixed photo box.
            else:
                photo.setText("Photo file not found")
        else:
            photo.setText("No photo available")
        photo_box.addStretch()
        photo_box.addWidget(photo, 0, Qt.AlignmentFlag.AlignCenter)
        photo_box.addStretch()
        content.addLayout(photo_box)

        # (Label, record key) pairs, in the order they show on the right; the two
        # long texts get tall text boxes, everything else a one-line box.
        fields = [
            ("Inquiry ID", "inquiry_id"), ("Student Name", "student_name"),
            ("T.I.P. Email", "tip_email"), ("Item Name", "item_name"),
            ("Item Description", "item_description"),
            ("Category", "category"), ("Color", "color"), ("Size", "size"),
            ("Brand", "brand"), ("Date Lost", "date_lost"),
            ("Last Seen Location", "location_last_seen"), ("Additional Details", "additional_details"),
            ("Date Reported", "date_reported"), ("Status", "status")
        ]
        details = QVBoxLayout()  # The right column: heading first, then one row per field.
        details.setContentsMargins(8, 0, 8, 0)
        details.setSpacing(22)
        heading = QLabel("Inquiry Details")
        heading.setObjectName("pageTitle")  # Styled by pages.qss.
        details.addWidget(heading)
        form = QVBoxLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setSpacing(22)
        for label_text, key in fields:
            label = QLabel(label_text + ":")
            label.setFont(QFont(label.font().family(), label.font().pointSize(), QFont.Weight.Bold))  # Bold labels make the rows scannable.
            label.setStyleSheet("background-color: #f5f5f5; color: #222222; padding: 4px; border: none;")
            box = QFrame()  # Each value sits in a named frame so dialogs.qss can style it.
            box.setObjectName("itemDetailValueBox")
            box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            box_layout = QVBoxLayout(box)
            box_layout.setContentsMargins(0, 0, 0, 0)
            value_text = (format_record_id("INQ", inquiry.get("date_reported"), inquiry.get("inquiry_id")) if key == "inquiry_id" else str(inquiry.get(key) or ""))  # IDs show as e.g. INQ-2610-001.
            if key not in ("item_description", "additional_details"):  # Short fields get a one-line read-only box.
                value = QLineEdit()
                value.setReadOnly(True)
                value.setText(value_text)
                value.setFixedHeight(34)
                value.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                if key == "status":
                    value.setFont(QFont(value.font().family(), value.font().pointSize(), QFont.Weight.Bold))
            else:  # The long texts get taller scrolling text boxes.
                value = QTextEdit()
                value.setReadOnly(True)
                value.setPlainText(value_text)
                value.setFixedHeight(100)
                value.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                value.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
                value.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
                value.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            value.setStyleSheet("background-color: white; color: #222222; border: 1px solid #d5d5d5; border-radius: 4px; padding: 6px;")
            box_layout.addWidget(value)
            field_row = QHBoxLayout()  # One row: label on the left, value frame stretching on the right.
            field_row.setContentsMargins(0, 0, 0, 0)
            field_row.setSpacing(12)
            label.setFixedWidth(145)  # All labels share a width so the value boxes line up.
            label.setAlignment(Qt.AlignmentFlag.AlignLeft | (Qt.AlignmentFlag.AlignTop if key in ("item_description", "additional_details") else Qt.AlignmentFlag.AlignVCenter))
            field_row.addWidget(label, 0, Qt.AlignmentFlag.AlignLeft | (Qt.AlignmentFlag.AlignTop if key in ("item_description", "additional_details") else Qt.AlignmentFlag.AlignVCenter))
            field_row.addWidget(box, 1)  # 1 = the value frame takes all leftover width.
            form.addLayout(field_row)
        details.addLayout(form)
        details_widget = QWidget()  # Everything above goes into a widget so the scroll area can move it.
        details_widget.setMinimumWidth(500)
        details_widget.setStyleSheet("background-color: #f5f5f5; color: #222222;")
        details_widget.setLayout(details)
        scroll = QScrollArea()  # Long windows scroll instead of growing past the screen.
        scroll.setWidgetResizable(True)
        scroll.setMinimumWidth(500)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidget(details_widget)
        content.addWidget(scroll, 1)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)  # Details are read-only, so the only button is Close.
        buttons.rejected.connect(self.reject)
        layout = QVBoxLayout(self)  # The dialog's outer layout.
        layout.setContentsMargins(12, 12, 12, 12)
        layout.addLayout(content, 1)
        layout.addWidget(buttons, 0, Qt.AlignmentFlag.AlignRight)
