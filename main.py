import sys
import psutil
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QMessageBox, QCheckBox
import requests
from bs4 import BeautifulSoup

class WorkerThread(QtCore.QThread):
    result_signal = QtCore.pyqtSignal(str)

    def __init__(self, login, old_password, new_password, parent=None):
        super().__init__(parent)
        self.login = login
        self.old_password = old_password
        self.new_password = new_password

    def run(self):
        success = self.attempt_password_change_with_requests(self.login, self.old_password, self.new_password)
        if success:
            self.result_signal.emit("Пароль успешно изменён.")
        else:
            self.result_signal.emit("Ошибка при смене пароля. Попробуйте снова.")

    def attempt_password_change_with_requests(self, login, old_password, new_password):
        login_url = "https://change.snackprod.com/RDWeb/Pages/ua-UA/password.aspx"
        session = requests.Session()
        
        # Получаем страницу для входа
        response = session.get(login_url)
        if response.status_code != 200:
            print(f"Ошибка загрузки страницы: {response.status_code}")
            return False

        # Парсим HTML
        soup = BeautifulSoup(response.text, "lxml-xml")

        # Ищем необходимые формы
        form = soup.find("form", {"id": "FrmLogin"})
        inputs = form.find_all("input")
        form_data = {}

        # Собираем данные для отправки формы
        for input_tag in inputs:
            if input_tag.get("name") == "DomainUserName":
                form_data["DomainUserName"] = login
            elif input_tag.get("name") == "UserPass":
                form_data["UserPass"] = old_password
            elif input_tag.get("name") == "NewUserPass":
                form_data["NewUserPass"] = new_password
            elif input_tag.get("name") == "ConfirmNewUserPass":
                form_data["ConfirmNewUserPass"] = new_password

        # Отправляем запрос на смену пароля
        post_response = session.post(login_url, data=form_data)
        
        # Проверяем успешность смены пароля
        if "Ваш пароль успішно змінено" in post_response.text:
            return True
        elif "Введені паролі не збігаються" in post_response.text:
            print("Пароли не совпадают!")
        elif "Новий пароль не відповідає вимогам" in post_response.text:
            print("Новый пароль не соответствует требованиям!")
        else:
            print("Произошла ошибка при смене пароля.")
        return False

