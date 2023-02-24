from qfluentwidgets import Slider
from .AppWidget import AppWidget, AppWidgetHintClass
from typing import Union, Literal, Callable
from PySide2.QtCore import Qt

sliderHint = Union[Slider, AppWidgetHintClass]
class AppSlider(AppWidget(Slider)):
    def __init__(self:sliderHint, *ars, direction:Literal['Horizontal','Vertical']='Horizontal',
                 onValueChanged:Callable[[Union[int, float]],any]=None, minimum=0, maximum=100,
                 value=None, **kwargs):
        if direction=='Horizontal':
            super().__init__(*ars, orientation=Qt.Horizontal, **kwargs)
        else:
            super().__init__(*ars, orientation=Qt.Vertical, **kwargs)

        if onValueChanged:
            self.valueChanged.connect(onValueChanged)

        self.setMinimum(minimum)
        self.setMaximum(maximum)
        if value:
            self.setValue(value)
        else:
            self.setValue(minimum)