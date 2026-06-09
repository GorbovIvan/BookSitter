#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright(c) 2026 GorbovIvan



import json
import os
import sys

DICT_FILE = "agrotrans_memory.json"

def load_dict():
    """Загружает словарь из файла"""
    if not os.path.exists(DICT_FILE):
        print(f"❌ Файл {DICT_FILE} не найден!")
        print("📁 Убедись, что скрипт лежит в одной папке с файлом словаря")
        sys.exit(1)
    
    with open(DICT_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_dict(data):
    """Сохраняет словарь в файл"""
    with open(DICT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("✅ Словарь сохранён!")

def add_ru_en(data, ru_word, en_word):
    """Добавляет перевод ru -> en"""
    ru_word = ru_word.lower().strip()
    en_word = en_word.lower().strip()
    
    if ru_word in data["ru-en"]:
        print(f"⚠️ Слово '{ru_word}' уже есть в ru-en со значением '{data['ru-en'][ru_word]}'")
        overwrite = input(f"📝 Перезаписать на '{en_word}'? (y/n): ").lower()
        if overwrite != 'y':
            print("❌ Добавление отменено")
            return False
    
    data["ru-en"][ru_word] = en_word
    print(f"✅ Добавлено: {ru_word} -> {en_word}")
    return True

def add_en_ru(data, en_word, ru_word):
    """Добавляет перевод en -> ru"""
    en_word = en_word.lower().strip()
    ru_word = ru_word.lower().strip()
    
    if en_word in data["en-ru"]:
        print(f"⚠️ Слово '{en_word}' уже есть в en-ru со значением '{data['en-ru'][en_word]}'")
        overwrite = input(f"📝 Перезаписать на '{ru_word}'? (y/n): ").lower()
        if overwrite != 'y':
            print("❌ Добавление отменено")
            return False
    
    data["en-ru"][en_word] = ru_word
    print(f"✅ Добавлено: {en_word} -> {ru_word}")
    return True

def add_both(data, ru_word, en_word):
    """Добавляет перевод в обе стороны"""
    ru_word = ru_word.lower().strip()
    en_word = en_word.lower().strip()
    
    # Добавляем ru -> en
    if ru_word in data["ru-en"]:
        print(f"⚠️ Слово '{ru_word}' уже есть в ru-en со значением '{data['ru-en'][ru_word]}'")
        overwrite = input(f"📝 Перезаписать на '{en_word}'? (y/n): ").lower()
        if overwrite == 'y':
            data["ru-en"][ru_word] = en_word
            print(f"✅ Обновлено: {ru_word} -> {en_word}")
    else:
        data["ru-en"][ru_word] = en_word
        print(f"✅ Добавлено: {ru_word} -> {en_word}")
    
    # Добавляем en -> ru
    if en_word in data["en-ru"]:
        print(f"⚠️ Слово '{en_word}' уже есть в en-ru со значением '{data['en-ru'][en_word]}'")
        overwrite = input(f"📝 Перезаписать на '{ru_word}'? (y/n): ").lower()
        if overwrite == 'y':
            data["en-ru"][en_word] = ru_word
            print(f"✅ Обновлено: {en_word} -> {ru_word}")
    else:
        data["en-ru"][en_word] = ru_word
        print(f"✅ Добавлено: {en_word} -> {ru_word}")
    
    return True

def show_stats(data):
    """Показывает статистику"""
    ru_en_count = len(data["ru-en"])
    en_ru_count = len(data["en-ru"])
    
    print("\n" + "="*40)
    print("📊 СТАТИСТИКА СЛОВАРЯ")
    print("="*40)
    print(f"📖 ru-en: {ru_en_count} слов")
    print(f"📖 en-ru: {en_ru_count} слов")
    print(f"🔗 Всего пар: {min(ru_en_count, en_ru_count)} (синхронизировано)")
    print("="*40 + "\n")

def search_word(data):
    """Поиск слова в словаре"""
    word = input("🔍 Введите слово для поиска: ").lower().strip()
    
    found = False
    
    # Ищем в ru-en
    if word in data["ru-en"]:
        print(f"\n📗 ru-en: {word} -> {data['ru-en'][word]}")
        found = True
    
    # Ищем в en-ru
    if word in data["en-ru"]:
        print(f"📘 en-ru: {word} -> {data['en-ru'][word]}")
        found = True
    
    # Ищем как перевод
    for ru, en in data["ru-en"].items():
        if en == word:
            print(f"\n📖 Найдено в переводе: {ru} ({ru}) -> {en}")
            found = True
    
    for en, ru in data["en-ru"].items():
        if ru == word:
            print(f"📖 Найдено в переводе: {en} -> {ru}")
            found = True
    
    if not found:
        print(f"❌ Слово '{word}' не найдено в словаре")
    
    return found

def interactive_mode():
    """Интерактивный режим"""
    data = load_dict()
    
    print("\n" + "="*50)
    print("📚 ИНТЕРАКТИВНЫЙ РЕДАКТОР СЛОВАРЯ")
    print("="*50)
    
    while True:
        print("\n📌 ДОСТУПНЫЕ КОМАНДЫ:")
        print("  1  - Добавить перевод ru → en")
        print("  2  - Добавить перевод en → ru")
        print("  3  - Добавить перевод в обе стороны (ru ↔ en)")
        print("  4  - Показать статистику")
        print("  5  - Поиск слова")
        print("  6  - Массовое добавление (пары через пробел)")
        print("  0  - Выход и сохранение")
        
        choice = input("\n👉 Ваш выбор: ").strip()
        
        if choice == '0':
            save_dict(data)
            print("👋 До свидания!")
            break
        
        elif choice == '1':
            ru = input("🇷🇺 Русское слово: ")
            en = input("🇬🇧 Английское слово: ")
            add_ru_en(data, ru, en)
        
        elif choice == '2':
            en = input("🇬🇧 Английское слово: ")
            ru = input("🇷🇺 Русское слово: ")
            add_en_ru(data, en, ru)
        
        elif choice == '3':
            ru = input("🇷🇺 Русское слово: ")
            en = input("🇬🇧 Английское слово: ")
            add_both(data, ru, en)
        
        elif choice == '4':
            show_stats(data)
        
        elif choice == '5':
            search_word(data)
        
        elif choice == '6':
            print("\n📝 Вводи пары 'русское=английское' (каждая с новой строки)")
            print("   Пример: привет=hi")
            print("   Для завершения ввода оставь строку пустой и нажми Enter\n")
            
            added = 0
            while True:
                line = input().strip()
                if not line:
                    break
                
                if '=' in line:
                    ru, en = line.split('=', 1)
                    if add_both(data, ru.strip(), en.strip()):
                        added += 1
                else:
                    print(f"⚠️ Неверный формат: '{line}' (пропускаем, нужно использовать =)")
            
            print(f"\n✅ Добавлено/обновлено {added} пар!")
        
        else:
            print("❌ Неверная команда, попробуй снова")

def batch_mode(pairs):
    """Пакетный режим: добавляет несколько пар из командной строки"""
    data = load_dict()
    
    print(f"\n📦 Пакетное добавление {len(pairs)} пар...")
    
    added = 0
    for pair in pairs:
        if '=' in pair:
            ru, en = pair.split('=', 1)
            if add_both(data, ru.strip(), en.strip()):
                added += 1
        elif '->' in pair:
            ru, en = pair.split('->', 1)
            if add_both(data, ru.strip(), en.strip()):
                added += 1
        else:
            print(f"⚠️ Неверный формат: '{pair}' (используй = или ->)")
    
    save_dict(data)
    print(f"\n🎉 Готово! Добавлено {added} новых пар.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Пакетный режим: python dict_updater.py "привет=hello" "мир=world"
        batch_mode(sys.argv[1:])
    else:
        # Интерактивный режим
        interactive_mode()
