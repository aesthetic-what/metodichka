from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
from PyQt5 import uic
from ui.main import Ui_MainWindow
from ui.form import Ui_FormWindow
import pyodbc
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        con_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER=KLABSQLW19S1,49172;Trusted_Connection=yes;user=22200322; Database=db_metodichka;"
        connect = pyodbc.connect(con_str)
        self.cur_page = 1
        self.num_page_elem = 1
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Меню")
        self.setWindowIcon(QIcon("ui/resourses/Мастер пол.ico"))
        self.cursor = connect.cursor()
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
        # for i in range(self.ui.scrollAreaList.count()):
        #     item = self.ui.scrollAreaList.item(i)
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
        
        
    def showData(self):
        self.get_data_from_table()
        self.draw_frames()
        
    def call_form(self, func: str):
        data_row = self.data_db[self.ui.scrollAreaList.currentIndex().row() + self.num_page_elem] if self.ui.scrollAreaList.currentIndex().row() != -1 else []\
            
        # print(data_row)
        
        self.form = Form(self, func, data_row)
        self.form.show()
        
class Form(QMainWindow):
    def __init__(self, link_basewindow, func, data_row):
        super().__init__()
        self.ui = Ui_FormWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Форма")
        self.windowModality()
        self.setWindowIcon(QIcon("ui/resourses/Мастер пол.ico"))
        
        conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER=KLABSQLW19S1,49172;Trusted_Connection=yes;user=22200322; Database=db_metodichka;"
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
            'delete': lambda: self.ui.pushButton.setText('Удалить')
        }
        button_text[self.func]()
        self.ui.pushButton.clicked.connect(self.execution_operation)
        
    def execution_operation(self):
        operations = {
            'add': lambda: self.request(self.create_query_add()),
            'edit': lambda: self.request(self.create_query_edit()),
            'delete': lambda: self.request(self.create_query_delete())
        }
        operations[self.func]()
        self.close()
        
    def request(self):
        pass
    
    def create_query_add(self):
        pass
    
    def create_query_edit(self):
        pass
    
    def create_query_delete(self):
        pass
    
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
        
        print(self.ui.verticalLayout_2.count())
        
        
        for i in range(8):
            # item = self.ui.verticalLayout_2.itemAt(i)
            # if item is not None:
            #     widget = item.widget()
            #     if widget is not None:
            #         widget.setText(connect_widget_with_data_row[i])
            #     else:
            #         print(f"На позиции {i} отсутствует виджет.")
            # else:
            #     print(f"В `verticalLayout_2` нет элемента на позиции {i}.")
            self.ui.verticalLayout_2.itemAt(i).widget().setText(connect_widget_with_data_row[i])
            if i == 1:
                continue
            else:
                self.ui.verticalLayout_2.itemAt(i).widget().setCurrentText(connect_widget_with_data_row[i])
            
            self.ui.label.itemAt(i).widget().setEnabled(False) if self.func == 'delete' else None

    def browsing(self, func):
        if func == 'next' and self.number_page_elements < len(self.data_db):
            self.current_number_page += 1
            self.number_page_elements += 4

        elif func == 'back' and self.number_page_elements > 1:
            self.current_number_page -= 1
            self.number_page_elements -= 4
            
        self.label_name_page.setText(f'Страница {self.current_number_page}')
        self.draw_frames()
        
    def closeEvent(self, event) -> None:
        self.link_basewindow.showData()
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())