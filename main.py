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
from PyQt6.QtCore import Qt, QSortFilterProxyModel
import re
import sqlite3

db_name = 'MyDb.db'


class CustomSortProxyModel(QSortFilterProxyModel):
    def __init__(self):
        super(CustomSortProxyModel, self).__init__()
        self.sorting_option = "По умолчанию"

    def setSortingOption(self, option):
        self.sorting_option = option

    def lessThan(self, left, right):
        left_data = [self.sourceModel().index(left.row(), col).data() for col in (0, 1, 2, 3, 4)]
        right_data = [self.sourceModel().index(right.row(), col).data() for col in (0, 1, 2, 3, 4)]

        if left_data[0] is None or right_data[0] is None:
            return False  # Handle None values as needed, for example, by placing them at the end

        # Define custom sorting logic based on your criteria
        if self.sorting_option == "По умолчанию":
            return left_data[0] < right_data[0]
        elif self.sorting_option == "Код конкурса + Код Нир":
            if left_data[0] == right_data[0]:
                return left_data[1] < right_data[1]
            return left_data[0] < right_data[0]
        elif self.sorting_option == "Название ВУЗа":
            if left_data[3] is None or right_data[3] is None:
                return False
            return left_data[3] < right_data[3]
        elif self.sorting_option == "Плановый об. финансирования":
            if left_data[4] is None or right_data[4] is None:
                return False
            return left_data[4] < right_data[4]

        return left_data[0] < right_data[0]


