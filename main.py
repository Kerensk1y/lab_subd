from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QHeaderView, QMessageBox, QAbstractItemView
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
from PyQt6.QtCore import Qt, QSortFilterProxyModel, QItemSelectionModel
import re

db_name = 'MyDb.db'


class CustomSortProxyModel(QSortFilterProxyModel):
    def __init__(self):
        super(CustomSortProxyModel, self).__init__()

    def lessThan(self, left, right):
        left_data = [self.sourceModel().index(left.row(), col).data() for col in
                     range(self.sourceModel().columnCount())]
        right_data = [self.sourceModel().index(right.row(), col).data() for col in
                      range(self.sourceModel().columnCount())]

        # Handle None values by considering them greater than any integer
        for i in range(len(left_data)):
            if left_data[i] is None:
                left_data[i] = float('inf')  # Consider None as positive infinity
            if right_data[i] is None:
                right_data[i] = float('inf')  # Consider None as positive infinity

        # Implement your custom sorting logic here
        # For example, sort by the first column, and if they are equal, sort by the second column
        if left_data[0] != right_data[0]:
            return left_data[0] < right_data[0]
        else:
            return left_data[1] < right_data[1]


class MainUI(QMainWindow):
    def __init__(self):
        super(MainUI, self).__init__()
        loadUi("MainForm.ui", self)
        self.setWindowTitle("Сопровождение конкурсов на соискание грантов")
        self.model = QSqlTableModel()
        self.model.setTable('Gr_prog')
        self.model.select()
        self.Table_Gr_prog.triggered.connect(self.Gr_prog)
        self.Table_gr_konk.triggered.connect(self.gr_konk)
        self.Table_VUZ.triggered.connect(self.VUZ)
        self.action_exit.triggered.connect(self.exit)
        self.Edit.clicked.connect(self.open_window_edit)
        self.Add.clicked.connect(self.open_window_add)
        self.Delete.clicked.connect(self.delete_selected_row)
        self.model.setSort(0, Qt.SortOrder.AscendingOrder)  # Sort by the first column in ascending order
        self.model.select()
        self.customProxyModel = CustomSortProxyModel()
        self.customProxyModel.setSourceModel(self.model)
        self.customProxyModel.setDynamicSortFilter(True)

        self.tableView.setModel(self.customProxyModel)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        # Connect signals for automatic sorting when data changes
        self.model.dataChanged.connect(self.sort_table)
        self.model.rowsInserted.connect(self.sort_table)
        self.model.rowsRemoved.connect(self.sort_table)

        # ... (your existing code)

    def showEvent(self, event):
        # Call the base class showEvent to ensure any default behavior is executed
        super(MainUI, self).showEvent(event)

        # Set the initial sorting order for columns 0 and 1 (change as needed)
        self.customProxyModel.sort(0, Qt.SortOrder.AscendingOrder)
        self.customProxyModel.sort(1, Qt.SortOrder.AscendingOrder)

    def sort_table(self):
        # Sort the table by the first and second columns
        self.tableView.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.tableView.sortByColumn(1, Qt.SortOrder.AscendingOrder)

        # Ensure that the sorting is applied to both columns
        self.customProxyModel.sort(0, Qt.SortOrder.AscendingOrder)
        self.customProxyModel.sort(1, Qt.SortOrder.AscendingOrder)

    def delete_selected_row(self):
        selected_row_proxy = self.tableView.selectionModel().currentIndex().row()
        if selected_row_proxy >= 0:
            # Map the proxy index to the source index
            selected_row_source = self.customProxyModel.mapToSource(
                self.tableView.model().index(selected_row_proxy, 0)).row()

            # Ask for confirmation
            confirmation = QMessageBox.question(
                self,
                "Подтвердите действие",
                "Вы уверены, что хотите удалить запись?",
                buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if confirmation == QMessageBox.StandardButton.Yes:
                source_model = self.customProxyModel.sourceModel()  # Get the source model
                source_model.removeRow(selected_row_source)

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

        # colnames = [  # Comboboxes
        #     "Код конк.", "Сокр-е наим-е ВУЗа",
        #
        #     # Text edits
        #     "Код НИР", "Руководитель",
        #     "План. объём финанс-я", "Код по ГРНТИ",
        #     "Должность", "Звание",
        #     "Ученая степень", "Код вуза",
        #     "Наименование НИР"]

        colnames = ["tender_code", "vuz", "nir_code", "nir_chief", "plan_finance",
                    "grnti_code", "chief_post", "scientific_rank", "scientific_degree", "vuz_code", "nir_title"]

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

        REGEX_TO_VALIDATE = {
            'plan_finance': r'^[0-9]+$',
            'nir_chief': r'^[ а-яА-Я]+$',
            # 'plan_finance': r'^0$'
            # 'grnti_code': r'^\d\d\.\d\d\.\d\d$'
        }

        REQUIRED_COLS = ['tender_code', 'vuz', 'nir_title']

        errors_message = ''

        if 'plan_finance' in handled_values():
            k = float(handled_values['plan_finance'])
            if k > 0:
                pass
            else:
                errors_message += 'Некорректное значение объёма финансирования;\n'

        for colname in REQUIRED_COLS:
            if colname not in handled_values:
                errors_message += f'Не заполнено обязательное поле {colname};\n'

        for colname, colvalue in handled_values.items():
            regex = REGEX_TO_VALIDATE.get(colname, None)

            if regex and not re.match(regex, colvalue):
                errors_message += f'Ошибка ввода в колонке {colname};\n'
        if errors_message:
            QMessageBox.warning(self, 'Warning!', errors_message)
        else:
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
            query = QSqlQuery(sql_query)
            if query.lastError().type() == QSqlError.ErrorType.NoError:
                print('Новая строка успешно добавлена в таблицу Gr_prog')
                self.parent.model.select()  # Update the source model
                new_row_data = column_values
                new_row_index_source = -1
                for row in range(self.parent.model.rowCount()):
                    row_data = {self.parent.model.headerData(col, Qt.Orientation.Horizontal): self.parent.model.data(
                        self.parent.model.index(row, col)) for col in range(self.parent.model.columnCount())}
                    row_data['Код конк.'] = str(row_data.get('Код конк.', ''))
                    new_row_data['Код конк.'] = str(new_row_data.get('Код конк.', ''))
                    row_data['Код НИР'] = str(row_data.get('Код НИР', ''))
                    new_row_data['Код НИР'] = str(new_row_data.get('Код НИР', ''))
                    if row_data.get('Код конк.') == new_row_data.get('Код конк.') and row_data.get(
                            'Код НИР') == new_row_data.get('Код НИР'):
                        new_row_index_source = row
                        break
                self.parent.customProxyModel.sort(0, Qt.SortOrder.AscendingOrder)
                self.parent.customProxyModel.sort(1, Qt.SortOrder.AscendingOrder)
                new_model_index_source = self.parent.model.index(new_row_index_source, 0)
                new_model_index_proxy = self.parent.customProxyModel.mapFromSource(new_model_index_source)
                self.parent.tableView.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
                self.parent.tableView.selectionModel().clearSelection()
                self.parent.tableView.selectionModel().setCurrentIndex(new_model_index_proxy,
                                                                       QItemSelectionModel.SelectionFlag.Select)
                self.parent.tableView.scrollTo(new_model_index_proxy)
                QMessageBox.information(self, "Успех", "Новая запись была успешно добавлена в таблицу")
                self.close()
            else:
                print('Ошибка при добавлении строки в таблицу Gr_prog:', query.lastError().text())
        except Exception as error:
            print("Ошибка при добавлении строки в таблицу Gr_prog:", error)

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
                'Наименование НИР': self.ui.textEdit_9.toPlainText()
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
