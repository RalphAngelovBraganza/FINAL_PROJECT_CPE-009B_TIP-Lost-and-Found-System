import os
import sys

from PyQt6.QtWidgets import QApplication

from data.store import BASE_DIR, create_database
from main_window import MainWindow
from login_window import LoginWindow


# Loads and applies the application styles.
def load_stylesheet(app):
    styles = []
    for name in ("styles.qss", "pages.qss", "dialogs.qss"):
        qss_path = os.path.join(BASE_DIR, name)
        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as file:
                style_text = file.read()
                checkmark_path = os.path.join(BASE_DIR, "checkmark.png").replace(os.sep, "/")
                style_text = style_text.replace(
                    "url(checkmark.png)", f'url("{checkmark_path}")'
                )
                styles.append(style_text)
    app.setStyleSheet("\n".join(styles))


# Starts the application.
def main():
    create_database()

    app = QApplication(sys.argv)

    login = LoginWindow()
    main_window = None


    # Opens the main window after sign-in.
    def open_application():
        nonlocal main_window
        load_stylesheet(app)
        main_window = MainWindow()
        main_window.show()
        login.close()

    login.login_successful.connect(open_application)
    login.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
