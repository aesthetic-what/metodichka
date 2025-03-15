from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
from ui.form import Ui_FormWindow
from ui.main import Ui_MainWindow
from PyQt5 import uic
import pyodbc
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        con_str = f"DRIVER={{SQL Server}};SERVER=KLABSQLW19S1,49172;Trusted_Connection=yes;user=22200322; Database=db_metodichka;"
        connect = pyodbc.connect(con_str)
        self.cursor = connect.cursor()
        
        self.cur_page = 1
        self.num_page_elem = 0
        self.data_db = [[], []]
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # uic.loadUi("ui/main.ui", self)
        self.setWindowTitle("Меню")
        self.setWindowIcon(QIcon("ui/resourses/Мастер пол.ico"))
        
        self.get_data_from_table()
        self.connect_widgets()
        self.draw_frames()
        
        self.ui.scrollAreaList.setStyleSheet("""
            QListWidget::item {
                border: 1px solid rgb(0,0,0);
                margin: 15px;
                padding: 20px;
            }

            QListWidget::item:selected {
                background-color: #F4E8D3;
                color: rgb(0,0,0);
            }
            """)
        # for i in range(self.scrollAreaList.count()):
        #     item = self.scrollAreaList.item(i)
        #     item.setSizeHint(QSize(200, 50))  # Устанавливаем размер для каждого элемента
        
    def connect_widgets(self):
        self.ui.button_add.clicked.connect(lambda: self.call_form('add'))
        self.ui.button_del.clicked.connect(lambda: self.call_form('del'))
        self.ui.button_back.clicked.connect(lambda: self.browsing('back'))
        self.ui.button_next.clicked.connect(lambda: self.browsing('next'))
        self.ui.scrollAreaList.itemDoubleClicked.connect(lambda: self.call_form('edit'))
        
    def get_data_from_table(self):
        try:
            with self.cursor as session:
                self.data_db = session.execute("select * from Partners").fetchall()
                # print(self.data_db)
            return self.data_db
                
        except pyodbc.Error as ex:
            print(ex.args[1])
            
            
    def draw_frames(self):
        self.ui.scrollAreaList.clear()  # Очищаем список в scrollArea

        # Предполагаем, что self.data_db возвращает список элементов
        for item_list in self.data_db[self.cur_page:self.num_page_elem + 4]:
            # Формируем строку для отображения
            item_text = f"{item_list[1]} | {item_list[2]} | {item_list[3]} | {item_list[4]} | {item_list[5]} | {item_list[7]} | Рейтинг: {item_list[14]}"
            
            # Добавляем сформированную строку в scrollArealist
            self.ui.scrollAreaList.addItem(item_text)
            # print(item_list)
    
    def browsing(self, func):
        if func == 'next' and self.num_page_elem + 1 < len(self.data_db):
            self.cur_page += 1
            self.num_page_elem += 4

        elif func == 'back' and self.num_page_elem > 1:
            self.cur_page -= 1
            self.num_page_elem -= 4
            
        self.ui.label.setText(f'Страница {self.cur_page}')
        self.draw_frames()
        
        
    def showData(self):
        self.get_data_from_table()
        self.draw_frames()
        
    def call_form(self, func: str):
        data_row = self.data_db[self.ui.scrollAreaList.currentIndex().row() + self.num_page_elem] if self.ui.scrollAreaList.currentIndex().row() != -1 else []
            
        # print(data_row)
        
        self.form = Form(self, func, data_row)
        self.form.show()
        
