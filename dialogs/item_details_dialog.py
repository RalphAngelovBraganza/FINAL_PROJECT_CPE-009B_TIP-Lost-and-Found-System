import os  # Resolves relative photo paths against the project folder.

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtWidgets import (QDialog, QDialogButtonBox, QFrame,
                             QHBoxLayout, QLabel, QScrollArea, QSizePolicy, QTextEdit,
                             QVBoxLayout, QWidget, QLineEdit)

from data.store import BASE_DIR, format_record_id


class ItemDetailsDialog(QDialog):  # A read-only window that shows one found item in full: the photo on the left and every saved field on the right.
    def __init__(self, item, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Item Details")
        self.setMinimumSize(1100, 700)
        self.resize(1200, 800)

        content = QHBoxLayout()  # Photo on one side, the scrollable details on the other.
        content.setContentsMargins(16, 16, 16, 12)
        content.setSpacing(40)

        photo_box = QVBoxLayout()  # The photo column is centred vertically.
        photo_box.setContentsMargins(0, 0, 0, 0)
        photo_label = QLabel()
        photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        photo_label.setFixedSize(420, 520)  # The photo area keeps a fixed size so the window does not jump around when an item has no photo.
        photo_label.setStyleSheet("background-color: white; color: #222222; border: 1px solid #dddddd; border-radius: 4px;")
        self.show_photo(photo_label, item.get("photo_path", ""))
        photo_box.addStretch()
        photo_box.addWidget(photo_label, 0, Qt.AlignmentFlag.AlignCenter)
        photo_box.addStretch()
        content.addLayout(photo_box)

        # (Label, record key) pairs, in the order they show on the right; the
        # description gets a tall text box, everything else a one-line box.
        fields = [
            ("Item ID", "item_id"),
            ("Item Name", "item_name"),
            ("Category", "category"),
            ("Subcategory", "subcategory"),
            ("Item Description", "description"),
            ("Color", "color"),
            ("Size", "size"),
            ("Brand", "brand"),
            ("Date Found", "date_found"),
            ("Location Found", "location_found"),
            ("Finder Name", "finder_name"),
            ("Status", "status"),
        ]

        details_box = QVBoxLayout()  # The right column: heading first, then one row per field.
        details_box.setContentsMargins(8, 0, 8, 0)
        details_box.setSpacing(14)
        heading = QLabel("Item Details")
        heading.setObjectName("pageTitle")  # Styled by pages.qss.
        details_box.addWidget(heading)

        form = QVBoxLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setSpacing(12)
        for label_text, column in fields:
            label = QLabel(label_text + ":")
            label.setFont(QFont(label.font().family(), label.font().pointSize(), QFont.Weight.Bold))  # Bold labels make the rows scannable.
            label.setStyleSheet("background-color: transparent; color: #222222; border: none;")
            value_text = (format_record_id("ITM", item.get("date_found"), item.get("item_id")) if column == "item_id" else str(item.get(column) or ""))  # IDs show as e.g. ITM-2610-001.

            if column != "description":  # Short fields get a one-line read-only box.
                value = QLineEdit()
                value.setReadOnly(True)
                value.setText(value_text)
                value.setFixedHeight(34)
                value.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                if column == "status":
                    value.setFont(QFont(value.font().family(), value.font().pointSize(), QFont.Weight.Bold))
            else:  # The description gets a taller scrolling text box.
                value = QTextEdit()
                value.setReadOnly(True)
                value.setPlainText(value_text)
                value.setFixedHeight(100)
                value.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                value.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
                value.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
                value.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

            value.setStyleSheet("background-color: white; color: #222222; border: 1px solid #d5d5d5; border-radius: 4px; padding: 6px;")
            field_row = QHBoxLayout()  # One row: label on the left, value box stretching on the right.
            field_row.setContentsMargins(0, 0, 0, 0)
            field_row.setSpacing(12)
            label.setFixedWidth(145)  # All labels share a width so the value boxes line up.
            label.setAlignment(Qt.AlignmentFlag.AlignLeft | (Qt.AlignmentFlag.AlignTop if column == "description" else Qt.AlignmentFlag.AlignVCenter))
            field_row.addWidget(label, 0, Qt.AlignmentFlag.AlignLeft | (Qt.AlignmentFlag.AlignTop if column == "description" else Qt.AlignmentFlag.AlignVCenter))
            field_row.addWidget(value, 1)  # 1 = the value box takes all leftover width.
            form.addLayout(field_row)

        details_box.addLayout(form)
        details_widget = QWidget()  # Everything above goes into a widget so the scroll area can move it.
        details_widget.setMinimumWidth(0)
        details_widget.setStyleSheet("background-color: #f5f5f5; color: #222222;")
        details_widget.setLayout(details_box)

        scroll = QScrollArea()  # Long windows scroll instead of growing past the screen.
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background-color: #f5f5f5; border: none; } QWidget#qt_scrollarea_viewport { background-color: #f5f5f5; }")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidget(details_widget)
        content.addWidget(scroll, 1)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)  # Details are read-only, so the only button is Close.
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)  # The dialog's outer layout.
        layout.setContentsMargins(12, 12, 12, 12)
        layout.addLayout(content, 1)
        layout.addWidget(buttons, 0, Qt.AlignmentFlag.AlignRight)

    def show_photo(self, label, photo_path):  # Shows the photo, or a message inside the box if there is none.
        if not photo_path:
            label.setText("No photo available")
            return

        full_path = photo_path if os.path.isabs(photo_path) else os.path.join(BASE_DIR, photo_path)  # Records store paths relative to the project folder.
        pixmap = QPixmap(full_path)
        if pixmap.isNull():
            label.setText("Photo file not found")
            return

        scaled = pixmap.scaled(  # Fit inside the fixed photo box, keeping the aspect ratio.
            label.size().width() - 16,
            label.size().height() - 16,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        label.setPixmap(scaled)
