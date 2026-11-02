from datetime import date

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (QFileDialog, QGroupBox, QHBoxLayout, QLabel,
                             QMessageBox, QPushButton, QVBoxLayout)

from data.store import DATA_PATH, backup_database, import_database
from pages.base_page import BasePage, guarded


# Provides database backup controls.
class SettingsPage(BasePage):

    data_imported = pyqtSignal()

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
        self.import_button = QPushButton("Load JSON Data")
        backup_row.addWidget(self.backup_button)
        backup_row.addWidget(self.import_button)
        backup_row.addStretch()
        database_layout.addLayout(backup_row)

        self.main_layout.addWidget(database_box)
        self.main_layout.addStretch()

        self.backup_button.clicked.connect(self.backup_database)
        self.import_button.clicked.connect(self.import_json_data)


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


    # Replaces the current database with a validated JSON file.
    def import_json_data(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load JSON Data", "", "JSON Files (*.json)"
        )
        if not file_path:
            return

        answer = QMessageBox.question(
            self, "Replace Current Data",
            "Loading this file will replace the current items, inquiries, and claims. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        try:
            counts = import_database(file_path)
        except (OSError, ValueError, TypeError) as error:
            self.show_error(f"Could not load that JSON file.\n{error}")
            return

        self.data_imported.emit()
        self.show_info(
            "JSON data loaded successfully.\n"
            f"Items: {counts['items']}  |  Inquiries: {counts['inquiries']}  |  Claims: {counts['claims']}"
        )
