from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QHeaderView
from PyQt6.uic import loadUi
from PyQt6.QtSql import *
import sys

db_name = 'databases/MyDb.db'


class MainUI(QMainWindow):
    def __init__(self):
        super(MainUI, self).__init__()
        loadUi("MainForm.ui", self)

        self.tableView.setSortingEnabled(True)
        self.tableView.setModel(Gr_prog)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.Table_Gr_prog.triggered.connect(self.Gr_prog)
        self.Table_gr_konk.triggered.connect(self.gr_konk)
        self.Table_VUZ.triggered.connect(self.VUZ)
        # self.action_exit.triggered.connect(self.exit)

    def Gr_prog(self):
        Gr_prog = QSqlTableModel()
        Gr_prog.setTable('Gr_prog')
        Gr_prog.select()
        self.tableView.setSortingEnabled(True)
        self.tableView.setModel(Gr_prog)

    def gr_konk(self):
        gr_konk = QSqlTableModel()
        gr_konk.setTable('gr_konk')
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
        print("test")
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


Gr_prog = QSqlTableModel()
Gr_prog.setTable('Gr_prog')
Gr_prog.select()
gr_konk = QSqlTableModel()
gr_konk.setTable('gr_konk')
gr_konk.select()
VUZ = QSqlTableModel()
VUZ.setTable('VUZ')
VUZ.select()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = MainUI()
    ui.show()
    app.exec()
