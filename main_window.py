from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QButtonGroup, QFrame, QHBoxLayout, QLabel, QMainWindow,
                             QPushButton, QStackedWidget, QVBoxLayout, QWidget)

from pages.claims_page import ClaimsPage
from pages.inquiries_page import InquiriesPage
from pages.home_page import HomePage
from pages.reports_page import ReportsPage
from pages.settings_page import SettingsPage


# Builds the main window and page navigation.
class MainWindow(QMainWindow):

    # Builds the window and connects page navigation.
    def __init__(self):
        super().__init__()
        self.setWindowTitle("T.I.P. Lost and Found Office Management and Tracking System")
        self.resize(1150, 700)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(2)

        title = QLabel("T.I.P. Lost & Found")
        title.setObjectName("logoLabel")
        title.setFixedHeight(90)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(title)

        self.pages = QStackedWidget()

        page_list = [
            ("Dashboard and Items", HomePage()),
            ("Lost-Item Inquiries", InquiriesPage()),
            ("Claims and Releases", ClaimsPage()),
            ("Reports", ReportsPage()),
            ("Settings", SettingsPage()),
        ]

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)

        for index, (name, page) in enumerate(page_list):
            button = QPushButton(name)
            button.setObjectName("navButton")
            button.setCheckable(True)
            self.button_group.addButton(button, index)
            sidebar_layout.addWidget(button)
            self.pages.addWidget(page)

        sidebar_layout.addStretch()

        self.button_group.idClicked.connect(self.switch_page)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.pages, 1)

        self.button_group.button(0).setChecked(True)
        self.switch_page(0)


    # Displays the selected page and refreshes it.
    def switch_page(self, index):
        self.pages.setCurrentIndex(index)
        self.pages.currentWidget().refresh()
