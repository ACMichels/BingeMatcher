from PySide6.QtCore import QSize
from PySide6.QtGui import Qt, QPixmap
from PySide6.QtWidgets import QVBoxLayout, QPushButton, QWidget, QLabel

from Style import rating_colors


class ButtonWithOverlay(QWidget):
    def __init__(self, callback=None, parent=None):
        super().__init__(parent)

        self.size = QSize(100, 150)
        self.setFixedSize(self.size)

        # Base layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Button with icon
        self.button = QPushButton()
        self.button.setIconSize(self.size)
        self.button.setFixedSize(self.size)
        self.button.setStyleSheet("border: none;")
        if callback:
            self.button.clicked.connect(callback)
        layout.addWidget(self.button)

        # Overlay widget
        self.overlay = QWidget(self)
        self.overlay.setFixedSize(self.size)
        self.overlay.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.overlay.setAttribute(Qt.WA_TransparentForMouseEvents)

        self.v_layout = QVBoxLayout()

        self.rating_label = QLabel(self)
        self.rating_label.setStyleSheet("border: 0px solid #00000000;")
        self.rating_label.setFixedSize(QSize(30, 30))
        self.rating_label.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.rating_label.setAlignment(Qt.AlignCenter)  # Optional: center the text

        self.v_layout.addStretch()
        self.v_layout.addWidget(self.rating_label)
        self.v_layout.setContentsMargins(0,0,0,0)
        self.overlay.setLayout(self.v_layout)

    def set_pixmap(self, pixmap: QPixmap):
        self.button.setIcon(pixmap)

    def set_rating(self, rating=2):
        if rating >= 0:
            self.overlay.setStyleSheet(f"background-color: #33{rating_colors[rating]}; border: 3px solid #{rating_colors[rating]};")
            self.rating_label.setStyleSheet(f"background-color: #44000000; border: 3px solid #{rating_colors[rating]}; color: #{rating_colors[rating]}; font-weight: bold; font-size: 18px;")
            self.rating_label.setText(f"{rating+1}")
        else:
            self.overlay.setStyleSheet(f"background-color: #00000000; border: 0px solid #00000000;")
            self.rating_label.setStyleSheet(f"border: 0px solid #00000000;")
            self.rating_label.setText(" ")
