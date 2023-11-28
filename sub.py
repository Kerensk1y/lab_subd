import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QTableWidget, QTableWidgetItem
import sqlite3

class Analiz_sub(QMainWindow):
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

        central_widget.setLayout(layout)

        self.table_widget.setSortingEnabled(True)

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

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = Analiz_sub()
#     window.show()
#     sys.exit(app.exec())
