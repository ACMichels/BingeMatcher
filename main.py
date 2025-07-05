import sys
from PySide6.QtWidgets import QApplication
from dotenv import load_dotenv
from GUI.MainGUI import MyWindow

def main():
    load_dotenv()

    app = QApplication(sys.argv)
    MyWindow()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()