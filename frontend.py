import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
import translator
from syntax_highlighter import SyntaxHighlighter  # ДОБАВЛЕН ИМПОРТ

# Настройка внешнего вида customtkinter
ctk.set_appearance_mode("dark")  # Темная тема
ctk.set_default_color_theme("blue")  # Синяя цветовая схема

# Инициализация подсветки синтаксиса
syntax_highlighter = SyntaxHighlighter()

def update_line_numbers(event=None):
    """Обновление номеров строк для обоих текстовых полей."""
    lines = source_text.get("1.0", tk.END).splitlines()
    source_lines_text.config(state=tk.NORMAL)
    source_lines_text.delete("1.0", tk.END)
    for i in range(1, len(lines) + 1):
        source_lines_text.insert(tk.END, f"{i:3d} \n")
    source_lines_text.config(state=tk.DISABLED)
    
    lines = target_text.get("1.0", tk.END).splitlines()
    target_lines_text.config(state=tk.NORMAL)
    target_lines_text.delete("1.0", tk.END)
    for i in range(1, len(lines) + 1):
        target_lines_text.insert(tk.END, f"{i:3d} \n")
    target_lines_text.config(state=tk.DISABLED)

def on_source_change(event=None):
    """Проверка изменения в исходном коде."""
    update_line_numbers()
    # Автоматическая подсветка синтаксиса C++
    syntax_highlighter.highlight_cpp(source_text)

def on_target_change(event=None):
    """Автоматическая подсветка синтаксиса Python для целевого кода."""
    syntax_highlighter.highlight_python(target_text)

def translate_code():
    """Вызов функции перевода из backend."""
    source_code = source_text.get("1.0", tk.END).strip()
    translated, message = translator.translate_code(source_code)
    if translated:
        target_text.config(state=tk.NORMAL)
        target_text.delete("1.0", tk.END)
        target_text.insert(tk.END, translated)
        target_text.config(state=tk.DISABLED)
        # Подсветка синтаксиса Python после перевода
        on_target_change()
    update_line_numbers()
    log_message(message)

def clear_all():
    """Очистка обоих окон через backend."""
    source_text.delete("1.0", tk.END)
    target_text.config(state=tk.NORMAL)
    target_text.delete("1.0", tk.END)
    target_text.config(state=tk.DISABLED)
    update_line_numbers()
    log_message(translator.clear_all())
    # Очищаем подсветку
    for tag in source_text.tag_names():
        source_text.tag_delete(tag)
    for tag in target_text.tag_names():
        target_text.tag_delete(tag)

def log_message(message):
    """Вывод сообщения в лог с перезаписью."""
    log_text.config(state=tk.NORMAL)
    log_text.delete("1.0", tk.END)
    log_text.insert("1.0", message + "\n")
    log_text.config(state=tk.DISABLED)
    log_text.see(tk.END)

def show_context_menu(event):
    """Показать контекстное меню для копирования в правом окне."""
    context_menu.tk_popup(event.x_root, event.y_root)


def run_app():
    """Функция для запуска приложения из main.py"""
    root.mainloop()



# Создание главного окна
root = ctk.CTk()
root.title("Транслятор C++ в Python")

root.geometry(f"1920x1080+0+0")

root.resizable(False, False)


# Основной контейнер
main_container = ctk.CTkFrame(root, corner_radius=10)
main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

# Заголовок
header_frame = ctk.CTkFrame(main_container, fg_color="transparent", height=50)
header_frame.pack(fill=tk.X, padx=20, pady=(5, 5))

title_label = ctk.CTkLabel(header_frame, 
                          text="Транслятор C++ → Python", 
                          font=ctk.CTkFont(size=22, weight="bold"))
title_label.pack(side=tk.LEFT, pady=5)

# Фрейм для двух панелей кода - УМЕНЬШЕНА ВЫСОТА
panels_frame = ctk.CTkFrame(main_container, fg_color="transparent")
panels_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)  # Уменьшены отступы

# Левая панель: Исходный код (C++)
source_panel = ctk.CTkFrame(panels_frame, corner_radius=8)
source_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

# Заголовок панели исходного кода
source_header = ctk.CTkFrame(source_panel, fg_color="#2b5278", corner_radius=8)
source_header.pack(fill=tk.X, padx=5, pady=(5, 0))

source_label = ctk.CTkLabel(source_header, 
                           text="Исходный код (C++)", 
                           font=ctk.CTkFont(size=14, weight="bold"),
                           text_color="white")
source_label.pack(pady=6)  # Уменьшены отступы

# Контейнер для текстового поля и номеров строк
source_content = ctk.CTkFrame(source_panel, fg_color="transparent")
source_content.pack(fill=tk.BOTH, expand=True, padx=5, pady=3)  # Уменьшены отступы

# Номера строк для исходника - УМЕНЬШЕНА ВЫСОТА
source_lines_text = tk.Text(source_content, width=5, height=20, state=tk.DISABLED, 
                           bg="#1e2a44", fg="#8f9bb3", font=("Consolas", 13), 
                           bd=0, relief=tk.FLAT, padx=8, pady=6)
source_lines_text.pack(side=tk.LEFT, fill=tk.Y)

# Текстовое поле для исходника - УМЕНЬШЕНА ВЫСОТА
source_text = tk.Text(source_content, height=20, wrap=tk.NONE, 
                     bg="#1f2937", fg="#e5e7eb", font=("Consolas", 13),
                     insertbackground="#60a5fa", bd=0, relief=tk.FLAT,
                     selectbackground="#3b82f6", selectforeground="white",
                     padx=12, pady=6,
                     tabs=('1c'))  # Уменьшены отступы
