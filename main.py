# ============================================
# AGROTRANS — переводчик без импортов
# Автор: Vanya the Boar
# АГРОМОО! МИР_ПРЕКРАСЕН!
# ============================================

from booksitter import BookSitter

# создаём библиотекаря
bs = BookSitter()

print("АГРОМОО! AGROTRANS запущен!")
print("=" * 40)

# тест 1
result = bs.translate("Переведи привет на английский")
print(f"Тест 1: {result}")

# тест 2
result = bs.translate("Скажи мир по-английски")
print(f"Тест 2: {result}")

# тест 3 (русско-английский)
result = bs.translate("Как будет агромоо на английском?")
print(f"Тест 3: {result}")

# маленькое обучение
print("\n--- ОБУЧЕНИЕ ---")
print(bs.learn("круто", "cool", "ru", "en"))

# тест после обучения
result = bs.translate("Переведи круто на английский")
print(f"Тест после обучения: {result}")

print("\nМИР_ПРЕКРАСЕН! АГРОМОО! 🐗")
