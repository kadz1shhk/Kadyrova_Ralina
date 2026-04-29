import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from datetime import datetime

# ---------- Класс конвертера валют ----------
class CurrencyConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter")
        self.root.geometry("700x500")

        # API настройки (бесплатный ключ с exchangerate-api.com)
        self.api_key = "ВАШ_API_КЛЮЧ"  # Замените на реальный ключ
        self.base_url = "https://v6.exchangerate-api.com/v6/"

        # Доступные валюты (можно расширить)
        self.currencies = ["USD", "EUR", "RUB", "GBP", "JPY", "CNY", "BYN", "KZT", "UAH"]

        # Файл истории
        self.history_file = "conversion_history.json"
        self.history = self.load_history()

        # Создание интерфейса
        self.create_widgets()
        self.update_history_table()

    def create_widgets(self):
        # Рамка для ввода
        input_frame = ttk.LabelFrame(self.root, text="Конвертация валют", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(input_frame, text="Сумма:").grid(row=0, column=0, sticky="w")
        self.amount_entry = ttk.Entry(input_frame, width=15)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)
        self.amount_entry.insert(0, "1.00")

        ttk.Label(input_frame, text="Из валюты:").grid(row=1, column=0, sticky="w")
        self.from_currency = ttk.Combobox(input_frame, values=self.currencies, width=10)
        self.from_currency.grid(row=1, column=1, padx=5, pady=5)
        self.from_currency.set("USD")

        ttk.Label(input_frame, text="В валюту:").grid(row=2, column=0, sticky="w")
        self.to_currency = ttk.Combobox(input_frame, values=self.currencies, width=10)
        self.to_currency.grid(row=2, column=1, padx=5, pady=5)
        self.to_currency.set("EUR")

        self.convert_btn = ttk.Button(input_frame, text="Конвертировать", command=self.convert)
        self.convert_btn.grid(row=3, column=0, columnspan=2, pady=10)

        self.result_label = ttk.Label(input_frame, text="Результат: --", font=("Arial", 12, "bold"))
        self.result_label.grid(row=4, column=0, columnspan=2)

        # Рамка для истории
        history_frame = ttk.LabelFrame(self.root, text="История конвертаций", padding=10)
        history_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("Дата", "Сумма", "Из", "В", "Результат")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show="headings")
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=100)

        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        self.history_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Кнопки управления историей
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=5)
        ttk.Button(btn_frame, text="Обновить историю", command=self.update_history_table).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Очистить историю", command=self.clear_history).pack(side="left", padx=5)

    def get_exchange_rate(self, from_cur, to_cur):
        """Получение курса через API"""
        url = f"{self.base_url}{self.api_key}/pair/{from_cur}/{to_cur}"
        try:
            response = requests.get(url, timeout=10)
            data = response.json()
            if data.get("result") == "success":
                return data["conversion_rate"]
            else:
                messagebox.showerror("Ошибка API", "Не удалось получить курс. Проверьте ключ.")
                return None
        except Exception as e:
            messagebox.showerror("Ошибка соединения", f"Проблема с API: {e}")
            return None

    def convert(self):

exchangerate-api.com
ExchangeRate-API - Free & Pro Currency Converter API
Accurate & reliable Exchange Rates API trusted by tens of thousands of developers since 2010. Free access, all world currencies, helpful support & easy to integrate JSON API.
12:20
amount_str = self.amount_entry.get().strip()
        # Проверка корректности ввода (положительное число)
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Сумма должна быть положительным числом!")
            return

        from_cur = self.from_currency.get()
        to_cur = self.to_currency.get()

        if from_cur == to_cur:
            result = amount
        else:
            rate = self.get_exchange_rate(from_cur, to_cur)
            if rate is None:
                return
            result = amount * rate

        result_text = f"{amount:.2f} {from_cur} = {result:.2f} {to_cur}"
        self.result_label.config(text=result_text)

        # Сохраняем в историю
        record = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "amount": amount,
            "from": from_cur,
            "to": to_cur,
            "result": round(result, 2)
        }
        self.history.append(record)
        self.save_history()
        self.update_history_table()

    def load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_history(self):
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=4)

    def update_history_table(self):
        for row in self.history_tree.get_children():
            self.history_tree.delete(row)
        for rec in self.history[-20:]:  # показываем последние 20 записей
            self.history_tree.insert("", "end", values=(
                rec["timestamp"],
                rec["amount"],
                rec["from"],
                rec["to"],
                rec["result"]
            ))

    def clear_history(self):
        if messagebox.askyesno("Подтверждение", "Очистить всю историю?"):
            self.history = []
            self.save_history()
            self.update_history_table()

# ---------- Запуск приложения ----------
if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyConverter(root)
    root.mainloop()
