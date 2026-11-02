import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon, QPixmap
from PyQt6.QtWidgets import (QDialog, QDialogButtonBox, QFrame, QHBoxLayout,
                             QLabel, QScrollArea, QSizePolicy, QTextEdit, QVBoxLayout, QWidget, QLineEdit)

from data.store import BASE_DIR, format_record_id, window_icon_path


# Displays saved inquiry details and its photo.
class InquiryDetailsDialog(QDialog):

    # Builds the form and connects its controls.
    def __init__(self, inquiry, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Inquiry Details")
        self.setWindowIcon(QIcon(window_icon_path("inquiry_details.png")))
        self.setMinimumSize(1100, 700)
        self.resize(1200, 800)

        content = QHBoxLayout()
        content.setContentsMargins(16, 16, 16, 12)
        content.setSpacing(48)
        photo_box = QVBoxLayout()
        photo = QLabel()
        photo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        photo.setFixedSize(420, 520)
        photo.setStyleSheet("background-color: white; color: #222222; border: 1px solid #dddddd; border-radius: 4px;")
        photo_path = inquiry.get("photo_path", "")
        if photo_path:
            full_path = photo_path if os.path.isabs(photo_path) else os.path.join(BASE_DIR, photo_path)
            pixmap = QPixmap(full_path)
            if not pixmap.isNull():
                photo.setPixmap(pixmap.scaled(404, 504, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            else:
                photo.setText("Photo file not found")
        else:
            photo.setText("No photo available")
        photo_box.addStretch()
        photo_box.addWidget(photo, 0, Qt.AlignmentFlag.AlignCenter)
        photo_box.addStretch()
        content.addLayout(photo_box)


        fields = [
            ("Inquiry ID", "inquiry_id"), ("Student Name", "student_name"),
            ("T.I.P. Email", "tip_email"), ("Item Name", "item_name"),
            ("Item Description", "item_description"),
            ("Category", "category"), ("Color", "color"), ("Size", "size"),
            ("Brand", "brand"), ("Date Lost", "date_lost"),
            ("Last Seen Location", "location_last_seen"), ("Additional Details", "additional_details"),
            ("Date Reported", "date_reported"), ("Status", "status")
        ]
        details = QVBoxLayout()
        details.setContentsMargins(8, 0, 8, 0)
        details.setSpacing(22)
        heading = QLabel("Inquiry Details")
        heading.setObjectName("pageTitle")
        details.addWidget(heading)
        form = QVBoxLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setSpacing(22)
        for label_text, key in fields:
            label = QLabel(label_text + ":")
            label.setFont(QFont(label.font().family(), label.font().pointSize(), QFont.Weight.Bold))
            label.setStyleSheet("background-color: #f5f5f5; color: #222222; padding: 4px; border: none;")
            box = QFrame()
            box.setObjectName("itemDetailValueBox")
            box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            box_layout = QVBoxLayout(box)
            box_layout.setContentsMargins(0, 0, 0, 0)
            value_text = (format_record_id("INQ", inquiry.get("date_reported"), inquiry.get("inquiry_id")) if key == "inquiry_id" else str(inquiry.get(key) or ""))
            if key not in ("item_description", "additional_details"):
                value = QLineEdit()
                value.setReadOnly(True)
                value.setText(value_text)
                value.setFixedHeight(34)
                value.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                if key == "status":
                    value.setFont(QFont(value.font().family(), value.font().pointSize(), QFont.Weight.Bold))
            else:
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
            field_row = QHBoxLayout()
            field_row.setContentsMargins(0, 0, 0, 0)
            field_row.setSpacing(12)
            label.setFixedWidth(145)
            label.setAlignment(Qt.AlignmentFlag.AlignLeft | (Qt.AlignmentFlag.AlignTop if key in ("item_description", "additional_details") else Qt.AlignmentFlag.AlignVCenter))
            field_row.addWidget(label, 0, Qt.AlignmentFlag.AlignLeft | (Qt.AlignmentFlag.AlignTop if key in ("item_description", "additional_details") else Qt.AlignmentFlag.AlignVCenter))
            field_row.addWidget(box, 1)
            form.addLayout(field_row)
        details.addLayout(form)
        details_widget = QWidget()
        details_widget.setMinimumWidth(500)
        details_widget.setStyleSheet("background-color: #f5f5f5; color: #222222;")
        details_widget.setLayout(details)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumWidth(500)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidget(details_widget)
        content.addWidget(scroll, 1)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.addLayout(content, 1)
        layout.addWidget(buttons, 0, Qt.AlignmentFlag.AlignRight)
