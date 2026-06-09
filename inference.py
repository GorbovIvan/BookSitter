# ============================================
# Бесконечный диалог с BookSitter
# Автор: GorbovIvan
# Copyright(c) 2026 GorbovIvan
# ============================================

from booksitter import BookSitter

def main():
    print("\n" + "="*50)
    print("BookSitter в режиме ИНФЕРЕНСА!")
    print("Говори что хочешь перевести. Я сам пойму направление.")
    print("Команды: !почему, !обучи, !выход")
    print("="*50 + "\n")
    
    bs = BookSitter("agrotrans_memory.json")
    
    while True:
        user_input = input("Ты: ").strip()
        
        if user_input.lower() in ["!выход", "!exit", "пока", "агромоо пока"]:
            print("До свидания 🐗\n")
            break
        
        # команда !почему
        if user_input.startswith("!почему"):
            # берём последнюю фразу (можно усложнить, но пока просто)
            print(bs.explain(user_input.replace("!почему", "").strip() or "последняя фраза"))
            continue
        
        # команда !обучи слово перевод from to
        if user_input.startswith("!обучи"):
            parts = user_input.split()
            if len(parts) >= 4:
                _, word, translation, from_lang, to_lang = parts[0], parts[1], parts[2], parts[3], parts[4] if len(parts) > 4 else "ru"
                print(bs.learn(word, translation, from_lang, to_lang))
            else:
                print("Формат: !обучи слово перевод from_lang to_lang")
            continue
        
        # команда !похвала
        if user_input == "!похвала":
            print(bs.praise(""))
            continue
        
        # команда !красная
        if user_input == "!красная":
            print(bs.red_button(""))
            continue
        
        # обычный перевод
        result = bs.translate(user_input)
        print(f"BookSitter: {result}\n")

if __name__ == "__main__":
    main()
