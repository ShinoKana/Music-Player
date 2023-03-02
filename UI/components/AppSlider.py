from qfluentwidgets import Slider
from .AppWidget import AppWidget, AppWidgetHintClass
from typing import Union, Literal, Callable
from Core import appManager
from PySide2.QtCore import Qt

sliderHint = Union[Slider, AppWidgetHintClass,'AppSlider']
class AppSlider(AppWidget(Slider)):
    def __init__(self:sliderHint, *args, direction:Literal['Horizontal', 'Vertical']= 'Horizontal',
                 onValueChanged:Callable[[Union[int, float]],any]=None, minimum=0, maximum=100,
                 value=None, **kwargs):
        if direction=='Horizontal':
            super().__init__(*args, orientation=Qt.Horizontal, **kwargs)
        else:
            super().__init__(*args, orientation=Qt.Vertical, **kwargs)

        if onValueChanged:
            self.valueChanged.connect(onValueChanged)

        self.setMinimum(minimum)
        self.setMaximum(maximum)
        if value:
            self.setValue(value)
        else:
            self.setValue(minimum)
    def changeStyle(self:sliderHint, styleKey, value):
        '''override appwidget method'''
        super().changeStyle(styleKey, value)
        bgColor = self.furthurBackgroundColor
        furthurColor = bgColor.darker(150) if appManager.config.isLightTheme() else bgColor.lighter(150)
        furthurColor=furthurColor.toTuple()
        bgColor = bgColor.toTuple()
        sty = f"""
                QSlider:horizontal {{
                    min-height: 60px;
                }}
                QSlider::groove:horizontal {{
                    height: 1px;
                    background: {'black' if appManager.config.isLightTheme() else 'white'}; 
                }}
                QSlider::handle:horizontal {{
                    width: 30px;
                    margin-top: -15px;
                    margin-bottom: -15px;
                    border-radius: 15px;
                    background: qradialgradient(spread:reflect, cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0.6 rgba{bgColor}, stop:0.7 rgba{bgColor[:3]+(100,)});
                }}
                QSlider::handle:horizontal:hover {{
                    background: qradialgradient(spread:reflect, cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0.6 rgba{furthurColor}, stop:0.7 rgba{furthurColor[:3]+(100,)});
                }}
                
                /*vertical*/
                QSlider:vertical {{
                    min-width: 60px;
                }}
                QSlider::groove:vertical {{
                    width: 1px;
                    background: {'black' if appManager.config.isLightTheme() else 'white'}; 
                }}
                QSlider::handle:vertical {{
                    height: 30px;
                    margin-left: -15px;
                    margin-right: -15px;
                    border-radius: 15px;
                    background: qradialgradient(spread:reflect, cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0.6 rgba{bgColor}, stop:0.7 rgba{bgColor[:3]+(100,)});
                }}
                QSlider::handle:vertical:hover {{
                    background: qradialgradient(spread:reflect, cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0.6 rgba{furthurColor}, stop:0.7 rgba{furthurColor[:3]+(100,)});
                }}
                """
        self.setStyleSheet(sty)