source_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
source_text.bind("<KeyRelease>", on_source_change)
source_text.bind("<Key>", update_line_numbers)

# Добавляем скроллбар для исходного кода
source_scrollbar = ctk.CTkScrollbar(source_content, command=source_text.yview)
source_text.config(yscrollcommand=source_scrollbar.set)
source_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Правая панель: Переведённый код (Python)
target_panel = ctk.CTkFrame(panels_frame, corner_radius=8)
target_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

# Заголовок панели переведенного кода
target_header = ctk.CTkFrame(target_panel, fg_color="#0f766e", corner_radius=8)
target_header.pack(fill=tk.X, padx=5, pady=(5, 0))

target_label = ctk.CTkLabel(target_header, 
                           text="Переведённый код (Python)", 
                           font=ctk.CTkFont(size=14, weight="bold"),
                           text_color="white")
target_label.pack(pady=6)  # Уменьшены отступы

# Контейнер для текстового поля и номеров строк
target_content = ctk.CTkFrame(target_panel, fg_color="transparent")
target_content.pack(fill=tk.BOTH, expand=True, padx=5, pady=3)  # Уменьшены отступы

# Номера строк для целевого - УМЕНЬШЕНА ВЫСОТА
target_lines_text = tk.Text(target_content, width=5, height=20, state=tk.DISABLED,
                           bg="#1e2a44", fg="#8f9bb3", font=("Consolas", 13),
                           bd=0, relief=tk.FLAT, padx=8, pady=6)
target_lines_text.pack(side=tk.LEFT, fill=tk.Y)

# Текстовое поле для целевого - УМЕНЬШЕНА ВЫСОТА
target_text = tk.Text(target_content, height=20, wrap=tk.NONE, state=tk.DISABLED,
                     bg="#1f2937", fg="#e5e7eb", font=("Consolas", 13),
                     insertbackground="#60a5fa", bd=0, relief=tk.FLAT,
                     selectbackground="#3b82f6", selectforeground="white",
                     padx=12, pady=6)  # Уменьшены отступы
target_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Добавляем скроллбар для целевого кода
target_scrollbar = ctk.CTkScrollbar(target_content, command=target_text.yview)
target_text.config(yscrollcommand=target_scrollbar.set)
target_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Контекстное меню для правого окна
context_menu = tk.Menu(root, tearoff=0, bg="#374151", fg="#e5e7eb", 
                      activebackground="#3b82f6", activeforeground="white",
                      font=("Segoe UI", 10))
context_menu.add_command(label="Копировать", command=lambda: target_text.event_generate("<<Copy>>"))
target_text.bind("<Button-3>", show_context_menu)

# Синхронизация скролла номеров строк
def sync_line_numbers(*args):
    source_lines_text.yview_moveto(args[0])
    target_lines_text.yview_moveto(args[0])

source_text.bind("<MouseWheel>", lambda e: sync_line_numbers(source_text.yview()[0]))
target_text.bind("<MouseWheel>", lambda e: sync_line_numbers(target_text.yview()[0]))

# Фрейм для кнопок - ПОДНЯТ ВЫШЕ
buttons_frame = ctk.CTkFrame(main_container, fg_color="transparent", height=50)
buttons_frame.pack(fill=tk.X, padx=20, pady=8)  # Уменьшены отступы

# Кнопка "Перевести"
play_button = ctk.CTkButton(buttons_frame, 
                           text="▶ Перевести", 
                           command=translate_code,
                           font=ctk.CTkFont(size=14, weight="bold"),
                           height=35,  # Уменьшена высота
                           fg_color="#0ea5e9",
                           hover_color="#0284c7")
play_button.pack(side=tk.LEFT, padx=8)

# Кнопка "Очистить"
clear_button = ctk.CTkButton(buttons_frame, 
                            text="🗑️ Очистить", 
                            command=clear_all,
                            font=ctk.CTkFont(size=14, weight="bold"),
                            height=35,  # Уменьшена высота
                            fg_color="#ef4444",
                            hover_color="#dc2626")
clear_button.pack(side=tk.LEFT, padx=8)

# Нижнее окошко для логов - ПОДНЯТО ВЫШЕ И УВЕЛИЧЕНО
log_frame = ctk.CTkFrame(main_container, corner_radius=8)
log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(5, 15))  # Убрано expand=False

# Заголовок логов
log_header = ctk.CTkFrame(log_frame, fg_color="#374151", corner_radius=8)
log_header.pack(fill=tk.X, padx=5, pady=(5, 0))

log_label = ctk.CTkLabel(log_header, 
                        text="Системные сообщения", 
                        font=ctk.CTkFont(size=12, weight="bold"),
                        text_color="white")
log_label.pack(pady=5)

# Контейнер для текста лога и скроллбара
log_content = ctk.CTkFrame(log_frame, fg_color="transparent")
log_content.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

# Текст лога - УВЕЛИЧЕНА ВЫСОТА
log_text = tk.Text(log_content, height=8, state=tk.DISABLED,  # Увеличена высота
                  bg="#1f2937", fg="#10b981", font=("Consolas", 12),
                  bd=0, relief=tk.FLAT, padx=12, pady=8,
                  wrap=tk.WORD)
log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Добавляем скроллбар для логов
log_scrollbar = ctk.CTkScrollbar(log_content, command=log_text.yview)
log_text.config(yscrollcommand=log_scrollbar.set)
log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Инициализация
update_line_numbers()
log_message("Программа готова. Вставьте код в левое окно.")

