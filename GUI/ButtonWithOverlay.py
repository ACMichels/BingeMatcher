from PySide6.QtCore import QSize
from PySide6.QtGui import Qt, QPixmap
from PySide6.QtWidgets import QVBoxLayout, QPushButton, QWidget, QLabel

from Style import rating_colors, select_height, use_overlay_colors


class ButtonWithOverlay(QWidget):
    def __init__(self, callback=None, parent=None):
        super().__init__(parent)

        self.size = QSize(100, 150)
        self.movable_size = QSize(100, 150 + select_height)
        self.setFixedSize(self.movable_size)

        self.setContentsMargins(0, 0, 0, 0)

        self.spacing = QWidget()
        self.spacing.setFixedHeight(select_height)

        # Movable part
        self.movable_widget = QWidget()
        self.movable_widget.setFixedSize(self.movable_size)
        self.movable_layout = QVBoxLayout()
        self.movable_layout.setContentsMargins(0, 0, 0, 0)
        self.movable_layout.setSpacing(0)

        self.movable_widget.setLayout(self.movable_layout)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.spacing)
        self.layout.addWidget(self.movable_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

        # Button with icon
        self.button = QPushButton(self.movable_widget)
        self.button.setIconSize(self.size)
        self.button.setFixedSize(self.size)
        self.button.setStyleSheet("border: none;")
        if callback:
            self.button.clicked.connect(callback)

        # Overlay widget
        self.overlay = QWidget(self.movable_widget)
        self.overlay.setFixedSize(self.size)
        self.overlay.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.v_layout = QVBoxLayout()

        self.rating_label = QLabel(self.movable_widget)
        self.rating_label.setFixedSize(QSize(30, 30))
        self.rating_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.rating_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.v_layout.addStretch()
        self.v_layout.addWidget(self.rating_label)
        self.v_layout.setContentsMargins(0,0,0,0)
        self.overlay.setLayout(self.v_layout)

    def set_pixmap(self, pixmap: QPixmap):
        self.button.setIcon(pixmap)

    def set_rating(self, rating:int=-1):
        if rating >= 0:
            if use_overlay_colors:
                self.overlay.setStyleSheet(f"background-color: #33{rating_colors[rating]}; border: 3px solid #{rating_colors[rating]};")
            else:
                self.overlay.setStyleSheet(f"border: 3px solid #{rating_colors[rating]};")
            self.rating_label.setStyleSheet(f"background-color: #44000000; border: 3px solid #{rating_colors[rating]}; color: #{rating_colors[rating]}; font-weight: bold; font-size: 18px;")
            self.rating_label.setText(f"{rating+1}")
        else:
            self.overlay.setStyleSheet("")
            self.rating_label.setStyleSheet("")
            self.rating_label.setText("")

    def select(self):
        self.spacing.setFixedHeight(0)

    def deselect(self):
        self.spacing.setFixedHeight(select_height)
