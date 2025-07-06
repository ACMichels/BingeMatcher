import json
import os
from functools import partial

from PySide6.QtCore import QObject, QEvent, QSize
from PySide6.QtGui import QPixmap, QFont, Qt, QPainter, QColor, QShortcut, QKeySequence, QPaintEvent, QWheelEvent
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QScrollArea

from API import get_genres, get_movies
from GUI.ButtonWithOverlay import ButtonWithOverlay
from ImageLoading import load_image
from Style import rating_colors, rating_texts, select_height


class ScrollRedirectFilter(QObject):
    def __init__(self, scroll_area):
        super().__init__()
        self.scroll_area = scroll_area

    def eventFilter(self, watched: QObject, event: QEvent):
        if event.type() == QEvent.Type.Wheel and isinstance(event, QWheelEvent):
            delta = event.angleDelta().y() / 2
            bar = self.scroll_area.horizontalScrollBar()
            bar.setValue(bar.value() - delta)
            return True
        return False

def create_font(family: str, size: int, bold: bool=False, italic: bool=False):
    font = QFont()
    font.setFamily(family)
    font.setPointSize(size)
    font.setBold(bold)
    font.setItalic(italic)
    return font

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.movies: list[dict] = []
        self.movie_buttons: list[ButtonWithOverlay] = []
        self.movie_idx = 0
        self.ratings = dict()

        self.background_image: QPixmap | None = None

        # Main layout
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.top_layout = QHBoxLayout()
        self.main_layout.addLayout(self.top_layout)

        # Image placeholder
        self.poster_label = QLabel()
        self.poster_label.setFixedSize(300, 400)
        self.top_layout.addWidget(self.poster_label)

        # Add widgets to the main layout
        self.detail_layout = QVBoxLayout()
        self.top_layout.addLayout(self.detail_layout)

        # Title text area
        self.title_text = QLabel("<Title>")
        self.title_text.setFont(create_font("Roboto", 22, bold=True))
        self.title_text.setStyleSheet("color: rgb(255, 255, 255);")
        self.title_text.setWordWrap(True)

        # Small text area
        self.detail_text = QLabel("Text")
        self.detail_text.setFont(create_font("Roboto", 10, italic=True))
        self.detail_text.setStyleSheet("color: rgb(225, 225, 225);")
        self.detail_text.setFixedHeight(20)
        self.detail_text.setIndent(5)

        # Large text area
        self.description_text = QLabel("<Description>")
        self.description_text.setFont(create_font("Roboto", 11))
        self.description_text.setStyleSheet("color: rgb(255, 255, 255);")
        self.description_text.setWordWrap(True)

        self.detail_layout.addWidget(self.title_text)
        self.detail_layout.addWidget(self.detail_text)
        self.detail_layout.addWidget(self.description_text)
        self.detail_layout.addStretch()

        # Movie list
        self.rating_buttons = []
        rating_layout = QHBoxLayout()
        for i in range(5):
            button = QPushButton(rating_texts[i])
            button.setFixedHeight(40)
            button.clicked.connect(partial(self.toggle_rate, i))
            self.rating_buttons.append(button)
            rating_layout.addWidget(button)
        self.main_layout.addLayout(rating_layout)

        self.movie_button_pane = QHBoxLayout()
        self.movie_button_pane.setSpacing(10)

        self.scroll_widget = QWidget()
        self.scroll_widget.setLayout(self.movie_button_pane)
        self.scroll_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.scroll_widget.setMinimumHeight(160 + select_height)
        self.scroll_widget.setStyleSheet("background: transparent;")
        self.movie_scroll_area = QScrollArea()
        self.movie_scroll_area.setWidgetResizable(False)  # Crucial for horizontal scrolling
        self.movie_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.movie_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.movie_scroll_area.setStyleSheet("background: transparent;")
        self.movie_scroll_area.setFixedHeight(185 + select_height)
        self.movie_scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        self.movie_scroll_area.setWidget(self.scroll_widget)

        self.scroll_filter = ScrollRedirectFilter(self.movie_scroll_area)
        self.scroll_widget.installEventFilter(self.scroll_filter)
        self.movie_scroll_area.installEventFilter(self.scroll_filter)

        self.main_layout.addWidget(self.movie_scroll_area)

        # Window settings
        self.setWindowTitle('Breves Bingers')
        self.setGeometry(100, 100, 800, 600)
        self.show()

        list_ids = json.loads(os.getenv("MOVIE_LIST_IDS"))
        genre_list = get_genres()
        for list_id in list_ids:
            movie_list = get_movies(list_id)
            self.add_movie_list(movie_list, genre_list)
        self.set_movie(0)
        self.load_ratings()

        # Register shortcuts
        QShortcut(QKeySequence(Qt.Key.Key_N), self, self.goto_unrated_movie)
        QShortcut(QKeySequence(Qt.Key.Key_Left), self, self.goto_last_movie)
        QShortcut(QKeySequence(Qt.Key.Key_Right), self, self.goto_next_movie)
        for i in range(5):
            QShortcut(QKeySequence(self.tr(str(i+1))), self, partial(self.toggle_rate, i))

    def toggle_rate(self, rating: int, movie_id: int|None=None, save: bool=True):
        self.rate(-1 if self.ratings.get(self.movies[self.movie_idx]['id'], -1) == rating else rating, movie_id, save)

    def rate(self, rating: int, movie_id: int|None=None, save: bool=True):
        if movie_id is None:
            movie_id = self.movies[self.movie_idx]['id']

        for i_id, item in enumerate(self.movies):
            if item['id'] == movie_id:
                self.movie_buttons[i_id].set_rating(rating)

        if rating >= 0:
            self.ratings[movie_id] = rating
        else:
            del self.ratings[movie_id]
        if save:
            self.save_ratings()
        self.load_current_movie_rating()

    def load_ratings(self):
        if os.path.isfile("ratings.json"):
            with open('ratings.json', 'r') as f:
                self.ratings = json.load(f)
            self.ratings = {int(k): v for k, v in self.ratings.items()}
            for m_id, rating in self.ratings.items():
                self.rate(rating, movie_id=m_id, save=False)
        self.load_current_movie_rating()

    def save_ratings(self):
        with open('ratings.json', 'w') as f:
            json.dump(self.ratings, f)

    def paintEvent(self, event: QPaintEvent):
        if self.background_image is None:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        scale = min(self.background_image.width() / self.width(), self.background_image.height() / self.height())

        source_rect = self.rect()
        source_rect.setSize(QSize(int(source_rect.width() * scale), int(source_rect.height() * scale)))
        source_rect.moveCenter(self.background_image.rect().center())

        # Draw the background image
        painter.drawPixmap(self.rect(), self.background_image, source_rect)

        # Apply a semi-transparent white overlay
        overlay = QColor(0, 0, 0, 128)
        painter.fillRect(self.rect(), overlay)

        painter.end()

    def load_current_movie_rating(self):
        movie_item = self.movies[self.movie_idx]
        rating = self.ratings.get(movie_item['id'], -1)
        for idx in range(5):
            if idx == rating:
                self.rating_buttons[idx].setStyleSheet(f"background-color: #{rating_colors[idx]}; font-weight: bold;")
            else:
                self.rating_buttons[idx].setStyleSheet("")

    def set_background_pixmap(self, pixmap: QPixmap):
        self.background_image = pixmap
        self.update()

    def set_movie_poster_pixmap(self, pixmap: QPixmap):
        self.poster_label.setPixmap(pixmap.scaled(300, 400, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def goto_unrated_movie(self):
        max_movie_idx = len(self.movies)
        found = False
        checked_movie_idx = 0
        for idx in range(max_movie_idx):
            checked_movie_idx = (self.movie_idx + idx + 1) % max_movie_idx
            movie_item = self.movies[checked_movie_idx]
            if movie_item['id'] not in self.ratings:
                found = True
                break
        if found:
            self.set_movie(checked_movie_idx)

    def goto_next_movie(self):
        self.set_movie((self.movie_idx + 1) % len(self.movies))

    def goto_last_movie(self):
        self.set_movie((self.movie_idx - 1) % len(self.movies))

    def set_movie(self, idx: int):
        self.movie_buttons[self.movie_idx].deselect()
        self.movie_buttons[idx].select()

        self.movie_idx = idx
        movie_item = self.movies[idx]

        movie_btn = self.movie_button_pane.itemAt(idx).widget()
        self.movie_scroll_area.ensureWidgetVisible(movie_btn)

        load_image(movie_item['poster_path'], self.set_movie_poster_pixmap)

        self.title_text.setText(f"{movie_item['title']} ({movie_item['release_date'][:4]})")

        self.detail_text.setText(movie_item['genres'])
        self.description_text.setText(movie_item["overview"])

        load_image(movie_item['backdrop_path'], self.set_background_pixmap)
        self.load_current_movie_rating()

    @staticmethod
    def add_movie_list_pixmap(btn: ButtonWithOverlay, pixmap: QPixmap):
        btn.set_pixmap(pixmap.scaledToHeight(150, Qt.TransformationMode.SmoothTransformation))

    def add_movie_list(self, movies: list[dict], genres: dict):
        start_id = len(self.movies)
        self.movies.extend(movies)

        for idx, m in enumerate(movies):
            m['genres'] = ", ".join([genres[g_id] for g_id in m['genre_ids']])
            callback = partial(self.set_movie, idx+start_id)
            btn = ButtonWithOverlay(callback=callback)
            load_image(m['poster_path'], partial(self.add_movie_list_pixmap, btn))
            self.movie_button_pane.addWidget(btn)
            self.movie_buttons.append(btn)

        total_width = 110 * self.movie_button_pane.count()
        self.scroll_widget.setMinimumWidth(total_width)
