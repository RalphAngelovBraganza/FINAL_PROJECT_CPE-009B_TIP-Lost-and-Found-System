from pages.base_page import BasePage


# Provides database backup controls.
class SettingsPage(BasePage):

    # Builds the page controls and connects their signals.
    def __init__(self):
        super().__init__("Settings")
