# Music Player
CUHK22-23 CSCI3280 Group Project

### 需要安裝的package
      * PySide2
      * Pillow
      * certifi
      * charset-normalizer
      * colorthief
      * idna
      * numpy
      * pywin32
      * requests
      * scipy
      * shiboken2
      * urllib3
      * darkdetect

### Python版本
* Python 3.8.5 或以上

### 文件夾說明
* ### `Core`
  * `Managers`: 單例模式的manager，管理所有操作
    * `AppManager`: 專門處理軟件的manager，包括軟件path、設定、語言、主題等
  * `DataType`: 數據類型、結構
    * `AutoTranslate系列`: 生成時自動翻譯成當前語言（切換語言需要重新打開軟件）
    * `FileInfo`: 最基礎的文件信息，包括文件名、路徑、類型、大小等
* ### `UI`: UI界面與組件
  * `Components`: UI組件, 有共通的底層屬性，可參閱`AppWidget.py`。method多數以大寫開始，方便與PYQT原本的method區分。
  * `pages`: UI頁面。 嵌入在窗口右側。可以通過`addComponent`方法增加組件。其他細節請參閱`AppPage.py`。
  * `windows`: UI窗口。 獨立的窗口，可以是單例或多例。其他細節請參閱`AppWindow.py`。
* ### `External Package`: 修改過的外部package。請勿嘗試使用原版庫。
* ### `Resources`: 資源文件
  * `Images`: 圖片
  * `appSetting.json`: 軟件設定
  * `translation.csv`: 翻譯文件