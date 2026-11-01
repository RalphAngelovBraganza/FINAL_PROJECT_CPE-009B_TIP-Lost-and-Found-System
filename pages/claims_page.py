from datetime import date  # Supplies today's date for the release stamp.

from PyQt6.QtWidgets import (QDialog, QHBoxLayout, QInputDialog, QLabel, QLineEdit,  # Widgets for the buttons row, the table label,
                             QMessageBox, QPushButton)                              # and the staff-name input for releases.

from data.claims import add_claim, cancel_claim, get_claims, release_claim  # All claim operations, including release and cancel.
from data.items import get_unclaimed_items  # Feeds the dropdown: only Unclaimed items can be claimed.
from data.store import format_record_id  # Builds the human-readable record IDs like CLM-2610-001.
from dialogs.claim_dialog import ClaimDialog  # The form window that records a claim.
from pages.base_page import BasePage, guarded  # The shared page base and the error-catching decorator.


class ClaimsPage(BasePage):  # The claims and releases screen, one of the pages in the main window.
    def __init__(self):  # Builds the UI once when the window is created.
        super().__init__("Claims and Releases")  # BasePage sets up the main layout and the page title.

        self.search_input = QLineEdit()  # Filters the table while typing.
        self.search_input.setPlaceholderText("Search")  # Shows the hint inside the empty box.
        self.main_layout.addWidget(self.search_input)  # The search field sits at the top of the page.

        button_row = QHBoxLayout()  # Row that holds the three actions.
        self.claim_button = QPushButton("Record Claim")  # Opens the claim form.
        self.release_button = QPushButton("Mark as Released")  # Stamps today's release on the selected claim.
        self.cancel_button = QPushButton("Cancel Claim")  # Deletes the claim and puts the item back to Unclaimed.
        button_row.addWidget(self.claim_button)  # All three sit in one row, left to right.
        button_row.addWidget(self.release_button)
        button_row.addWidget(self.cancel_button)
        button_row.addStretch()  # Pushes them together on the left edge.
        self.main_layout.addLayout(button_row)  # Puts the row between the search field and the table.

        self.table = self.create_table(  # BasePage helper that builds the empty table.
            ["Claim ID", "Item", "Claimant", "Contact Info", "Date Claimed",  # Column titles, one per list entry.
             "Release Date", "Released By", "Status"]
        )
        self.main_layout.addWidget(self.table)  # Places the table on the page; it stretches to fill the space.

        self.count_label = QLabel("")  # Shows the row count, e.g. "Showing 3 claim(s)".
        self.main_layout.addWidget(self.count_label)  # The label sits under the table.

        self.search_input.textChanged.connect(self.load_claims)  # Retypes the table on every keystroke.
        self.claim_button.clicked.connect(self.record_claim)  # Clicking opens the form.
        self.release_button.clicked.connect(self.mark_released)  # Acts on the selected row.
        self.cancel_button.clicked.connect(self.cancel_selected_claim)  # Also acts on the selected row.

    def refresh(self):  # BasePage calls this whenever the page is shown.
        self.load_claims()  # Reloads the table so the data is never stale.

    @guarded()  # Wraps the method so a bad JSON file shows an error box instead of closing the app.
    def load_claims(self):  # Rebuilds every table row, filtered by the search text.
        claims = get_claims(self.search_input.text().strip())  # Loads the claim records, keeping the ones whose fields match.
        rows = []  # Collects one list of strings per table row.
        for claim in claims:  # Walks through the claims one by one.
            if claim["release_date"]:  # A filled release date means the item was handed back already.
                status = "Released"  # Shows in the last column.
            else:
                status = "Pending Release"  # The claim is recorded but the item is still waiting.
            item_prefix = format_record_id("ITM", claim.get("item_date_found"), claim["item_id"])  # The item's own ID, put inside the Item column.
            rows.append([
                format_record_id("CLM", claim.get("date_claimed"), claim["claim_id"]),  # Claim ID column, e.g. CLM-2610-001.
                f"{item_prefix} - {claim['item_name']}",  # Item column: which item was claimed.
                claim["claimant_name"], claim["contact_info"], claim["date_claimed"],  # Who claimed it and when.
                claim["release_date"], claim["released_by"], status,  # Release details and the status column.
            ])
        self.fill_table(self.table, rows)  # BasePage helper that writes the rows into the table.
        self.count_label.setText(f"Showing {len(rows)} claim(s)")  # Reports the filtered count below the table.

    @guarded()  # Errors from the data layer or the form are turned into message boxes.
    def record_claim(self):  # Opens the claim form and saves a claim from it.
        unclaimed_items = get_unclaimed_items()  # Only items without a claim yet are offered.
        if len(unclaimed_items) == 0:  # Nothing to claim: tell the user instead of opening an empty form.
            self.show_info("There are no unclaimed items to record a claim for.")
            return  # Stops the method; the JSON file was not touched.
        dialog = ClaimDialog(self, unclaimed_items)  # Builds the form with the item dropdown filled.
        if dialog.exec() == QDialog.DialogCode.Accepted:  # exec() opens it window-for-window; Accepted means Save was clicked.
            data = dialog.get_data()  # Collects the five claim fields the user entered.
            add_claim(
                data["item_id"], data["claimant_name"], data["contact_info"],  # Saves the claim through the data layer, which also
                data["date_claimed"], data["verification_notes"]  # flips the item's status to Claimed.
            )
            self.show_info("The claim was recorded. The item is now marked as Claimed.")  # Confirms what happened.
            self.load_claims()  # Reloads so the new claim shows up right away.

    @guarded()  # Keeps input and file problems on the message-box path.
    def mark_released(self):  # Stamps the selected claim as released today.
        claim_id = self.get_selected_id(self.table)  # BasePage helper: reads the selected CLM id as a number; warns and returns None when nothing is selected.
        if claim_id is None:  # No row picked: get_selected_id already showed a warning.
            return  # Nothing was changed.
        staff_name, ok = QInputDialog.getText(  # Small pop-up that asks for one line of text.
            self, "Mark as Released",
            "Name of the staff member releasing the item:",
            text=""
        )
        if not ok:  # OK was clicked, ok is False means the dialog was cancelled.
            return  # The claim stays untouched.
        staff_name = staff_name.strip()  # Removes stray spaces from the typed name.
        if staff_name == "":  # A release without a name would be untraceable.
            QMessageBox.warning(self, "Missing Information", "Please enter the staff member's name.")
            return  # Stops before any record is written.
        changed = release_claim(claim_id, date.today().isoformat(), staff_name)  # Writes the release and returns how many records changed.
        if changed == 0:  # Zero means the claim was already released; the data layer refused to release it twice.
            self.show_info("This item was already released.")
        else:
            self.show_info("The item was marked as released.")
        self.load_claims()  # Reloads so the Release Date and Status columns update.

    @guarded()  # Same protection as the other buttons.
    def cancel_selected_claim(self):  # Deletes the selected claim and puts the item back to Unclaimed.
        claim_id = self.get_selected_id(self.table)  # Which row the user wants cancelled; warns when none is selected.
        if claim_id is None:
            return
        if not self.confirm("Cancel Claim",  # BasePage helper: Yes/No box, so a mis-click cannot destroy the claim.
                            "Cancel this claim? The item will be marked as Unclaimed again."):
            return  # The user said No; nothing happens.
        cancel_claim(claim_id)  # Removes the claim and flips the item status back in one save.
        self.show_info("The claim was cancelled.")
        self.load_claims()  # Reloads so the row disappears immediately.
