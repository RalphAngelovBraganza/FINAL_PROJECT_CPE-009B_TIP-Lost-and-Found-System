from pages.base_page import BasePage


class SettingsPage(BasePage): # the only thing we are adding here is the json file back up
    def __init__(self):
        super().__init__("Settings")
