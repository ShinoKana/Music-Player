from PySide2.QtWidgets import QWidget
from PySide2.QtCore import Qt
from PySide2.QtGui import QColor,QResizeEvent

import Core
from Core import appManager
from typing import Union, Literal
import os

# app widget base class
class ComponentTemplate(type):
    def __new__(metacls, f):
        cls = type.__new__(metacls, f.__name__, (), {
            '_f': f,
            '__qualname__': f.__qualname__,
            '__module__': f.__module__,
            '__doc__': f.__doc__
        })
        cls.__instances = {}
        return cls
    def __init__(cls, f):
        pass
    def __getitem__(cls, item):
        if not isinstance(item, tuple):
            item = (item,)
        try:
            return cls.__instances[item]
        except KeyError:
            c = cls._f(*item)
            cls.__instances[item] = c
            item_repr = '[' + ', '.join(repr(i) for i in item) + ']'
            c.__name__ = cls.__name__ + item_repr
            c.__qualname__ = cls.__qualname__ + item_repr
            c.__template__ = cls
            return c
    def __subclasscheck__(cls, subclass):
        for c in subclass.mro():
            if getattr(c, '__template__', None) == cls:
                return True
        return False
    def __instancecheck__(cls, instance):
        return cls.__subclasscheck__(type(instance))

    def __repr__(cls):
        from inspect import signature
        return '<template {!r}>'.format('{}.{}[{}]'.format(
            cls.__module__, cls.__qualname__, str(signature(cls._f))[1:-1]
        ))
