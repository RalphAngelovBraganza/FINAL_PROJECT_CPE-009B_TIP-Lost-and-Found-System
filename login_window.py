from pathlib import Path

from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QCheckBox,
    QVBoxLayout, QHBoxLayout, QFrame, QGraphicsDropShadowEffect
)

from data.store import window_icon_path


# Handles staff sign-in.
class LoginWindow(QWidget):
    login_successful = pyqtSignal()


    # Sets up this component.
    def __init__(self):
        super().__init__()
        self.setWindowTitle("T.I.P. Lost & Found Office Management & Tracking System")
        self.setWindowIcon(QIcon(window_icon_path("login.png")))
        self.resize(440, 430)
        self.setMinimumSize(400, 400)

        style_path = Path(__file__).with_name("login.qss")
        if style_path.exists():
            style_text = style_path.read_text(encoding="utf-8")
            checkmark_path = style_path.with_name("checkmark.png").resolve().as_posix()
            style_text = style_text.replace(
                "url(checkmark.png)", f'url("{checkmark_path}")'
            )
            self.setStyleSheet(style_text)

        self.title = QLabel("T.I.P. Lost & Found")
        self.subtitle = QLabel("Office Management & Tracking System")
        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.show_password = QCheckBox("Show Password")
        self.login_btn = QPushButton("Login")
        self.clear_btn = QPushButton("Clear")
        self.status = QLabel("")

        self.title.setObjectName("title")
        self.subtitle.setObjectName("subtitle")
        self.login_btn.setObjectName("loginBtn")
        self.clear_btn.setObjectName("clearBtn")
        self.status.setObjectName("status")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        self.add_button_shadow(self.login_btn)
        self.add_button_shadow(self.clear_btn)

        self.card = QFrame()
        self.card.setObjectName("card")
        buttons = QHBoxLayout()
        buttons.addWidget(self.clear_btn)
        buttons.addWidget(self.login_btn)

        card_layout = QVBoxLayout()
        card_layout.setSpacing(12)
        card_layout.addWidget(self.title)
        card_layout.addWidget(self.subtitle)
        card_layout.addSpacing(8)
        card_layout.addWidget(self.username)
        card_layout.addWidget(self.password)
        card_layout.addWidget(self.show_password)
        card_layout.addLayout(buttons)
        card_layout.addWidget(self.status)
        self.card.setLayout(card_layout)

        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.addStretch()
        layout.addWidget(self.card)
        layout.addStretch()
        self.setLayout(layout)

        self.login_btn.clicked.connect(self.login)
        self.clear_btn.clicked.connect(self.clear)
        self.show_password.toggled.connect(self.toggle_password)
        self.password.returnPressed.connect(self.login)
        self.username.returnPressed.connect(self.login)

        self.setWindowOpacity(0.0)
        self.fade = QPropertyAnimation(self, b"windowOpacity", self)
        self.fade.setDuration(800)
        self.fade.setStartValue(0.0)
        self.fade.setEndValue(1.0)
        self.fade.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.fade.start()


    # Adds the button shadow.
    def add_button_shadow(self, button):
        shadow = QGraphicsDropShadowEffect(button)
        shadow.setBlurRadius(10)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(Qt.GlobalColor.darkGray)
        button.setGraphicsEffect(shadow)


    # Updates the sign-in field style.
    def set_style_property(self, widget, name, value):
        widget.setProperty(name, value)
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        widget.update()


    # Shows or hides the password text.
    def toggle_password(self, checked):
        self.password.setEchoMode(
            QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
        )


    # Checks the staff sign-in details.
    def login(self):
        user = self.username.text().strip()
        password = self.password.text()

        if user == "staffLF" and password == "1234":
            self.set_style_property(self.username, "error", False)
            self.set_style_property(self.password, "error", False)
            self.set_style_property(self.status, "state", "success")
            self.status.setText("Login successful. Opening application...")
            self.login_btn.setEnabled(False)
            self.login_successful.emit()
        else:
            self.set_style_property(self.username, "error", True)
            self.set_style_property(self.password, "error", True)
            self.set_style_property(self.status, "state", "error")
            self.status.setText("Invalid username or password.")
            self.shake()


    # Clears the sign-in fields.
    def clear(self):
        self.username.clear()
        self.password.clear()
        self.status.clear()
        self.set_style_property(self.username, "error", False)
        self.set_style_property(self.password, "error", False)
        self.set_style_property(self.status, "state", "")
        self.login_btn.setEnabled(True)
        self.username.setFocus()


    # Shakes the login window after invalid details.
    def shake(self):
        if hasattr(self, "shake_anim") and self.shake_anim.state() == QPropertyAnimation.State.Running:
            return
        start = self.pos()
        offsets = [0, -10, 10, -8, 8, -4, 4, 0]
        self.shake_anim = QPropertyAnimation(self, b"pos", self)
        self.shake_anim.setDuration(400)
        for i, dx in enumerate(offsets):
            step = i / (len(offsets) - 1)
            self.shake_anim.setKeyValueAt(step, start + QPoint(dx, 0))
        self.shake_anim.start()
