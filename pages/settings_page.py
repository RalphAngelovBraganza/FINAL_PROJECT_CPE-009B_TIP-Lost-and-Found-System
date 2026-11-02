from datetime import date

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QFileDialog, QGroupBox, QHBoxLayout, QLabel,
                             QPushButton, QVBoxLayout)

from data.store import DATA_PATH, backup_database
from pages.base_page import BasePage, guarded


# Provides database backup controls.
class SettingsPage(BasePage):

    # Builds the page controls and connects their signals.
    def __init__(self):
        super().__init__("Settings")

        database_box = QGroupBox()
        database_layout = QVBoxLayout(database_box)
        database_title = QLabel("Database")
        database_title.setObjectName("databaseSectionTitle")
        database_layout.addWidget(database_title)

        location_label = QLabel(f"Data file: {DATA_PATH}")
        location_label.setWordWrap(True)
        location_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        database_layout.addWidget(location_label)

        backup_row = QHBoxLayout()
        self.backup_button = QPushButton("Back Up Data")
        backup_row.addWidget(self.backup_button)
        backup_row.addStretch()
        database_layout.addLayout(backup_row)

        self.main_layout.addWidget(database_box)
        self.main_layout.addStretch()

        self.backup_button.clicked.connect(self.backup_database)


    # Reloads the displayed data.
    def refresh(self):
        return


    # Copies the database to the selected location.
    @guarded()
    def backup_database(self):
        suggested_name = f"lost_and_found_backup_{date.today().isoformat()}.json"
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Back Up Data", suggested_name, "JSON Files (*.json)"
        )
        if not file_path:
            return
        backup_database(file_path)
        self.show_info("The data was backed up successfully.")
