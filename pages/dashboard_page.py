from pages.base_page import BasePage


# Displays the system overview.
class DashboardPage(BasePage):

    # Builds the page controls and connects their signals.
    def __init__(self):
        super().__init__("Dashboard")
