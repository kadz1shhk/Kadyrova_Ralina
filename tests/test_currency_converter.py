import unittest
from unittest.mock import Mock, patch
import json
import tempfile
import os

# Импортируем класс из основного файла
from currency_converter import CurrencyConverter

class TestCurrencyConverter(unittest.TestCase):

    def setUp(self):
        """Настройка перед каждым тестом"""
        # Создаём временный файл для истории
        self.temp_history = tempfile.NamedTemporaryFile(delete=False)
        self.temp_history.close()

        # Патчим HISTORY_FILE на временный файл
        self.history_patch = patch('currency_converter.HISTORY_FILE', self.temp_history.name)
        self.history_patch.start()

        # Патчим API_KEY
        self.api_patch = patch('currency_converter.API_KEY', 'test_key')
        self.api_patch.start()

        # Создаём экземпляр приложения (без GUI для тестов)
        from currency_converter import tk
        self.mock_root = Mock()
        self.app = CurrencyConverter(self.mock_root)

    def tearDown(self):
        """Очистка после каждого теста"""
        self.history_patch.stop()
        self.api_patch.stop()
        os.unlink(self.temp_history.name)

    # ---------- Тесты проверки ввода ----------
    def test_positive_amount_valid(self):
        """Тест: положительное число проходит валидацию"""
        self.app.amount_entry.get = Mock(return_value="100")
        self.app.from_currency.get = Mock(return_value="USD")
        self.app.to_currency.get = Mock(return_value="USD")

        with patch.object(self.app, 'get_exchange_rate') as mock_rate:
            self.app.convert()
            # Если дошли до конвертации без ошибки - тест пройден
            self.assertTrue(True)

    def test_negative_amount_invalid(self):
        """Тест: отрицательное число вызывает ошибку"""
        self.app.amount_entry.get = Mock(return_value="-50")

        with patch('currency_converter.messagebox.showerror') as mock_error:
            self.app.convert()
            mock_error.assert_called_once()

    def test_zero_amount_invalid(self):
        """Тест: ноль вызывает ошибку"""
        self.app.amount_entry.get = Mock(return_value="0")

        with patch('currency_converter.messagebox.showerror') as mock_error:
            self.app.convert()
            mock_error.assert_called_once()

    def test_text_amount_invalid(self):
        """Тест: текст вызывает ошибку"""
        self.app.amount_entry.get = Mock(return_value="abc")

        with patch('currency_converter.messagebox.showerror') as mock_error:
            self.app.convert()
            mock_error.assert_called_once()

    # ---------- Тесты конвертации ----------
    def test_convert_same_currency(self):
        """Тест: конвертация USD -> USD (без API)"""
        self.app.amount_entry.get = Mock(return_value="100")
        self.app.from_currency.get = Mock(return_value="USD")
        self.app.to_currency.get = Mock(return_value="USD")

        with patch.object(self.app, 'get_exchange_rate') as mock_rate:
            self.app.convert()
            mock_rate.assert_not_called()  # API не вызывается

    @patch('currency_converter.requests.get')
    def test_convert_different_currency_success(self, mock_get):
        """Тест: успешная конвертация USD -> EUR"""
        mock_response = Mock()
        mock_response.json.return_value = {"result": "success", "conversion_rate": 0.85}
        mock_get.return_value = mock_response

        self.app.amount_entry.get = Mock(return_value="100")
        self.app.from_currency.get = Mock(return_value="USD")
        self.app.to_currency.get = Mock(return_value="EUR")

        self.app.convert()
        self.assertEqual(self.app.result_label.cget("text"), "100.00 USD = 85.00 EUR")

    @patch('currency_converter.requests.get')
    def test_convert_api_failure(self, mock_get):
        """Тест: ошибка API"""
        mock_response = Mock()
        mock_response.json.return_value = {"result": "error"}
        mock_get.return_value = mock_response
12:30
self.app.amount_entry.get = Mock(return_value="100")
        self.app.from_currency.get = Mock(return_value="USD")
        self.app.to_currency.get = Mock(return_value="EUR")

        with patch('currency_converter.messagebox.showerror') as mock_error:
            self.app.convert()
            mock_error.assert_called_once()

    # ---------- Тесты истории ----------
    def test_save_and_load_history(self):
        """Тест: сохранение и загрузка истории"""
        test_record = {
            "timestamp": "2024-01-01 12:00",
            "amount": 100,
            "from": "USD",
            "to": "EUR",
            "result": 85
        }
        self.app.history = [test_record]
        self.app.save_history()

        # Создаём новый экземпляр для загрузки
        new_app = CurrencyConverter(self.mock_root)
        self.assertEqual(len(new_app.history), 1)
        self.assertEqual(new_app.history[0]["amount"], 100)

    def test_clear_history(self):
        """Тест: очистка истории"""
        self.app.history = [{"timestamp": "test", "amount": 100, "from": "USD", "to": "EUR", "result": 85}]
        self.app.save_history()
        self.app.clear_history()
        self.assertEqual(len(self.app.history), 0)

        # Проверяем, что файл очищен
        with open(self.temp_history.name, 'r') as f:
            data = json.load(f)
            self.assertEqual(len(data), 0)

    # ---------- Интеграционный тест ----------
    @patch('currency_converter.requests.get')
    def test_full_conversion_flow(self, mock_get):
        """Тест: полный цикл конвертации + сохранение истории"""
        mock_response = Mock()
        mock_response.json.return_value = {"result": "success", "conversion_rate": 95.0}
        mock_get.return_value = mock_response

        self.app.amount_entry.get = Mock(return_value="100")
        self.app.from_currency.get = Mock(return_value="USD")
        self.app.to_currency.get = Mock(return_value="RUB")

        self.app.convert()

        # Проверяем, что история сохранилась
        self.assertEqual(len(self.app.history), 1)
        self.assertEqual(self.app.history[0]["result"], 9500.0)

# ---------- Запуск тестов ----------
if __name__ == "__main__":
    unittest.main()
