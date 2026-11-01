from PyQt6.QtWidgets import QDialog, QHBoxLayout, QLabel, QMessageBox, QPushButton  # Widgets for the buttons, layout, and count label.

from data.claims import add_claim, get_claims  # The claim records: read them and save new ones.
from data.items import get_unclaimed_items  # Feeds the dropdown: only items with status Unclaimed can be claimed.
from data.store import format_record_id  # Builds the human-readable record IDs like CLM-2610-001.
from dialogs.claim_dialog import ClaimDialog  # The form window that records a claim.
from pages.base_page import BasePage, guarded  # The shared page base and the error-catching decorator.


class ClaimsPage(BasePage):  # The claims and releases screen, one of the pages in the main window.
    def __init__(self):  # Builds the UI once when the window is created.
        super().__init__("Claims and Releases")  # BasePage sets up the main layout and the page title.

        button_row = QHBoxLayout()  # Row that holds the Record Claim button.
        self.claim_button = QPushButton("Record Claim")  # Opens the claim form.
        button_row.addWidget(self.claim_button)  # Adds the button to the row.
        button_row.addStretch()  # Pushes the button to the left edge.
        self.main_layout.addLayout(button_row)  # Puts the button row above the table.

        self.table = self.create_table(  # BasePage helper that builds the empty table.
            ["Claim ID", "Item", "Claimant", "Contact Info", "Date Claimed",  # Column titles, one per list entry.
             "Release Date", "Released By", "Status"]
        )
        self.main_layout.addWidget(self.table)  # Places the table on the page; it stretches to fill the space.

        self.count_label = QLabel("")  # Shows the row count, e.g. "Showing 3 claim(s)".
        self.main_layout.addWidget(self.count_label)  # The label sits under the table.

        self.claim_button.clicked.connect(self.record_claim)  # Clicking the button opens the form.

    def refresh(self):  # BasePage calls this whenever the page is shown.
        self.load_claims()  # Reloads the table so the data is never stale.

    @guarded()  # Wraps the method so a bad JSON file shows an error box instead of closing the app.
    def load_claims(self):  # Rebuilds every table row in claim order.
        claims = get_claims()  # Loads the claim records saved in the JSON file.
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
        self.count_label.setText(f"Showing {len(rows)} claim(s)")  # Reports the count below the table.

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
