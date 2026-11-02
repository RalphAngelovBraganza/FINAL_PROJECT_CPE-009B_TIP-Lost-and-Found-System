from datetime import date

from PyQt6.QtWidgets import (QDialog, QHBoxLayout, QInputDialog, QLabel, QLineEdit,
                             QMessageBox, QPushButton)

from data.claims import add_claim, cancel_claim, get_claims, release_claim
from data.items import get_unclaimed_items
from data.store import format_record_id
from dialogs.claim_dialog import ClaimDialog
from pages.base_page import BasePage, guarded


# Manages claims and item releases.
class ClaimsPage(BasePage):

    # Builds the page controls and connects their signals.
    def __init__(self):
        super().__init__("Claims and Releases")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search")
        self.search_input.setFixedHeight(32)
        date_filter_widget, self.date_filter, self.date_input = self.create_date_filter()

        search_row = QHBoxLayout()
        search_row.addWidget(self.search_input, 1)
        search_row.addWidget(date_filter_widget)
        self.main_layout.addLayout(search_row)

        button_row = QHBoxLayout()
        self.claim_button = QPushButton("Record Claim")
        self.release_button = QPushButton("Mark as Released")
        self.cancel_button = QPushButton("Cancel Claim")
        button_row.addWidget(self.claim_button)
        button_row.addWidget(self.release_button)
        button_row.addWidget(self.cancel_button)
        button_row.addStretch()
        self.main_layout.addLayout(button_row)

        self.table = self.create_table(
            ["Claim ID", "Item", "Claimant", "Contact Info", "Date Claimed",
             "Release Date", "Released By", "Status"]
        )
        self.main_layout.addWidget(self.table)

        self.count_label = QLabel("")
        self.main_layout.addWidget(self.count_label)

        self.search_input.textChanged.connect(self.load_claims)
        self.date_filter.toggled.connect(self.load_claims)
        self.date_input.dateChanged.connect(self.load_claims)
        self.claim_button.clicked.connect(self.record_claim)
        self.release_button.clicked.connect(self.mark_released)
        self.cancel_button.clicked.connect(self.cancel_selected_claim)


    # Reloads the displayed data.
    def refresh(self):
        self.load_claims()


    # Loads claims matching the current search.
    @guarded()
    def load_claims(self):
        date_filter = self.date_input.date().toString("yyyy-MM-dd") if self.date_filter.isChecked() else ""
        claims = get_claims(self.search_input.text().strip(), date_filter)
        rows = []
        for claim in claims:
            if claim["release_date"]:
                status = "Released"
            else:
                status = "Pending Release"
            item_prefix = format_record_id("ITM", claim.get("item_date_found"), claim["item_id"])
            rows.append([
                format_record_id("CLM", claim.get("date_claimed"), claim["claim_id"]),
                f"{item_prefix} - {claim['item_name']}",
                claim["claimant_name"], claim["contact_info"], claim["date_claimed"],
                claim["release_date"], claim["released_by"], status,
            ])
        self.fill_table(self.table, rows)
        self.count_label.setText(f"Showing {len(rows)} claim(s)")


    # Opens the form to record a claim.
    @guarded()
    def record_claim(self):
        unclaimed_items = get_unclaimed_items()
        if len(unclaimed_items) == 0:
            self.show_info("There are no unclaimed items to record a claim for.")
            return
        dialog = ClaimDialog(self, unclaimed_items)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            add_claim(
                data["item_id"], data["claimant_name"], data["contact_info"],
                data["date_claimed"], data["verification_notes"]
            )
            self.show_info("The claim was recorded. The item is now marked as Claimed.")
            self.load_claims()


    # Marks the selected claim as released.
    @guarded()
    def mark_released(self):
        claim_id = self.get_selected_id(self.table)
        if claim_id is None:
            return
        staff_name, ok = QInputDialog.getText(
            self, "Mark as Released",
            "Name of the staff member releasing the item:",
            text=""
        )
        if not ok:
            return
        staff_name = staff_name.strip()
        if staff_name == "":
            QMessageBox.warning(self, "Missing Information", "Please enter the staff member's name.")
            return
        changed = release_claim(claim_id, date.today().isoformat(), staff_name)
        if changed == 0:
            self.show_info("This item was already released.")
        else:
            self.show_info("The item was marked as released.")
        self.load_claims()


    # Cancels the selected claim.
    @guarded()
    def cancel_selected_claim(self):
        claim_id = self.get_selected_id(self.table)
        if claim_id is None:
            return
        if not self.confirm("Cancel Claim",
                            "Cancel this claim? The item will be marked as Unclaimed again."):
            return
        cancel_claim(claim_id)
        self.show_info("The claim was cancelled.")
        self.load_claims()
