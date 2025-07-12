# Audibo Challenge Response Generator v2.2 (仅记录challenge日志版)
import binascii
import random
import string
import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_pem_private_key
import pyperclip
import webbrowser
from datetime import datetime
import json
import hashlib

class AudiboGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.language = "en"  # 默认语言
        self.version = "2.2"  # 版本号
        self.log_file = "audibo_challenges.json"  # 日志文件名
        self.private_key = None
        self.key_file_path = None
        self.challenge_log = []  # 只记录challenge的日志
        
        # 初始化翻译
        self.translations = {
            "en": {
                "title": f"Audibo Challenge Response Generator v{self.version}",
                "file_menu": "File",
                "load_key": "Load Private Key",
                "exit": "Exit",
                "help_menu": "Help",
                "documentation": "Documentation",
                "about": "About",
                "language_menu": "Language",
                "english": "English",
                "chinese": "Chinese",
                "german": "German",
                "russian": "Russian",
                "key_info": "Private Key Information",
                "no_key_loaded": "No private key loaded",
                "key_path": "Key path: {}",
                "challenge_label": "Challenge:",
                "generate_btn": "Generate Response",
                "copy_btn": "Copy to Clipboard",
                "clear_btn": "Clear",
                "view_log_btn": "View Challenges",
                "response_label": "Response",
                "status_ready": "Ready",
                "key_load_success": "Private key loaded successfully",
                "key_load_failed": "Private key load failed",
                "key_loaded_from": "Private key loaded from {}",
                "key_load_error": "Error loading private key",
                "empty_challenge": "Challenge cannot be empty",
                "no_key_error": "Private key not loaded",
                "response_generated": "Response generated successfully",
                "response_copied": "Response copied to clipboard",
                "no_response": "No response to copy",
                "fields_cleared": "Fields cleared",
                "log_cleared": "Challenge log cleared",
                "about_title": f"Audibo Challenge Response Generator v{self.version}",
                "about_text": f"""A secure tool for generating signed responses to Audibo challenges.

Version: {self.version}
Features:
- Load private keys from any location
- Copy to clipboard functionality
- Multi-language support (EN/CN/DE/RU)
- Challenge history logging

© 2023 Audibo""",
                "invalid_format": "Invalid challenge format - expected 4 segments separated by 0A",
                "error": "Error",
                "warning": "Warning",
                "failed_to_process": "Failed to process challenge"
            },
            "zh": {
                "title": f"Audibo挑战响应生成器 v{self.version}",
                "file_menu": "文件",
                "load_key": "加载私钥",
                "exit": "退出",
                "help_menu": "帮助",
                "documentation": "文档",
                "about": "关于",
                "language_menu": "语言",
                "english": "英文",
                "chinese": "中文",
                "german": "德文",
                "russian": "俄文",
                "key_info": "私钥信息",
                "no_key_loaded": "未加载私钥",
                "key_path": "密钥路径: {}",
                "challenge_label": "挑战码:",
                "generate_btn": "生成响应",
                "copy_btn": "复制到剪贴板",
                "clear_btn": "清除",
                "view_log_btn": "查看挑战记录",
                "response_label": "响应",
                "status_ready": "准备就绪",
                "key_load_success": "私钥加载成功",
                "key_load_failed": "私钥加载失败",
                "key_loaded_from": "私钥已从 {} 加载",
                "key_load_error": "加载私钥出错",
                "empty_challenge": "挑战码不能为空",
                "no_key_error": "未加载私钥",
                "response_generated": "响应生成成功",
                "response_copied": "响应已复制到剪贴板",
                "no_response": "没有可复制的响应",
                "fields_cleared": "已清除所有字段",
                "log_cleared": "挑战记录已清除",
                "about_title": f"Audibo挑战响应生成器 v{self.version}",
                "about_text": f"""用于生成Audibo挑战签名的安全工具

版本: {self.version}
功能:
- 从任意位置加载私钥
- 复制到剪贴板功能
- 多语言支持(英文/中文/德文/俄文)
- 挑战记录保存

© 2023 Audibo""",
                "invalid_format": "无效的挑战格式 - 需要4个由0A分隔的部分",
                "error": "错误",
                "warning": "警告",
                "failed_to_process": "处理挑战失败"
            },
            "de": {
                "title": f"Audibo Challenge Response Generator v{self.version}",
                "file_menu": "Datei",
                "load_key": "Privaten Schlüssel laden",
                "exit": "Beenden",
                "help_menu": "Hilfe",
                "documentation": "Dokumentation",
                "about": "Über",
                "language_menu": "Sprache",
                "english": "Englisch",
                "chinese": "Chinesisch",
                "german": "Deutsch",
                "russian": "Russisch",
                "key_info": "Privater Schlüssel Information",
                "no_key_loaded": "Kein privater Schlüssel geladen",
                "key_path": "Schlüssel Pfad: {}",
                "challenge_label": "Challenge:",
                "generate_btn": "Antwort generieren",
                "copy_btn": "In Zwischenablage kopieren",
                "clear_btn": "Löschen",
                "view_log_btn": "Challenges anzeigen",
                "response_label": "Antwort",
                "status_ready": "Bereit",
                "key_load_success": "Privater Schlüssel erfolgreich geladen",
                "key_load_failed": "Laden des privaten Schlüssels fehlgeschlagen",
                "key_loaded_from": "Privater Schlüssel geladen von {}",
                "key_load_error": "Fehler beim Laden des privaten Schlüssels",
                "empty_challenge": "Challenge darf nicht leer sein",
                "no_key_error": "Kein privater Schlüssel geladen",
                "response_generated": "Antwort erfolgreich generiert",
                "response_copied": "Antwort in Zwischenablage kopiert",
                "no_response": "Keine Antwort zum Kopieren",
                "fields_cleared": "Felder gelöscht",
                "log_cleared": "Challenge Log gelöscht",
                "about_title": f"Audibo Challenge Response Generator v{self.version}",
                "about_text": f"""Ein sicheres Tool zur Generierung signierter Antworten auf Audibo-Challenges.

Version: {self.version}
Funktionen:
- Laden privater Schlüssel von jedem Ort
- Kopieren-in-Zwischenablage-Funktion
- Mehrsprachige Unterstützung (EN/CN/DE/RU)
- Challenge-Historie-Protokollierung

© 2023 Audibo""",
                "invalid_format": "Ungültiges Challenge-Format - erwartet 4 durch 0A getrennte Segmente",
                "error": "Fehler",
                "warning": "Warnung",
                "failed_to_process": "Challenge-Verarbeitung fehlgeschlagen"
            },
            "ru": {
                "title": f"Audibo Challenge Response Generator v{self.version}",
                "file_menu": "Файл",
                "load_key": "Загрузить приватный ключ",
                "exit": "Выход",
                "help_menu": "Помощь",
                "documentation": "Документация",
                "about": "О программе",
                "language_menu": "Язык",
                "english": "Английский",
                "chinese": "Китайский",
                "german": "Немецкий",
                "russian": "Русский",
                "key_info": "Информация о приватном ключе",
                "no_key_loaded": "Приватный ключ не загружен",
                "key_path": "Путь к ключу: {}",
                "challenge_label": "Челлендж:",
                "generate_btn": "Сгенерировать ответ",
                "copy_btn": "Копировать в буфер",
                "clear_btn": "Очистить",
                "view_log_btn": "Просмотр истории челленджей",
                "response_label": "Ответ",
                "status_ready": "Готов",
                "key_load_success": "Приватный ключ успешно загружен",
                "key_load_failed": "Ошибка загрузки приватного ключа",
                "key_loaded_from": "Приватный ключ загружен из {}",
                "key_load_error": "Ошибка при загрузке приватного ключа",
                "empty_challenge": "Челлендж не может быть пустым",
                "no_key_error": "Приватный ключ не загружен",
                "response_generated": "Ответ успешно сгенерирован",
                "response_copied": "Ответ скопирован в буфер",
                "no_response": "Нет ответа для копирования",
                "fields_cleared": "Поля очищены",
                "log_cleared": "История челленджей очищена",
                "about_title": f"Audibo Challenge Response Generator v{self.version}",
                "about_text": f"""Безопасный инструмент для генерации подписанных ответов на челленджи Audibo.

Версия: {self.version}
Функции:
- Загрузка приватных ключей из любого места
- Функция копирования в буфер
- Поддержка нескольких языков (EN/CN/DE/RU)
- Логирование истории челленджей

© 2023 Audibo""",
                "invalid_format": "Неверный формат челленджа - ожидается 4 сегмента, разделенных 0A",
                "error": "Ошибка",
                "warning": "Предупреждение",
                "failed_to_process": "Ошибка обработки челленджа"
            }
        }
        
        self.root.title(self._("title"))
        self.root.geometry("850x650")
        
        # 初始化UI
        self.create_widgets()
        self.load_default_private_key()
        self.create_menu()
        self.load_challenge_log()
    
    def _(self, key):
        """翻译辅助函数"""
        return self.translations[self.language].get(key, key)
    
    def set_language(self, lang):
        """设置应用程序语言"""
        self.language = lang
        self.update_ui_text()
        self.status_var.set(f"{self._('status_ready')} | v{self.version}")
    
    def update_ui_text(self):
        """更新所有UI文本"""
        self.root.title(self._("title"))
        
        # 更新菜单
        self.file_menu.entryconfig(0, label=self._("load_key"))
        self.file_menu.entryconfig(2, label=self._("exit"))
        self.help_menu.entryconfig(0, label=self._("documentation"))
        self.help_menu.entryconfig(1, label=self._("about"))
        
        # 更新UI元素
        self.key_frame.config(text=self._("key_info"))
        self.key_status_label.config(text=self._("no_key_loaded"))
        self.challenge_label.config(text=self._("challenge_label"))
        self.generate_btn.config(text=self._("generate_btn"))
        self.copy_btn.config(text=self._("copy_btn"))
        self.clear_btn.config(text=self._("clear_btn"))
        self.view_log_btn.config(text=self._("view_log_btn"))
        self.response_frame.config(text=self._("response_label"))
    
    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        # 文件菜单
        self.file_menu = tk.Menu(menubar, tearoff=0)
        self.file_menu.add_command(label=self._("load_key"), command=self.load_custom_private_key)
        self.file_menu.add_separator()
        self.file_menu.add_command(label=self._("exit"), command=self.root.quit)
        menubar.add_cascade(label=self._("file_menu"), menu=self.file_menu)
        
        # 语言菜单
        self.language_menu = tk.Menu(menubar, tearoff=0)
        self.language_menu.add_command(label=self._("english"), command=lambda: self.set_language("en"))
        self.language_menu.add_command(label=self._("chinese"), command=lambda: self.set_language("zh"))
        self.language_menu.add_command(label=self._("german"), command=lambda: self.set_language("de"))
        self.language_menu.add_command(label=self._("russian"), command=lambda: self.set_language("ru"))
        menubar.add_cascade(label=self._("language_menu"), menu=self.language_menu)
        
        # 帮助菜单
        self.help_menu = tk.Menu(menubar, tearoff=0)
        self.help_menu.add_command(label=self._("documentation"), command=self.open_docs)
        self.help_menu.add_command(label=self._("about"), command=self.show_about)
        menubar.add_cascade(label=self._("help_menu"), menu=self.help_menu)
        
        self.root.config(menu=menubar)
    
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题区域
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 使用锁图标作为logo
        logo_label = ttk.Label(title_frame, text="🔐", font=('Helvetica', 24))
        logo_label.pack(side=tk.LEFT, padx=5)
        
        title_label = ttk.Label(
            title_frame, 
            text=self._("title"),
            font=('Helvetica', 14, 'bold')
        )
        title_label.pack(side=tk.LEFT)
        
        # 密钥信息区域
        self.key_frame = ttk.LabelFrame(main_frame, text=self._("key_info"), padding=10)
        self.key_frame.pack(fill=tk.X, pady=5)
        
        self.key_status_label = ttk.Label(
            self.key_frame, 
            text=self._("no_key_loaded"),
            font=('Helvetica', 10)
        )
        self.key_status_label.pack(anchor=tk.W)
        
        self.key_path_label = ttk.Label(
            self.key_frame, 
            text="",
            font=('Helvetica', 8)
        )
        self.key_path_label.pack(anchor=tk.W)
        
        # 挑战输入区域
        challenge_frame = ttk.Frame(main_frame)
        challenge_frame.pack(fill=tk.X, pady=5)
        
        self.challenge_label = ttk.Label(challenge_frame, text=self._("challenge_label"))
        self.challenge_label.pack(side=tk.LEFT)
        
        self.challenge_entry = ttk.Entry(challenge_frame, width=70)
        self.challenge_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        # 按钮区域
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        # 生成按钮
        self.generate_btn = ttk.Button(
            buttons_frame, 
            text=self._("generate_btn"), 
            command=self.generate_response
        )
        self.generate_btn.pack(side=tk.LEFT, padx=5)
        
        # 复制按钮
        self.copy_btn = ttk.Button(
            buttons_frame, 
            text=self._("copy_btn"), 
            command=self.copy_to_clipboard
        )
        self.copy_btn.pack(side=tk.LEFT, padx=5)
        
        # 清除按钮
        self.clear_btn = ttk.Button(
            buttons_frame, 
            text=self._("clear_btn"), 
            command=self.clear_fields
        )
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # 查看日志按钮
        self.view_log_btn = ttk.Button(
            buttons_frame, 
            text=self._("view_log_btn"), 
            command=self.view_challenge_log
        )
        self.view_log_btn.pack(side=tk.LEFT, padx=5)
        
        # 响应显示区域
        self.response_frame = ttk.LabelFrame(main_frame, text=self._("response_label"), padding=5)
        self.response_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.response_text = scrolledtext.ScrolledText(
            self.response_frame, 
            width=80, 
            height=15,
            font=('Courier', 10),
            wrap=tk.WORD
        )
        self.response_text.pack(fill=tk.BOTH, expand=True)
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set(f"{self._('status_ready')} | v{self.version}")
        status_bar = ttk.Label(
            main_frame, 
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        status_bar.pack(fill=tk.X, pady=(10, 0))
    
    def load_challenge_log(self):
        """加载挑战日志"""
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    self.challenge_log = json.load(f)
            else:
                self.challenge_log = []
        except Exception as e:
            messagebox.showerror(
                self._("error"),
                f"Failed to load challenge log: {str(e)}"
            )
            self.challenge_log = []
    
    def save_challenge_log(self):
        """保存挑战日志"""
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(self.challenge_log, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror(
                self._("error"),
                f"Failed to save challenge log: {str(e)}"
            )
    
    def log_challenge(self, challenge):
        """记录挑战"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        challenge_hash = hashlib.sha256(challenge.encode()).hexdigest()
        
        entry = {
            "timestamp": timestamp,
            "challenge": challenge,
            "challenge_hash": challenge_hash
        }
        
        self.challenge_log.append(entry)
        self.save_challenge_log()
    
    def view_challenge_log(self):
        """查看挑战日志"""
        log_window = tk.Toplevel(self.root)
        log_window.title(f"{self._('title')} - Challenge Log")
        log_window.geometry("800x600")
        
        log_frame = ttk.Frame(log_window, padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        log_text = scrolledtext.ScrolledText(
            log_frame,
            width=85,
            height=30,
            font=('Courier', 10),
            wrap=tk.WORD
        )
        log_text.pack(fill=tk.BOTH, expand=True)
        
        # 添加日志内容
        if not self.challenge_log:
            log_text.insert(tk.END, "No challenge history found.")
        else:
            for entry in self.challenge_log:
                log_text.insert(tk.END, f"Time: {entry['timestamp']}\n")
                log_text.insert(tk.END, f"Challenge: {entry['challenge']}\n")
                log_text.insert(tk.END, f"Hash: {entry['challenge_hash']}\n")
                log_text.insert(tk.END, "-"*50 + "\n")
        
        log_text.config(state='disabled')
        
        # 清除日志按钮
        clear_log_btn = ttk.Button(
            log_frame,
            text="Clear Challenge Log",
            command=lambda: self.clear_challenge_log(log_window)
        )
        clear_log_btn.pack(pady=5)
    
    def clear_challenge_log(self, log_window=None):
        """清除挑战日志"""
        self.challenge_log = []
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
            self.status_var.set(f"{self._('log_cleared')} | v{self.version}")
            if log_window:
                log_window.destroy()
        except Exception as e:
            messagebox.showerror(
                self._("error"),
                f"Failed to clear challenge log: {str(e)}"
            )
    
    def load_default_private_key(self):
        """加载默认私钥"""
        if os.path.exists('private.pem'):
            self.load_private_key('private.pem')
    
    def load_custom_private_key(self):
        """加载自定义私钥"""
        file_path = filedialog.askopenfilename(
            title=self._("load_key"),
            filetypes=[("PEM files", "*.pem"), ("All files", "*.*")]
        )
        if file_path:
            self.load_private_key(file_path)
    
    def load_private_key(self, file_path):
        """加载私钥"""
        try:
            with open(file_path, 'rb') as key_file:
                self.private_key = load_pem_private_key(
                    key_file.read(),
                    password=None,
                    backend=default_backend()
                )
            self.key_file_path = file_path
            self.key_status_label.config(text=self._("key_load_success"))
            self.key_path_label.config(text=self._("key_path").format(file_path))
            self.status_var.set(f"{self._('key_loaded_from').format(os.path.basename(file_path))} | v{self.version}")
        except Exception as e:
            messagebox.showerror(
                self._("error"), 
                f"{self._('key_load_error')}: {str(e)}"
            )
            self.key_status_label.config(text=self._("key_load_failed"))
            self.key_path_label.config(text="")
            self.status_var.set(f"{self._('key_load_error')} | v{self.version}")
    
    def get_random_unicode(self, length):
        """生成随机Unicode字符"""
        try:
            get_char = chr  # Python 3
        except NameError:
            get_char = unichr  # Python 2
            
        include_ranges = [(128, 999)]
        alphabet = [
            get_char(code_point) 
            for current_range in include_ranges 
            for code_point in range(current_range[0], current_range[1] + 1)
        ]
        return ''.join(random.choice(alphabet) for _ in range(length))
    
    def generate_response(self):
        """生成响应"""
        challenge = self.challenge_entry.get().strip()
        
        if not challenge:
            messagebox.showwarning(self._("warning"), self._("empty_challenge"))
            self.status_var.set(f"{self._('error')}: {self._('empty_challenge')} | v{self.version}")
            return
        
        if not self.private_key:
            messagebox.showerror(self._("error"), self._("no_key_error"))
            self.status_var.set(f"{self._('error')}: {self._('no_key_error')} | v{self.version}")
            return
            
        try:
            challenge_array = challenge.split('0A')
            if len(challenge_array) < 4:
                raise ValueError(self._("invalid_format"))
                
            random_data = challenge_array[1]
            
            # 生成随机组件
            random_string = self.get_random_unicode(9)
            random_string2 = ''.join(
                random.choice(string.punctuation + string.whitespace) 
                for _ in range(5)
            )
            
            # 构建签名数据
            data_parts = [
                binascii.unhexlify(random_data).decode('utf-8'),
                '\n' + random_string + binascii.unhexlify(challenge_array[3]).decode('utf-8'),
                '\n' + binascii.unhexlify(challenge_array[2]).decode('utf-8')
            ]
            data = ''.join(data_parts).encode('utf-8')
            
            # 生成签名
            signature = self.private_key.sign(
                data,
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            
            # 构建响应
            response_parts = [
                random_data,
                '0A',
                binascii.hexlify(random_string.encode('utf-8')).decode('utf-8').upper(),
                binascii.hexlify(random_string2.encode('utf-8')).decode('utf-8').upper(),
                signature.hex().upper()
            ]
            response = ''.join(response_parts)
            
            # 显示响应
            self.response_text.delete(1.0, tk.END)
            self.response_text.insert(tk.END, response)
            self.status_var.set(f"{self._('response_generated')} | v{self.version}")
            
            # 记录挑战
            self.log_challenge(challenge)
            
        except Exception as e:
            messagebox.showerror(
                self._("error"), 
                f"{self._('failed_to_process')}: {str(e)}"
            )
            self.status_var.set(f"{self._('error')}: {str(e)} | v{self.version}")
    
    def copy_to_clipboard(self):
        """复制到剪贴板"""
        response = self.response_text.get(1.0, tk.END).strip()
        if response:
            pyperclip.copy(response)
            self.status_var.set(f"{self._('response_copied')} | v{self.version}")
        else:
            messagebox.showwarning(self._("warning"), self._("no_response"))
            self.status_var.set(f"{self._('warning')}: {self._('no_response')} | v{self.version}")
    
    def clear_fields(self):
        """清除字段"""
        self.challenge_entry.delete(0, tk.END)
        self.response_text.delete(1.0, tk.END)
        self.status_var.set(f"{self._('fields_cleared')} | v{self.version}")
    
    def open_docs(self):
        """打开文档"""
        webbrowser.open("https://github.com/jiangbo2571/MH2P_MIB3_challenge-tools")
    
    def show_about(self):
        """显示关于信息"""
        messagebox.showinfo(self._("about_title"), self._("about_text"))

def main():
    root = tk.Tk()
    app = AudiboGeneratorApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
