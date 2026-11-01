from PyQt6.QtWidgets import QFormLayout, QGroupBox, QHBoxLayout, QLabel  # Widgets for the three summary boxes.

from data.stats import get_report_summary  # Counts everything and builds the by-category table in one pass.
from pages.base_page import BasePage, guarded  # The shared page base and the error-catching decorator.

# SUMMARY_GROUPS drives the summary boxes: every entry becomes one "Label: value"
# row, and the string keys match the dictionary get_report_summary() returns.
SUMMARY_GROUPS = {
    "Found Items": [
        ("Total items", "total_items"),
        ("Unclaimed", "unclaimed_items"),
        ("Claimed", "claimed_items"),
    ],
    "Lost-Item Inquiries": [
        ("Total inquiries", "total_inquiries"),
        ("Open", "open_inquiries"),
        ("Resolved", "resolved_inquiries"),
    ],
    "Claims and Releases": [
        ("Total claims", "total_claims"),
        ("Pending release", "pending_releases"),
        ("Released", "released_claims"),
    ],
}


class ReportsPage(BasePage):  # The reports screen: nine totals plus one table per category.
    def __init__(self):  # Builds the three boxes and the category table once.
        super().__init__("Reports")  # BasePage sets up the main layout and the page title.

        self.value_labels = {}  # Remember which QLabel belongs to which metric key so refresh() can update it.

        summary_row = QHBoxLayout()  # The three boxes sit side by side in one row.
        for group_title, rows in SUMMARY_GROUPS.items():  # One QGroupBox per dictionary entry.
            group_box = QGroupBox()  # The white card; its heading is added inside.
            form = QFormLayout(group_box)  # Form layout puts each "Label: value" on its own row.
            form.addRow(QLabel(group_title))  # Keeps the title fully inside the card.
            for label_text, key in rows:
                value_label = QLabel("0")  # Starts at 0; refresh() fills in the real number.
                self.value_labels[key] = value_label  # Keep it reachable by its metric key.
                form.addRow(label_text + ":", value_label)  # One line of the summary.
            summary_row.addWidget(group_box)  # Add the finished box to the row.
        self.main_layout.addLayout(summary_row)  # The row sits under the page title.

        self.main_layout.addWidget(QLabel("Found Items by Category"))  # Heading above the breaks-down table.
        self.category_table = self.create_table(["Category", "Total", "Unclaimed", "Claimed"])  # One row per category with its counts.
        self.main_layout.addWidget(self.category_table)  # The table fills the rest of the page.

    @guarded()  # A corrupt or locked JSON file shows an error box instead of crashing.
    def refresh(self):  # Runs every time the page is opened, so the numbers are never stale.
        counts, categories = get_report_summary()  # The counts for the boxes and the rows for the table, from one read of the file.
        for key, label in self.value_labels.items():  # Copy each count into its QLabel.
            label.setText(str(counts[key]))  # setText needs a string, so the number is converted.
        rows = [[row["category"], row["total"], row["unclaimed"], row["claimed"]] for row in categories]  # Turn each category dictionary into a table row.
        self.fill_table(self.category_table, rows)  # BasePage helper that writes the rows into the table.
