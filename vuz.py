import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QTableWidget, QTableWidgetItem, QLineEdit
import sqlite3

class Analiz_vuz(QMainWindow):
    def __init__(self):
        super().__init__()

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

        self.filter_line_edit = QLineEdit()
        self.filter_line_edit.setPlaceholderText("Фильтр по ВУЗу")
        layout.addWidget(self.filter_line_edit)

        filter_button = QPushButton("Применить фильтр")
        filter_button.clicked.connect(self.update_table)
        layout.addWidget(filter_button)

        central_widget.setLayout(layout)

        self.table_widget.setSortingEnabled(True)

    def update_table(self):
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




        # Get the filter text
        filter_text = self.filter_line_edit.text()

        # Modify the SQL query with a WHERE clause based on the filter text
        sql_query = f"""
        SELECT
            "Сокр-е наим-е ВУЗа" AS "ВУЗ",
            COUNT(*) AS "Кол-во НИР",
            SUM("План. объём финанс-я") AS "Сум. объём финанс-я",
            COUNT(DISTINCT "Код конк.") AS "Кол-во конк."
        FROM "Gr_prog"
        {'WHERE "Сокр-е наим-е ВУЗа" LIKE ?' if filter_text else ''}
        GROUP BY "Сокр-е наим-е ВУЗа"
        ORDER BY "Сокр-е наим-е ВУЗа" ASC;
        """

        # Modify the execute method to include the filter text parameter
        cursor.execute(sql_query, (f'%{filter_text}%',) if filter_text else ())
        result = cursor.fetchall()

        # Заполнение таблицы результатами запроса
        for row_num, row_data in enumerate(result):
            self.table_widget.insertRow(row_num)
            for col_num, col_data in enumerate(row_data):
                item = QTableWidgetItem(str(col_data))
                self.table_widget.setItem(row_num, col_num, item)

#
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = Analiz_vuz()
#     window.show()
#     sys.exit(app.exec())
