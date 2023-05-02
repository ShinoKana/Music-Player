from Core.DataType import AutoTranslateWord
from .AppPage import AppPage
from typing import Union
from PySide2.QtWidgets import QFrame, QLayout, QLabel, QVBoxLayout, QHBoxLayout, QGraphicsPixmapItem, QGraphicsScene, QGraphicsView, QGraphicsScene, QGraphicsPathItem
from PySide2.QtGui import QPixmap, QPainterPath, QBrush, QPainter
from components.AppScrollBox import AppScrollBox
from PySide2.QtCore import QRectF, QTimer, Qt
from Core import appManager

import os

class PlayerPage(AppPage):

    def __init__(self, appWindow, parent: Union[QFrame, QLayout] = None):
        super().__init__(appWindow=appWindow, parent=parent, titleText=AutoTranslateWord("Play"))
        self.pageLayout = QHBoxLayout()
        self.setLayout(self.pageLayout)
        self.labels = []
        self.switchingIn = False
        self.isDark = appManager.config.isDarkTheme()
        self.musicNow = ""
        self.lyric_path = "" 
        self.cover_path = ""
        app_music_box = self.appWindow.musicBox
        app_music_box.music_info_signal.connect(self.print_music_info)

        self.imageLayout = QVBoxLayout()
        self.image_view = QGraphicsView()
        self.imageLayout.addWidget(self.image_view)
        self.pageLayout.addLayout(self.imageLayout)
        self.update_image("")  # initialize transparent background

        self.scrollBox = AppScrollBox(titleText="Lyrics")
        self.pageLayout.addWidget(self.scrollBox)

        self.user_scrolling = False
        self.scrollBox.verticalScrollBar().valueChanged.connect(self.on_scrollbar_value_changed)
        self.last_lyrics_index = -1

        self.rotation_timer = QTimer()
        self.rotation_timer.timeout.connect(self.rotate_cover_image)


    def parse_lrc(self, file_path: str):
        lyrics_data = []
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith('['):
                    time_parts = line.split(']')
                    timestamp_str = time_parts[0][1:]
                    lyrics_line = time_parts[1].strip()
                    if ':' in timestamp_str:
                        time_parts = timestamp_str.split(':')
                        if len(time_parts) == 2:
                            minutes, seconds = time_parts
                        else:
                            continue
                        try:
                            timestamp = int(minutes) * 60 + float(seconds)
                            lyrics_data.append((timestamp, lyrics_line))
                        except ValueError:
                            continue
        return lyrics_data
    

    def on_scrollbar_value_changed(self, value):
        self.user_scrolling = True

    def rotate_cover_image(self):
        self.image_view.rotate(1)

    def pause_rotation(self):
        self.rotation_timer.stop()

    def update_lyrics_and_labels(self):
        if not self.lyric_path:
            return
        self.scrollBox.removeAllComponents()
        self.lyrics = []
        self.labels = []
        self.timeline = []

        imagePath = self.cover_path
        file_path = self.lyric_path

        # pixmap = QPixmap(imagePath).scaled(500, 500)
        self.update_image(imagePath)

        lyrics_data = self.parse_lrc(file_path)
        self.lyrics = [line[1] for line in lyrics_data]
        self.timeline = [line[0] for line in lyrics_data]
        for lyrics_line in self.lyrics:
            label = QLabel(lyrics_line.strip().replace("\n", ""))
            label.setFixedHeight(30)
            label.setAlignment(Qt.AlignCenter)
            if self.isDark:
                label.setStyleSheet("color: white;")
            self.labels.append(label)
            self.scrollBox.addComponent(label)

    def update_image(self, image_path):
        scene = QGraphicsScene()

        if image_path:
            pixmap = QPixmap(image_path).scaled(500, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        else:
            pixmap = QPixmap(500, 500)
            pixmap.fill(Qt.transparent)

        item = QGraphicsPixmapItem(pixmap)

        pixmap = QPixmap(image_path).scaled(500, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        item = QGraphicsPixmapItem(pixmap)

        path = QPainterPath()
        path.addEllipse(QRectF(0, 0, 500, 500))
        path_item = QGraphicsPathItem(path)
        path_item.setBrush(QBrush(item.pixmap()))
        path_item.setPen(Qt.NoPen)

        scene.addItem(path_item)
        self.image_view.setScene(scene)
        self.image_view.setRenderHint(QPainter.Antialiasing)
        self.image_view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        self.image_view.setOptimizationFlag(QGraphicsView.DontAdjustForAntialiasing, True)
        self.image_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.image_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.image_view.setFrameShape(QFrame.NoFrame)
        self.image_view.setStyleSheet("background: transparent; border: none;")

    def onSwitchIn(self):
        self.switchingIn = True
        if not hasattr(self, 'imageLayout'):
            self.imageLayout = QVBoxLayout()
            self.imageLabel = QLabel()
            self.imageLayout.addWidget(self.imageLabel)
            self.pageLayout.addLayout(self.imageLayout)

        if not hasattr(self, 'scrollBox'):
            self.scrollBox = AppScrollBox(titleText="Lyrics")
            self.pageLayout.addWidget(self.scrollBox)

        self.update_lyrics_and_labels()

    def print_music_info(self, title, position, lyric_path, cover_path):
        if self.musicNow != title:
            self.musicNow = title
            self.lyric_path = lyric_path
            self.cover_path = cover_path
            self.update_lyrics_and_labels()
            self.rotation_timer.stop()
        else:
            if not self.rotation_timer.isActive():
                self.rotation_timer.start(40)

        if position == 0:  # Pause
            self.rotation_timer.stop()
            self.pause_rotation()
        elif position == -1:  # Stopped
            self.rotation_timer.stop()
        else:
            if not self.rotation_timer.isActive():
                self.rotation_timer.start(40)

        if self.switchingIn:
            current_lyrics_index = -1
            for i in range(len(self.timeline) - 1):
                if self.timeline[i] <= position < self.timeline[i + 1]:
                    current_lyrics_index = i
                    break

            for i, label in enumerate(self.labels):
                label.setStyleSheet("")
                if self.isDark:
                    label.setStyleSheet("color: white;")
                    label.setFixedHeight(30)
                    if i == current_lyrics_index:
                        label.setStyleSheet("font-weight: bold; color: red;")

                if current_lyrics_index != self.last_lyrics_index:
                    self.last_lyrics_index = current_lyrics_index
                    if not self.user_scrolling:
                        if current_lyrics_index >= 0:
                            scroll_position = max(0, self.labels[current_lyrics_index].y() - self.scrollBox.height() // 2)
                            self.scrollBox.verticalScrollBar().setValue(scroll_position)
                    else:
                        self.user_scrolling = False

def onSwitchOut(self):
    self.switchingIn = False
    pass