class MainUI(QMainWindow):
    def __init__(self):
        super(MainUI, self).__init__()
        loadUi("MainForm.ui", self)

        self.setWindowTitle("Сопровождение конкурсов на соискание грантов")

        self.model = QSqlTableModel()
        self.model.setTable('Gr_prog')
        self.model.select()
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.Table_Gr_prog.triggered.connect(self.Gr_prog)
        self.Table_gr_konk.triggered.connect(self.gr_konk)
        self.Table_VUZ.triggered.connect(self.VUZ)
        self.action.triggered.connect(self.analiz_vuz)
        self.action_2.triggered.connect(self.analiz_sub)
        self.action_exit.triggered.connect(self.exit)
        self.Edit.clicked.connect(self.open_window_edit)
        self.Add.clicked.connect(self.open_window_add)
        self.Delete.clicked.connect(self.delete_selected_row)
        self.customProxyModel = CustomSortProxyModel()
        self.customProxyModel.setSourceModel(self.model)
        self.tableView.setModel(self.customProxyModel)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.sortingbox.currentIndexChanged.connect(self.update_sorting_option)

    def update_sorting_option(self):
        sorting_option = self.sortingbox.currentText()

        if sorting_option == "По умолчанию":
            self.customProxyModel.setSortingOption("По умолчанию")
            self.customProxyModel.sort(0, Qt.SortOrder.AscendingOrder)

        elif sorting_option == "Код конкурса + Код Нир":
            self.customProxyModel.setSortingOption("Код конкурса + Код Нир")
            self.customProxyModel.sort(0, Qt.SortOrder.AscendingOrder)

        elif sorting_option == "Название ВУЗа":
            self.customProxyModel.setSortingOption("Название ВУЗа")
            self.customProxyModel.sort(3, Qt.SortOrder.AscendingOrder)

        elif sorting_option == "Плановый об. финансирования":
            self.customProxyModel.setSortingOption("Плановый об. финансирования")
            self.customProxyModel.sort(4, Qt.SortOrder.AscendingOrder)

        # Обновите модель в представлении
        self.tableView.setModel(self.customProxyModel)

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
                source_model = self.customProxyModel.sourceModel()  # Получаем исходную модель
                source_model.removeRow(selected_row)

                if source_model.submitAll():
                    QMessageBox.information(self, 'Успешно', 'Запись удалена.')
                else:
                    QMessageBox.warning(self, 'Ошибка', 'Не удалось удалить запись.')
            else:
                # User chose not to delete the record
                QMessageBox.information(self, 'Отмена', 'Запись не удалена.')
        else:
            QMessageBox.warning(self, 'Ошибка', 'Ни одна строка не выбрана для удаления.')

    def open_window_edit(self):
        selected_row_index = self.tableView.selectionModel().currentIndex().row()
        if selected_row_index >= 0:
            selected_row_data = self.get_selected_row_data(selected_row_index)
            self.wEdit = EditUI(self, selected_row_data)
            self.wEdit.show()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Ни одна строка не выбрана для редактирования.')

    def get_selected_row_data(self, row_index):
        row_data = {}
        for col in range(self.model.columnCount()):
            column_name = self.model.headerData(col, Qt.Orientation.Horizontal)
            cell_data = self.model.data(self.model.index(row_index, col))
            row_data[column_name] = cell_data
        if re.findall(r'..\..*,(.*)', row_data["Код по ГРНТИ"]):
            g1 = re.findall(r'(..\..*),.*', row_data["Код по ГРНТИ"])[0]
            g2 = re.findall(r'..\..*,(.*)', row_data["Код по ГРНТИ"])[0]
            print(f"{g1}\n{g2}")
        else:
            print(row_data["Код по ГРНТИ"])

        return row_data

    def update_selected_row(self, old_data, new_data):
        # Update the database with new_data while keeping the primary key (e.g., "Код НИР") from old_data unchanged
        # Construct and execute an SQL UPDATE statement to update the selected row in the database
        # You can use QSqlQuery to execute the UPDATE statement

        # After successfully updating the database, refresh the table view with the updated data
        print(old_data)
        print(new_data)
        update_sql = f"""UPDATE Gr_prog
                         SET "Код конк." =  {''},
                             "Код НИР" = {''},
                             "Сокр-е наим-е ВУЗа" = {''},
                             "Код по ГРНТИ" = {''},
                             "Руководитель" = {''},
                             "Должность" = {''},
                             "Звание" = {''},
                             "Ученая степень" = {''},
                             "План. объём финанс-я" = {''},
                             "Наименование НИР" = {''},
                         WHERE "Код конк." = {''};"""

        query = QSqlQuery()
        query.prepare(update_sql)
        query.bindValue(0, new_data['textEdit_2'])
        query.bindValue(1, new_data['textEdit'])
        query.bindValue(2, new_data['textEdit_3'])
        query.bindValue(3, new_data['textEdit_11'])
        # query.bindValue(3, new_data['textEdit_10'])
        query.bindValue(4, new_data['textEdit_4'])
        query.bindValue(5, new_data['textEdit_5'])
        query.bindValue(6, new_data['textEdit_6'])
        query.bindValue(7, new_data['textEdit_7'])
        query.bindValue(8, new_data['textEdit_8'])
        query.bindValue(9, new_data['textEdit_9'])
        query.bindValue(10, old_data['Код конк.'])

        if query.exec():
            QMessageBox.information(self, 'Успешно', 'Запись обновлена.')
            self.model.select()  # Refresh the model after updating
        else:
            QMessageBox.warning(self, 'Ошибка', 'Не удалось обновить запись в базе данных.')

    def open_window_add(self):
        self.wAdd = AddUI(parent=self)
        self.wAdd.show()

    def analiz_sub(self):
        self.setWindowTitle("Таблица с данными из SQL")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        self.table_widget = QTableWidget()
        layout.addWidget(self.table_widget)

        button = QPushButton("Обновить таблицу")
        button.clicked.connect(self.update_table)
        layout.addWidget(button)

        central_widget.setLayout(layout)

    def update_table(self):
        connection = sqlite3.connect("MyDb.db")
        cursor = connection.cursor()

        sql_query = """
                       SELECT 
                 t."Субъект РФ",
                 t."Кол-во Работ",
                 t."Кол-во конкурсов",
                 t."Объём финансирования"
               FROM
                 (SELECT 
                   VUZ."Субъект РФ",
                   COUNT(*) AS "Кол-во Работ",
                   COUNT(DISTINCT Gr_prog."Код конк.") AS "Кол-во конкурсов",
                   SUM(Gr_prog."План. объём финанс-я") AS "Объём финансирования"
                 FROM 
                   VUZ 
                   JOIN Gr_prog ON VUZ."Сокр. наим-е ВУЗа" = Gr_prog."Сокр-е наим-е ВУЗа" 
                 GROUP BY VUZ."Субъект РФ") t

               UNION ALL

               SELECT
                 'Итого:' AS "Субъект РФ",
                 COUNT(*) AS "Кол-во Работ",
                 COUNT(DISTINCT "Код конк.") AS "Кол-во конкурсов",
                 SUM("План. объём финанс-я") AS "Объём финансирования"
               FROM "Gr_prog";
               """

        cursor.execute(sql_query)
        result = cursor.fetchall()

        self.table_widget.setRowCount(0)
        self.table_widget.setColumnCount(len(result[0]))

        header_labels = ["Субъект РФ", "Кол-во Работ", "Кол-во конкурсов", "Объём финансирования"]
        self.table_widget.setHorizontalHeaderLabels(header_labels)

        for row_num, row_data in enumerate(result):
            self.table_widget.insertRow(row_num)
            for col_num, col_data in enumerate(row_data):
                item = QTableWidgetItem(str(col_data))
                self.table_widget.setItem(row_num, col_num, item)

        connection.close()

    def analiz_vuz(self):
        self.setWindowTitle("Таблица с данными из SQL")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        self.table_widget = QTableWidget()
        layout.addWidget(self.table_widget)

        button = QPushButton("Обновить таблицу")
        button.clicked.connect(self.update_table)
        layout.addWidget(button)

        central_widget.setLayout(layout)

    def update_table(self):
        # Убедитесь, что у вас есть соединение с вашей базой данных
        # В данном примере используется SQLite
        connection = sqlite3.connect('MyDb.db')
        cursor = connection.cursor()

        # Ваш SQL-запрос
        sql_query = """SELECT
                *
                FROM
                    (SELECT
                        "Сокр-е наим-е ВУЗа" AS "ВУЗ",
                        COUNT(*) AS "Кол-во НИР",
                        SUM("План. объём финанс-я") AS "Сум. объём финанс-я",
                        COUNT(DISTINCT "Код конк.") AS "Кол-во конк."
                    FROM "Gr_prog"
                    GROUP BY "Сокр-е наим-е ВУЗа"
                    ORDER BY "Сокр-е наим-е ВУЗа") t
                UNION ALL
                SELECT
                    'Итого:',
                    COUNT(*),
                    SUM("План. объём финанс-я"),
                    COUNT(DISTINCT "Код конк.")
                FROM "Gr_prog";
                """

        # Set header labels for the table columns
        header_labels = ["ВУЗ", "Кол-во НИР", "Сум объём финанс", "Кол-во конк."]

        self.table_widget.setColumnCount(len(header_labels))
        self.table_widget.setHorizontalHeaderLabels(header_labels)

        # Выполнение запроса
        cursor.execute(sql_query)
        result = cursor.fetchall()

        # Очищение таблицы перед обновлением
        self.table_widget.setRowCount(0)
        self.table_widget.setColumnCount(len(result[0]))

        # Заполнение таблицы результатами запроса
        for row_num, row_data in enumerate(result):
            self.table_widget.insertRow(row_num)
            for col_num, col_data in enumerate(row_data):
                item = QTableWidgetItem(str(col_data))
                self.table_widget.setItem(row_num, col_num, item)

        # Закрытие соединения
        connection.close()

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
        sql_query = f'SELECT DISTINCT("{column}") FROM Gr_prog ORDER BY "{column}"'
        query = QSqlQuery()
        query.exec(sql_query)

        unique_values = ['']
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
        print(fields)
        print(f'{handled_values}')

        # if len(handled_values) !=

        # errorrs = ['Ошибка! Некорректное значение в поле ']
        # for col in handled_values:
        #     if not validated:
        #         erorrs.append(colname, )
        # message_text = ';\n'.join(errors)
        print(handled_values.keys())
        if not handled_values['Код конк.']:
            QMessageBox.warning(self, 'Ошибка! Введено некорректное значение поля "Код конк."')
        elif handled_values['Сокр-е наим-е ВУЗа'] == '':
            QMessageBox.warning(self, 'Ошибка! Введено некорректное значение поля "Сокр-е наим-е ВУЗа"')
        elif handled_values['Код по ГРНТИ'] == '..,..':
            QMessageBox.warning(self, 'Ошибка! Введено некорректное значение поля "Код по ГРНТИ"')
        elif not re.match(r'^[ а-яА-Я]+$', handled_values['Руководитель']):
            QMessageBox.warning(self, 'Ошибка! Введено некорректное значение поля "Руководитель"')
        elif not re.match(r'^[0-9]+$', handled_values['План. объём финанс-я']):
            QMessageBox.warning(self, 'Ошибка! Введено некорректное значение поля "Плановый объём финансирования"')
        # Display a confirmation message

        message = QMessageBox(self)
        message.setWindowTitle("Подтвердите действие")
        message.setText("Вы действительно хотите добавить запись в таблицу?")
        message.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        message.buttonClicked.connect(lambda x: self.add_data(x, handled_values))

        message.show()

        # if message == QMessageBox.StandardButton.Yes:
        #     self.add_data(handled_values)
        # else:
        #     QMessageBox.information(self, "Отмена", "Добавление записи отменено.")

    def add_data(self, button, column_values: dict):
        print('пришли в адд дата')
        print(column_values)
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
    def __init__(self, parent, row_data):
        super(EditUI, self).__init__()
        self.ui = Ui_EditWindow()
        self.ui.setupUi(self)
        self.parent = parent
        self.row_data = row_data
        self.setWindowTitle("Редактирование НИР")
        self.populate_form_fields()
        self.ui.pushButton.clicked.connect(self.update_data)

    def populate_form_fields(self):
        # self.ui.comboBox_3.setCurrentText(str(self.row_data.get('Код конк.', '')))
        self.ui.textEdit_2.setPlainText(str(self.row_data['Код конк.']))
        self.ui.textEdit.setPlainText(str(self.row_data['Код НИР']))
        self.ui.textEdit_3.setPlainText(str(self.row_data['Сокр-е наим-е ВУЗа']))
        # self.ui.comboBox_4.setCurrentText(self.row_data.get('Сокр-е наим-е ВУЗа', ''))
        self.ui.textEdit_11.setPlainText(str(self.row_data['Код по ГРНТИ']))
        self.ui.textEdit_4.setPlainText(self.row_data['Руководитель'])
        self.ui.textEdit_5.setPlainText(self.row_data['Должность'])
        self.ui.textEdit_6.setPlainText(self.row_data['Звание'])
        self.ui.textEdit_7.setPlainText(self.row_data['Ученая степень'])
        self.ui.textEdit_8.setPlainText(str(self.row_data['План. объём финанс-я']))
        self.ui.textEdit_9.setPlainText(self.row_data['Наименование НИР'])

        # Connect the Push Button to an update function
        self.ui.pushButton.clicked.connect(self.update_data)

    def update_data(self):
        confirmation = QMessageBox.question(
            self,
            "Подтвердите действие",
            "Вы уверены, что хотите изменить данные?",
            buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirmation == QMessageBox.StandardButton.Yes:
            edited_data = {
                # 'Код конк.': self.ui.comboBox_3.currentText(),
                'Код конк.': self.ui.textEdit_2.toPlainText(),
                'Код НИР': self.ui.textEdit.toPlainText(),
                'Сокр-е наим-е ВУЗа': self.ui.textEdit_3.toPlainText(),
                # 'Сокр-е наим-е ВУЗа': self.ui.comboBox_4.currentText(),
                'Код по ГРНТИ': self.ui.textEdit_11.toPlainText(),
                'Руководитель': self.ui.textEdit_4.toPlainText(),
                'Должность': self.ui.textEdit_5.toPlainText(),
                'Звание': self.ui.textEdit_6.toPlainText(),
                'Ученая степень': self.ui.textEdit_7.toPlainText(),
                'План. объём финанс-я': self.ui.textEdit_8.toPlainText(),
                'Наименование НИР': self.ui.textEdit_9.toPlainText(),
            }

            # Update the database with the edited data
            row = self.parent.tableView.selectionModel().currentIndex().row()
            if row >= 0:
                for key, value in edited_data.items():
                    column_index = self.parent.model.record().indexOf(key)
                    if column_index != -1:
                        self.parent.model.setData(self.parent.model.index(row, column_index), value)

                if self.parent.model.submitAll():
                    QMessageBox.information(self, 'Успешно', 'Запись обновлена.')
                else:
                    QMessageBox.warning(self, 'Ошибка', 'Не удалось обновить запись в базе данных.')
                self.close()
            else:
                QMessageBox.warning(self, 'Ошибка', 'Ни одна строка не выбрана для редактирования.')
        else:
            QMessageBox.information(self, "Отмена", "Изменение данных отменено.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = MainUI()
    ui.show()
    app.exec()
