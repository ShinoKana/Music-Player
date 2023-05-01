# MusicInfo Player
CUHK22-23 CSCI3280 Group Project

### 未完成列表：
- PHASE 1
* [ ] database第一次使用需要手动创建
- PHASE 1 Enhanced
* [ ] 封面和歌词的寻址方式更改
- PHASE 2
* [ ] 网络连接(Flask)：应支持至少三个终端，通过TCP/IP网络堆栈连接到其他计算机，不硬编码地获取可连接计算机的IP地址
* [ ] 音乐搜索(sqlite3)：服务器保存了各个用户持有的音乐信息，包括hash, 名称等。 搜索音乐资源实际上是向服务器查询持有该音乐的用户，然后向服务器请求协助p2p连线从而从该用户处获取音乐文件。如果因为网络NAT等原因导致连线失败，则转成TURN模式透过服务器转发。
* [ ] 可用性检查：当用户从搜索结果中选择音频时，程序应检查本地是否存在音频文件，如存在，则直接播放；否则从其他计算机上流式传输。
* [ ] 实时音频流(socket)：程序在从其他计算机上流式传输时，应在接收到一定量的音频数据后尽快自动播放。
* [ ] P2P：程序应能同时从至少两个其他计算机接收一个音频文件，并交错播放。
- PHASE 2 Enhanced
* [ ] 支持流式传输其他音频格式。
* [ ] 支持多于三个客户端。
* [ ] 支持多于两个音频来源。

### 需要安裝的package
    * PySide2 (UI庫， 相當於PYQT5，但許可更寬鬆)
    * shiboken2 (PYQT綁定c++的庫)
    * Pillow （圖片處理庫， python3的PIL）
    * certifi (SSL認證庫)
    * charset-normalizer (編碼處理庫)
    * colorthief (顏色提取庫)
    * idna (網址處理庫)
    * numpy，scipy (數學庫)
    * pywin32 (Windows API庫)
    * requests (網路請求庫)
    * urllib3 (網址處理庫)
    * darkdetect (檢測系統主題，在設定UI顏色中的“跟隨系統設置”中使用。)
    * tiny tag (音樂文件tag信息提取)
____________________________________________________________________________________
### Python版本
* Python 3.8.5 或以上。
  > 請盡量使用3.8， 已知3.10可能存在無法設置task bar圖標的問題。未修復。
____________________________________________________________________________________
### 文件夾說明
### `Core`: 核心代碼
#### `Managers`: 單例模式的manager，管理所有操作。
- `AppManager`: 專門處理軟件的manager，包括文件路徑、設定、翻譯、記錄等
  * `config`: 軟件設定manager，包括主題，語言等
  * `record`: 軟件記錄manager，包括關閉前停止的位置、音量等
- `MusicPlayerManager`: 音樂播放器的manager，包括播放、暫停、停止等
- `LocalDataManager`: 數據庫和本地文件的manager
#### `DataType`: 數據類型、結構
- `AutoTranslate系列`: 生成時自動翻譯成當前語言（切換語言需要重新打開軟件）
- `FileInfo`: 最基礎的文件信息，包括文件名、路徑、類型、大小等
- `MusicInfo`: 音樂文件的信息，包括音樂名、作者、封面、時長等。繼承自`FileInfo`
### `UI`: UI界面與組件
> #### `Components`: UI組件, 有共通的底層屬性，可參閱`AppWidget.py`。method多數以大寫開始，方便與PYQT原本的method區分。
- `backgroundColor (set/get/init)`: 背景顏色
- `foregroundColor (set/get/init)`: 前景顏色（一般是文字顏色）
- `borderColor (set/getter/init)`: 邊框顏色
- `borderWidth (set/get/init)`: 邊框寬度
- `borderCornerRadius (set/ge/init)`: 邊框圓角
- `textAlign (set/get/init)`: 文字對齊方式
- `fontSize (set/get/init)`: 字體大小
- `fontItalic (set/get/init)`: 字體是否斜體
- `fontBold (set/get/init)`: 字體是否粗體
- `fontUnderline (set/get/init)`: 字體是否有下劃線
- `fontStrikeOut (set/get/init)`: 字體是否有刪除線
- `margin (set/get/init)`: 邊距
- `padding (set/get/init)`: 內邊距
  > ##### 如果有parent且没有設置顏色，則顏色為parent 更淺/更深 顏色（視乎深色/淺色主題）。
 
#### `pages`: UI頁面。 嵌入在窗口右側。可以通過`addComponent`方法增加組件。其他細節請參閱`AppPage.py`。
- `addComponent`: 增加組件。所有頁面component必須在此方法中增加，否則無法正常顯示。可以是Widget或Layout。
- `onSwitchIn`: 當頁面切換到此頁面時調用
- `onSwitchOut`: 當頁面切換出此頁面時調用

#### `windows`: UI窗口。 獨立的窗口，可以是單例或多例。其他細節請參閱`AppWindow.py`。
- `toast`: 通知。
- `goLoading`: 彈出loading提示。
- `onSwitchOut`: 結束loading提示。
-  `addPage`: 增加頁面。
- `switchPage`: 切換頁面。
- `addNavBarButton`: 增加導航欄按鈕。
### `External Package`: 修改過的外部package
  >   *請勿嘗試使用原版庫。*
*  `pyqt5Custom`: UI組件庫，用作文件上傳組件及按鈕組件
*  `qfluentwidgets`: UI組件庫，用作頁面自動滾動、設定面板等
*  `qframelesswindow`: UI組件庫，用作無邊框窗口
*  `sqlite_utils`: sqlite庫，在原有庫的基礎上增加了一些功能
### `Resources`: 資源文件
* `Images`: 圖片
* `appSetting.json`: 軟件設定
* `translation.csv`: 翻譯文件
*  `appRecord.json`: 用户記錄，例如關閉前停止的位置、音量等
*  `appTempSetting.json`: 臨時記錄，類似Unity的PlayerPrefs，用於儲存臨時數據（常用的數據建議使用正常Record）
### `Tools`: 工具類
* `translationKeyDetector`: 翻譯key檢測器，用於檢測.py文件中所有的key。多余的key會從翻譯文件中刪除，反之增加。

____________________________________________________________________________________
