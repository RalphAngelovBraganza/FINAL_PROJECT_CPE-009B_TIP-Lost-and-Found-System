from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout

from data.stats import get_dashboard_counts
from pages.base_page import BasePage
from pages.items_page import ItemsPage


# Displays a dashboard total.
class StatCard(QFrame):

    # Sets up this component.
    def __init__(self, title):
        super().__init__()
        self.setObjectName("statCard")
        layout = QVBoxLayout(self)
        self.value_label = QLabel("0")
        self.value_label.setObjectName("statValue")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label = QLabel(title)
        title_label.setObjectName("statTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.value_label)
        layout.addWidget(title_label)


    # Updates the total displayed on the card.
    def set_value(self, value):
        self.value_label.setText(str(value))


# Defines the DashboardWidget component.
class DashboardWidget(BasePage):

    # Sets up this component.
    def __init__(self):
        super().__init__("Dashboard", show_title=False)
        self.total_card = StatCard("Total Found Items")
        self.unclaimed_card = StatCard("Unclaimed Items")
        self.claimed_card = StatCard("Claimed Items")
        self.inquiries_card = StatCard("Lost-Item Inquiries")

        grid = QGridLayout()
        grid.setSpacing(15)
        grid.addWidget(self.total_card, 0, 0)
        grid.addWidget(self.unclaimed_card, 0, 1)
        grid.addWidget(self.claimed_card, 0, 2)
        grid.addWidget(self.inquiries_card, 0, 3)
        self.main_layout.addLayout(grid)


    # Reloads the displayed data.
    def refresh(self):
        try:
            counts = get_dashboard_counts()
        except (OSError, ValueError, TypeError):
            self.show_error("An error occurred.")
            return

        self.total_card.set_value(counts["total_items"])
        self.unclaimed_card.set_value(counts["unclaimed_items"])
        self.claimed_card.set_value(counts["claimed_items"])
        self.inquiries_card.set_value(counts["total_inquiries"])


# Combines the overview cards and items list.
class HomePage(BasePage):

    # Builds the page controls and connects their signals.
    def __init__(self):
        super().__init__("Dashboard and Lost & Found Items")
        self.dashboard = DashboardWidget()
        self.items = ItemsPage(show_title=False)
        self.dashboard.main_layout.setContentsMargins(0, 0, 0, 0)
        self.items.main_layout.setContentsMargins(0, 0, 0, 0)

        self.main_layout.setSpacing(8)
        self.main_layout.addWidget(self.dashboard)
        self.main_layout.addWidget(self.items, 1)


    # Reloads the displayed data.
    def refresh(self):
        self.dashboard.refresh()
        self.items.refresh()