class Ui_ChangePass(object):
    def setupUi(self, ChangePass):
        ChangePass.setObjectName("ChangePass")
        ChangePass.resize(313, 500)
        ChangePass.setStyleSheet("""
        QMainWindow {
            background-color: #2e2e2e;
            border: none;
            border-radius: 20px;
        }
        QFrame#main_frame {
            background-color: #3e3e3e;
            border: 1px solid #0078d7;
            border-radius: 15px;
            padding: 10px;
        }
        QPushButton {
            background-color: #3b4260;
            color: white;
        }
        QPushButton:hover {
            background-color: #4c5470;
        }
        QLineEdit {
            background-color: #3b4260;
            color: white;
            border: 1px solid #4c5470;
            border-radius: 5px;
            padding: 8px;
        }
        QLabel {
            color: #d1d1e0;
            font-size: 14px;
        }
        """)

        self.centralwidget = QtWidgets.QWidget(ChangePass)
        self.centralwidget.setObjectName("centralwidget")

        self.input_login = QtWidgets.QLineEdit(self.centralwidget)
        self.input_login.setGeometry(QtCore.QRect(30, 20, 251, 41))
        self.input_login.setPlaceholderText("Логин")
        self.input_login.setObjectName("input_login")
        self.input_login.textChanged.connect(self.add_domain_prefix)

        self.input_old_password = QtWidgets.QLineEdit(self.centralwidget)
        self.input_old_password.setGeometry(QtCore.QRect(30, 80, 251, 41))
        self.input_old_password.setPlaceholderText("Старый пароль")
        self.input_old_password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.input_old_password.setObjectName("input_old_password")

        self.input_new_password = QtWidgets.QLineEdit(self.centralwidget)
        self.input_new_password.setGeometry(QtCore.QRect(30, 140, 251, 41))
        self.input_new_password.setPlaceholderText("Новый пароль")
        self.input_new_password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.input_new_password.setObjectName("input_new_password")

        self.input_confirm_password = QtWidgets.QLineEdit(self.centralwidget)
        self.input_confirm_password.setGeometry(QtCore.QRect(30, 200, 251, 41))
        self.input_confirm_password.setPlaceholderText("Подтверждение нового пароля")
        self.input_confirm_password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.input_confirm_password.setObjectName("input_confirm_password")

        self.show_passwords_checkbox = QCheckBox("Показать пароли", self.centralwidget)
        self.show_passwords_checkbox.setGeometry(QtCore.QRect(30, 250, 150, 30))
        self.show_passwords_checkbox.stateChanged.connect(self.toggle_all_passwords_visibility)

        self.history_button = QtWidgets.QPushButton("История паролей", self.centralwidget)
        self.history_button.setGeometry(QtCore.QRect(80, 290, 151, 41))
        self.history_button.clicked.connect(self.show_password_history)

        self.submit_button = QtWidgets.QPushButton("Изменить пароль", self.centralwidget)
        self.submit_button.setGeometry(QtCore.QRect(80, 340, 151, 41))
        self.submit_button.clicked.connect(self.change_password)

        self.cancel_button = QtWidgets.QPushButton("Отмена", self.centralwidget)
        self.cancel_button.setGeometry(QtCore.QRect(80, 390, 151, 41))
        self.cancel_button.clicked.connect(ChangePass.close)

        ChangePass.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(ChangePass)
        ChangePass.setStatusBar(self.statusbar)

        self.previous_passwords = []
        self.check_system_resources()

    def show_password_history(self):
        history_str = "\n".join(self.previous_passwords) if self.previous_passwords else "История пуста."
        self.show_message(f"История паролей:\n{history_str}")

    def change_password(self):
        login = self.input_login.text()
        old_password = self.input_old_password.text()
        new_password = self.input_new_password.text()
        confirm_password = self.input_confirm_password.text()

        if self.validate_new_password(new_password, confirm_password):
            if new_password in self.previous_passwords:
                self.show_message("Пароль уже использовался ранее. Пожалуйста, выберите другой.")
            else:
                self.worker = WorkerThread(login, old_password, new_password)
                self.worker.result_signal.connect(self.show_message)
                self.worker.start()
                self.previous_passwords.append(new_password)

    def validate_new_password(self, new_password, confirm_password):
        if new_password != confirm_password:
            self.show_message("Пароли не совпадают.")
            return False
        if len(new_password) < 8:
            self.show_message("Пароль слишком короткий. Минимальная длина - 8 символов.")
            return False
        return True

    def show_message(self, message):
        QMessageBox.information(self.centralwidget, "Результат", message)

    def add_domain_prefix(self):
        text = self.input_login.text()
        if not text.startswith("sp\\"):
            self.input_login.setText("sp\\" + text)

    def toggle_all_passwords_visibility(self):
        password_mode = not self.show_passwords_checkbox.isChecked()
        mode = QtWidgets.QLineEdit.EchoMode.Normal if not password_mode else QtWidgets.QLineEdit.EchoMode.Password
        self.input_old_password.setEchoMode(mode)
        self.input_new_password.setEchoMode(mode)
        self.input_confirm_password.setEchoMode(mode)

    def check_system_resources(self):
        memory_usage = psutil.virtual_memory().percent
        if memory_usage > 85:
            self.show_message("Предупреждение: Высокое использование памяти.")
        cpu_usage = psutil.cpu_percent(interval=1)
        if cpu_usage > 85:
            self.show_message("Предупреждение: Высокая загрузка процессора.")

def main():
    app = QtWidgets.QApplication(sys.argv)
    ChangePass = QtWidgets.QMainWindow()
    ui = Ui_ChangePass()
    ui.setupUi(ChangePass)
    ChangePass.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
