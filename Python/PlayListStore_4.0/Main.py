# -*- coding: utf-8 -*-
import sqlite3
import sys
from datetime import datetime

from PyQt5.QtCore import (QEventLoop, QTimer, Qt, QPoint,
                          QPropertyAnimation, QEasingCurve, QSize, QRect, QRegExp)
from PyQt5.QtGui import QIntValidator, QCursor, QIcon, QPixmap, QRegExpValidator, QFont
from PyQt5.QtWidgets import (QMessageBox, QProxyStyle, QWidget, QHBoxLayout, QPushButton,
                             QMenu, QTabBar, QMainWindow, QApplication, QLineEdit, QStyle, QInputDialog)
from PyQt5.uic import loadUi

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
Icon = [
    'Icons/viewed.png',
    'Icons/continuation.ico',
    'Icons/pause.ico',
    'Icons/viewing.ico',
    '',
    'Icons/not_finished.ico']
Icons = {
    'n': 4,
    'viewed': 0,
    'not_finished': 5,
    'con': 1,
    'viewing': 3,
    'pause': 2}
Color = {
    'n': '#D9D9D9',
    'edit': 'none',
    'viewed': '#AEDD17',
    'viewing': '#6EBCD2',
    'pause': '#DC143C',
    'is_con': '#FEE02F'}
# Skin = 'Skins/dark_orange.css'
Skin = 'style.css'
SideWidth = 300
SideAnimDur = 500
AddFormDur = 500  # Add title form anim
RowAnimDur = 6
RowLoadDur = 20
AddRowDur = 550
AddPlDur = 500
ConSearchDur = 600
RowHeightMin = 34
RowHeightMax = 72

MainP = None
EpisodeTime = 20
ConTabName = '|Список продолжений|'
SortTitlesBy = "count"


def show_exception(name_from, error):
    QMessageBox.critical(MainP, "PLS4_ERROR: %s" % name_from, str(error))


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
        db.commit()
    except Exception as e:
        show_exception("__main__save_data", e)


class SelfStyledIcon(QProxyStyle):
    def pixelMetric(self, q_style_pixel_metric, option=None, widget=None):
        if q_style_pixel_metric == QStyle.PM_SmallIconSize:
            return 30
        else:
            return QProxyStyle.pixelMetric(self, q_style_pixel_metric, option, widget)


# todo: формат кол-во серий \ время тайтла
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
            self.cancel.clicked.connect(self.show_)
            self.ok.clicked.connect(self.submit)
        except Exception as e:
            print('Add_Title_Form:', e)

    # Show/hide add form
    def show_(self):
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
            print('show_:', e)

    def submit(self):
        try:
            name = self.title_name.text()
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

            self.show_()
            self.parent.add_title(name, count, genre, link, desc, icon, color)
        except Exception as e:
            show_exception("submit", e)


class TabBar(QTabBar):
    def __init__(self, parent):
        super(TabBar, self).__init__(parent)
        self.setMovable(True)
        self.setTabsClosable(True)
        self.setExpanding(True)