class AppWidgetHintClass(QWidget):
    def __init__(self: QWidget, *args, appWindow: 'AppWindow' = None, parent=None, width: int = None,
                 height: int = None,
                 padding: Union[tuple, int] = 0, backgroundColor: Union[QColor, str] = None,
                 foregroundColor: Union[QColor, str] = None,
                 borderCornerRadius: Union[tuple, int] = 10, margin: Union[tuple, int] = 0, fontSize=None,
                 borderWidth=None,
                 borderColor=None, fontBold: bool = None, fontItalic: bool = None, fontStrikeOut: bool = None,
                 fontUnderLine: bool = None, textAlign: Literal['left', 'right', 'center', 'bottom', 'top'] = None,
                 **kwargs):
        pass
    @property
    def appWindow(self) -> 'AppWindow':
        pass
    @appWindow.setter
    def appWindow(self, appWindow: 'AppWindow'):
        pass
    @property
    def borderCornerRadius(self) -> tuple:
        pass
    @property
    def leftUpBorderCornerRadius(self) -> int:
        pass
    @property
    def rightUpBorderCornerRadius(self) -> int:
        pass
    @property
    def leftDownBorderCornerRadius(self) -> int:
        pass
    @property
    def rightDownBorderCornerRadius(self) -> int:
        pass
    @leftUpBorderCornerRadius.setter
    def leftUpBorderCornerRadius(self, leftUpBorderCornerRadius: int):
        pass
    @rightUpBorderCornerRadius.setter
    def rightUpBorderCornerRadius(self, rightUpBorderCornerRadius: int):
        pass
    @leftDownBorderCornerRadius.setter
    def leftDownBorderCornerRadius(self, leftDownBorderCornerRadius: int):
        pass
    @rightDownBorderCornerRadius.setter
    def rightDownBorderCornerRadius(self, rightDownBorderCornerRadius: int):
        pass
    @borderCornerRadius.setter
    def borderCornerRadius(self, borderCornerRadius: Union[int, tuple]):
        pass
    def SetBorderCornerRadius(self, *args):
        pass
    @property
    def borderWidth(self) -> int:
        pass
    @borderWidth.setter
    def borderWidth(self, borderWidth: int):
        pass
    def SetBorderWidth(self, borderWidth: int):
        pass
    @property
    def borderColor(self) -> QColor:
        pass
    @borderColor.setter
    def borderColor(self, borderColor: Union[QColor, str]):
        pass
    def SetBorderColor(self, borderColor: Union[QColor, str]):
        pass
    @property
    def backgroundColor(self) -> QColor:
        pass
    @backgroundColor.setter
    def backgroundColor(self, backgroundColor: Union[QColor, str]):
        pass
    @property
    def furthurBackgroundColor(self) -> QColor:
        pass
    def SetBackgroundColor(self, backgroundColor: Union[QColor, str]):
        pass
    @property
    def foregroundColor(self) -> QColor:
        pass
    @foregroundColor.setter
    def foregroundColor(self, foregroundColor: Union[QColor, str]):
        pass
    def SetForegroundColor(self, foregroundColor: Union[QColor, str]):
        pass
    @property
    def margin(self) -> tuple:
        pass
    @margin.setter
    def margin(self, margin: Union[tuple, int]):
        pass
    @property
    def leftMargin(self) -> int:
        pass
    @leftMargin.setter
    def leftMargin(self, leftMargin: int):
        pass
    @property
    def rightMargin(self) -> int:
        pass
    @rightMargin.setter
    def rightMargin(self, rightMargin: int):
        pass
    @property
    def topMargin(self) -> int:
        pass
    @topMargin.setter
    def topMargin(self, topMargin: int):
        pass
    @property
    def bottomMargin(self) -> int:
        pass
    @bottomMargin.setter
    def bottomMargin(self, bottomMargin: int):
        pass
    def SetMargin(self, *args):
        pass
    @property
    def fontSize(self) -> int:
        pass
    @fontSize.setter
    def fontSize(self, fontSize: int):
        pass
    def SetFontSize(self, fontSize: int):
        pass
    @property
    def fontBold(self) -> bool:
        pass
    @fontBold.setter
    def fontBold(self, fontBold: bool):
        pass
    def SetFontBold(self, fontBold: bool):
        pass
    @property
    def fontItalic(self) -> bool:
        pass
    @fontItalic.setter
    def fontItalic(self, fontItalic: bool):
        pass
    def SetFontItalic(self, fontItalic: bool):
        pass
    @property
    def fontUnderline(self) -> bool:
        pass
    @fontUnderline.setter
    def fontUnderline(self, fontUnderline: bool):
        pass
    def SetFontUnderline(self, fontUnderline: bool):
        pass
    @property
    def fontStrikeOut(self) -> bool:
        pass
    @fontStrikeOut.setter
    def fontStrikeOut(self, fontStrikeOut: bool):
        pass
    def SetFontStrikeOut(self, fontStrikeOut: bool):
        pass
    @property
    def textAlign(self) -> Literal['left', 'right', 'center', 'bottom', 'top']:
        pass
    @textAlign.setter
    def textAlign(self, textAlign: Literal['left', 'right', 'center', 'bottom', 'top']):
        pass
    def SetTextAlign(self, textAlign: Literal['left', 'right', 'center', 'bottom', 'top']):
        pass
    @property
    def componentStyleDict(self) -> dict:
        pass
    def changeStyle(self, styleKey, value):
        pass
    def deleteStyle(self, styleKey):
        pass
    def resizeEvent(self, event: QResizeEvent):
        pass
