from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QHeaderView, QMessageBox
from PyQt6 import uic
from PyQt6.uic import loadUi
from PyQt6.QtSql import *
import sys
from PyQt6.uic.properties import QtWidgets
from EditForm import Ui_EditWindow
from AddForm import Ui_AddWindow
from PyQt6.QtWidgets import QDialog, QFormLayout, QLabel, QLineEdit, QPushButton
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from typing import List

db_name = 'MyDb.db'


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
        self.Delete.clicked.connect(self.delete_selected_row)

    def delete_selected_row(self):
        selected_row = self.tableView.selectionModel().currentIndex().row()
        if selected_row >= 0:
            # Ask for confirmation
            confirmation = QMessageBox.question(
                self,
                "Подтвердите действие",
                "Вы уверены, что хотите удалить запись?",
                buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if confirmation == QMessageBox.StandardButton.Yes:
                model = self.tableView.model()
                model.removeRow(selected_row)
                if model.submitAll():
                    QMessageBox.information(self, 'Успешно', 'Запись удалена.')
                else:
                    QMessageBox.warning(self, 'Ошибка', 'Не удалось удалить запись.')
            else:
                # User chose not to delete the record
                QMessageBox.information(self, 'Отмена', 'Запись не удалена.')
        else:
            QMessageBox.warning(self, 'Ошибка', 'Ни одна строка не выбрана для удаления.')

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

        sql_request_kv1 = """UPDATE "gr_konk"
SET "1 кв-л" = (SELECT SUM("1 кв-л") FROM "Gr_prog" WHERE "gr_konk"."Код конк." = "Gr_prog"."Код конк.");"""
        sql_request_kv2 = """UPDATE "gr_konk"
        SET "1 кв-л" = (SELECT SUM("2 кв-л") FROM "Gr_prog" WHERE "gr_konk"."Код конк." = "Gr_prog"."Код конк.");"""
        sql_request_kv3 = """UPDATE "gr_konk"
        SET "1 кв-л" = (SELECT SUM("3 кв-л") FROM "Gr_prog" WHERE "gr_konk"."Код конк." = "Gr_prog"."Код конк.");"""
        sql_request_kv4 = """UPDATE "gr_konk"
        SET "1 кв-л" = (SELECT SUM("4 кв-л") FROM "Gr_prog" WHERE "gr_konk"."Код конк." = "Gr_prog"."Код конк.");"""

        sql_request_fact_fin = """UPDATE "gr_konk"
SET "Факт. объем финанс-я" = "1 кв-л" + "2 кв-л" + "3 кв-л" + "4 кв-л";
"""

        query = QSqlQuery()
        query.exec(sql_request)
        query.exec(sql_request2)
        query.exec(sql_request_kv1)
        query.exec(sql_request_kv2)
        query.exec(sql_request_kv3)
        query.exec(sql_request_kv4)
        query.exec(sql_request_fact_fin)

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
        super().__init__()
        self.ui = Ui_AddWindow()
        self.ui.setupUi(self)
        self.parent = parent
        # self.setAttribute(Qt.WidgetAttribute.)
        self.setWindowTitle("Добавление НИР")
        self.ui.pushButton.clicked.connect(self.handle_values)
        self.ui.pushButtonClear.clicked.connect(self.clear_input_fields)
        self.ui.comboBox_4.currentTextChanged.connect(self.set_vuz_code_value)
        self.set_default_values()
        # Устанавливаем маски ввода
        self.ui.lineEdit_12.setInputMask("DD.DD.DD")
        self.ui.lineEdit_11.setInputMask("DD.DD.DD")

    def set_vuz_code_value(self, text):
        sql_query = f'SELECT "Код вуза" FROM VUZ WHERE "Сокр. наим-е ВУЗа" = "{text}"'
        query = QSqlQuery()
        query.exec(sql_query)
        query.next()
        vuz_code = query.value(0)
        self.ui.textEdit_2.setPlainText(str(vuz_code))

    @staticmethod
    def get_unique_values(column: str) -> List:
        sql_query = f'SELECT DISTINCT("{column}") FROM Gr_prog'
        query = QSqlQuery()
        query.exec(sql_query)

        unique_values = []
        while query.next():
            unique_values.append(query.value(0))
        return unique_values

    @staticmethod
    def maxi_nir_code():
        sql_query = 'SELECT MAX("Код НИР") FROM "Gr_prog"'
        query = QSqlQuery()
        query.exec(sql_query)
        if query.next():
            suggested_code = query.value(0) + 1
        return suggested_code

    def set_default_values(self):
        tender_codes = [str(code) for code in self.get_unique_values('Код конк.')]
        vuzes = self.get_unique_values('Сокр-е наим-е ВУЗа')
        suggested_code = self.maxi_nir_code()

        self.ui.comboBox_3.addItems(tender_codes)
        self.ui.comboBox_4.addItems(vuzes)
        self.ui.textEdit.setPlainText(str(suggested_code))


    def handle_values(self):
        colnames = [  # Comboboxes
            "Код конк.", "Сокр-е наим-е ВУЗа",

            # Text edits
            "Код НИР", "Руководитель",
            "План. объём финанс-я", "Код по ГРНТИ",
            "Должность", "Звание",
            "Ученая степень", "Код вуза",
            "Наименование НИР"]

        # Comboboxes
        tender_code = self.ui.comboBox_3.currentText()
        vuz = self.ui.comboBox_4.currentText()

        # Text edits
        nir_code = self.ui.textEdit.toPlainText()
        nir_chief = self.ui.textEdit_4.toPlainText()
        plan_finance = self.ui.textEdit_8.toPlainText()
        grnti_code_1 = self.ui.lineEdit_11.text()
        grnti_code_2 = self.ui.lineEdit_12.text()
        if grnti_code_2:
            grnti_code = f"{grnti_code_1},{grnti_code_2}"
        else:
            grnti_code = f"{grnti_code_1}"
        # grnti_code = self.ui.textEdit_3.toPlainText()
        chief_post = self.ui.textEdit_5.toPlainText()
        scientific_rank = self.ui.textEdit_6.toPlainText()
        scientific_degree = self.ui.textEdit_7.toPlainText()
        vuz_code = self.ui.textEdit_2.toPlainText()
        nir_title = self.ui.textEdit_9.toPlainText()

        fields = [tender_code, vuz, nir_code, nir_chief, plan_finance,
                  grnti_code, chief_post, scientific_rank, scientific_degree, vuz_code, nir_title]

        handled_values = {colname: field for colname, field in zip(colnames, fields) if field}
        print(f'{handled_values=}')

        # Display a confirmation message
        confirmation = QMessageBox.question(
            self,
            "Подтвердите действие",
            "Вы действительно хотите добавить запись в таблицу?",
            buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirmation == QMessageBox.StandardButton.Yes:
            self.add_data(handled_values)
        else:
            QMessageBox.information(self, "Отмена", "Добавление записи отменено.")



    def add_data(self, column_values: dict):
        columns, values = column_values.keys(), column_values.values()

        try:
            sql_query = f"""INSERT INTO Gr_prog ("{'", "'.join(columns)}") 
                            VALUES ("{'", "'.join(values)}");"""

            print(sql_query)
            query = QSqlQuery(sql_query)

            if query.lastError().type() == QSqlError.ErrorType.NoError:
                print('Новая строка успешно добавлена в таблицу Gr_prog')
                # Обновляем отображение данных в таблице
                self.parent.Gr_prog()
                QMessageBox.information(self, "Успех", "Новая запись была успешно добавлена в таблицу")

            else:
                print('Ошибка при добавлении строки в таблицу Gr_prog:', query.lastError().text())
        except Exception as error:
            print("Ошибка при добавлении строки в таблицу Gr_prog:", error)

        self.parent.Gr_prog()

    def clear_input_fields(self):  # Очистить поля ввода, чтобы пользователь мог ввести новые данные
        buttonReply = QMessageBox.question(self, 'Подтвердите действие', "Вы действительно хотите очистить все поля?",
                                           buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if buttonReply == QMessageBox.StandardButton.Yes:
            self.ui.comboBox_3.setCurrentIndex(0)
            self.ui.comboBox_4.setCurrentIndex(0)
            self.ui.textEdit_4.clear()
            self.ui.textEdit_8.clear()
            self.ui.textEdit_5.clear()
            self.ui.textEdit_6.clear()
            self.ui.textEdit_7.clear()
            self.ui.textEdit_9.clear()
            self.ui.lineEdit_12.clear()
            self.ui.lineEdit_11.clear()


class EditUI(QMainWindow):
    def __init__(self, parent):
        super(EditUI, self).__init__()
        self.ui = Ui_EditWindow()
        self.ui.setupUi(self)
        self.parent = parent
        # self.setAttribute(Qt.WidgetAttribute.)
        self.setWindowTitle("Редактирование НИР")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = MainUI()
    ui.show()
    app.exec()
