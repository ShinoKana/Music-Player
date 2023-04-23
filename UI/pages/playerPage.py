from Core.DataType import AutoTranslateWord
from .AppPage import AppPage
from typing import Union
from PySide2.QtWidgets import QFrame, QLayout, QLabel, QVBoxLayout, QHBoxLayout
from PySide2.QtGui import QPixmap
from components.AppScrollBox import AppScrollBox
import os

class PlayerPage(AppPage):
    def __init__(self, appWindow, parent: Union[QFrame, QLayout] = None):
        super().__init__(appWindow=appWindow, parent=parent, titleText=AutoTranslateWord("Play"))

        #Create images and Lyrics scroll box
        #TODO: Because the color of the scroll box is different
        #TODO: I deliberately set to white, which may lead to the dark mode display strange
        self.imageLayout = QVBoxLayout()
        self.imageLabel = QLabel()
        self.imageLayout.addWidget(self.imageLabel)
        self.pageLayout = QHBoxLayout()
        self.pageLayout.addLayout(self.imageLayout)
        self.scrollBox = AppScrollBox(titleText="Lyrics")
        self.scrollBox.setStyleSheet("QLabel { padding: 5px; }")
        self.pageLayout.addWidget(self.scrollBox)
        self.scrollBox.viewport().setStyleSheet("background-color: #FFFFFF;")



    def onSwitchIn(self):
        #TODO:Here the file address is found based on the absolute path, and the file name is also fixed
        #TODO:Need to get the name of the song and find the corresponding file
        self.imagePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "image1.png")
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "text_file.txt")
        
        pixmap = QPixmap(self.imagePath).scaled(500,500)
        self.imageLabel.setPixmap(pixmap)
        self.setLayout(self.pageLayout)

        #Read the file, I put it in the same folder as playerPage
        #Lyrics(Japanese) with timeline is in 'text_file.txt' 
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                label = QLabel(line.strip().replace("\n",""))
                label.setFixedHeight(30)
                self.scrollBox.addComponent(label)

            #The following codes calculates the time interval between each two lines of text, 
            # i.e. the time each line of text should be displayed
            #The results are stored in the list "delay"
            delay = []
            for i in range(0,len(lines)):
                if(i == 0):
                    time = lines[0].split(']')[0][1:]
                    time = int(time.split(':')[0])*60000 + int(time.split(':')[1].split('.')[0])*1000+ int(time.split(':')[1].split('.')[1])
                    delay.append(time)
                else:
                    time = [lines[i].split(']')[0], lines[i-1].split(']')[0]]
                    for j in range(2):
                        time[j] = time[j][1:]
                        time[j] = int(time[j].split(':')[0])*6000 + int(time[j].split(':')[1].split('.')[0])*1000+ int(time[j].split(':')[1].split('.')[1])
                    delay.append(abs(time[0]-time[1]))

                    
            
    def onSwitchOut(self):
        pass;

