from Core.DataType import AutoTranslateWord
from .AppPage import AppPage
from typing import Union
from PySide2.QtWidgets import QFrame, QLayout, QLabel, QVBoxLayout, QHBoxLayout
from PySide2.QtGui import QPixmap
from components.AppScrollBox import AppScrollBox
from Core import appManager


import os

class PlayerPage(AppPage):
    
    def __init__(self, appWindow, parent: Union[QFrame, QLayout] = None):
        super().__init__(appWindow=appWindow, parent=parent, titleText=AutoTranslateWord("Play"))
        print("Initial")
        #TODO: Because the color of the scroll box is different
        #TODO: I deliberately set to white, which may lead to the dark mode display strange
        self.pageLayout = QHBoxLayout()
        self.setLayout(self.pageLayout)
        self.labels = []
        self.switchingIn = False
        self.isDark = appManager.config.isDarkTheme()
        self.musicNow = ""
        app_music_box = self.appWindow.musicBox
        app_music_box.music_info_signal.connect(self.print_music_info)


    def update_lyrics_and_labels(self):
        self.scrollBox.removeAllComponents()
        self.lyrics = []
        self.labels = []
        self.timeline = []

        self.imagePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lyric\\", self.musicNow + ".png")
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lyric\\", self.musicNow + ".txt")

        pixmap = QPixmap(self.imagePath).scaled(500, 500)
        self.imageLabel.setPixmap(pixmap)

        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            self.lyrics = lines
            for line in lines:
                label = QLabel(line.strip().replace("\n", ""))
                label.setFixedHeight(30)
                if self.isDark:
                    label.setStyleSheet("color: white;")
                self.labels.append(label)
                self.scrollBox.addComponent(label)

            for i in range(0, len(lines)):
                time = lines[i].split(']')[0][1:]
                time = int(time.split(':')[0]) * 60 + int(time.split(':')[1].split('.')[0])
                self.timeline.append(time)

            for label in self.labels:
                label.setStyleSheet("")
                if self.isDark:
                    label.setStyleSheet("color: white;")
                label.setFixedHeight(30)
                self.labels[0].setStyleSheet("font-weight: bold; color: red;")
        

    def onSwitchIn(self):
        print("onSwitchIn")
            #TODO:Here the file address is found based on the absolute path, and the file name is also fixed
            #TODO:Need to get the name of the song and find the corresponding file
        
        self.switchingIn = True
        if not hasattr(self, 'imageLayout'):
            # Create the image layout if it doesn't exist
            self.imageLayout = QVBoxLayout()
            self.imageLabel = QLabel()
            self.imageLayout.addWidget(self.imageLabel)
            self.pageLayout.addLayout(self.imageLayout)

        if not hasattr(self, 'scrollBox'):
            # Create the scroll box if it doesn't exist
            self.scrollBox = AppScrollBox(titleText="Lyrics")
            #self.scrollBox.setStyleSheet("QLabel { padding: 5px; }")
            self.pageLayout.addWidget(self.scrollBox)
            #self.scrollBox.viewport().setStyleSheet("background-color: #FFFFFF;")

        

        self.update_lyrics_and_labels()


    def print_music_info(self, title, position):

        if self.musicNow != title:
                print("newtitle: ", title)
                print("oldtitle: ",self.musicNow)
                self.musicNow = title
                self.update_lyrics_and_labels()

        if self.switchingIn:
            for i in range(0, len(self.timeline)-1):
                    
                if self.timeline[0] <= position and self.timeline[i] < position < self.timeline[i+1]:
                    for label in self.labels:
                        label.setStyleSheet("")
                        if self.isDark:
                            label.setStyleSheet("color: white;")
                        label.setFixedHeight(30)
                    self.labels[i].setStyleSheet("font-weight: bold; color: red;")

            
    def onSwitchOut(self):
        print("onSwitchOut")
        self.switchingIn = False
        pass
