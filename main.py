from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget,QHeaderView
from PyQt6 import uic
from PyQt6.uic import loadUi
from PyQt6.QtSql import *
import sys
from PyQt6.uic.properties import QtWidgets
from EditForm import Ui_EditWindow
from AddForm import Ui_AddWindow
db_name = 'databases/MyDb.db'


class MainUI(QMainWindow):

    def __init__(self):
        super(MainUI, self).__init__()
        loadUi("MainForm.ui", self)

        self.setWindowTitle("Сопровождение конкурсов на соискание грантов")

        self.Gr_prog()
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.Table_Gr_prog.triggered.connect(self.Gr_prog)
        self.Table_gr_konk.triggered.connect(self.gr_konk)
        self.Table_VUZ.triggered.connect(self.VUZ)
        self.action_exit.triggered.connect(self.exit)
        self.Edit.clicked.connect(self.open_window_edit)
        self.Add.clicked.connect(self.open_window_add)

    def open_window_edit(self):
        self.wEdit = EditUI(parent=self)
        self.wEdit.show()


    def open_window_add(self):
        self.wAdd = AddUI(parent=self)
        self.wAdd.show()



    def Gr_prog(self):
        Gr_prog = QSqlTableModel()
        Gr_prog.setTable('Gr_prog')
        Gr_prog.select()
        self.tableView.setSortingEnabled(True)
        self.tableView.setModel(Gr_prog)

    def gr_konk(self):
        gr_konk = QSqlTableModel()
        gr_konk.setTable('gr_konk')
        sql_request = """UPDATE gr_konk
               SET `Кол-во НИР` = query1.count_nir
               FROM (
                    SELECT "Код конк." as code_konk, COUNT("Код НИР") AS count_nir
                    FROM "Gr_prog"
                    GROUP BY "Код конк."
                    ) AS query1
                WHERE gr_konk.`Код конк.` = query1.code_konk;"""

        sql_request2 = """UPDATE gr_konk
                SET `План. объем финанс-я` = query1.sum_fin
               FROM (
                    SELECT "Код конк." as code_konk, SUM("План. объём финанс-я") AS sum_fin
                    FROM Gr_prog
                    GROUP BY "Код конк."
                    ) AS query1
                WHERE gr_konk.`Код конк.` = query1.code_konk;"""

        query = QSqlQuery()
        query.exec(sql_request)
        query.exec(sql_request2)

        if query.lastError().type() == QSqlError.ErrorType.NoError:
            print('Successfully updated!')
        else:
            print('Not executed:', query.lastError().text())
        gr_konk.select()
        self.tableView.setSortingEnabled(True)
        self.tableView.setModel(gr_konk)

    def VUZ(self):
        VUZ = QSqlTableModel()
        VUZ.setTable('VUZ')
        VUZ.select()
        self.tableView.setSortingEnabled(True)
        self.tableView.setModel(VUZ)

    def exit(self):
        sys.exit(-1)

    def test_click(self):
        print("test ok")

    def connect_db(db_name):
        db = QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName(db_name)
        if not db.open():
            print("Невозможно установить соединение {}!".format(db_name))
            return False
        return db

    if not connect_db(db_name):
        sys.exit(-1)
    else:
        print("connection ok")

class AddUI(QMainWindow):
    def __init__(self, parent):
        super(AddUI, self).__init__()
        self.ui = Ui_AddWindow()
        self.ui.setupUi(self)
        self.parent = parent
        #self.setAttribute(Qt.WidgetAttribute.)
        self.setWindowTitle("Добавление НИР")

class EditUI(QMainWindow):
    def __init__(self, parent):
        super(EditUI, self).__init__()
        self.ui = Ui_EditWindow()
        self.ui.setupUi(self)
        self.parent = parent
        #self.setAttribute(Qt.WidgetAttribute.)
        self.setWindowTitle("Редактирование НИР")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = MainUI()
    ui.show()
    app.exec()