# todo: на какой серии остановился
# todo: отрыть ссылку
class SideBar(QWidget):
    def __init__(self, parent):
        super(SideBar, self).__init__(parent)
        try:
            loadUi('GUI/SideBar.ui', self)
            self.p = parent
            self.change_check = True

            self.closeSide.clicked.connect(self.show_hide)

            self.genre.doubleClicked.connect(self.do_edit)
            self.genre.setCursor(QCursor(Qt.PointingHandCursor))
            self.genre.returnPressed.connect(self.save_desc)

            self.desc.doubleClicked.connect(self.do_edit)
            self.desc.setCursor(QCursor(Qt.PointingHandCursor))

            self.link.doubleClicked.connect(self.do_edit)
            self.link.setCursor(QCursor(Qt.PointingHandCursor))
            self.link.returnPressed.connect(self.save_desc)

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
            self.do_edit(False)
            genre = self.genre.text()
            link = self.link.text()
            desc = self.desc.toPlainText()
            query = "update titles set genre='%s', link='%s', desc='%s' where id=%s" \
                    % (genre, link, desc, self.p.curRow.id)
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
                self.p.curRow.set_icon(Icons['not_finished'])
            else:
                self.p.curRow.set_icon(Icons['n'])

    def set_is_con(self, state):
        if self.change_check:
            if state == 2:
                self.p.curRow.set_color('is_con')
            else:
                self.p.curRow.set_color('n')

    # On doubleclick
    def do_edit(self, edit=True):
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
                self.do_edit(False)
        except Exception as e:
            show_exception("sideBar_esc", e)

    # Load and set title-data into side bar
    def load_side_data(self, t_id):
        try:
            self.do_edit(False)

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
            count = count * episode
            time = "%s%s" % (count // 60, 'ч') if count >= 60 else ""
            time += "%s%s" % (count % 60, 'м') if count % 60 else ""
            return time
        except Exception as e:
            show_exception("count_title_time", e)

    # Switch hide/show side bar
    def show_hide(self):
        try:
            if self.p.side_hidden:
                self.animSide.setEndValue(QRect(self.p.w - SideWidth, 0,
                                                SideWidth, self.p.h))
                self.p.side_hidden = False
                self.closeSide.setText('>')
            else:
                self.animSide.setEndValue(QRect(self.p.w - 20, 0, SideWidth, self.p.h))
                self.p.side_hidden = True
                self.closeSide.setText('<')
            self.animSide.start()
        except Exception as e:
            show_exception("hide_show_sidebar", e)


class RowButtons(QWidget):
    def __init__(self, con=False):
        super(RowButtons, self).__init__()
        try:
            self.p = None
            self.btns = QHBoxLayout(self)
            self.btns.setContentsMargins(3, 0, 3, 0)

            self.delT = QPushButton('УДАЛИТЬ')
            self.delT.setFocusPolicy(Qt.NoFocus)
            self.delT.setCursor(QCursor(Qt.PointingHandCursor))
            self.delT.clicked.connect(self.delete_title)
            if con:
                self.btns.addWidget(self.delT)
            else:
                self.row_left = QHBoxLayout()
                self.row_left.setAlignment(Qt.AlignLeft)
                self.row_right = QHBoxLayout()
                self.row_right.setAlignment(Qt.AlignRight)

                self.viewing = QPushButton('СМОТРЮ')
                self.viewing.setFixedSize(115, 30)
                self.viewing.setFocusPolicy(Qt.NoFocus)
                self.viewing.setCursor(QCursor(Qt.PointingHandCursor))
                self.viewing.clicked.connect(self.viewing_now)

                self.viewed = QPushButton('ПРОСМОТРЕНО')
                self.viewed.setFixedSize(170, 30)
                self.viewed.setFocusPolicy(Qt.NoFocus)
                self.viewed.setCursor(QCursor(Qt.PointingHandCursor))
                self.viewed.clicked.connect(self.select_mark)

                self.delT.setFixedSize(90, 30)

                self.row_left.addWidget(self.viewing)
                self.row_left.addWidget(self.viewed)
                self.row_right.addWidget(self.delT)
                self.btns.addLayout(self.row_left)
                self.btns.addLayout(self.row_right)

                self.date = QLineEdit(self)
                self.date.setAlignment(Qt.AlignCenter)
                self.date.setGeometry(123, 0, 170, 30)
                reg_exp = QRegExp(r"\d{4}(\.(\d{1,2})(\.(\d{1,2}))?)?")
                validator = QRegExpValidator(reg_exp, self.date)
                self.date.setValidator(validator)
                self.date.setStyleSheet(
                    'QLineEdit{font-size:16px;font-weight:bold;background:#D9D9D9}')
                self.date.hide()
                self.date.focusOutEvent = lambda x: self.date.hide()
                self.date.returnPressed.connect(self.set_con_date)
        except Exception as e:
            show_exception("RowButtons__init", e)

    def viewing_now(self):
        try:
            self.p.leave(False)
            if self.p.icon == Icons['viewing']:
                self.p.set_color('n')
                self.p.set_icon(Icons['n'])
                self.viewing.setText('СМОТРЮ')
                self.p.p.side_bar.load_side_data(self.p.id)
            else:
                self.p.set_color('viewing')
                self.p.set_icon(Icons['viewing'])
                self.viewing.setText('НЕ СМОТРЮ')
                self.p.p.side_bar.load_side_data(self.p.id)

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

            text = self.date.text()
            sql('update titles set con_date="%s" where id=%s' % (text, self.p.id))
            db.commit()

            if ConTabName in MainP.tab_map:
                tab = MainP.tabWidget.widget(MainP.tab_map.index(ConTabName))
                name = self.p.title_name.text()
                count = self.p.count.text()
                id_ = self.p.id
                date = self.date.text()
                tab.add_row(name, count, id_, date, 'n', -1)
        except Exception as e:
            show_exception("set_con_date", e)

    # todo: отменить метку
    def select_mark(self):
        try:
            menu = QMenu(self)

            ico = QIcon(Icon[Icons['viewed']])
            on_viewed = menu.addAction(ico, 'Просмотрен')
            on_viewed.setEnabled(self.p.icon != Icons['viewed'])

            ico = QIcon(Icon[Icons['con']])
            on_con = menu.addAction(ico, 'Будет продолжение')
            on_con.setEnabled(self.p.icon != Icons['con'])

            ico = QIcon(Icon[Icons['pause']])
            on_pause = menu.addAction(ico, 'Просмотр брошен')
            on_pause.setEnabled(self.p.icon not in [Icons['viewed'], Icons['con']])

            cursor = QPoint(self.viewed.x(), -35)
            selected = menu.exec_(self.mapToGlobal(cursor))

            if selected == on_viewed:
                if self.p.color not in ['is_con', 'viewed']:
                    save_data('viewed')
                if self.p.icon == Icons['con']:
                    query = "update Titles set con_date='', icon='%s'" % Icons['viewed']
                    sql(query + " WHERE id=%s" % self.p.id)
                self.p.set_color('viewed')
                self.p.set_icon(Icons['viewed'])
            if selected == on_con:
                self.date.show()
                self.date.setText(datetime.today().strftime('%Y'))
                self.date.setFocus()
                self.date.selectAll()
            if selected == on_pause:
                self.p.set_color('pause')
                self.p.set_icon(Icons['pause'])

            self.p.p.side_bar.load_side_data(self.p.id)
        except Exception as e:
            show_exception("select_mark", e)


class Title(QWidget):
    def __init__(self, parent, name, count, id_, icon, color):
        try:
            super(Title, self).__init__(parent)
            loadUi('GUI/Title.ui', self)
            self.id = id_
            self.p = parent
            self.icon = icon
            self.name = name
            self.color = color
            self.borderColor = "blue"
            self.hoverColor = "#6ebcd2"

            self.row_layout.setAlignment(Qt.AlignTop)

            self.title_name.setText(name)
            self.title_name.clicked.connect(self.select_row)
            self.title_name.doubleClicked.connect(self.edit_line)
            self.title_name.returnPressed.connect(self.end_line_edit)
            self.title_name.setCursor(QCursor(Qt.PointingHandCursor))

            self.count.setCursor(QCursor(Qt.PointingHandCursor))
            self.count.setValidator(QIntValidator(1, 9999))
            self.count.setText(str(count))
            self.count.returnPressed.connect(self.end_line_edit)
            self.count.clicked.connect(self.select_row)
            self.count.doubleClicked.connect(self.edit_line)

            self.con_date.clicked.connect(self.select_row)
            self.con_date.doubleClicked.connect(self.edit_line)
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

            self.show_side = False

            self.min_height = RowHeightMin
            self.animOn = QTimer(self)
            self.animOn.timeout.connect(self.anim_down)
            self.animOff = QTimer(self)
            self.animOff.timeout.connect(self.anim_up)
        except Exception as e:
            show_exception("NewTitle__init", e)

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
                    query = "update Titles set con_date'',icon='%s'" % Icons['viewed']
                    sql(query + " WHERE id=%s" % self.id)
                    pl = list(sql("SELECT playlist FROM Titles WHERE id=%s" % self.id))
                    if pl[0][0] in MainP.tab_map:
                        index = MainP.tab_map.index(pl[0][0])
                        MainP.close_tab(index)
                        MainP.add_tab(pl[0][0], index)
                else:
                    sql('DELETE FROM Titles WHERE id=%s' % self.id)
                db.commit()

                self.min_height = 0
                self.animOff.start(1)

                if not self.p.side_hidden:
                    self.p.side_bar.show_hide()
                    self.p.just_opened = True

                if self.color == 'viewed':
                    save_data('viewed', -1)
                save_data('added', -1)
        except Exception as e:
            show_exception("delete_title", e)

    def set_icon(self, ico):
        try:
            icon = QPixmap(Icon[ico]).scaled(30, 30)
            self.status.setPixmap(icon)
            if ico != self.icon:
                self.icon = ico
                sql('UPDATE Titles SET icon="%s" WHERE id=%s' % (ico, self.id))
                db.commit()
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
                        ''' % (Color[color], self.borderColor))

                if color not in ['edit', self.color]:
                    self.color = color
                    sql('UPDATE Titles SET color="%s" WHERE id=%s' % (color, self.id))
                    db.commit()
        except Exception as e:
            show_exception("set_color", e)

    # Hide/show buttons
    def set_buttons(self, show):
        if show:
            self.row_layout.addWidget(self.p.row_btns)
        elif not self.p.con:
            self.p.row_btns.viewing.setText('СМОТРЮ')
            self.p.row_btns.viewing.setEnabled(True)

    # ON click row
    def select_row(self):
        try:
            if self.p.curRow not in [self, None]:
                self.p.curRow.leave()
            if self.p.curRow is not self:
                self.setStyleSheet('''
                    #t_row{border-color: %s}
                    #title_name,#count,#con_date{background: %s}
                    ''' % (self.borderColor, Color[self.color]))
                self.p.curRow = self
                self.p.side_bar.closeSide.setEnabled(True)
                self.p.side_bar.load_side_data(self.id)
                self.animOn.start(RowAnimDur)

                self.p.row_btns.setParent(self)
                self.p.row_btns.p = self

                self.p.scroll_to(self.p.rowMap.index(self.id))

                if self.p.just_opened:
                    self.p.side_bar.show_hide()
                    self.p.just_opened = False

                if self.icon == 'viewing':
                    self.p.row_btns.viewing.setText('НЕ СМОТРЮ')
                if self.icon in ['viewed', 'con']:
                    self.p.row_btns.viewing.setEnabled(False)
        except Exception as e:
            show_exception("select_row", e)

    # ON doubleclick row
    def edit_line(self):
        try:
            self.set_edit()
            self.set_color('edit')
            if self.p.con:
                self.con_date.setText(self.con_date.text().rstrip("!"))

            if not self.p.side_hidden:
                self.p.side_bar.show_hide()
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
                db.commit()

                self.p.side_bar.load_side_data(self.id)
                self.leave(False)
            else:
                QMessageBox.warning(self, "PLS4", "Имя тайтла не может быть пустым!")
        except Exception as e:
            show_exception("on_line_edited", e)

    def set_edit(self, edit=True):
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
                self.set_buttons(True)
        except Exception as e:
            show_exception("anim_down", e)

    # Anim row up
    def anim_up(self):
        if self.height() > self.min_height:
            self.setFixedHeight(self.height() - 1)
        else:
            self.finish_anim_up()

    def finish_anim_up(self):
        if self.min_height == 0:
            self.animOff.stop()
            self.p.row_btns.setParent(None)
            self.p.curRow = None
            self.setParent(None)
            row_count = self.p.rowList.count()
            self.p.row_count.setText('Тайтлов в плейлисте:' + str(row_count))
            if not row_count:
                MainP.close_tab(MainP.tab_map.index(ConTabName))

            del self
        else:
            self.animOff.stop()

    def leave(self, change=True):
        try:
            self.animOff.stop()
            self.animOn.stop()
            if change:
                self.set_buttons(False)
                self.keyPressEvent(esc=True)
                self.animOff.start(RowAnimDur)
                self.setStyleSheet('''
                    #t_row{border-color: #F0F0F0}
                    QLineEdit{background: %s}
                    #t_row:hover{border-color: %s;}'''
                                   % (Color[self.color], self.hoverColor))
            else:
                self.set_color(self.color)
                if self.show_side:
                    self.p.side_bar.show_hide()
                    self.show_side = False

            self.set_edit(False)
        except Exception as e:
            show_exception("leave", e)


