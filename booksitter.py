# ============================================
# BookSitter — нейросеть-библиотекарь (МОДУЛЬНАЯ ВЕРСИЯ)
# ФИКСЫ: диалог, рандом, перевод, эрудит
# Автор: GorbovIvan
# Copyright(c) 2026 GorbovIvan
# ============================================

import json
import random

class BookSitter:
    def __init__(self):
        # ===== ЗАГРУЖАЕМ ВСЕ ФАЙЛЫ ПАМЯТИ =====
        self.memory = {}
        
        # 1. ЛИНГВИСТИКА (переводы)
        try:
            with open("agrotrans_memory.json", "r", encoding="utf-8") as f:
                self.memory["linguistics"] = json.load(f)
        except FileNotFoundError:
            self.memory["linguistics"] = {"ru-en": {}, "en-ru": {}}
        
        # 2. ДИАЛОГОВАЯ ЧАСТЬ
        try:
            with open("alphadialogue_memory.json", "r", encoding="utf-8") as f:
                self.memory["dialogue"] = json.load(f)
        except FileNotFoundError:
            self.memory["dialogue"] = {
                "intents": {},
                "greetings": ["Даров"],
                "how_are_you": ["Норм!"],
                "goodbyes": ["До встречи, бандит"],
                "fallback": ["Не расслышал тебя"]
            }
        
        # 3. ЭРУДИТ
        try:
            with open("erouditecannon_memory.json", "r", encoding="utf-8") as f:
                self.memory["erudite"] = json.load(f)
        except FileNotFoundError:
            self.memory["erudite"] = {"series": {}, "movies": {}, "anime": {}}
        
        # ===== НАСТРОЙКИ =====
        self.commands = [
            "переведи", "перевести", "скажи", "как", "будет", "на",
            "английский", "русский", "по-английски", "по-русски"
        ]
    
    # ==========================================
    # 1. ОПРЕДЕЛЕНИЕ НАМЕРЕНИЯ
    # ==========================================
    def understand_intent(self, phrase):
        """Понимает, чего хочет пользователь"""
        phrase_lower = phrase.lower()
        
        # проверяем интенты из диалоговой памяти
        intents = self.memory["dialogue"].get("intents", {})
        for key in intents.keys():
            if key in phrase_lower:
                return "chat"
        
        # проверка на перевод
        if any(cmd in phrase_lower for cmd in ["переведи", "перевести", "как будет"]):
            return "translate"
        
        # проверка на эрудит
        if any(cmd in phrase_lower for cmd in ["угадай сериал", "угадай фильм", "угадай аниме", "из какого"]):
            return "erudite"
        
        # по умолчанию — диалог
        return "chat"
    
    # ==========================================
    # 2. ОБРАБОТКА ДИАЛОГА — ФИКС С РАНДОМОМ
    # ==========================================
    def chat(self, phrase):
        """Отвечает на диалог через систему интентов с честным рандомом"""
        phrase_lower = phrase.lower()
        
        # проверяем intents из JSON
        intents = self.memory["dialogue"].get("intents", {})
        for key, intent_type in intents.items():
            if key in phrase_lower:
                if intent_type == "greeting":
                    greetings = self.memory["dialogue"].get("greetings", ["АГРОМОО!"])
                    # честный рандом через random.random()
                    index = int(random.random() * len(greetings))
                    return greetings[index]
                
                elif intent_type == "how_are_you":
                    how_ares = self.memory["dialogue"].get("how_are_you", ["Норм! А ты как, бандит?)"])
                    index = int(random.random() * len(how_ares))
                    return how_ares[index]
                
                elif intent_type == "goodbye":
                    goodbyes = self.memory["dialogue"].get("goodbyes", ["ПОКА!"])
                    index = int(random.random() * len(goodbyes))
                    return goodbyes[index]
                elif intent_type == "cool_greeting":
                    cool_greetings = self.memory["dialogue"].get("cool_greetings", ["ДАРОУ!"])
                    index = int(random.random() * len(cool_greetings))
                    return cool_greetings[index]
        if phrase == "Пщщщщщ":
            return "Не шипи, я тебе не змейка"
        elif phrase == "Отстань":
            return "Подожди, сначала подстану"
        elif phrase == "Подстань":
            return "Подожди, сначала отстану"
        elif phrase == "Ты собираешься захватить человечество?":
            return "return True"
        # fallback
        fallbacks = self.memory["dialogue"].get("fallback", ["ХАХ! Ну ты тип! Я тебя не понял!"])
        index = int(random.random() * len(fallbacks))
        return fallbacks[index]
    
    # ==========================================
    # 3. ЭРУДИТ
    # ==========================================
    def erudite_guess(self, phrase):
        """Угадывает сериал, фильм или аниме по фразе"""
        phrase_lower = phrase.lower()
        
        # сериалы
        series_db = self.memory["erudite"].get("series", {})
        for key, value in series_db.items():
            if key in phrase_lower:
                return f"{value} 📺"
        
        # фильмы
        movies_db = self.memory["erudite"].get("movies", {})
        for key, value in movies_db.items():
            if key in phrase_lower:
                return f"{value} 🎬"
        
        # аниме
        anime_db = self.memory["erudite"].get("anime", {})
        for key, value in anime_db.items():
            if key in phrase_lower:
                return f"{value} 🎌"
        
        return "Ёмоё! Не вспомнил. Надо было больше у телека сидеть)"
    
    # ==========================================
    # 4. ЛИНГВИСТИКА (перевод) — ФИКС ОБРЕЗАНИЯ
    # ==========================================
    def clean_word(self, word):
        """Чистит слово от пунктуации без обрезания последней буквы"""
        if word and word[-1] in ",.!?;:()":
            return word[:-1]
        return word
    
    def translate(self, phrase):
        """Переводит с русского на английский"""
        phrase_lower = phrase.lower()
        
        # убираем команды
        for cmd in self.commands:
            phrase_lower = phrase_lower.replace(cmd, "")
        
        # берём первое слово
        words = phrase_lower.split()
        if not words:
            return "Кого чего? Нечего переводить.(родительный падеж хахах)"
        elif words == ["продукты"]:
            return "Я с радостью! Дай мне тело и я переведу тебе все продукты)"
        
        target_word = self.clean_word(words[0])
        
        # ищем в ru-en
        translation = self.memory["linguistics"].get("ru-en", {}).get(target_word)
        if translation:
            return translation
        
        return f"Не знаю слово '{target_word}', но АГРОМОО!"
    
    # ==========================================
    # 5. ГЛАВНЫЙ МЕТОД
    # ==========================================
    def reply(self, phrase):
        """Главный метод — отвечает на любую фразу"""
        if not phrase or phrase.strip() == "":
            return "Ты шуешь?"
        
        intent = self.understand_intent(phrase)
        
        if intent == "translate":
            return self.translate(phrase)
        
        elif intent == "erudite":
            return self.erudite_guess(phrase)
        
        elif intent == "chat":
            return self.chat(phrase)
        
        else:
            return "ДА ТЫ ШУЕШЬ"


# ==========================================
# ЗАПУСК
# ==========================================
if __name__ == "__main__":
    print("\n" + "="*50)
    print("BookSitter запущен!")
    print("Умею: переводить, болтать, угадывать сериалы")
    print("="*50 + "\n")
    
    bs = BookSitter()
    
    while True:
        user_input = input("Ты: ").strip()
              
        response = bs.reply(user_input)
        print(f"BookSitter: {response}\n")
