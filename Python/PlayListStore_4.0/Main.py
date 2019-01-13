# -*- coding: utf-8 -*-
import sys
import sqlite3
import webbrowser
from datetime import datetime

from PyQt5.uic import loadUi
from PyQt5.QtGui import QIntValidator
from PyQt5.QtGui import QCursor
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QEventLoop
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QPoint
from PyQt5.QtCore import QPropertyAnimation
from PyQt5.QtCore import QEasingCurve
from PyQt5.QtCore import QSize
from PyQt5.QtCore import QRect
from PyQt5.QtCore import QRegExp
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QProxyStyle
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QTabBar
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QStyle
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtWidgets import QHeaderView

# LOAD DB
try:
    if __name__ == "__main__":
        db = sqlite3.connect("Data.pls")
        sql = db.cursor().execute
        data = [int(d[0]) for d in sql("SELECT value FROM Data")]
        ID = data[0]
        TotalViewed = data[1]
        TotalAdded = data[2]
except Exception as e:
    print('Load db:', e.args)
# CONSTANTS
RowIcons = [
    'Icons/viewed.png',
    'Icons/continuation.png',
    'Icons/pause.png',
    'Icons/viewing.png',
    '',
    'Icons/not_finished.png']
Icons = {
    'n': 4,
    'viewed': 0,
    'not_finished': 5,
    'con': 1,
    'viewing': 3,
    'pause': 2,
    'cancel_mark': 'Icons/cancel_mark.png',
    'search_title': 'Icons/search_title.png'}
Color = {
    'n': '#D9D9D9',
    'edit': 'none',
    'viewed': '#AEDD17',
    'viewing': '#6EBCD2',
    'pause': '#DC143C',
    'is_con': '#FEE02F'}
# Skin = 'Skins/dark_orange.css'
Skin = open('style.css').read()
SideWidth = 300
SideAnimDur = 500
AddFormDur = 500  # Add title form anim
RowAnimDur = 6
RowLoadDur = 20
AddRowDur = 550
AddPlDur = 500
EditEnterDur = 600
RowHeightMin = 34
RowHeightMax = 72
IconSize = 32

MainP = None
EpisodeTime = 20
ConTabName = '|Список продолжений|'
SortTitlesBy = "count"


def show_exception(name_from, error, parent=MainP):
    QMessageBox.critical(parent, "PLS4_ERROR: %s" % name_from, str(error))


def save_data(save: str, value=1):
    try:
        global ID, TotalAdded, TotalViewed
        if save == 'id':
            ID += 1
            sql('UPDATE Data set value=%s where name="id"' % ID)
        if save == 'viewed':
            TotalViewed += value
            MainP.viewed_count.setText('Всего просмотрено:' + str(TotalViewed))
            sql('UPDATE Data set value=%s where name="viewed"' % TotalViewed)
        if save == 'added':
            TotalAdded += value
            sql('UPDATE Data set value=%s where name="added"' % TotalAdded)
    except Exception as e:
        show_exception("__main__save_data", e)


class SelfStyledIcon(QProxyStyle):
    def pixelMetric(self, q_style_pixel_metric, option=None, widget=None):
        if q_style_pixel_metric == QStyle.PM_SmallIconSize:
            return IconSize
        else:
            return QProxyStyle.pixelMetric(self, q_style_pixel_metric, option, widget)


class SearchTitleForm(QWidget):
    def __init__(self):
        super().__init__(None, Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint)
        try:
            loadUi("GUI/SearchTitleForm.ui", self)
            self.setStyleSheet(Skin)
            self.setWindowIcon(QIcon(Icons['search_title']))

            self.result.horizontalHeader().resizeSection(0, 60)
            self.result.horizontalHeader().resizeSection(2, 90)
            self.result.horizontalHeader().resizeSection(3, 0)
            self.result.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
            self.result.cellClicked.connect(self.select_item)
            self.result.cellDoubleClicked.connect(self.close)

            self.genre_search.stateChanged.connect(self.do_search)

            self.search_timer = QTimer(self)
            self.search_timer.timeout.connect(self.do_search)
            self.search_timer.setSingleShot(True)
            self.search_timer.setInterval(EditEnterDur)
            self.search_edit.textEdited.connect(self.search_timer.start)

            self.rows = list()
            self.selected_row = -1
        except Exception as e:
            show_exception("SearchTitleForm__init", e, self)

    def do_search(self):
        try:
            text = self.search_edit.text()
            self.result.clear()
            self.result.setHorizontalHeaderLabels(["Кол-во",
                                                   "Название тайтла",
                                                   "Плейлист"])
            if text != '':
                if self.genre_search.checkState() == 2:
                    query = ["genre LIKE '%{}%'".format(word) for word in text.split()]
                    query = ' and '.join(query)
                else:
                    query = "title_name LIKE '%{}%'".format(text)

                query = "SELECT count, title_name, playlist, id FROM Titles " \
                        "WHERE %s" % query
                self.rows = list(sql(query))
                self.show_result(self.rows)
        except Exception as e:
            show_exception("search_title_do_search", e, self)

    def show_result(self, results):
        self.result.setRowCount(len(results))
        for i, row in enumerate(results):
            count = QTableWidgetItem(str(row[0]))
            count.setTextAlignment(4)
            self.result.setItem(i, 0, count)
            self.result.setItem(i, 1, QTableWidgetItem(row[1]))
            self.result.setItem(i, 2, QTableWidgetItem(row[2]))

    def select_item(self, row):
        if row != self.selected_row:
            MainP.find_select_title(self.rows[row][2], self.rows[row][3])
            self.selected_row = row


