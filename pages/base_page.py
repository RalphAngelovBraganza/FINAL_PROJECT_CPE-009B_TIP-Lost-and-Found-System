from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

# okay pages are responsible for the content of the main window, they are not responsible for the navigation
#  bar or the header bar, those are handled by the main window
class BasePage(QWidget):
    def __init__(self, title):
        super().__init__()
        self.page_title = title

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)

        title_label = QLabel(title)
        title_label.setObjectName("pageTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(title_label)

        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(12)
        layout.addLayout(self.main_layout)

        tLabel = QLabel("YOW WE WILL ADD SOMETHING HERE LATER AH")
        tLabel.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addStretch()
        layout.addWidget(tLabel)
        layout.addStretch()

    def refresh(self):
        pass
