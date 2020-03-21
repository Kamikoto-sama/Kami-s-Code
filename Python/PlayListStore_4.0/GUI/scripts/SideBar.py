# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './/SideBar.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(323, 434)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.sideBar = QtWidgets.QFrame(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.sideBar.sizePolicy().hasHeightForWidth())
        self.sideBar.setSizePolicy(sizePolicy)
        self.sideBar.setStyleSheet("")
        self.sideBar.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.sideBar.setFrameShadow(QtWidgets.QFrame.Raised)
        self.sideBar.setObjectName("sideBar")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.sideBar)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.close_side = QtWidgets.QPushButton(self.sideBar)
        self.close_side.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.close_side.sizePolicy().hasHeightForWidth())
        self.close_side.setSizePolicy(sizePolicy)
        self.close_side.setMaximumSize(QtCore.QSize(20, 16777215))
        self.close_side.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.close_side.setFocusPolicy(QtCore.Qt.NoFocus)
        self.close_side.setObjectName("close_side")
        self.horizontalLayout.addWidget(self.close_side)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout.setSpacing(7)
        self.verticalLayout.setObjectName("verticalLayout")
        self._2 = QtWidgets.QHBoxLayout()
        self._2.setObjectName("_2")
        self.title_time = QtWidgets.QLabel(self.sideBar)
        self.title_time.setMinimumSize(QtCore.QSize(0, 20))
        self.title_time.setAlignment(QtCore.Qt.AlignCenter)
        self.title_time.setObjectName("title_time")
        self._2.addWidget(self.title_time, 0, QtCore.Qt.AlignLeft)
        self.title_date = QtWidgets.QLabel(self.sideBar)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.title_date.setFont(font)
        self.title_date.setToolTipDuration(-1)
        self.title_date.setScaledContents(False)
        self.title_date.setAlignment(QtCore.Qt.AlignCenter)
        self.title_date.setObjectName("title_date")
        self._2.addWidget(self.title_date, 0, QtCore.Qt.AlignRight)
        self.verticalLayout.addLayout(self._2)
        self.genre = ExLineEdit(self.sideBar)
        self.genre.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.genre.setFocusPolicy(QtCore.Qt.NoFocus)
        self.genre.setMaxLength(60)
        self.genre.setReadOnly(True)
        self.genre.setObjectName("genre")
        self.verticalLayout.addWidget(self.genre)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setSpacing(2)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.open = QtWidgets.QPushButton(self.sideBar)
        self.open.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.open.setFocusPolicy(QtCore.Qt.NoFocus)
        self.open.setObjectName("open")
        self.horizontalLayout_2.addWidget(self.open, 0, QtCore.Qt.AlignLeft)
        self.link = ExLineEdit(self.sideBar)
        self.link.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.link.setFocusPolicy(QtCore.Qt.NoFocus)
        self.link.setMaxLength(2000)
        self.link.setReadOnly(True)
        self.link.setObjectName("link")
        self.horizontalLayout_2.addWidget(self.link)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.desc = ExTextEdit(self.sideBar)
        self.desc.setFocusPolicy(QtCore.Qt.NoFocus)
        self.desc.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.desc.setTabChangesFocus(True)
        self.desc.setDocumentTitle("")
        self.desc.setReadOnly(True)
        self.desc.setAcceptRichText(False)
        self.desc.setObjectName("desc")
        self.verticalLayout.addWidget(self.desc)
        self.save = QtWidgets.QPushButton(self.sideBar)
        self.save.setEnabled(False)
        self.save.setMaximumSize(QtCore.QSize(16777215, 23))
        self.save.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.save.setObjectName("save")
        self.verticalLayout.addWidget(self.save)
        self.is_con = QtWidgets.QCheckBox(self.sideBar)
        self.is_con.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.is_con.setFocusPolicy(QtCore.Qt.NoFocus)
        self.is_con.setObjectName("is_con")
        self.verticalLayout.addWidget(self.is_con)
        self.is_finished = QtWidgets.QCheckBox(self.sideBar)
        self.is_finished.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.is_finished.setFocusPolicy(QtCore.Qt.NoFocus)
        self.is_finished.setObjectName("is_finished")
        self.verticalLayout.addWidget(self.is_finished)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout_3.addWidget(self.sideBar)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.close_side.setText(_translate("Form", "<"))
        self.title_time.setText(_translate("Form", "9999h-99m"))
        self.title_date.setToolTip(_translate("Form", "<html><head/><body><p><span style=\" font-size:12pt; font-weight:600;\">Добавлено\\Просмотрено</span></p></body></html>"))
        self.title_date.setText(_translate("Form", "0000.00.00"))
        self.genre.setToolTip(_translate("Form", "Жанр"))
        self.genre.setPlaceholderText(_translate("Form", "Жанр"))
        self.open.setToolTip(_translate("Form", "<html><head/><body><p><span style=\" font-size:12pt; font-weight:600;\">Открыть ссылку</span></p></body></html>"))
        self.open.setText(_translate("Form", "Открыть"))
        self.link.setToolTip(_translate("Form", "Ссылка"))
        self.link.setPlaceholderText(_translate("Form", "Ссылка"))
        self.desc.setToolTip(_translate("Form", "Описание"))
        self.desc.setPlaceholderText(_translate("Form", "Описание"))
        self.save.setText(_translate("Form", "Сохранить"))
        self.is_con.setText(_translate("Form", "Это продолжение"))
        self.is_finished.setText(_translate("Form", "Тайтл не закончен"))
from gui.exobjects import ExLineEdit, ExTextEdit


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())