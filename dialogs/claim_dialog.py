from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QColor, QPalette

from data.store import format_record_id
from PyQt6.QtWidgets import (QComboBox, QCompleter, QDateEdit, QDialog, QDialogButtonBox,
                             QGridLayout, QHBoxLayout, QLabel, QLineEdit,
                             QMessageBox, QTextEdit, QVBoxLayout, QWidget)


class ClaimDialog(QDialog):  # The form opened by the Record Claim button on the claims page.
    def __init__(self, parent, unclaimed_items):  # Receives the page and the already-filtered Unclaimed items.
        super().__init__(parent)  # Normal dialog window on top of its parent page.
        self.setWindowTitle("Record Claim")
        self.setMinimumSize(800, 480)
        self.resize(900, 540)

        self.item_input = QComboBox()  # The unclaimed item picker.
        self.item_input.setFixedHeight(36)
        self.item_input.setEditable(True)  # Editable so the user can type to search instead of scrolling.
        self.item_input.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)  # Typed text never becomes a new list entry.
        self.item_input.lineEdit().setPlaceholderText("Type item name or ID to search...")  # Explains the typing behaviour.
        self.item_input.addItem("", None)  # First entry: the blank "no item chosen" state; currentData() is None.
        for item in unclaimed_items:  # One entry per unclaimed item.
            text = f"{format_record_id('ITM', item.get('date_found'), item['item_id'])} - {item['item_name']} ({item['category']})"
            self.item_input.addItem(text, item["item_id"])  # Visible text for the user; the item_id travels as hidden mark-up data.
        completer = QCompleter(self.item_input.model(), self.item_input)  # Typing shows a filtered list of the entries.
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)  # The match can be anywhere in the text, not only the start.
        completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.item_input.setCompleter(completer)

        popup = completer.popup()  # The list widget the completer shows.
        popup.setObjectName("completerPopup")  # Name used by dialogs.qss.
        palette = popup.palette()
        for role, hex_color in (  # Hard colours keep the popup readable on every platform.
            (QPalette.ColorRole.Base, "#ffffff"),
            (QPalette.ColorRole.Text, "#222222"),
            (QPalette.ColorRole.Highlight, "#f7e7a0"),
            (QPalette.ColorRole.HighlightedText, "#1e1e1e"),
        ):
            palette.setColor(role, QColor(hex_color))  # Apply each (role, colour) pair.
        popup.setPalette(palette)

        self.claimant_input = QLineEdit()  # Who is claiming the item.
        self.claimant_input.setFixedHeight(36)
        self.claimant_input.setMaxLength(100)  # Room for two to three names.
        self.contact_input = QLineEdit()  # How the office can reach the claimant.
        self.contact_input.setFixedHeight(36)
        self.contact_input.setMaxLength(150)

        self.date_input = QDateEdit()  # The day the claim was made.
        self.date_input.setFixedHeight(36)
        self.date_input.setCalendarPopup(True)  # Clicking the arrow opens a real calendar.
        self.date_input.setDisplayFormat("MM/dd/yyyy")
        self.date_input.setMinimumDate(QDate(2020, 1, 1))
        self.date_input.setMaximumDate(QDate.currentDate())  # A claim cannot be dated in the future.
        self.date_input.setDate(QDate.currentDate())  # Starts on today, which is the common case.

        self.notes_input = QTextEdit()  # Free text for how ownership was verified.
        self.notes_input.setFixedHeight(80)
        self.notes_input.textChanged.connect(self.limit_notes)  # Keeps the field capped while typing.

        root = QVBoxLayout(self)  # The outer layout of the dialog.
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)
        title = QLabel("Claim & Release Details")
        title.setObjectName("formTitle")  # Styled by dialogs.qss.
        subtitle = QLabel("Record the claimant's details and how ownership was verified.")
        subtitle.setObjectName("formSubtitle")
        root.addWidget(title)
        root.addWidget(subtitle)

        columns = QGridLayout()  # Two columns of fields side by side.
        columns.setHorizontalSpacing(24)
        columns.setVerticalSpacing(12)
        left = QVBoxLayout()  # Each vertical list is one column.
        right = QVBoxLayout()
        left.setSpacing(10)
        right.setSpacing(10)

        left.addWidget(self.field("Select Unclaimed Item", self.item_input, True))  # field() pairs a label with each input; True adds the red asterisk.
        left.addWidget(self.field("Claimant Name", self.claimant_input, True))
        left.addWidget(self.field("Contact Info", self.contact_input, True))
        right.addWidget(self.field("Date Claimed", self.date_input, True))
        right.addWidget(self.field("Verification Notes", self.notes_input, True))
        left.addStretch(1)  # Stretches keep the fields aligned at the top.
        right.addStretch(1)

        columns.addLayout(left, 0, 0)  # Column 0.
        columns.addLayout(right, 0, 1)  # Column 1.
        columns.setColumnStretch(0, 1)
        columns.setColumnStretch(1, 1)
        root.addLayout(columns)
        root.addStretch(1)

        required_note = QLabel("* Required")
        required_note.setObjectName("requiredNote")
        root.addWidget(required_note)
        root.addLayout(self.action_bar())  # The Save / Cancel row at the bottom.

    def field(self, label_text, widget, required=False):  # Builds "label above input" for one form field.
        container = QWidget()  # The pair lives in one container so it can be added as a single unit.
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        label = QLabel(f"{label_text} <span style='color:#d93025'>*</span>" if required else label_text)  # Required fields get a red asterisk after the name.
        label.setObjectName("formFieldLabel")  # Styled by dialogs.qss.
        label.setStyleSheet("font-weight: bold;")
        if required:
            label.setTextFormat(Qt.TextFormat.RichText)  # The asterisk is HTML, so the label must render rich text.
        layout.addWidget(label)
        layout.addWidget(widget)
        return container

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

    def limit_notes(self):  # Runs on every keystroke in the notes box.
        text = self.notes_input.toPlainText()
        if len(text) > 1000:  # The notes are capped at 1000 characters, like the other long fields.
            position = min(self.notes_input.textCursor().position(), 1000)  # Keep the cursor where the user was.
            self.notes_input.blockSignals(True)  # setPlainText would call textChanged again; block it so this runs once.
            self.notes_input.setPlainText(text[:1000])
            cursor = self.notes_input.textCursor()
            cursor.setPosition(position)
            self.notes_input.setTextCursor(cursor)
            self.notes_input.blockSignals(False)

    def check_and_accept(self):  # Refuses to close until every required field passes.
        if self.item_input.currentData() is None:  # currentData() is None while the blank first entry is chosen.
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
        self.accept()  # All checks passed: close with Accepted, which the page treats as "save".

    def get_data(self):  # Called by the page after exec() returns Accepted.
        return {
            "item_id": self.item_input.currentData(),  # The hidden item_id behind the chosen text.
            "claimant_name": self.claimant_input.text().strip(),
            "contact_info": self.contact_input.text().strip(),
            "date_claimed": self.date_input.date().toString("yyyy-MM-dd"),  # Stored in the ISO format the records use.
            "verification_notes": self.notes_input.toPlainText().strip(),
        }
