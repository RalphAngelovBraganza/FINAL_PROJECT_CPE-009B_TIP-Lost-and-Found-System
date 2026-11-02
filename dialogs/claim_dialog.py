from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QColor, QIcon, QPalette

from data.store import format_record_id, window_icon_path
from PyQt6.QtWidgets import (QComboBox, QCompleter, QDateEdit, QDialog, QDialogButtonBox,
                             QGridLayout, QHBoxLayout, QLabel, QLineEdit,
                             QMessageBox, QTextEdit, QVBoxLayout, QWidget)


# Collects claim and release details.
class ClaimDialog(QDialog):

    # Builds the form and connects its controls.
    def __init__(self, parent, unclaimed_items):
        super().__init__(parent)
        self.setWindowTitle("Record Claim")
        self.setWindowIcon(QIcon(window_icon_path("claim.png")))
        self.setMinimumSize(800, 480)
        self.resize(900, 540)

        self.item_input = QComboBox()
        self.item_input.setFixedHeight(36)
        self.item_input.setEditable(True)
        self.item_input.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.item_input.lineEdit().setPlaceholderText("Type item name or ID to search...")
        self.item_input.addItem("", None)
        for item in unclaimed_items:
            text = f"{format_record_id('ITM', item.get('date_found'), item['item_id'])} - {item['item_name']} ({item['category']})"
            self.item_input.addItem(text, item["item_id"])
        completer = QCompleter(self.item_input.model(), self.item_input)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.item_input.setCompleter(completer)

        popup = completer.popup()
        popup.setObjectName("completerPopup")
        palette = popup.palette()
        for role, hex_color in (
            (QPalette.ColorRole.Base, "#ffffff"),
            (QPalette.ColorRole.Text, "#222222"),
            (QPalette.ColorRole.Highlight, "#f7e7a0"),
            (QPalette.ColorRole.HighlightedText, "#1e1e1e"),
        ):
            palette.setColor(role, QColor(hex_color))
        popup.setPalette(palette)

        self.claimant_input = QLineEdit()
        self.claimant_input.setFixedHeight(36)
        self.claimant_input.setMaxLength(100)
        self.contact_input = QLineEdit()
        self.contact_input.setFixedHeight(36)
        self.contact_input.setMaxLength(150)

        self.date_input = QDateEdit()
        self.date_input.setFixedHeight(36)
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("MM/dd/yyyy")
        self.date_input.setMinimumDate(QDate(2020, 1, 1))
        self.date_input.setMaximumDate(QDate.currentDate())
        self.date_input.setDate(QDate.currentDate())

        self.notes_input = QTextEdit()
        self.notes_input.setFixedHeight(80)
        self.notes_input.textChanged.connect(self.limit_notes)

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)
        title = QLabel("Claim & Release Details")
        title.setObjectName("formTitle")
        subtitle = QLabel("Record the claimant's details and how ownership was verified.")
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

        left.addWidget(self.field("Select Unclaimed Item", self.item_input, True))
        left.addWidget(self.field("Claimant Name", self.claimant_input, True))
        left.addWidget(self.field("Contact Info", self.contact_input, True))
        right.addWidget(self.field("Date Claimed", self.date_input, True))
        right.addWidget(self.field("Verification Notes", self.notes_input, True))
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
        layout.addWidget(label)
        layout.addWidget(widget)
        return container


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


    # Limits the length of verification notes.
    def limit_notes(self):
        text = self.notes_input.toPlainText()
        if len(text) > 1000:
            position = min(self.notes_input.textCursor().position(), 1000)
            self.notes_input.blockSignals(True)
            self.notes_input.setPlainText(text[:1000])
            cursor = self.notes_input.textCursor()
            cursor.setPosition(position)
            self.notes_input.setTextCursor(cursor)
            self.notes_input.blockSignals(False)


    # Validates the form before accepting it.
    def check_and_accept(self):
        if self.item_input.currentData() is None:
            QMessageBox.warning(self, "Missing Information", "Please select an unclaimed item.")
            return
        if not self.claimant_input.text().strip():
            QMessageBox.warning(self, "Missing Information", "Please enter the claimant's name.")
            return
        if not self.contact_input.text().strip():
            QMessageBox.warning(self, "Missing Information", "Please enter the claimant's contact info.")
            return
        if not self.notes_input.toPlainText().strip():
            QMessageBox.warning(self, "Missing Information", "Please enter the verification notes.")
            return
        self.accept()


    # Returns the values entered in the form.
    def get_data(self):
        return {
            "item_id": self.item_input.currentData(),
            "claimant_name": self.claimant_input.text().strip(),
            "contact_info": self.contact_input.text().strip(),
            "date_claimed": self.date_input.date().toString("yyyy-MM-dd"),
            "verification_notes": self.notes_input.toPlainText().strip(),
        }