class Playlist(QWidget):
    def __init__(self, parent, name, new):
        super(Playlist, self).__init__(parent)
        try:
            loadUi('GUI/Playlist.ui', self)
            self.p = parent
            self.name = name
            self.curRow = None
            self.rowMap = list()
            self.con = name == ConTabName
            self.row_btns = RowButtons(self.con)

            self.rowList.setAlignment(Qt.AlignTop)

            self.add_form = AddTitleForm(self)
            self.add_form.setGeometry(9, 49, 370, 0)

            self.addT.clicked.connect(self.add_form.show_)
            self.delP.clicked.connect(self.delete_playlist)

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
            self.search_timer.setInterval(ConSearchDur)
            self.search_edit.textEdited.connect(self.search_timer.start)

            self.search_anim = QPropertyAnimation(self.search_edit, b"size")
            self.search_anim.setEasingCurve(QEasingCurve.OutExpo)
            self.search_anim.setDuration(AddPlDur)

            self.rename.clicked.connect(self.rename_playlist)

            if self.con:
                self.addT.hide()
                self.delP.hide()
                self.rename.hide()
            else:
                self.search.hide()

            if new:
                QTimer.singleShot(500, self.add_form.show_)
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
                db.commit()

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
            for i in range(self.rowList.count()):
                row = self.rowList.itemAt(i).widget()
                if text in row.name.lower():
                    row.select_row()
                    break

    def select_row(self, index):
        try:
            self.rowList.itemAt(self.rowMap.index(index)).widget().select_row()
        except Exception as e:
            show_exception("select_row", e)

    # Move scroll bar
    def scroll_to(self, index: int):
        try:
            bar = self.scrollArea.verticalScrollBar()
            step = bar.pageStep()
            row_size = RowHeightMin + self.rowList.spacing()
            target_pos = row_size * index + self.rowList.spacing()
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
                db.commit()

                for i in range(self.rowList.count()):
                    if self.rowList.itemAt(i).widget().color == 'viewed':
                        save_data('viewed', -1)

                self.p.pl_list.removeItem(self.p.pl_list.currentIndex())
                self.p.close_tab(self.p.tab_map.index(self.name))
                if not self.p.tab_map:
                    self.p.select_playlist()
        except Exception as e:
            show_exception('delete_playlist', e)

    # todo: защита от дубликатов, поиск в con
    def add_title(self, t_name, count, genre, link, desc, icon, color):
        try:
            query = "INSERT INTO Titles VALUES "
            date = datetime.today().strftime("%d.%m.%Y")

            sql(query + "('%s',%s,%s,'%s','%s','%s','%s','%s','%s','', '%s')"
                % (t_name, count, ID, self.name, icon, color, genre, link, desc, date))
            db.commit()

            query = "SELECT id,count,icon FROM Titles WHERE playlist = '%s'" % self.name
            row_id = list(sql(query + " ORDER BY count desc,icon desc,id desc"))

            for i, item in enumerate(row_id):
                if item[0] == ID:
                    row_id = i
                    break
            self.add_row(t_name, count, ID, icon, color, row_id).select_row()
            self.row_count.setText('Тайтлов в плейлисте:' + str(self.rowList.count()))
            save_data('id')
            save_data('added')
        except Exception as e:
            show_exception('add_title', e)

    def add_row(self, name, count, t_id, icon_date, color, index, delay=0):
        try:
            row = Title(self, name, count, t_id, icon_date, color)
            index = self.rowList.count() if index == -1 else index
            loop = QEventLoop()
            QTimer.singleShot(delay, loop.quit)
            loop.exec_()
            self.rowList.insertWidget(index, row)
            self.rowMap.insert(index, t_id)
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
                    self.add_row(t[0], t[1], t[2], t[3], color, index, delay)
                    index += 1

            else:
                query = "SELECT title_name,count,id,icon,color FROM Titles WHERE " \
                        "playlist='%s' ORDER BY " % self.name
                titles = list(sql(query + "count desc, icon desc, id desc"))
                if not len(titles):
                    return
                delay = AddRowDur // len(titles)
                for t in titles:
                    self.add_row(t[0], t[1], t[2], t[3], t[4], index, delay)
                    index += 1

                if self.p.set_viewing:
                    self.select_row(self.p.set_viewing)
                    self.p.set_viewing = False

            self.row_count.setText('Тайтлов в плейлисте:' + str(self.rowList.count()))
        except Exception as e:
            show_exception('load_titles', e)


