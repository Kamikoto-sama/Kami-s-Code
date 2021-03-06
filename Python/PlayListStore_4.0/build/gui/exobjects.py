from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QLineEdit, QTextEdit


class ExLineEdit(QLineEdit):
    clicked = pyqtSignal()
    doubleClicked = pyqtSignal()

    def mousePressEvent(self, event):
        self.clicked.emit()
        QLineEdit.mousePressEvent(self, event)

    def mouseDoubleClickEvent(self, event):
        self.doubleClicked.emit()
        QLineEdit.mouseDoubleClickEvent(self, event)

class ExTextEdit(QTextEdit):
    clicked = pyqtSignal()
    doubleClicked = pyqtSignal()

    def mouseDoubleClickEvent(self, event):
        self.doubleClicked.emit()
        QTextEdit.mouseDoubleClickEvent(self, event)