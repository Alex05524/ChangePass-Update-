from cx_Freeze import setup, Executable
import os
import PyQt6.QtCore

# Получение путей к плагинам Qt и QML (в PyQt6 используется другое API)
qt_plugins_path = os.path.join(os.path.dirname(PyQt6.__file__), 'Qt6', 'plugins')
qml_imports_path = os.path.join(os.path.dirname(PyQt6.__file__), 'Qt6', 'qml')

# Проверяем, что эти директории существуют, чтобы избежать ошибок при сборке
if not os.path.exists(qml_imports_path):
    raise FileNotFoundError(f"QML path not found: {qml_imports_path}")
if not os.path.exists(qt_plugins_path):
    raise FileNotFoundError(f"Qt plugins path not found: {qt_plugins_path}")

# Определение файлов и папок для включения в сборку
include_files = [
    'main.py',  # Основной скрипт
    (qml_imports_path, 'qml'),  # Включение пути к QML2 библиотекам
    (qt_plugins_path, 'qt/plugins')  # Включение пути к плагинам Qt
]

# Опции сборки
build_exe_options = {
    'packages': ['os', 're', 'platform', 'PyQt6'],  # Необходимые пакеты
    'excludes': ['tkinter', 'PyQt6.QtQml', 'PyQt6.QtQuick'],  # Исключение ненужных пакетов
    'include_files': include_files,  # Включенные дополнительные файлы и папки
    'optimize': 2  # Оптимизация кода
}

# Определение исполняемого файла
executables = [
    Executable(
        script='main.py',  # Основной скрипт приложения
        base='Win32GUI' if os.name == 'nt' else None,  # Использование 'Win32GUI' для оконных приложений на Windows
        target_name='ChangePass.exe',  # Имя создаваемого исполняемого файла
    )
]

# Настройка сборки
setup(
    name='ChangePass',
    version='1.0',
    description='Приложение для смены пароля',
    options={'build_exe': build_exe_options},
    executables=executables
)

# Вывод информации о текущей директории и файлах в ней
print("Current directory:", os.getcwd())
print("Files in current directory:", os.listdir(os.getcwd()))
