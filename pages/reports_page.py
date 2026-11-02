from PyQt6.QtWidgets import QFormLayout, QGroupBox, QHBoxLayout, QLabel

from data.stats import get_report_summary
from pages.base_page import BasePage, guarded


# Groups report metrics under their card headings.
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


# Summarizes records and item categories.
class ReportsPage(BasePage):

    # Builds the page controls and connects their signals.
    def __init__(self):
        super().__init__("Reports")

        self.value_labels = {}

        summary_row = QHBoxLayout()
        for group_title, rows in SUMMARY_GROUPS.items():
            group_box = QGroupBox()
            form = QFormLayout(group_box)
            group_title_label = QLabel(group_title)
            group_title_label.setObjectName("reportGroupTitle")
            form.addRow(group_title_label)
            for label_text, key in rows:
                value_label = QLabel("0")
                self.value_labels[key] = value_label
                form.addRow(label_text + ":", value_label)
            summary_row.addWidget(group_box)
        self.main_layout.addLayout(summary_row)

        category_title = QLabel("Found Items by Category")
        category_title.setObjectName("categorySectionTitle")
        self.main_layout.addWidget(category_title)
        self.category_table = self.create_table(["Category", "Total", "Unclaimed", "Claimed"])
        self.main_layout.addWidget(self.category_table)


    # Reloads the displayed data.
    @guarded()
    def refresh(self):
        counts, categories = get_report_summary()
        for key, label in self.value_labels.items():
            label.setText(str(counts[key]))
        rows = [[row["category"], row["total"], row["unclaimed"], row["claimed"]] for row in categories]
        self.fill_table(self.category_table, rows)