# todo: формат: кол-во серий \ время тайтла
class AddTitleForm(QWidget):
    def __init__(self, parent):
        try:
            super(AddTitleForm, self).__init__(parent)
            loadUi('GUI/AddTitleForm.ui', self)
            self.parent = parent
            self.hide()

            self.anim = QPropertyAnimation(self, b"size")
            self.anim.setEasingCurve(QEasingCurve.OutExpo)
            self.anim.setDuration(AddFormDur)

            self.count.setValidator(QIntValidator(1, 9999))
            self.count.returnPressed.connect(self.ok.click)

            self.title_name.returnPressed.connect(self.ok.click)
            self.cancel.clicked.connect(self.switch_visible)
            self.ok.clicked.connect(self.submit)
        except Exception as e:
            print('Add_Title_Form:', e)

    # Show/hide add form
    def switch_visible(self):
        try:
            if self.isHidden():
                self.show()
                self.title_name.setFocus()
                self.title_name.selectAll()
                self.anim.setEndValue(QSize(370, 245))
                self.anim.start()
            else:
                self.anim.stop()
                self.anim.setEndValue(QSize(370, 0))
                self.anim.start()
                QTimer.singleShot(SideAnimDur, self.close)
        except Exception as e:
            print('switch_visible:', e)

    def submit(self):
        try:
            name = self.title_name.text()

            if not self.check_title(name):
                return

            self.switch_visible()
            count = self.count.text()
            genre = self.genre.text()
            link = self.link.text()
            desc = self.desc.toPlainText()

            if name == '':
                QMessageBox.warning(self, "PLS4", "Имя тайтла - обязательное поле!")
                self.title_name.setFocus()
                return
            elif count == '':
                message = "Количество серий - обязательное поле!"
                QMessageBox.warning(self, "PLS4", message)
                self.count.setFocus()
                return

            if self.is_con.checkState() == 2:
                color = 'is_con'
            else:
                color = 'n'
            if self.is_finished.checkState() == 2:
                icon = Icons['not_finished']
            else:
                icon = Icons['n']

            self.parent.add_title(name, count, genre, link, desc, icon, color)
            query = "SELECT id FROM Titles WHERE title_name='%s'" \
                    " and con_date!=''" % name
            check = list(sql(query))
            if len(check) > 0:
                message = "Данный тайтл находится в списке продолжений.\nУбрать его?"
                btns = QMessageBox.Yes | QMessageBox.No
                ask = QMessageBox.question(self, "PLS4", message, btns, QMessageBox.No)
                if ask == QMessageBox.Yes:
                    sql("UPDATE Titles SET con_date='' WHERE id=%s" % check[0][0])

        except Exception as e:
            show_exception("submit", e)

    def check_title(self, t_name):
        query = "SELECT id FROM Titles WHERE title_name='%s' " \
                "and playlist='%s'" % (t_name, self.parent.name)
        check = list(sql(query))
        if len(check) > 0:
            self.parent.select_row(check[0][0])
            message = "Похоже тайтл '%s' уже добавлен в данный плейлист." \
                      "\nХотите сделать дубликат?" % t_name
            btns = QMessageBox.Yes | QMessageBox.No
            ask = QMessageBox.question(self, "PLS4", message, btns, QMessageBox.No)
            if ask == QMessageBox.No:
                return False
        return True


class TabBar(QTabBar):
    def __init__(self, parent):
        super(TabBar, self).__init__(parent)
        self.setMovable(True)
        self.setTabsClosable(True)
        self.setExpanding(True)