# todo: settings
class MainForm(QMainWindow):

    def __init__(self):
        super(MainForm, self).__init__()
        loadUi('GUI/MainForm.ui', self)

        global MainP
        MainP = self
        with open(Skin) as style:
            self.setStyleSheet(style.read())
        self.selectedTab = ""
        self.tab_map = []

        self.addP.clicked.connect(self.add_playlist)
        self.pl_list.activated.connect(self.select_playlist)

        self.pl_name.returnPressed.connect(self.addP.click)
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

        self.add_pl_anim = QPropertyAnimation(self.pl_name, b"geometry")
        self.add_pl_anim.setEasingCurve(QEasingCurve.OutExpo)
        self.add_pl_anim.setDuration(AddPlDur)

        QTimer.singleShot(1, self.launch)
        self.launching = True
        self.set_viewing = False

    # todo: options
    def open_options(self):
        try:
            menu = QMenu(self)
            cons = list(sql("SELECT con_date, id FROM Titles WHERE con_date != ''"))

            ico = QIcon(Icon[Icons['con']])
            con_list = menu.addAction(ico, 'Список продолжений')
            con_list.setEnabled(bool(cons))

            clear = menu.addAction('Clear')

            cursor = QPoint(self.options.x() + 5, self.options.y() + 10)
            selected = menu.exec_(self.mapToGlobal(cursor))

            if selected == con_list:
                self.open_con_list()
            if selected == clear:
                self._clear()

        except Exception as e:
            show_exception('open_options', e)

    def open_con_list(self):
        self.add_tab(ConTabName)

    # Show/hide add playlist
    # todo: защита от будликатов
    def add_playlist(self):
        try:
            if self.pl_name.isHidden():
                self.pl_name.setText("PL" + str(self.pl_list.count() + 1))
                self.anim_add_pl(True)
            else:
                name = self.pl_name.text()
                if self.check_playlist(name):
                    sql("INSERT INTO Playlists VALUES ('%s')" % name)
                    db.commit()
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

    def close_tab(self, index):
        try:
            self.tab_map.remove(self.tabWidget.tabText(index))
            self.tabWidget.removeTab(index)
        except Exception as e:
            show_exception('close_tab', e)

    def select_playlist(self):
        if self.selectedTab != self.pl_list.currentText():
            self.selectedTab = self.pl_list.currentText()
            self.add_tab(self.selectedTab)

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
        except Exception as e:
            show_exception('add_tab', e)

    def select_tab(self, index):
        try:
            if index >= 0 and not self.launching:
                text = self.tabWidget.tabText(index)
                index = self.pl_list.findText(text)
                self.pl_list.setCurrentIndex(index)
                self.selectedTab = text

                if index != -1:
                    sql("UPDATE Data SET value='%s' WHERE name='cur_pl'" % index)
                    db.commit()
            elif not self.launching:
                self.selectedTab = ""
        except Exception as e:
            show_exception('select_tab', e)

    def move_tab(self, index):
        tab = self.tabWidget.tabText(index)
        self.tab_map.remove(tab)
        self.tab_map.insert(index, tab)

    # Temp
    def _clear(self):
        try:
            buttons = QMessageBox.Yes | QMessageBox.No
            action = QMessageBox.question(self, "Message", "Sure?", buttons)
            if action == QMessageBox.No: return
            sql("DELETE FROM Playlists")
            sql("DELETE FROM Titles")
            sql('UPDATE Data SET value="0"')
            db.commit()
            self.pl_list.clear()
            self.tabWidget.clear()
            self.tab_map.clear()
            global ID
            ID = 0
        except Exception as e:
            show_exception('_clear', e)

    # pl name esc
    def keyPressEvent(self, event):
        try:
            if not event or (event.key() == Qt.Key_Escape and self.pl_name.isVisible()):
                self.anim_add_pl(False)
        except Exception as e:
            show_exception('MainForm_on_esc', e)

    def select_last_playlist(self):
        try:
            pl = list(sql("SELECT value FROM Data WHERE name='cur_pl'"))[0][0]
            title_id = list(sql("SELECT id, playlist FROM Titles WHERE icon='viewing'"))
            if title_id:
                self.pl_list.setCurrentIndex(self.pl_list.findText(title_id[-1][1]))
                self.set_viewing = int(title_id[-1][0])
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
            db.commit()

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
