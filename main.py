from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QLabel, QColorDialog, QInputDialog, QErrorMessage, QFontDialog, QListWidgetItem
from PyQt5.QtGui import QPixmap, QPicture, QImage, QIcon, QPainter, QPen, QColor, QFontInfo, QFontDatabase, QFont, QBrush, QPen
from PyQt5 import Qt
from PyQt5.QtCore import QPoint, Qt
from PyQt5 import uic

from UI.ChanelChangeUi import Ui_ChannelChangeWindow
from UI.BrushSettingsWindowUi import BrushSettingWindow
from UI.galleryUi import GalleryMainWindow
from UI.BlurChangeUi import UiBlurChangeWindow
from UI.CanvasUi import CanvasWindow
from UI.FontSettingsWindowUi import FontSettingsWindow
from UI.RecentFilesWindowUi import RecentFilesWindow
import datetime
import sqlite3
import sys


WIDTHOFBRUSH = 2
COLOROFBRUSH = QColor(0, 0, 0)
COLOROFTEXT = QColor(0, 0, 0)
FONT = QFont('Arial', 2)
CON = sqlite3.connect('RecentColorsAndFiles.db')
CUR = CON.cursor()
IMAGE = None
NONCHANNELCHANGEIMAGE = None


class Program(QMainWindow, GalleryMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon('icon.svg'))
        self.setGeometry(0, 0, 600, 600)
        self.f = None     
        self.initUi()

    def initUi(self):
        self.setWindowTitle('Gallery from Gucci')
        
        # Настройка сигналов и слотов
        self.brushBtn.clicked.connect(self.OpenCanvas)
        self.ChannelsFilter.clicked.connect(self.ChannelChangeWindowOpen)
        self.black_white.clicked.connect(self.ConvertToBlackWhiteInterface)
        self.negativFilter.clicked.connect(self.ConvertToNegativeInterface)
        self.BlurBtn.clicked.connect(self.BluringImageInterface)

        # Настройка кнопок из menubar
        self.actionSave.triggered.connect(self.SaveCurrentPicture)
        self.action.triggered.connect(lambda: self.fileWindow.show())
        self.actionOpen.triggered.connect(self.OpenFile)
        self.actionSave_as.triggered.connect(self.SaveAsCurrentPicture)
        self.actionBack_to_source.triggered.connect(self.ChangeToOriginalPicture)
        
        # Инициализация классов для изменения картинки    
        self.ChannelChanger = ChannelChangeWindow()
        self.BrushChangeWindow = BrushSettingsWindow()
        self.canvas = PaintingImageWindow()
        self.FontWindow = FontSettingsWindow()
        self.fileWindow = RecentFileWindow(self)
        self.ChannelChanger.closeEvent = self.closeChannelChangeWindow
        self.canvas.closeEvent = self.closeCanvasWindow

    def BluringImageInterface(self):
        # Функция производит blur, работая непосредственно с пикселями
        if self.f:
            StepOfBlur, StatusOfApply = QInputDialog.getInt(self, 'Введите уровень размытия', 'Уровень размытия', 1, 1, 4, 1)
            if StatusOfApply:
                self.BluringImage(IMAGE, StepOfBlur)
                self.updatePicture()
                self.BluringImage(NONCHANNELCHANGEIMAGE, StepOfBlur)
                return
        self.statusbar.showMessage('Вы ещё не открыли файл!')
        self.statusbar.setStyleSheet('background-color: red')


    def BluringImage(self, image, StepOfBlur):
        for row in range(self.height):
            for col in range(self.width):
                start_col, stop_col = max(0, col - StepOfBlur), min(self.width, col + StepOfBlur + 1)
                start_row, stop_row = max(0, row - StepOfBlur), min(self.height, row + StepOfBlur + 1)
                neighbours = [image.pixelColor(i, j).getRgb()[:3] 
                    for i in range(start_col, stop_col) for j in range(start_row, stop_row)
                    if (i, j) != (col, row)]
                R_Value = [elem[0] for elem in neighbours]
                G_Value = [elem[1] for elem in neighbours]
                B_Value = [elem[2] for elem in neighbours]
                color = QColor(sum(R_Value) // len(R_Value), sum(G_Value) // len(G_Value), sum(B_Value) // len(B_Value))
                image.setPixelColor(col, row, color)

    def ChannelChangeWindowOpen(self):
        if self.f:
            self.ChannelChanger.show()
            return
        self.statusbar.showMessage('Вы ещё не открыли файл!')
        self.statusbar.setStyleSheet('background-color: red')
        
    def OpenCanvas(self):
        if self.f:
            self.canvas.show()
            self.updatePicture()
            return
        self.statusbar.showMessage('Вы ещё не открыли файл!')
        self.statusbar.setStyleSheet('background-color: red')
 
    def OpenFile(self, file=None):
        global IMAGE
        global NONCHANNELCHANGEIMAGE

        self.f = file if file else QFileDialog.getOpenFileName(self, 'Выберите картинку', '',
                'Картинка (*.jpg);;Картинка (*.jpeg);;Картинка (*.png);;Картинка (*.jfif)')[0]
        if self.f:
            IMAGE = QImage(self.f)
            if IMAGE.isNull():
                self.statusbar.showMessage('Данный формат файлов не поддерживается.')
                self.statusbar.setStyleSheet('background-color: red')
                return
            NONCHANNELCHANGEIMAGE = IMAGE.copy()
            self.width, self.height = IMAGE.width(), IMAGE.height()
            self.pixmap = QPixmap.fromImage(IMAGE).scaled(self.picture.size())
            CUR.execute(f'''INSERT into RecentFiles values ("{self.f}", "{datetime.date.today()}",
                                "{datetime.datetime.now().time()}")''')
            CON.commit()
            self.picture.setPixmap(self.pixmap)
            self.statusbar.clearMessage()
            self.statusbar.setStyleSheet('')

    def ConvertToBlackWhiteInterface(self):
        if self.f:
            self.ConvertToBlackWhite(IMAGE)
            self.updatePicture()
            self.ConvertToBlackWhite(NONCHANNELCHANGEIMAGE)
            return
        self.statusbar.showMessage('Вы ещё не открыли файл!')
        self.statusbar.setStyleSheet('background-color: red')

    # Функция для изменения картинки в чёрно-белый
    def ConvertToBlackWhite(self, image):
        for i in range(self.width):
            for j in range(self.height):
                r, g, b, a = image.pixelColor(i, j).getRgb()
                bw = (r + g + b) // 3
                image.setPixelColor(i, j, QColor(bw, bw, bw))
    
    def ConvertToNegativeInterface(self):
        if self.f:
            self.ConvertToNegative(IMAGE)
            self.updatePicture()
            self.ConvertToNegative(NONCHANNELCHANGEIMAGE)
            return
        self.statusbar.showMessage('Вы ещё не открыли файл!')
        self.statusbar.setStyleSheet('background-color: red')   
    
    # Функция для изменения картинки в негатив
    def ConvertToNegative(self, image):
        for i in range(self.width):
            for j in range(self.height):
                r, g, b, a = image.pixelColor(i, j).getRgb()
                image.setPixelColor(i, j, QColor(255 - r, 255 - g, 255 - b))
        
    # Функция сохраняет и сменяет Image в pixmap
    def updatePicture(self):
        try:
            self.pixmap = QPixmap.fromImage(IMAGE).scaled(self.picture.size())
            self.picture.setPixmap(self.pixmap)
            self.statusbar.clear()
            self.statusbar.setStyleSheet('')
        except: 
            pass

    # Функция возвращает картинку в исходное положение
    def ChangeToOriginalPicture(self):
        self.OpenFile(self.f)

    # Функция сохраняет нынешнюю картинку в тот же файл, через который она была открыта
    def SaveCurrentPicture(self):
        if self.f:
            IMAGE.save(self.f)

    # Сохраняет картинку по указанному пути
    def SaveAsCurrentPicture(self):
        if self.f:
            f = QFileDialog.getSaveFileName(self, 'Сохранить как')[0]
            if f:
                IMAGE.save(f)

    def resizeEvent(self, event):
        self.updatePicture()

    def closeEvent(self, event):
        CUR.execute('DELETE FROM RecentColors')
        CON.commit()
        CON.close()

    def show(self):
        super().show()
        self.fileWindow.show()
    
    def closeChannelChangeWindow(self, event):
        self.updatePicture()
    
    def closeCanvasWindow(self, event):
        self.updatePicture()
        
    
class ChannelChangeWindow(QMainWindow, Ui_ChannelChangeWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon('icon.svg'))
        self.dict = {'On': "Off", "Off": "On"}
        self.setupUi(self)

        for i in self.ChanelChangeGroup.buttons():
            i.clicked.connect(self.toggle)
        self.UseIt.clicked.connect(self.Apply)
        self.quitBtn.clicked.connect(self.quit)
        self.state = ['On', 'On', "On"]
        self.data = None

    def toggle(self):
        sender = self.sender()
        sender.setText(self.dict[sender.text()])

    def Apply(self):
        data = {}
        for i in self.ChanelChangeGroup.buttons():
            data[i.objectName()] = 1 if i.text() == 'On' else 0
        self.data = data
        self.ChangePictureChannels()
        self.close()
    
    def ChangePictureChannels(self):
        r1 = 1
        g1 = 1
        b1 = 1
        for button in self.data:
            if not self.data[button]:
                if button == 'R_channel':
                    r1 = 0
                elif button == 'G_channel':
                    g1 = 0
                elif button == 'B_channel':
                    b1 = 0
        for i in range(IMAGE.width()):
            for j in range(IMAGE.height()):
                r, g, b, a = NONCHANNELCHANGEIMAGE.pixelColor(i, j).getRgb()
                r = r if r1 else 0
                g = g if g1 else 0
                b = b if b1 else 0
                IMAGE.setPixelColor(i, j, QColor(r, g, b))       
    
    def quit(self):
        self.close()


class BrushSettingsWindow(QMainWindow, BrushSettingWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon('icon.svg'))
        self.width = 2
        self.color = QColor(0, 0, 0)
        self.setupUi(self)
        self.initUi()

    def initUi(self):
        self.apply.clicked.connect(self.applyChanges)
        self.cancel.clicked.connect(lambda: self.close())
        self.brushColorChanger.clicked.connect(self.setBrushColor)

    def setBrushColor(self):
        self.color = QColorDialog.getColor()
        self.brushColorChanger.setStyleSheet(f'''background-color: {self.color.name()}''')
    
    def applyChanges(self):
        global COLOROFBRUSH
        global WIDTHOFBRUSH

        COLOROFBRUSH = self.color
        CUR.execute(f'''INSERT INTO RecentColors VALUES ({self.color.red()}, {self.color.green()}, {self.color.blue()})''')
        CON.commit()
        self.brushColorChanger.setStyleSheet(f'''background-color: {self.color.name()}''')
        WIDTHOFBRUSH = self.widthBox.value()
        self.close()
    
    def show(self):
        self.brushColorChanger.setStyleSheet(f'background-color: rgb{COLOROFBRUSH.getRgb()[:3]}')
        super().show()


class PaintingImageWindow(QMainWindow, CanvasWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon('icon.svg'))
        self.setupUi(self)
        self.resize(500, 500) 
        self.setWindowTitle('Drawer')
        self.initUi()

    def initUi(self):
        self.apply_changes_btn.clicked.connect(self.applyChanges)
        self.cancelBtn.clicked.connect(self.cancel)
        self.DrawingModeSwitcher.clicked.connect(self.setModeToDrawing)
        self.TextModeSwitcher.clicked.connect(self.setModeToTexting)

        self.fontSettings = FontSettingsWindow()
        self.BrushSettings = BrushSettingsWindow()
        self.fontSettings.closeEvent = lambda x: self.RefreshRecentColors()
        self.BrushSettings.closeEvent = lambda x: self.RefreshRecentColors()

        self.last_x, self.last_y = None, None
        self.drawingMode = False
        self.writingMode = False
        self.font = QFont('Arial', 20)
        self.colorOfBrush = self.colorOfText = QColor(0, 0, 0)
        self.text = ''
        self.widthOfBrush = 2
        for btn in self.ColorButtonGroup.buttons():
            btn.clicked.connect(self.ChangeColor)
        
    def ChangeColor(self):
        global COLOROFBRUSH
        global COLOROFTEXT

        sender = self.sender()
        if self.drawingMode:
            COLOROFBRUSH = sender.color
        else:
            COLOROFTEXT = sender.color
        self.RefreshRecentColors()

    def setModeToDrawing(self):
        self.drawingMode = True
        self.writingMode = False
        self.writingStatus = False
        self.DrawingModeSwitcher.setStyleSheet('color: blue')
        self.TextModeSwitcher.setStyleSheet('color: black')
        self.BrushSettings.show()
    
    def setModeToTexting(self):
        error = QErrorMessage(self)
        error.showMessage("""Для того чтобы начать рисовать текст нажмите на\n
                            место, в котором хотите нарисовать текст. \n
                            Для дальнейщего ввода нужно просто напечатать \n
                            то что вы хотите напечатать, для удаления просто \n
                            нажмите backspace. Для окончания ввода нажмите Enter\n
                            или нажмите на другое место.""")
        self.DrawingModeSwitcher.setStyleSheet('color: black')
        self.TextModeSwitcher.setStyleSheet('color: blue')
        self.drawingMode = False
        self.writingMode = True
        self.writingStatus = False
        self.fontSettings.show()
        self.text = ''
        self.RefreshRecentColors()

    def mousePressEvent(self, event):
        self.status = True
        self.last_pos = event.pos()
        self.posOfText = event.pos()
        if self.writingMode:
            self.WritingStatus = True
            self.text = ''
            self.copyWithoutText = self.copy.copy()

    def mouseReleaseEvent(self, event):
        self.status = False
        self.last_pos = None
        
    def mouseMoveEvent(self, event):
        if self.drawingMode and self.status:
            self.drawingLine(event.pos(), self.copy)
            self.updatePicture()
            self.drawingLine(event.pos(), self.nonChannelChangeCopy)
            self.last_pos = event.pos()
            self.copyWithoutText = self.copy.copy()
        
    def drawingLine(self, pos, image):
        pen = QPen(COLOROFBRUSH, WIDTHOFBRUSH)
        painter = QPainter(image)
        painter.setPen(pen)
        painter.drawLine(self.last_pos - self.label.pos(), pos - self.label.pos())

    def keyPressEvent(self, event):
        if self.writingMode and self.WritingStatus:
            text = event.text()
            if event.key() == 16777220:
                self.WritingStatus = False
                self.copyWithoutText = self.copy.copy()
            elif event.key() == Qt.Key_Backspace:
                self.qimage = self.copyWithoutText.copy()
                self.text = self.text[0:-1]
                self.copy = self.copyWithoutText.copy()
                self.drawingTextInterface()
                self.updatePicture()
            elif event.key() == Qt.Key_Shift:
                self.text += " "
                self.updatePicture()
            else:
                self.text += text
                self.drawingTextInterface()
                self.updatePicture()

    def drawingText(self, image):
        qp = QPainter(image)
        qp.setFont(FONT)
        qp.setPen(QPen(COLOROFTEXT))
        qp.drawText(self.posOfText - self.label.pos() + QPoint(-5, 10), self.text)
        
    def drawingTextInterface(self):
        self.drawingText(self.copy)
        self.updatePicture()
        self.drawingText(self.nonChannelChangeCopy)

    def closeEvent(self, event):
        self.main.updatePicture()
        self.close()
    
    def applyChanges(self):
        global IMAGE
        global NONCHANNELCHANGEIMAGE

        IMAGE = self.copy
        NONCHANNELCHANGEIMAGE = self.nonChannelChangeCopy
        self.close()
    
    def cancel(self):
        self.close()
    
    def updatePicture(self):
        pixmap = QPixmap.fromImage(self.copy)
        self.label.setPixmap(pixmap)
    
    def show(self):
        self.copy = IMAGE.copy()
        self.copyWithoutText = self.copy.copy()
        self.nonChannelChangeCopy = NONCHANNELCHANGEIMAGE.copy()
        self.updatePicture()
        self.label.setFixedSize(IMAGE.width(), IMAGE.height())
        self.RefreshRecentColors()
        super().show()

    def RefreshRecentColors(self):
        self.recentColors = CUR.execute('''SELECT * FROM RecentColors''').fetchall()[::-1][:12]
        for i, btn in enumerate(self.ColorButtonGroup.buttons()):
            if i >= len(self.recentColors):
                break
            btn.setStyleSheet(f'background-color: rgb{self.recentColors[i]}')
            btn.color = QColor(*self.recentColors[i])

class FontSettingsWindow(QMainWindow, FontSettingsWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon('icon.svg'))
        self.initUi()

    def initUi(self):
        self.font = QFont('Arial', 20)
        self.color = QColor(0, 0, 0)
        self.ApplyChanges.clicked.connect(self.UseChanges)
        self.DenyChanges.clicked.connect(lambda: self.close())
        self.FontChangeBtn.clicked.connect(self.ChangeFont)
        self.ColorOfTextChangeBtn.clicked.connect(self.ChangeColor)
    
    def UseChanges(self):
        global FONT
        global COLOROFTEXT

        FONT = self.font if self.font else FONT
        COLOROFTEXT = self.color if self.color else COLOROFTEXT
        CUR.execute(f'''INSERT INTO RecentColors VALUES ({self.color.red()}, {self.color.green()}, {self.color.blue()})''')
        CON.commit()
        self.close()


    def ChangeFont(self):
        font, statusOfPressing = QFontDialog.getFont()
        if statusOfPressing:
            self.font = font
            self.FontChangeBtn.setText(self.font.family() + " " + str(self.font.pointSize()))
                
    
    def ChangeColor(self):
        color = QColorDialog().getColor()
        if color:
            self.color = color
            self.ColorOfTextChangeBtn.setStyleSheet(f'background-color: rgb{self.color.getRgb()[:3]}')

    def show(self):
        self.FontChangeBtn.setText(FONT.family() + ' ' + str(FONT.pointSize()))
        self.ColorOfTextChangeBtn.setStyleSheet(f'background-color: rgb{COLOROFTEXT.getRgb()[:3]}')
        super().show()


class RecentFileWindow(QMainWindow, RecentFilesWindow):
    def __init__(self, obj):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon('icon.svg'))
        self.main = obj
        self.FilesList.itemDoubleClicked.connect(self.OpenFile)

    def show(self):
        self.FilesList.clear()
        data = CUR.execute('SELECT * FROM RecentFiles').fetchall()[::-1][:10]
        for i in data:
            self.FilesList.addItem(QListWidgetItem(i[0]))
        super().show()

    def OpenFile(self, item):
        self.main.OpenFile(item.text())
        self.close()

def except_hook(cls, traceback, exception):
    sys.__excepthook__(cls, traceback, exception)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Program()
    sys.excepthook = except_hook
    win.show()
    sys.exit(app.exec())