class SideBar(QWidget):
    def __init__(self, parent):
        super(SideBar, self).__init__(parent)
        try:
            loadUi('GUI/SideBar.ui', self)
            self.p = parent
            self.change_check = True

            self.close_side.clicked.connect(self.switch_visible)

            self.genre.doubleClicked.connect(self.switch_edit)
            self.genre.setCursor(QCursor(Qt.PointingHandCursor))
            self.genre.returnPressed.connect(self.save_desc)

            self.desc.doubleClicked.connect(self.switch_edit)
            self.desc.setCursor(QCursor(Qt.PointingHandCursor))

            self.link.doubleClicked.connect(self.switch_edit)
            self.link.setCursor(QCursor(Qt.PointingHandCursor))
            self.link.returnPressed.connect(self.save_desc)

            self.open.clicked.connect(self.open_link)
            self.save.clicked.connect(self.save_desc)

            self.is_con.stateChanged.connect(self.set_is_con)
            self.is_finished.stateChanged.connect(self.set_is_finished)

            self.animSide = QPropertyAnimation(self, b"geometry")
            self.animSide.setEasingCurve(QEasingCurve.OutExpo)
            self.animSide.setDuration(SideAnimDur)
        except Exception as e:
            show_exception("SideBar__init", e)

    def save_desc(self):
        try:
            self.switch_edit(False)
            genre = self.genre.text()
            link = self.link.text()
            desc = self.desc.toPlainText()
            query = "update titles set genre='%s', link='%s', desc='%s' where id=%s" \
                    % (genre, link, desc, self.p.current_row.id)
            sql(query)
            db.commit()
        except sqlite3.Error as e:
            if str(e).split()[0] in ["unrecognized", "near"]:
                message = "Похоже, вы использовали недопустимый cимвол!"
                QMessageBox.warning(self, "PLS4: Warning", message)
            else:
                show_exception("save_desc", e)
                self.keyPressEvent('')
        except Exception as e:
            show_exception("save_desc", e)

    def set_is_finished(self, state):
        if self.change_check:
            if state == 2:
                self.p.current_row.set_icon(Icons['not_finished'])
            else:
                self.p.current_row.set_icon(Icons['n'])

    def set_is_con(self, state):
        if self.change_check:
            if state == 2:
                self.p.current_row.set_color('is_con')
            else:
                self.p.current_row.set_color('n')

    def open_link(self):
        if self.link.text() != '':
            webbrowser.open(self.link.text())

    # On doubleclick
    def switch_edit(self, edit=True):
        self.genre.setReadOnly(not edit)
        self.link.setReadOnly(not edit)
        self.desc.setReadOnly(not edit)
        self.save.setEnabled(edit)
        cursor = Qt.IBeamCursor if edit else Qt.PointingHandCursor
        self.genre.setCursor(QCursor(cursor))
        self.link.setCursor(QCursor(cursor))
        self.desc.setCursor(QCursor(cursor))

    # On esc at side bar
    def keyPressEvent(self, event):
        try:
            if event == '' or event.key() == Qt.Key_Escape:
                self.genre.undo()
                self.link.undo()
                self.desc.undo()
                self.switch_edit(False)
        except Exception as e:
            show_exception("sideBar_esc", e)

    # Load and set title-data into side bar
    def load_side_data(self, t_id):
        try:
            self.switch_edit(False)

            query = "SELECT genre, link, desc, date, count, icon, color FROM Titles"
            data = list(sql(query + " WHERE id=%s" % t_id))[0]
            self.genre.setText(data[0])
            self.link.setText(data[1])
            self.desc.setText(data[2])
            self.title_date.setText(data[3])
            self.title_time.setText(self.count_title_time(data[4]))

            icon_state = 2 if data[5] == Icons['not_finished'] else 0
            color_state = 2 if data[6] == 'is_con' else 0
            self.change_check = False
            self.is_con.setCheckState(color_state)
            self.is_con.setEnabled(data[5] in [Icons['n'], Icons['not_finished']])
            self.is_finished.setCheckState(icon_state)
            self.is_finished.setEnabled(data[5] in [Icons['n'], Icons['not_finished']])
            self.change_check = True
        except Exception as e:
            show_exception("load_side_data", e)

    @staticmethod
    def count_title_time(count, episode=EpisodeTime):
        try:
            count *= episode
            time = "%s%s" % (count // 60, 'ч') if count >= 60 else ""
            time += "%s%s" % (count % 60, 'м') if count % 60 else ""
            return time
        except Exception as e:
            show_exception("count_title_time", e)

    # Switch hide/show side bar
    def switch_visible(self):
        try:
            if self.p.side_hidden:
                self.animSide.setEndValue(QRect(self.p.w - SideWidth, 0,
                                                SideWidth, self.p.h))
                self.p.side_hidden = False
                self.close_side.setText('>')
            else:
                self.animSide.setEndValue(QRect(self.p.w - 20, 0, SideWidth, self.p.h))
                self.p.side_hidden = True
                self.close_side.setText('<')
            self.animSide.start()
        except Exception as e:
            show_exception("hide_show_sidebar", e)


class RowButtons(QWidget):
    def __init__(self, con=False):
        super(RowButtons, self).__init__()
        try:
            loadUi("GUI/RowButtons.ui", self)
            self.p = None

            self.del_title.clicked.connect(self.delete_title)
            self.viewing.clicked.connect(self.viewing_now)
            self.viewed.clicked.connect(self.select_mark)
            self.find_btn.clicked.connect(self.find_title)
            self.move_btn.clicked.connect(self.move_title)

            self.plus.clicked.connect(self.change_episode)
            self.episode_edit.setValidator(QIntValidator(1, 9999))
            self.minus.clicked.connect(self.change_episode)
            self.plus.hide()
            self.minus.hide()
            self.episode_edit.hide()
            if con:
                self.left_frame.hide()
                self.move_btn.hide()
            else:
                self.find_btn.hide()
                self.date = QLineEdit(self)
                self.date.setAlignment(Qt.AlignCenter)
                self.date.setGeometry(122, 0, 151, 30)
                reg_exp = QRegExp(r"\d{4}(\.(\d{1,2})(\.(\d{1,2}))?)?")
                validator = QRegExpValidator(reg_exp, self.date)
                self.date.setValidator(validator)
                self.date.setStyleSheet(
                    'QLineEdit{font-size:16px;font-weight:bold;background:#D9D9D9}')
                self.date.hide()
                self.date.focusOutEvent = lambda x: self.date.hide()
                self.date.returnPressed.connect(self.set_con_date)

                self.change_timer = QTimer(self)
                self.change_timer.timeout.connect(lambda: self.change_episode(True))
                self.change_timer.setSingleShot(True)
                self.change_timer.setInterval(EditEnterDur)
                self.episode_edit.textEdited.connect(self.change_timer.start)
        except Exception as e:
            show_exception("RowButtons__init", e)

    def setParent(self, parent, **kwargs):
        super(RowButtons, self).setParent(parent)
        if parent is not None:
            self.p = parent

            text = 'НЕ СМОТРЮ' if parent.icon == Icons['viewing'] else 'СМОТРЮ'
            self.viewing.setText(text)
            state = parent.icon in [Icons['viewing'], Icons['pause'], Icons['n']]
            self.viewing.setEnabled(state)
            if parent.icon in [Icons['viewing'], Icons['pause']]:
                self.switch_episode_edit(True)
        elif not self.plus.isHidden():
            self.switch_episode_edit(False)

    def switch_episode_edit(self, show):
        if show:
            self.plus.show()
            self.minus.show()
            self.episode_edit.show()
            self.episode_edit.setText(str(self.p.ep))
        else:
            self.plus.hide()
            self.minus.hide()
            self.episode_edit.hide()

    def change_episode(self, save):
        try:
            if not save:
                self.change_timer.start()
                if self.sender().text() == '+':
                    value = int(self.episode_edit.text()) + 1
                else:
                    value = int(self.episode_edit.text()) - 1
                if 1 <= value <= 9999:
                    self.episode_edit.setText(str(value))
            else:
                value = self.episode_edit.text()
                if value != '' and int(value) >= 1:
                    sql("UPDATE Titles SET episode=%s WHERE id=%s" % (value, self.p.id))
                    self.p.ep = value
        except Exception as e:
            show_exception("change_episode", e)

    def viewing_now(self):
        try:
            self.p.leave(False)
            if self.p.icon == Icons['viewing']:
                self.p.set_color('n')
                self.p.set_icon(Icons['n'])
                self.viewing.setText('СМОТРЮ')
                self.p.p.side_bar.load_side_data(self.p.id)
                self.switch_episode_edit(False)
            else:
                self.p.set_color('viewing')
                self.p.set_icon(Icons['viewing'])
                self.viewing.setText('НЕ СМОТРЮ')
                self.p.p.side_bar.load_side_data(self.p.id)
                self.switch_episode_edit(True)
        except Exception as e:
            show_exception("viewing_now", e)

    def delete_title(self):
        self.p.delete_title()

    def set_con_date(self):
        try:
            if self.p.color not in ['is_con', 'viewed']:
                save_data('viewed')
            self.p.set_icon(Icons['con'])
            self.p.set_color('viewed')
            self.date.hide()

            self.viewing.setText('СМОТРЮ')
            self.viewing.setEnabled(False)
            self.switch_episode_edit(False)

            text = self.date.text()
            sql('update titles set con_date="%s" where id=%s' % (text, self.p.id))

            if ConTabName in MainP.tab_map:
                tab = MainP.tabWidget.widget(MainP.tab_map.index(ConTabName))
                name = self.p.title_name.text()
                count = self.p.count.text()
                id_ = self.p.id
                date = self.date.text()
                tab.add_row(name, count, id_, date, 'n', 0, -1)
        except Exception as e:
            show_exception("set_con_date", e)

    def select_mark(self):
        try:
            menu = QMenu(self)

            ico = QIcon(RowIcons[Icons['viewed']])
            on_viewed = menu.addAction(ico, 'Просмотрен')
            on_viewed.setEnabled(self.p.icon != Icons['viewed'])

            ico = QIcon(RowIcons[Icons['con']])
            on_con = menu.addAction(ico, 'Будет продолжение')
            on_con.setEnabled(self.p.icon != Icons['con'])

            on_pause = False
            if self.p.icon not in [Icons['viewed'], Icons['con'], Icons['pause']]:
                ico = QIcon(RowIcons[Icons['pause']])
                on_pause = menu.addAction(ico, 'Просмотр брошен')

            on_cancel = False
            if self.p.icon not in [Icons['n'], Icons['viewing'], Icons['not_finished']]:
                ico = QIcon(Icons['cancel_mark'])
                on_cancel = menu.addAction(ico, 'Отменить метку')

            cursor = QPoint(self.viewed.x(), -35)
            selected = menu.exec_(self.mapToGlobal(cursor))

            if selected == on_viewed:
                if self.p.color not in ['is_con', 'viewed']:
                    save_data('viewed')
                if self.p.icon == Icons['con']:
                    query = "update Titles set con_date='' WHERE id=%s" % self.p.id
                    sql(query)
                self.p.set_color('viewed')
                self.p.set_icon(Icons['viewed'])
            elif selected == on_con:
                self.date.show()
                self.date.setText(datetime.today().strftime('%Y'))
                self.date.setFocus()
                self.date.selectAll()
            elif selected == on_pause:
                self.p.set_color('pause')
                self.p.set_icon(Icons['pause'])
            elif selected == on_cancel:
                if self.p.icon == Icons['con']:
                    query = "update Titles set con_date='' WHERE id=%s" % self.p.id
                    sql(query)
                if self.p.color == 'viewed':
                    save_data('viewed', -1)
                self.p.set_color('n')
                self.p.set_icon(Icons['n'])
            if selected not in [None, on_con]:
                self.viewing.setText('СМОТРЮ')
                self.viewing.setEnabled(selected in [on_pause, on_cancel])
                self.switch_episode_edit(selected is on_pause)

            self.p.p.side_bar.load_side_data(self.p.id)
        except Exception as e:
            show_exception("select_mark", e)

    def find_title(self):
        try:
            pl_name = list(sql("SELECT playlist FROM Titles WHERE id=%s" % self.p.id))
            MainP.find_select_title(pl_name[0][0], self.p.id)
        except Exception as e:
            show_exception("find_title", e)

    def move_title(self):
        try:
            self.p.p.paste_btn.show()
            MainP.paste_row = [self.p.name, self.p.count.text(), self.p.id, self.p.icon,
                               self.p.color, self.p.p.name, self.p.ep]
            self.p.min_height = 0
            self.p.animOff.start(1)
        except Exception as e:
            show_exception("move_title", e)


class Title(QWidget):
    def __init__(self, parent, name, count, id_, icon, color, episode):
        try:
            super(Title, self).__init__(parent)
            loadUi('GUI/Title.ui', self)
            self.id = id_
            self.p = parent
            self.icon = icon
            self.name = name
            self.ep = episode
            self.color = color
            self.border_color = "blue"
            self.hover_color = "#6ebcd2"
            self.show_side = False

            self.row_layout.setAlignment(Qt.AlignTop)

            self.title_name.setText(name)
            self.title_name.clicked.connect(self.select)
            self.title_name.doubleClicked.connect(self.set_line_edit)
            self.title_name.returnPressed.connect(self.end_line_edit)
            self.title_name.setCursor(QCursor(Qt.PointingHandCursor))

            self.count.setCursor(QCursor(Qt.PointingHandCursor))
            self.count.setValidator(QIntValidator(1, 9999))
            self.count.setText(str(count))
            self.count.returnPressed.connect(self.end_line_edit)
            self.count.clicked.connect(self.select)
            self.count.doubleClicked.connect(self.set_line_edit)

            self.con_date.clicked.connect(self.select)
            self.con_date.doubleClicked.connect(self.set_line_edit)
            self.con_date.returnPressed.connect(self.end_line_edit)
            reg_exp = QRegExp(r"\d{4}(\.(\d{1,2})(\.(\d{1,2}))?)?")
            validator = QRegExpValidator(reg_exp, self.con_date)
            self.con_date.setValidator(validator)
            self.con_date.setCursor(QCursor(Qt.PointingHandCursor))

            self.set_color(self.color, True)
            if parent.con:
                self.status.hide()
                self.con_date.setText(icon)
            else:
                self.con_date.hide()
                self.set_icon(icon)

            self.min_height = RowHeightMin
            self.animOn = QTimer(self)
            self.animOn.timeout.connect(self.anim_down)
            self.animOff = QTimer(self)
            self.animOff.timeout.connect(self.anim_up)
        except Exception as e:
            show_exception("Title__init", e)

    def delete_title(self):
        try:
            if not self.p.con:
                title = "PLS4: Delete title"
                ask = "Вы уверены, что хотите удалить '%s' из данного плейлиста?" \
                      % self.name
                btns = QMessageBox.Yes | QMessageBox.No
                req = QMessageBox.question(self, title, ask, btns, QMessageBox.No)
            else:
                req = QMessageBox.Yes

            if req == QMessageBox.Yes:
                if self.p.con:
                    # Delete title from con list
                    query = "update Titles set con_date='',icon=%s" % Icons['viewed']
                    sql(query + " WHERE id=%s" % self.id)
                    pl = list(sql("SELECT playlist FROM Titles WHERE id=%s" % self.id))
                    if pl[0][0] in MainP.tab_map:
                        index = MainP.tab_map.index(pl[0][0])
                        MainP.close_tab(index)
                        MainP.add_tab(pl[0][0], index)
                else:
                    sql('DELETE FROM Titles WHERE id=%s' % self.id)

                self.min_height = 0
                self.animOff.start(1)

                if not self.p.side_hidden:
                    self.p.side_bar.switch_visible()
                    self.p.just_opened = True

                if self.color == 'viewed':
                    save_data('viewed', -1)
                save_data('added', -1)
        except Exception as e:
            show_exception("delete_title", e)

    def set_icon(self, ico):
        try:
            icon = QPixmap(RowIcons[ico]).scaled(IconSize, IconSize)
            self.status.setPixmap(icon)
            if ico != self.icon:
                self.icon = ico
                sql('UPDATE Titles SET icon="%s" WHERE id=%s' % (ico, self.id))
        except Exception as e:
            show_exception("set_icon", e)

    def set_color(self, color, load=False):
        try:
            if self.color != 'is_con' or color in ('is_con', 'edit') or (
                    self.color == 'is_con' and color == 'n' and
                    self.icon in [Icons['n'], Icons['not_finished']]):
                if load:
                    self.setStyleSheet('''
                    #title_name,#count,#con_date{background: %s}''' % Color[color])
                else:
                    self.setStyleSheet('''
                        #title_name,#count,#con_date{background: %s}
                        #t_row{border-color: %s}
                        ''' % (Color[color], self.border_color))

                if color not in ['edit', self.color]:
                    self.color = color
                    sql('UPDATE Titles SET color="%s" WHERE id=%s' % (color, self.id))
        except Exception as e:
            show_exception("set_color", e)

    # ON click row
    def select(self):
        try:
            if self.p.current_row not in [self, None]:
                self.p.current_row.leave()
            if self.p.current_row is not self:
                self.setStyleSheet('''
                    #t_row{border-color: %s}
                    #title_name,#count,#con_date{background: %s}
                    ''' % (self.border_color, Color[self.color]))
                self.p.current_row = self
                self.p.side_bar.close_side.setEnabled(True)
                self.p.side_bar.load_side_data(self.id)
                self.animOn.start(RowAnimDur)

                self.p.row_btns.setParent(self)
                self.p.scroll_to(self.p.row_map.index(self.id))

                if self.p.just_opened:
                    self.p.side_bar.switch_visible()
                    self.p.just_opened = False

                if self.icon == 'viewing':
                    self.p.row_btns.viewing.setText('НЕ СМОТРЮ')
                if self.icon in ['viewed', 'con']:
                    self.p.row_btns.viewing.setEnabled(False)
        except Exception as e:
            show_exception("select", e)

    # ON doubleclick row
    def set_line_edit(self):
        try:
            self.switch_edit()
            self.set_color('edit')
            if self.p.con:
                self.con_date.setText(self.con_date.text().rstrip("!"))

            if not self.p.side_hidden:
                self.p.side_bar.switch_visible()
                self.show_side = True
        except Exception as e:
            show_exception("on_line_edit", e)

    # ON enter pressed
    def end_line_edit(self):
        try:
            name = self.title_name.text()
            count = self.count.text()

            if name:
                self.title_name.clearFocus()
                self.count.clearFocus()
                query = "UPDATE Titles SET title_name='%s', count=%s" % (name, count)
                if self.p.con:
                    self.color = 'n'
                    query += ", con_date'%s'" % self.con_date.text()
                sql(query + " WHERE id='%s'" % self.id)

                self.p.side_bar.load_side_data(self.id)
                self.leave(False)
            else:
                QMessageBox.warning(self, "PLS4", "Имя тайтла не может быть пустым!")
        except Exception as e:
            show_exception("on_line_edited", e)

    def switch_edit(self, edit=True):
        self.title_name.setReadOnly(not edit)
        self.count.setReadOnly(not edit)
        self.con_date.setReadOnly(not edit)
        cursor = Qt.IBeamCursor if edit else Qt.PointingHandCursor
        self.title_name.setCursor(QCursor(cursor))
        self.count.setCursor(QCursor(cursor))
        self.con_date.setCursor(QCursor(cursor))

    # ON edit ecs
    def keyPressEvent(self, event=None, esc=False):
        try:
            if esc or event.key() == Qt.Key_Escape:
                self.title_name.clearFocus()
                self.title_name.undo()
                self.count.clearFocus()
                self.count.undo()
                self.con_date.undo()
                self.leave(False)
                # On esc set date of con
                if not self.p.con:
                    self.p.row_btns.date.hide()
                elif self.color == "is_con" and self.con_date.text()[-1] != '!':
                    self.con_date.setText(self.con_date.text() + '!')

        except Exception as e:
            show_exception("row_edit_esc", e)

    # Anim row down
    def anim_down(self):
        try:
            if self.height() < RowHeightMax:
                self.setFixedHeight(self.height() + 1)
            else:
                self.animOn.stop()
                self.row_layout.addWidget(self.p.row_btns)
        except Exception as e:
            show_exception("anim_down", e)

    # Anim row up
    def anim_up(self):
        if self.height() > self.min_height:
            self.setFixedHeight(self.height() - 1)
        else:
            self.finish_anim_up()

    def finish_anim_up(self):
        try:
            self.animOff.stop()
            if self.min_height == 0:
                self.p.current_row = None
                self.setParent(None)
                row_count = self.p.row_list.count()
                self.p.row_count.setText('Тайтлов в плейлисте:' + str(row_count))
                if not row_count and self.p.con:
                    MainP.close_tab(MainP.tab_map.index(ConTabName))
        except Exception as e:
            show_exception("finish_anim_up", e)

    def leave(self, change=True):
        try:
            self.animOff.stop()
            self.animOn.stop()
            if change:
                self.p.row_btns.setParent(None)
                self.keyPressEvent(esc=True)
                self.animOff.start(RowAnimDur)
                self.setStyleSheet('''
                    #t_row{border-color: #F0F0F0}
                    QLineEdit{background: %s}
                    #t_row:hover{border-color: %s;}'''
                                   % (Color[self.color], self.hover_color))
            else:
                self.set_color(self.color)
                if self.show_side:
                    self.p.side_bar.switch_visible()
                    self.show_side = False

            self.switch_edit(False)
        except Exception as e:
            show_exception("leave", e)


# todo: снять метку со всех...
class Playlist(QWidget):
    def __init__(self, parent, name, new):
        super(Playlist, self).__init__(parent)
        try:
            loadUi('GUI/Playlist.ui', self)
            self.p = parent
            self.name = name
            self.current_row = None
            self.row_map = list()
            self.con = name == ConTabName
            self.row_btns = RowButtons(self.con)

            self.row_list.setAlignment(Qt.AlignTop)

            self.add_form = AddTitleForm(self)
            self.add_form.setGeometry(9, 49, 370, 0)

            self.add_title_btn.clicked.connect(self.add_form.switch_visible)
            self.del_pl.clicked.connect(self.delete_playlist)

            self.side_bar = SideBar(self)
            self.side_hidden = True

            self.search.clicked.connect(self.open_search)
            self.search_edit.resize(0, 25)
            self.search_edit.hide()
            self.search_edit.focusOutEvent = lambda _: self.open_search(True)
            self.search_edit.returnPressed.connect(self.open_search)

            self.search_timer = QTimer(self)
            self.search_timer.timeout.connect(self.do_search)
            self.search_timer.setSingleShot(True)
            self.search_timer.setInterval(EditEnterDur)
            self.search_edit.textEdited.connect(self.search_timer.start)

            self.search_anim = QPropertyAnimation(self.search_edit, b"size")
            self.search_anim.setEasingCurve(QEasingCurve.OutExpo)
            self.search_anim.setDuration(AddPlDur)

            self.rename.clicked.connect(self.rename_playlist)
            self.paste_btn.hide()
            self.paste_btn.clicked.connect(self.paste_title)

            if self.con:
                self.add_title_btn.hide()
                self.del_pl.hide()
                self.rename.hide()
            else:
                self.search.hide()

            if new:
                QTimer.singleShot(500, self.add_form.switch_visible)
            else:
                QTimer.singleShot(1, self.load_titles)
            self.just_opened = True
        except Exception as e:
            show_exception("NewPlaylist__init", e)

    def rename_playlist(self):
        font = QFont()
        font.setPointSize(12)
        font.setFamily('Comic Sans MS')
        font.setWeight(400)

        dialog = QInputDialog(None)
        dialog.setInputMode(QInputDialog.TextInput)
        dialog.setWindowTitle('PLS4: Rename playlist')
        dialog.setLabelText('Введите новое имя плейлиста')
        dialog.setFont(font)

        try:
            ok = dialog.exec_()
            name = dialog.textValue()
            if ok and MainP.check_playlist(name):
                names = name, self.name
                sql("UPDATE Playlists SET name='%s' WHERE name='%s'" % names)
                sql("UPDATE Titles SET playlist='%s' WHERE playlist='%s'" % names)

                index = MainP.tab_map.index(self.name)
                MainP.tabWidget.setTabText(index, name)
                MainP.tab_map[index] = name
                self.name = name
                index = MainP.pl_list.currentIndex()
                MainP.pl_list.removeItem(index)
                MainP.pl_list.insertItem(index, name)
                MainP.pl_list.setCurrentIndex(index)
            elif ok:
                self.rename_playlist()
        except Exception as e:
            show_exception("rename_pl", e)

    def paste_title(self):
        try:
            if self.p.paste_row[-1] == self.name \
                    or self.add_form.check_title(self.p.paste_row[0]):
                query = "UPDATE Titles SET playlist='%s' " \
                        "WHERE id='%s'" % (self.name, self.p.paste_row[2])
                sql(query)
                del self.p.paste_row[-1]
                index = self.get_rowid(self.p.paste_row[2])
                self.add_row(*self.p.paste_row, index).select()
                self.p.paste_row = None
                self.paste_btn.hide()
        except Exception as e:
            show_exception("paste_title", e)

    def open_search(self, defocused=False):
        try:
            hidden = self.search_edit.isHidden()
            if hidden and not defocused:
                self.search_edit.show()
                self.search_anim.setEndValue(QSize(182, 25))
            else:
                self.search_anim.setEndValue(QSize(0, 25))

            self.search_anim.start()
            loop = QEventLoop()
            QTimer.singleShot(AddPlDur, loop.quit)
            loop.exec_()
            if hidden:
                self.search_edit.setFocus()
                self.search_edit.selectAll()
            else:
                self.search_edit.hide()
        except Exception as e:
            show_exception("do_search", e)

    def do_search(self):
        text = self.search_edit.text().lower()
        if text != '':
            for i in range(self.row_list.count()):
                row = self.row_list.itemAt(i).widget()
                if text in row.name.lower():
                    row.select()
                    break

    def select_row(self, index):
        try:
            row = self.row_list.itemAt(self.row_map.index(index)).widget()
            row.select()
        except Exception as e:
            show_exception("select_row", e)

    # Move scroll bar
    def scroll_to(self, index: int):
        try:
            bar = self.scrollArea.verticalScrollBar()
            step = bar.pageStep()
            row_size = RowHeightMin + self.row_list.spacing()
            target_pos = row_size * index + self.row_list.spacing()
            bottom_border = bar.value() + step - RowHeightMax
            anim_step = abs(target_pos - bar.value()) * 0.09

            def scroll(anim_step):
                anim_step = 1 if anim_step == 0 else anim_step
                loop = QEventLoop()
                QTimer.singleShot(40, loop.quit)
                loop.exec_()
                bar.setValue(bar.value() + anim_step)

            if target_pos < bar.value():
                while bar.value() > target_pos:
                    scroll(-anim_step)
            elif target_pos > bottom_border:
                while bar.value() < target_pos and bar.value() < bar.maximum():
                    scroll(anim_step)
        except Exception as e:
            show_exception('scroll_to', e)

    def resizeEvent(self, event=None):
        try:
            self.w = self.width()
            self.h = self.height()
            if self.side_hidden:
                self.side_bar.setGeometry(self.w - 20, 0, SideWidth, self.h)
            else:
                self.side_bar.setGeometry(self.w - SideWidth, 0, SideWidth, self.h)
        except Exception as e:
            show_exception('NewPlaylist_resizeEvent', e)

    def delete_playlist(self):
        try:
            title = "PLS4: Delete playlist"
            ask = "Вы действительно хотите удалить весь плейлист '%s' ?" % self.name
            btns = QMessageBox.Yes | QMessageBox.No
            response = QMessageBox.warning(self, title, ask, btns, QMessageBox.No)
            if response == QMessageBox.Yes:
                sql("DELETE FROM Playlists WHERE Name=?", [self.name])
                sql('DELETE FROM Titles WHERE playlist="%s"' % self.name)

                for i in range(self.row_list.count()):
                    if self.row_list.itemAt(i).widget().color == 'viewed':
                        save_data('viewed', -1)

                self.p.pl_list.removeItem(self.p.pl_list.currentIndex())
                self.p.close_tab(self.p.tab_map.index(self.name))
                if not self.p.tab_map:
                    self.p.select_playlist()
        except Exception as e:
            show_exception('delete_playlist', e)

    def add_title(self, t_name, count, genre, link, desc, icon, color):
        try:
            query = "INSERT INTO Titles VALUES "
            date = datetime.today().strftime("%d.%m.%Y")

            sql(query + "('%s',%s,%s,'%s','%s','%s','%s','%s','%s','', '%s', 0, 0)"
                % (t_name, count, ID, self.name, icon, color, genre, link, desc, date))

            row_id = self.get_rowid(ID)
            self.add_row(t_name, count, ID, icon, color, 0, row_id).select()
            self.row_count.setText('Тайтлов в плейлисте:' + str(self.row_list.count()))
            save_data('id')
            save_data('added')
        except Exception as e:
            show_exception('add_title', e)

    def get_rowid(self, t_id):
        query = "SELECT id,count,icon FROM Titles WHERE playlist = '%s'" % self.name
        row_id = list(sql(query + " ORDER BY count desc,icon desc,id desc"))
        for i, item in enumerate(row_id):
            if item[0] == t_id:
                row_id = i
                break
        return row_id

    def add_row(self, name, count, t_id, icon_date, color, ep, index, delay=0):
        try:
            row = Title(self, name, count, t_id, icon_date, color, ep)
            index = self.row_list.count() if index == -1 else index
            loop = QEventLoop()
            QTimer.singleShot(delay, loop.quit)
            loop.exec_()
            self.row_list.insertWidget(index, row)
            self.row_map.insert(index, t_id)
            return row
        except Exception as e:
            show_exception('add_row', e)

    # todo: разбить по методам
    def load_titles(self):
        try:
            index = 0

            if self.con:
                query = "select title_name,count,id,con_date"
                titles = list(sql(query + " from titles WHERE con_date!=''"))
                delay = AddRowDur // len(titles)
                for t in titles:
                    color = 'is_con' if t[3][-1] == '!' else 'n'
                    self.add_row(t[0], t[1], t[2], t[3], color, 0, index, delay)
                    index += 1

            else:
                query = "SELECT title_name,count,id,icon,color, episode FROM Titles" \
                        " WHERE playlist='%s' ORDER BY " % self.name
                titles = list(sql(query + "count desc, icon desc, id desc"))
                if not len(titles):
                    return
                delay = AddRowDur // len(titles)
                for t in titles:
                    self.add_row(t[0], t[1], t[2], t[3], t[4], t[5], index, delay)
                    index += 1

                if self.p.set_viewing >= 0:
                    self.select_row(self.p.set_viewing)
                    self.p.set_viewing = -1

            self.row_count.setText('Тайтлов в плейлисте:' + str(self.row_list.count()))
        except Exception as e:
            show_exception('load_titles', e)


# todo: save pos
class MainForm(QMainWindow):

    def __init__(self):
        super(MainForm, self).__init__()
        loadUi('GUI/MainForm.ui', self)

        global MainP
        MainP = self
        self.setStyleSheet(Skin)
        self.selected_tab = ""
        self.tab_map = []

        self.add_pl.clicked.connect(self.switch_add_playlist)
        self.pl_list.activated.connect(self.select_playlist)

        self.pl_name.returnPressed.connect(self.add_pl.click)
        self.pl_name.hide()
        self.close_pl_name.clicked.connect(self.keyPressEvent)
        self.close_pl_name.hide()

        self.tabBar = TabBar(self)
        self.tabBar.currentChanged.connect(self.select_tab)
        self.tabBar.tabCloseRequested.connect(self.close_tab)
        self.tabBar.tabMoved.connect(self.move_tab)
        self.tabWidget.setTabBar(self.tabBar)

        self.options.clicked.connect(self.open_options)
        self.con_info.clicked.connect(self.open_con_list)
        self.con_info.hide()

        self.paste_row = None
        self.search_form = SearchTitleForm()

        self.add_pl_anim = QPropertyAnimation(self.pl_name, b"geometry")
        self.add_pl_anim.setEasingCurve(QEasingCurve.OutExpo)
        self.add_pl_anim.setDuration(AddPlDur)

        QTimer.singleShot(1, self.launch)
        self.launching = True
        self.set_viewing = -1

    # todo: settings
    def open_options(self):
        try:
            menu = QMenu(self)
            cons = list(sql("SELECT con_date, id FROM Titles WHERE con_date != ''"))

            ico = QIcon(RowIcons[Icons['con']])
            con_list = menu.addAction(ico, 'Список продолжений')
            con_list.setEnabled(bool(cons))

            ico = QIcon(Icons['search_title'])
            search_title = menu.addAction(ico, 'Найти тайтл')

            cursor = QPoint(self.options.x() + 5, self.options.y() + 10)
            selected = menu.exec_(self.mapToGlobal(cursor))

            if selected == con_list:
                self.open_con_list()
            if selected == search_title:
                self.search_form.show()
                self.search_form.search_edit.setFocus()
                self.search_form.search_edit.selectAll()

        except Exception as e:
            show_exception('open_options', e)

    def open_con_list(self):
        self.add_tab(ConTabName)

    # Show/hide add playlist
    def switch_add_playlist(self):
        try:
            if self.pl_name.isHidden():
                self.pl_name.setText("PL" + str(self.pl_list.count() + 1))
                self.anim_add_pl(True)
            else:
                name = self.pl_name.text()
                if self.check_playlist(name):
                    sql("INSERT INTO Playlists VALUES ('%s')" % name)
                    self.pl_list.insertItem(0, name)
                    self.add_tab(name, new=True)
                    self.pl_list.setCurrentIndex(0)
                    self.anim_add_pl(False)
                else:
                    self.pl_name.selectAll()
        except Exception as e:
            show_exception('add_playlist', e)

    def check_playlist(self, name):
        check = list(sql("SELECT * FROM Playlists WHERE name='%s'" % name))
        if check or name == ConTabName or name == '':
            message = "Плейлист с таким именем уже существует " \
                      "или является недопустимым"
            QMessageBox.information(self, "PLS4", message)
            return False
        return True

    def anim_add_pl(self, open):
        if open:
            self.pl_name.show()
            self.add_pl_anim.setStartValue(QRect(34 + 255, 11, 0, 30))
            self.add_pl_anim.setEndValue(QRect(34, 11, 255, 30))
        else:
            self.close_pl_name.hide()
            self.add_pl_anim.setStartValue(QRect(34, 11, 255, 30))
            self.add_pl_anim.setEndValue(QRect(34 + 255, 11, 0, 30))
            self.viewed_count.show()

        self.add_pl_anim.start()
        loop = QEventLoop()
        QTimer.singleShot(AddPlDur - 200, loop.quit)
        loop.exec_()
        if open:
            self.close_pl_name.show()
            self.viewed_count.hide()
            self.pl_name.setFocus()
            self.pl_name.selectAll()
        else:
            self.pl_name.hide()

    def select_playlist(self):
        if self.selected_tab != self.pl_list.currentText():
            self.selected_tab = self.pl_list.currentText()
            self.add_tab(self.selected_tab)

    def add_tab(self, tab_name, refresh=0, new=False):
        try:
            if tab_name in self.tab_map:
                self.tabWidget.setCurrentIndex(self.tab_map.index(tab_name))
            else:
                self.tab_map.insert(refresh, tab_name)
                new_tab = Playlist(self, tab_name, new)
                self.tabWidget.insertTab(refresh, new_tab, tab_name)
                if not refresh:
                    self.tabWidget.setCurrentIndex(0)
                if self.paste_row is not None and tab_name != ConTabName:
                    new_tab.paste_btn.show()
        except Exception as e:
            show_exception('add_tab', e)

    def select_tab(self, index):
        try:
            if index >= 0 and not self.launching:
                # show/hide paste_btn
                tab = self.tabWidget.widget(index)
                if self.paste_row is not None and tab.name != ConTabName:
                    tab.paste_btn.show()
                elif not tab.paste_btn.isHidden():
                    tab.paste_btn.hide()

                text = self.tabWidget.tabText(index)
                index = self.pl_list.findText(text)
                self.pl_list.setCurrentIndex(index)
                self.selected_tab = text

                if index != -1:
                    sql("UPDATE Data SET value='%s' WHERE name='cur_pl'" % index)
            elif not self.launching:
                self.selected_tab = ""
        except Exception as e:
            show_exception('select_tab', e)

    def move_tab(self, index):
        tab = self.tabWidget.tabText(index)
        self.tab_map.remove(tab)
        self.tab_map.insert(index, tab)

    def close_tab(self, index):
        try:
            self.tab_map.remove(self.tabWidget.tabText(index))
            self.tabWidget.removeTab(index)
        except Exception as e:
            show_exception('close_tab', e)

    # pl name esc
    def keyPressEvent(self, event):
        try:
            if not event or (event.key() == Qt.Key_Escape and self.pl_name.isVisible()):
                self.anim_add_pl(False)
        except Exception as e:
            show_exception('MainForm_on_esc', e)

    def find_select_title(self, pl_name, index):
        try:
            self.pl_list.setCurrentIndex(self.pl_list.findText(pl_name))
            exists = pl_name in self.tab_map
            if not exists:
                self.set_viewing = index
            self.select_playlist()
            if exists:
                tab = self.tabWidget.currentWidget()
                tab.select_row(index)

        except Exception as e:
            show_exception("find_select_title", e)

    # todo: открывать все смотрю сейчас
    def select_last_playlist(self):
        try:
            pl = list(sql("SELECT value FROM Data WHERE name='cur_pl'"))[0][0]
            query = "SELECT id, playlist FROM Titles WHERE "
            title_id = list(sql(query + "icon='%s'" % Icons['viewing']))
            if title_id:
                self.find_select_title(title_id[-1][1], title_id[-1][0])
            elif pl != '-1':
                self.pl_list.setCurrentIndex(int(pl))
                self.select_playlist()
        except Exception as e:
            show_exception('select_last_playlist', e)

    # todo: set_con_info
    def set_con_info(self):
        pass

    def check_continuations(self):
        try:
            cons = list(sql("SELECT con_date, id FROM Titles WHERE con_date != ''"))
            today = datetime.today()
            count = 0
            pattern = ('%Y', '%m', '%d')

            for title in cons:
                if title[0][-1] == '!':
                    self.con_info.show()
                    continue
                date = title[0].split('.')
                date = [str(today.year)] if date[0] == '0' else date

                if len(date) == 1:
                    date.append('12')
                    date.append('31')
                date = datetime.strptime('.'.join(date), '.'.join(pattern[:len(date)]))
                if today > date:
                    count += 1
                    query = "UPDATE Titles SET "
                    sql(query + "con_date'%s' WHERE id=%s" % (title[0] + '!', title[1]))

            if count > 0:
                text = 'Количество тайтлов получивших продолжение: '
                text += '%s\nОткрыть список продолжений?' % count
                buttons = QMessageBox.Yes | QMessageBox.No

                act = QMessageBox.question(self, 'PLS4', text, buttons)
                if act == QMessageBox.Yes:
                    self.open_con_list()
                else:
                    self.con_info.show()
        except Exception as e:
            show_exception('check_continuations', e)

    def closeEvent(self, event):
        try:
            db.commit()
            self.search_form.close()
            event.accept()
        except Exception as e:
            show_exception("closeEvent", e)

    def launch(self):
        try:
            playlists = list(sql("SELECT * FROM Playlists ORDER BY rowid desc"))
            self.pl_list.addItems([row[0] for row in playlists])

            self.select_last_playlist()

            self.viewed_count.setText('Всего просмотрено:' + str(TotalViewed))
            QTimer.singleShot(1000, self.check_continuations)
            print("Launched")
            self.launching = False
        except Exception as e:
            show_exception('launch', e)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle(SelfStyledIcon('Fusion'))
    exe = MainForm()
    exe.show()
    sys.exit(app.exec_())