@ComponentTemplate
def __AppWidget(WidgetClass) -> AppWidgetHintClass:
    if not issubclass(WidgetClass, QWidget):
        raise TypeError('AppWidget must be a subclass of QWidget')
    class AppWidget(WidgetClass):
        def __init__(self:QWidget, *args, appWindow:'AppWindow'=None, parent=None, width:int=None, height:int=None,
                     padding:Union[tuple,int]=0, backgroundColor:Union[QColor, str]=None, foregroundColor:Union[QColor, str]=None,
                     borderCornerRadius:Union[tuple,int]=10, margin:Union[tuple,int]=0, fontSize=None, borderWidth=None,
                     borderColor=None, fontBold:bool=None, fontItalic:bool=None, fontStrikeOut:bool= None,
                     fontUnderLine:bool=None, textAlign:Literal['left','right','center','bottom','top']=None, **kwargs):
            try:
                super().__init__(*args, parent=parent, **kwargs)
            except Exception as e :
                print('{} init error st, message:{}'.format(self.__class__.__name__, e))

            self._appWindow = appWindow
            self.setAttribute(Qt.WA_StyledBackground, True)

            self._backgroundColor = None
            self._foregroundColor = None

            self._padding = {"top": 0, "bottom": 0, "left": 0, "right": 0}
            self._margin = {"top": 0, "bottom": 0, "left": 0, "right": 0}

            self._fontSize = None
            self._fontBold = None
            self._fontItalic = None
            self._fontStrikeOut = None
            self._fontUnderLine = None
            self._textAlign = None

            self._borderWidth = None
            self._borderColor = None
            self._borderCornerRadius = {"leftUp": 0, "rightUp": 0, "leftDown": 0, "rightDown": 0}

            self._styleDict = {'font-family': 'Segoe UI, Microsoft YaHei, Arial, Helvetica, sans-serif'}
            self.adjustSize()

            if width:
                self.setMinimumWidth(width)
            if height:
                self.setMinimumHeight(height)
            self.adjustSize()

            # region color
            if backgroundColor is not None:
                self.SetBackgroundColor(backgroundColor)
            else:
                if parent:
                    try:
                        self.SetBackgroundColor(QColor(parent.backgroundColor).lighter(140)
                                                if not appManager.config.isLightTheme()
                                                else QColor(parent.backgroundColor).darker(110))
                    except:
                        self.SetBackgroundColor(QColor(appManager.config.componentLightColorConfig.value
                                                       if appManager.config.isLightTheme()
                                                       else appManager.config.componentDarkColorConfig.value))
                else:
                    self.SetBackgroundColor(QColor(appManager.config.componentLightColorConfig.value
                                               if appManager.config.isLightTheme()
                                               else appManager.config.componentDarkColorConfig.value))
            if foregroundColor:
                self.SetForegroundColor(foregroundColor)
            # endregion

            # region font
            if fontSize:
                self.SetFontSize(fontSize)
            if fontBold:
                self.SetFontBold(fontBold)
            if fontItalic:
                self.SetFontItalic(fontItalic)
            if fontStrikeOut:
                self.SetFontStrikeOut(fontStrikeOut)
            if fontUnderLine:
                self.SetFontUnderLine(fontUnderLine)
            if textAlign:
                self.SetTextAlign(textAlign)
            # endregion

            # region padding & margin
            if padding:
                self.SetPadding(*padding)
            if margin:
                self.SetMargin(*margin)
            # endregion

            # region border
            if borderCornerRadius:
                self.SetBorderCornerRadius(borderCornerRadius)
            if borderWidth:
                self.SetBorderWidth(borderWidth)
            if borderColor:
                self.SetBorderColor(borderColor)
            # endregion

            self.adjustSize()
        #region app window
        @property
        def appWindow(self) -> 'AppWindow':
            return self._appWindow
        @appWindow.setter
        def appWindow(self, appWindow: 'AppWindow'):
            if appWindow == self._appWindow:
                return
            self._appWindow = appWindow
        #endregion

        #region border
        @property
        def borderCornerRadius(self) -> tuple:
            return (self._borderCornerRadius['leftUp'], self._borderCornerRadius['rightUp'],
                    self._borderCornerRadius['leftDown'], self._borderCornerRadius['rightDown'])
        @property
        def leftUpBorderCornerRadius(self) -> int:
            return self._borderCornerRadius['leftUp']
        @property
        def rightUpBorderCornerRadius(self) -> int:
            return self._borderCornerRadius['rightUp']
        @property
        def leftDownBorderCornerRadius(self) -> int:
            return self._borderCornerRadius['leftDown']
        @property
        def rightDownBorderCornerRadius(self) -> int:
            return self._borderCornerRadius['rightDown']
        @leftUpBorderCornerRadius.setter
        def leftUpBorderCornerRadius(self, leftUpBorderCornerRadius: int):
            self.SetBorderCornerRadius(leftUpBorderCornerRadius, None, None, None)
        @rightUpBorderCornerRadius.setter
        def rightUpBorderCornerRadius(self, rightUpBorderCornerRadius: int):
            self.SetBorderCornerRadius(None, rightUpBorderCornerRadius, None, None)
        @leftDownBorderCornerRadius.setter
        def leftDownBorderCornerRadius(self, leftDownBorderCornerRadius: int):
            self.SetBorderCornerRadius(None, None, leftDownBorderCornerRadius, None)
        @rightDownBorderCornerRadius.setter
        def rightDownBorderCornerRadius(self, rightDownBorderCornerRadius: int):
            self.SetBorderCornerRadius(None, None, None, rightDownBorderCornerRadius)
        @borderCornerRadius.setter
        def borderCornerRadius(self, borderCornerRadius: Union[int, tuple]):
            self.SetRadiusCorner(borderCornerRadius)
        def SetBorderCornerRadius(self, *args):
            if len(args) == 1:
                if isinstance(args[0], int):
                    AppWidget.SetBorderCornerRadius(self, args[0], args[0], args[0], args[0])
                elif isinstance(args[0], tuple) and len(args[0]) == 4:
                    AppWidget.SetBorderCornerRadius(self, args[0][0], args[0][1], args[0][2], args[0][3])
            elif len(args) == 4:
                self._borderCornerRadius['leftUp']= args[0] if args[0] is not None else None
                self._borderCornerRadius['rightUp'] = args[1] if args[1] is not None else None
                self._borderCornerRadius['leftDown'] = args[2] if args[2] is not None else None
                self._borderCornerRadius['rightDown'] = args[3] if args[3] is not None else None
            self.changeStyle('border-top-left-radius', f'{self._borderCornerRadius["leftUp"]}px')
            self.changeStyle('border-top-right-radius', f'{self._borderCornerRadius["rightUp"]}px')
            self.changeStyle('border-bottom-left-radius', f'{self._borderCornerRadius["leftDown"]}px')
            self.changeStyle('border-bottom-right-radius', f'{self._borderCornerRadius["rightDown"]}px')
        @property
        def borderWidth(self) -> int:
            return self._borderWidth
        @borderWidth.setter
        def borderWidth(self, borderWidth: int):
            self.SetBorderWidth(borderWidth)
        def SetBorderWidth(self, borderWidth: int):
            if borderWidth == self._borderWidth:
                return
            self._borderWidth = borderWidth
            self.changeStyle('border-width', f'{self._borderWidth}px')
        @property
        def borderColor(self) -> QColor:
            return self._borderColor
        @borderColor.setter
        def borderColor(self, borderColor: Union[QColor,str]):
            self.SetBorderColor(borderColor)
        def SetBorderColor(self, borderColor: Union[QColor,str]):
            if isinstance(borderColor, str):
                borderColor = QColor(borderColor)
            if borderColor is not None and self._borderColor is not None and borderColor.name() == self._borderColor.name():
                return
            elif borderColor is None and self._borderColor is None:
                return
            self._borderColor = borderColor
            self.changeStyle('border-color', self._borderColor.name() if self._borderColor.alpha() > 0 else 'transparent')

        #endregion

        #region backgroundColor
        @property
        def backgroundColor(self) -> QColor:
            return self._backgroundColor
        @backgroundColor.setter
        def backgroundColor(self, backgroundColor: Union[QColor,str]):
            self.SetBackgroundColor(backgroundColor)
        def SetBackgroundColor(self, backgroundColor: Union[QColor,str]):
            if isinstance(backgroundColor, str):
                backgroundColor = QColor(backgroundColor)
            if self._backgroundColor is not None and backgroundColor is not None and backgroundColor.name() == self._backgroundColor.name():
                return
            elif backgroundColor is None and self._backgroundColor is None:
                return
            self._backgroundColor = backgroundColor
            self.changeStyle('background-color', self._backgroundColor.name() if self._backgroundColor.alpha() > 0 else 'transparent')
        @property
        def furthurBackgroundColor(self) -> QColor:
            return self.backgroundColor.lighter() if appManager.config.isDarkTheme() else self.backgroundColor.darker()
        #endregion

        #region foregroundColor
        @property
        def foregroundColor(self) -> QColor:
            return self._foregroundColor
        @foregroundColor.setter
        def foregroundColor(self, foregroundColor: Union[QColor,str]):
            self.SetForegroundColor(foregroundColor)
        def SetForegroundColor(self, foregroundColor: Union[QColor,str]):
            if isinstance(foregroundColor, str):
                foregroundColor = QColor(foregroundColor)
            if foregroundColor is not None and self._foregroundColor is not None and foregroundColor.name() == self._foregroundColor.name():
                return
            elif foregroundColor is None and self._foregroundColor is None:
                return
            self._foregroundColor = foregroundColor
            self.changeStyle('color', self._foregroundColor.name() if self._foregroundColor.alpha() > 0 else 'transparent')
        #endregion

        #region padding
        @property
        def padding(self) -> tuple:
            return (self._padding['top'], self._padding['bottom'], self._padding['left'], self._padding['right'])
        @padding.setter
        def padding(self, padding:Union[tuple,int]):
            self.SetPadding(padding)
        @property
        def leftPadding(self) -> int:
            return self._padding['left']
        @leftPadding.setter
        def leftPadding(self, leftPadding: int):
            self.SetPadding(None,None,leftPadding,None)
        @property
        def rightPadding(self) -> int:
            return self._padding['right']
        @rightPadding.setter
        def rightPadding(self, rightPadding: int):
            self.SetPadding(None,None,None,rightPadding)
        @property
        def topPadding(self) -> int:
            return self._padding['top']
        @topPadding.setter
        def topPadding(self, topPadding: int):
            self.SetPadding(topPadding,None,None,None)
        @property
        def bottomPadding(self) -> int:
            return self._padding['bottom']
        @bottomPadding.setter
        def bottomPadding(self, bottomPadding: int):
            self.SetPadding(None,bottomPadding,None,None)
        def SetPadding(self, *args):
            if len(args) == 1:
                if isinstance(args[0], int):
                    AppWidget.SetPadding(self, args[0], args[0], args[0], args[0])
                elif isinstance(args[0], tuple) and len(args[0]) == 4:
                    AppWidget.SetPadding(self, args[0][0], args[0][1], args[0][2], args[0][3])
            elif len(args) == 4:
                self._padding['top'] = args[0] if args[0] is not None else self._padding['top']
                self._padding['bottom'] = args[1] if args[1] is not None else self._padding['bottom']
                self._padding['left'] = args[2] if args[2] is not None else self._padding['left']
                self._padding['right'] = args[3] if args[3] is not None else self._padding['right']
                self.changeStyle('padding-left', f'{self.leftPadding}px')
                self.changeStyle('padding-right', f'{self.rightPadding}px')
                self.changeStyle('padding-top', f'{self.topPadding}px')
                self.changeStyle('padding-bottom', f'{self.bottomPadding}px')
        #endregion

        #region margin
        @property
        def margin(self) -> tuple:
            return (self._margin['top'], self._margin['bottom'], self._margin['left'], self._margin['right'])
        @margin.setter
        def margin(self, margin:Union[tuple,int]):
            self.SetMargin(margin)
        @property
        def leftMargin(self) -> int:
            return self._margin['left']
        @leftMargin.setter
        def leftMargin(self, leftMargin: int):
            self.SetMargin(None, None, leftMargin, None)
        @property
        def rightMargin(self) -> int:
            return self._margin['right']
        @rightMargin.setter
        def rightMargin(self, rightMargin: int):
            self.SetMargin(None, None, None, rightMargin)
        @property
        def topMargin(self) -> int:
            return self._margin['top']
        @topMargin.setter
        def topMargin(self, topMargin: int):
            self.SetMargin(topMargin, None, None, None)
        @property
        def bottomMargin(self) -> int:
            return self._margin['bottom']
        @bottomMargin.setter
        def bottomMargin(self, bottomMargin: int):
            self.SetMargin(None, bottomMargin, None, None)
        def SetMargin(self, *args):
            if len(args) == 1:
                if isinstance(args[0], tuple) and len(args[0]) == 4:
                    AppWidget.SetMargin(self, args[0][0], args[0][1], args[0][2], args[0][3])
                elif isinstance(args[0], int):
                    AppWidget.SetMargin(self, args[0], args[0], args[0], args[0])
            elif len(args) == 4:
                self._margin["top"] = args[0] if args[0] is not None else None
                self._margin["bottom"] = args[1] if args[1] is not None else None
                self._margin["left"] = args[2] if args[2] is not None else None
                self._margin["right"] = args[3] if args[3] is not None else None
                self.changeStyle('margin-left', f'{self.leftMargin}px')
                self.changeStyle('margin-right', f'{self.rightMargin}px')
                self.changeStyle('margin-top', f'{self.topMargin}px')
                self.changeStyle('margin-bottom', f'{self.bottomMargin}px')
        #endregion

        #region font
        @property
        def fontSize(self) -> int:
            return self._fontSize
        @fontSize.setter
        def fontSize(self, fontSize: int):
            self.SetFontSize(fontSize)
        def SetFontSize(self, fontSize: int):
            if fontSize == self._fontSize:
                return
            self._fontSize = fontSize
            self.changeStyle('font-size', f'{self._fontSize}px')
        @property
        def fontBold(self) -> bool:
            return self._fontBold
        @fontBold.setter
        def fontBold(self, fontBold: bool):
            self.SetFontBold(fontBold)
        def SetFontBold(self, fontBold: bool):
            if fontBold == self._fontBold:
                return
            self._fontBold = fontBold
            self.changeStyle('font-weight', 'bold' if self._fontBold else 'normal')
        @property
        def fontItalic(self) -> bool:
            return self._fontItalic
        @fontItalic.setter
        def fontItalic(self, fontItalic: bool):
            self.SetFontItalic(fontItalic)
        def SetFontItalic(self, fontItalic: bool):
            if fontItalic == self._fontItalic:
                return
            self._fontItalic = fontItalic
            self.changeStyle('font-style', 'italic' if self._fontItalic else 'normal')
        @property
        def fontUnderline(self) -> bool:
            return self._fontUnderline
        @fontUnderline.setter
        def fontUnderline(self, fontUnderline: bool):
            self.SetFontUnderline(fontUnderline)
        def SetFontUnderline(self, fontUnderline: bool):
            if fontUnderline == self._fontUnderline:
                return
            self._fontUnderline = fontUnderline
            self.changeStyle('text-decoration', 'underline' if self._fontUnderline else 'none')
        @property
        def fontStrikeOut(self) -> bool:
            return self._fontStrikeOut
        @fontStrikeOut.setter
        def fontStrikeOut(self, fontStrikeOut: bool):
            self.SetFontStrikeOut(fontStrikeOut)
        def SetFontStrikeOut(self, fontStrikeOut: bool):
            if fontStrikeOut == self._fontStrikeOut:
                return
            self._fontStrikeOut = fontStrikeOut
            self.changeStyle('text-decoration', 'line-through' if self._fontStrikeOut else 'none')
        @property
        def textAlign(self) -> Literal['left','right','center','bottom','top']:
            return self._textAlign
        @textAlign.setter
        def textAlign(self, textAlign: Literal['left','right','center','bottom','top']):
            self.SetTextAlign(textAlign)
        def SetTextAlign(self, textAlign: Literal['left','right','center','bottom','top']):
            if textAlign == self._textAlign:
                return
            self._textAlign = textAlign
            self.changeStyle('qproperty-alignment', 'Align'+(self._textAlign).capitalize())
            self.changeStyle('text-align', self._textAlign)
        #endregion

        #region style dict
        @property
        def componentStyleDict(self) -> dict:
            return self._styleDict
        def changeStyle(self, styleKey, value):
            if value is None:
                self.deleteStyle(styleKey)
                return
            self._styleDict[styleKey] = value
            self.setStyleSheet(''.join([f'{key}:{value};' for key, value in self._styleDict.items() if value is not None]))
        def deleteStyle(self, styleKey):
            if styleKey in self._styleDict:
                del self._styleDict[styleKey]
                self.setStyleSheet(''.join([f'{key}:{value};' for key, value in self._styleDict.items() if value is not None]))
        #endregion

        def resizeEvent(self, event:QResizeEvent):
            super().resizeEvent(event)

    return AppWidget
def AppWidget(WidgetClass)-> AppWidgetHintClass:
    return __AppWidget[WidgetClass]