class Form(QMainWindow):
    def __init__(self, link_basewindow, func, data_row):
        super().__init__()
        # uic.loadUi("ui/form.ui", self)
        self.ui = Ui_FormWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Форма")
        self.windowModality()
        self.setWindowIcon(QIcon("ui/resourses/Мастер пол.ico"))
        self.data_db = [[], []]
        
        conn_str = f"DRIVER={{SQL Server}};SERVER=KLABSQLW19S1,49172;Trusted_Connection=yes;user=22200322; Database=db_metodichka;"
        connect = pyodbc.connect(conn_str)
        self.cursor = connect.cursor()
        
        self.func = func
        self.data_row = data_row
        self.link_basewindow = link_basewindow
        
        self.changing_lines_edit() if self.func != 'add' else None
        self.connect_widget()
        
    def connect_widget(self):
        button_text = {
            'add': lambda: self.ui.pushButton.setText('Добавить'),
            'edit': lambda: self.ui.pushButton.setText('Изменить'),
            'del': lambda: self.ui.pushButton.setText('Удалить')
        }
        button_text[self.func]()
        self.ui.pushButton.clicked.connect(self.execution_operation)
        
    def execution_operation(self):
        operations = {
            'add': lambda: self.request(self.create_query_add()),
            'edit': lambda: self.request(self.create_query_edit()),
            'del': lambda: self.request(self.create_query_delete())
        }
        operations[self.func]()
        self.close()
        
    def request(self, query):
        try:
            with self.cursor as conn:
                conn.execute(query)
                conn.commit()
        except pyodbc.Error as ex:
            print(ex.args[1])
            
    def get_input_data(self):
        list_data = []
        for i in range(8):
            text = self.ui.text_layout.itemAt(i).widget().text() if i != 1 else\
            self.ui.text_layout.itemAt(i).widget().currentText()
            text = text.split(' ') if i in [3, 4] else text
            print(text)

            if type(text) == list:
                for item in text:
                    print(item)
                    list_data.append(item)
            else:
                list_data.append(text)

        return list_data
    
    def create_query_add(self):
        input_data = self.get_input_data()
        return f"insert into Partners(type, name_partners, first_name_director, last_name_director, " + \
                f"surname_director, email, number_phone, postal_code, region, city, street, " + \
                f"number_home, tin, rating) values ('{input_data[1]}, '{input_data[0]}," + \
                f"'{input_data[9]},','{input_data[8]},','{input_data[10]},','{input_data[12]},','{input_data[11]}," + \
                f"'{input_data[3]},','{input_data[4]},','{input_data[5]},','{input_data[6]},','{input_data[7]}," + \
                f"'{input_data[13]},','{input_data[2]},"
    
    def create_query_edit(self):
        input_data = self.get_input_data()
        input_data = [item if item.isdigit() else f"'{item}'" for item in input_data]
        return f'update Partners set type={input_data[1]}, name_partners={input_data[0]}, first_name_director={input_data[9]},' + \
                f'last_name_director={input_data[8]}, surname_director={input_data[10]}, email={input_data[12]}, ' + \
                f'number_phone={input_data[11]}, postal_code={input_data[3]}, region={input_data[4]}, city={input_data[5]}, ' + \
                f'street={input_data[6]}, number_home={input_data[7]}, tin={input_data[13]}, rating={input_data[2]} where id = {self.data_row[0]}'
    
    def create_query_delete(self):
        return f"delete from Partners where id = {self.data_row[0]}"
    
    def changing_lines_edit(self):
        connect_widget_with_data_row = {
            0: f'{self.data_row[2]}',
            1: f'{self.data_row[1]}',
            2: f'{self.data_row[14]}',
            3: f'{self.data_row[8]} {self.data_row[9]} {self.data_row[10]} {self.data_row[11]} {self.data_row[12]}',
            4: f'{self.data_row[3]} {self.data_row[4]} {self.data_row[5]}',
            5: f'{self.data_row[7]}',
            6: f'{self.data_row[6]}',
            7: f'{self.data_row[13]}',
        }
        
        # print(self.text_layout.count())
        
        
        for i in range(8):
            self.ui.text_layout.itemAt(i).widget().setText(connect_widget_with_data_row[i]) if i != 1 else \
                self.ui.text_layout.itemAt(i).widget().setCurrentText(connect_widget_with_data_row[i])
            self.ui.text_layout.itemAt(i).widget().setEnabled(False) if self.func == 'del' else None
        
    def closeEvent(self, event) -> None:
        self.link_basewindow.showData()
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())