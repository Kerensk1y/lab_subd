from PyQt6.QtWidgets import QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QLabel, QPushButton, QComboBox, QMessageBox
import sqlite3

class Filtrate(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Фильтр по коду конкурса и субъекту РФ")
        self.setGeometry(100, 100, 800, 600)

        # Создание виджета и таблицы
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()

        # Добавление комбобоксов для выбора значений полей
        self.comboBox_code = QComboBox(self)
        self.comboBox_subject = QComboBox(self)

        # Добавление комбобоксов в список для последующего обновления значений
        self.comboboxes = [self.comboBox_code, self.comboBox_subject]

        # Добавление пустых значений по умолчанию
        for combobox in self.comboboxes:
            combobox.addItem("")

        self.layout.addWidget(QLabel("Выберите код конкурса:"))
        self.layout.addWidget(self.comboBox_code)

        self.layout.addWidget(QLabel("Выберите субъект РФ:"))
        self.layout.addWidget(self.comboBox_subject)

        self.filter_button = QPushButton("Применить фильтр")
        self.reset_button = QPushButton("Сбросить фильтр")

        self.filter_button.clicked.connect(self.apply_filter)
        self.reset_button.clicked.connect(self.reset_filter)

        self.layout.addWidget(self.filter_button)
        self.layout.addWidget(self.reset_button)

        # Таблица для отображения данных
        self.table = QTableWidget(self)
        self.layout.addWidget(self.table)

        self.central_widget.setLayout(self.layout)

        # Подключение к базе данных
        self.conn = sqlite3.connect("MyDB.db")
        self.cursor = self.conn.cursor()

        # Загрузка данных из базы данных в таблицу и в комбобоксы
        self.load_data()
        self.load_combobox_values()

    def load_data(self):
        # Выполнение JOIN-запроса к базе данных
        query = """SELECT Gr_prog.*, VUZ."Субъект РФ"
                           FROM Gr_prog
                           LEFT JOIN VUZ ON Gr_prog."Сокр-е наим-е ВУЗа" = VUZ."Сокр. наим-е ВУЗа" """
        self.cursor.execute(query)
        data = self.cursor.fetchall()

        # Установка числа строк и столбцов в таблице
        self.table.setRowCount(len(data))
        self.table.setColumnCount(len(data[0]))

        # Заполнение таблицы данными
        for row_num, row_data in enumerate(data):
            for col_num, col_data in enumerate(row_data):
                item = QTableWidgetItem(str(col_data))
                self.table.setItem(row_num, col_num, item)

    def load_combobox_values(self):
        # Получение уникальных значений для заполнения комбобоксов
        query_code = "SELECT DISTINCT \"Код конк.\" FROM Gr_prog"
        query_subject = "SELECT DISTINCT VUZ.\"Субъект РФ\" FROM VUZ"

        self.cursor.execute(query_code)
        code_values = [str(item[0]) for item in self.cursor.fetchall()]

        self.cursor.execute(query_subject)
        subject_values = [str(item[0]) for item in self.cursor.fetchall()]

        # Очистка комбобоксов перед обновлением
        for combobox in self.comboboxes:
            combobox.clear()
            combobox.addItem("")  # Добавление пустого значения

        # Заполнение комбобоксов уникальными значениями
        for value in code_values:
            self.comboBox_code.addItem(value)

        for value in subject_values:
            self.comboBox_subject.addItem(value)

    def apply_filter(self):
        # Получение текста из комбобоксов
        filter_code_value = self.comboBox_code.currentText()
        filter_subject_value = self.comboBox_subject.currentText()

        # Формирование фильтрации по коду конкурса и субъекту РФ
        filter_query = "SELECT Gr_prog.*, VUZ.\"Субъект РФ\" FROM Gr_prog LEFT JOIN VUZ ON Gr_prog.\"Сокр-е наим-е ВУЗа\" = VUZ.\"Сокр. наим-е ВУЗа\" WHERE 1"

        if filter_code_value:
            filter_query += f" AND \"Код конк.\" = {filter_code_value}"

        if filter_subject_value:
            filter_query += f" AND VUZ.\"Субъект РФ\" = '{filter_subject_value}'"

        self.cursor.execute(filter_query)
        data = self.cursor.fetchall()

        # Показывать предупреждение, если ничего не было найдено
        if not data:
            QMessageBox.warning(self, "Предупреждение", "Ничего не найдено.")
            return

        # Очистка таблицы перед обновлением
        self.table.clear()

        # Установка числа строк и столбцов в таблице
        self.table.setRowCount(len(data))
        self.table.setColumnCount(len(data[0]))

        # Заполнение таблицы данными
        for row_num, row_data in enumerate(data):
            for col_num, col_data in enumerate(row_data):
                item = QTableWidgetItem(str(col_data))
                self.table.setItem(row_num, col_num, item)

    def reset_filter(self):
        # Очистка комбобоксов и обновление данных без фильтра
        for combobox in self.comboboxes:
            combobox.setCurrentIndex(0)  # Установка индекса на пустое значение

        self.load_data()