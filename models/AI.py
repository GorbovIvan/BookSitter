import json
import os
import sys
import random
from typing import List, Dict, Tuple, Optional

class Logic:
    def __init__(self, weight: float = 2.0, temperature: float = 5.0, model_file: str = "model.mmr", dynamic_temp: bool = True):
        self.weight = weight
        self.temperature = temperature
        self.base_temperature = temperature
        self.dynamic_temp_enabled = dynamic_temp
        self.attention = weight * temperature
        self.active_chain = []
        self.associations = {}
        self.error_log = []
        self.memory = []
        self.model_file = model_file
        self.pain_words = ["боль", "больно", "опасно", "страх", "ужас", "вред", "опасность"]
        self.load()
    
    def set_dynamic_temperature(self, prompt: str) -> Dict:
        if not self.dynamic_temp_enabled:
            return None
        
        prompt_length = len(prompt)
        random_shift = random.randint(2, 5)
        new_temp = prompt_length + random_shift
        new_temp = max(1, min(15, new_temp))
        
        old_temp = self.temperature
        self.temperature = new_temp
        self.attention = self.weight * self.temperature
        
        return {
            "old_temp": old_temp,
            "new_temp": new_temp,
            "prompt_length": prompt_length,
            "random_shift": random_shift
        }
    
    def reset_temperature(self):
        self.temperature = self.base_temperature
        self.attention = self.weight * self.temperature
    
    def avoid_pain(self, from_node: str, to_node: str) -> bool:
        if to_node in self.pain_words:
            if from_node in self.associations and to_node in self.associations[from_node]:
                old_strength = self.associations[from_node][to_node]
                new_strength = old_strength * 0.3
                self.associations[from_node][to_node] = new_strength
                
                self.memory.append({
                    "type": "pain_avoidance",
                    "from": from_node,
                    "to": to_node,
                    "old_strength": old_strength,
                    "new_strength": new_strength
                })
                
                print(f"  😖 Избегание боли: '{from_node} → {to_node}' ослаблена: {old_strength:.2f} → {new_strength:.2f}")
                return True
        return False
    
    def tokenize(self, prompt: str) -> List[str]:
        if self.temperature <= 0:
            chunk_size = 1
        else:
            chunk_size = max(1, int(self.temperature))
        
        tokens = []
        for i in range(0, len(prompt), chunk_size):
            token = prompt[i:i + chunk_size]
            tokens.append(token)
        return tokens
    
    def add_association(self, from_node: str, to_node: str, strength: float = None):
        if from_node not in self.associations:
            self.associations[from_node] = {}
        
        if strength is None:
            strength = self.attention
        
        if to_node in self.associations[from_node]:
            old = self.associations[from_node][to_node]
            self.associations[from_node][to_node] = (old + strength) / 2
        else:
            self.associations[from_node][to_node] = strength
        
        self.memory.append({
            "type": "association",
            "from": from_node,
            "to": to_node,
            "strength": strength,
            "attention": self.attention,
            "weight": self.weight,
            "temperature": self.temperature
        })
        
        self.save()
    
    def get_next_nodes(self, node: str) -> List[Tuple[str, float]]:
        if node not in self.associations:
            return []
        
        nodes = list(self.associations[node].items())
        nodes.sort(key=lambda x: x[1], reverse=True)
        return nodes
    
    def get_prev_nodes(self, node: str) -> List[Tuple[str, float]]:
        """Возвращает все узлы, которые ведут к данному (обратные связи)"""
        result = []
        for from_node, targets in self.associations.items():
            if node in targets:
                result.append((from_node, targets[node]))
        result.sort(key=lambda x: x[1], reverse=True)
        return result
    
    def build_chain(self, start_node: str, max_depth: int = None) -> List[str]:
        if max_depth is None:
            max_depth = max(1, min(20, int(self.weight * 5)))
        
        chain = [start_node]
        current = start_node
        steps_taken = 0
        visited = set([start_node])
        
        while steps_taken < max_depth - 1:
            next_nodes = self.get_next_nodes(current)
            if not next_nodes:
                break
            
            best_next, strength = next_nodes[0]
            
            if best_next in visited:
                if best_next == current or len(chain) > 1:
                    break
            
            if self.temperature > 2.0 and len(next_nodes) > 1:
                if random.random() < 0.3:
                    best_next, strength = random.choice(next_nodes[1:])
            
            self.avoid_pain(current, best_next)
            
            chain.append(best_next)
            visited.add(best_next)
            current = best_next
            steps_taken += 1
        
        return chain
    
    def build_tree(self, node: str, max_depth: int = 3, direction: str = "both") -> Dict:
        """
        Строит дерево связей от узла.
        direction: "forward" (вперёд), "backward" (назад), "both" (оба направления)
        """
        tree = {"node": node, "children": [], "parents": []}
        
        if direction in ["forward", "both"]:
            children = self.get_next_nodes(node)
            for child, strength in children[:5]:  # Ограничиваем для читаемости
                if max_depth > 1:
                    subtree = self.build_tree(child, max_depth - 1, "forward")
                else:
                    subtree = {"node": child, "children": [], "parents": []}
                subtree["strength"] = strength
                tree["children"].append(subtree)
        
        if direction in ["backward", "both"]:
            parents = self.get_prev_nodes(node)
            for parent, strength in parents[:5]:
                if max_depth > 1:
                    parent_tree = self.build_tree(parent, max_depth - 1, "backward")
                else:
                    parent_tree = {"node": parent, "children": [], "parents": []}
                parent_tree["strength"] = strength
                tree["parents"].append(parent_tree)
        
        return tree
    
    def print_tree(self, tree: Dict, indent: int = 0, prefix: str = "", is_last: bool = True, direction: str = "forward"):
        """Красиво печатает дерево"""
        if direction == "forward":
            children_key = "children"
            arrow = "→"
        else:
            children_key = "parents"
            arrow = "←"
        
        node_str = f"{tree['node']}"
        if "strength" in tree:
            node_str += f" ({tree['strength']:.1f})"
        
        if indent == 0:
            print(f"📊 ДЕРЕВО ЦЕПОЧЕК ОТ '{tree['node']}':")
            print(f"   {tree['node']}")
        else:
            connector = "└── " if is_last else "├── "
            print(f"{' ' * indent}{connector}{arrow} {node_str}")
        
        children = tree.get(children_key, [])
        for i, child in enumerate(children):
            new_indent = indent + (4 if indent > 0 else 4)
            self.print_tree(child, new_indent, "", i == len(children) - 1, direction)
    
    def explain(self, target_node: str) -> List[str]:
        """Рефлексия: показывает пути к целевому узлу"""
        paths = []
        parents = self.get_prev_nodes(target_node)
        
        for parent, strength in parents[:5]:
            chain = self.build_chain(parent)
            if target_node in chain:
                path = chain[:chain.index(target_node) + 1]
                paths.append((path, strength))
        
        return paths
    
    def plan(self, goal: str) -> List[List[str]]:
        """Планирование: показывает, что нужно сделать, чтобы достичь цели"""
        paths = self.explain(goal)
        plans = []
        for path, strength in paths:
            # Обратный путь (от начала к цели)
            plans.append((path, strength))
        return plans
    
    def predict(self, token: str, show_branches: bool = True) -> Tuple[str, List[str], List[Tuple[str, float]]]:
        if self.weight < 0.5:
            next_nodes = self.get_next_nodes(token)
            if next_nodes:
                prediction = next_nodes[0][0]
                return prediction, [token, prediction], next_nodes
            else:
                return token, [token], []
        
        branches = self.get_next_nodes(token)
        
        if not branches:
            return token, [token], []
        
        weighted_branches = []
        for node, strength in branches:
            if node in self.pain_words:
                strength = strength * 0.2
            weighted_branches.append((node, strength))
        
        weighted_branches.sort(key=lambda x: x[1], reverse=True)
        
        if self.temperature > 5.0 and len(weighted_branches) > 1:
            weights = [max(0.1, s) for _, s in weighted_branches]
            total = sum(weights)
            probs = [w/total for w in weights]
            chosen_index = random.choices(range(len(weighted_branches)), weights=weights, k=1)[0]
            chosen = weighted_branches[chosen_index][0]
        else:
            chosen = weighted_branches[0][0]
        
        rest_chain = self.build_chain(chosen)
        full_chain = [token] + rest_chain
        
        return full_chain[-1], full_chain, branches
    
    def correct(self, input_token: str, wrong_prediction: str, correct_prediction: str):
        correction_strength = self.attention * 2.0
        
        if (input_token in self.associations and 
            wrong_prediction in self.associations[input_token]):
            old_strength = self.associations[input_token][wrong_prediction]
            new_strength = old_strength / correction_strength
            self.associations[input_token][wrong_prediction] = max(0.01, new_strength)
            
            self.error_log.append({
                "input": input_token,
                "wrong": wrong_prediction,
                "correct": correct_prediction,
                "old_strength": old_strength,
                "new_strength": new_strength,
                "attention": self.attention
            })
        else:
            self.error_log.append({
                "input": input_token,
                "wrong": wrong_prediction,
                "correct": correct_prediction,
                "old_strength": 0,
                "new_strength": 0,
                "attention": self.attention
            })
        
        self.add_association(input_token, correct_prediction, correction_strength)
        
        if self.active_chain and len(self.active_chain) > 1:
            for i in range(len(self.active_chain) - 1):
                from_node = self.active_chain[i]
                to_node = self.active_chain[i + 1]
                if (from_node in self.associations and 
                    to_node in self.associations[from_node]):
                    old = self.associations[from_node][to_node]
                    self.associations[from_node][to_node] = max(0.01, old / 2.0)
        
        self.memory.append({
            "type": "correction",
            "input": input_token,
            "wrong": wrong_prediction,
            "correct": correct_prediction,
            "attention": self.attention
        })
        
        self.save()
    
    def praise(self, chain: List[str]) -> Dict:
        results = []
        for i in range(len(chain) - 1):
            from_node = chain[i]
            to_node = chain[i + 1]
            
            if from_node in self.associations and to_node in self.associations[from_node]:
                old_strength = self.associations[from_node][to_node]
                new_strength = old_strength * 1.5
                self.associations[from_node][to_node] = new_strength
                
                results.append({
                    "from": from_node,
                    "to": to_node,
                    "old": old_strength,
                    "new": new_strength
                })
                
                self.memory.append({
                    "type": "praise",
                    "from": from_node,
                    "to": to_node,
                    "old_strength": old_strength,
                    "new_strength": new_strength
                })
        
        self.save()
        return {"strengthened": results}
    
    def add_pain_word(self, word: str):
        if word not in self.pain_words:
            self.pain_words.append(word)
            print(f"  😖 Добавлено слово-триггер боли: '{word}'")
            self.save()
    
    def think(self, prompt: str) -> Dict:
        tokens = self.tokenize(prompt)
        self.active_chain = []
        results = []
        all_branches = {}
        
        for i, token in enumerate(tokens):
            prediction, chain, branches = self.predict(token)
            self.active_chain = chain
            results.append({
                "token": token,
                "prediction": prediction,
                "chain": chain,
                "attention": self.attention
            })
            all_branches[token] = branches
            
            if prediction != token:
                self.add_association(token, prediction, self.attention)
        
        if results:
            final_prediction = results[-1]["prediction"]
        else:
            final_prediction = ""
        
        return {
            "tokens": tokens,
            "results": results,
            "final_prediction": final_prediction,
            "active_chain": self.active_chain,
            "attention": self.attention,
            "branches": all_branches
        }
    
    def save(self):
        model_data = {
            "version": "1.5",
            "model_type": "LogicChain",
            "parameters": {
                "weight": self.weight,
                "temperature": self.base_temperature,
                "attention": self.attention,
                "dynamic_temp_enabled": self.dynamic_temp_enabled,
                "pain_words": self.pain_words
            },
            "brain": {
                "associations": self.associations,
                "memory_log": self.memory[-200:],
                "error_log": self.error_log[-100:]
            }
        }
        
        try:
            with open(self.model_file, 'w', encoding='utf-8') as f:
                json.dump(model_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
            return False
    
    def load(self):
        if not os.path.exists(self.model_file):
            print(f"Новая модель: {self.model_file}")
            return False
        
        try:
            with open(self.model_file, 'r', encoding='utf-8') as f:
                model_data = json.load(f)
            
            self.weight = model_data["parameters"]["weight"]
            self.base_temperature = model_data["parameters"]["temperature"]
            self.temperature = self.base_temperature
            self.attention = model_data["parameters"]["attention"]
            self.dynamic_temp_enabled = model_data["parameters"].get("dynamic_temp_enabled", True)
            self.pain_words = model_data["parameters"].get("pain_words", ["боль", "больно", "опасно", "страх", "ужас", "вред", "опасность"])
            self.associations = model_data["brain"]["associations"]
            self.memory = model_data["brain"]["memory_log"]
            self.error_log = model_data["brain"]["error_log"]
            
            print(f"Загружена модель: {self.model_file}")
            print(f"  Вес: {self.weight}, Базовая темп: {self.base_temperature}, Вним: {self.attention}")
            print(f"  Динамическая температура: {'ВКЛ' if self.dynamic_temp_enabled else 'ВЫКЛ'}")
            print(f"  Слова боли: {self.pain_words}")
            print(f"  Ассоциаций: {len(self.associations)}")
            return True
        except Exception as e:
            print(f"Ошибка загрузки: {e}")
            return False
    
    def stats(self) -> Dict:
        return {
            "total_associations": sum(len(v) for v in self.associations.values()),
            "unique_nodes": len(self.associations),
            "memory_entries": len(self.memory),
            "errors_count": len(self.error_log),
            "weight": self.weight,
            "temperature": self.temperature,
            "base_temperature": self.base_temperature,
            "attention": self.attention,
            "dynamic_temp": self.dynamic_temp_enabled,
            "pain_words": self.pain_words
        }
    
    def respond(self, user_input: str, show_branches: bool = True) -> str:
        if not user_input.strip():
            return "..."
        
        temp_info = None
        if self.dynamic_temp_enabled and not user_input.startswith("!"):
            temp_info = self.set_dynamic_temperature(user_input)
        
        result = self.think(user_input)
        
        if temp_info and show_branches:
            print(f"  🌡️  темп: {temp_info['old_temp']:.1f} → {temp_info['new_temp']:.1f} (длина {temp_info['prompt_length']} +{temp_info['random_shift']})")
        
        if show_branches and user_input in self.associations:
            branches = list(self.associations[user_input].items())
            if len(branches) > 1:
                branch_info = [f"{b[0]} ({b[1]:.1f})" for b in branches[:5]]
                print(f"  🌿 варианты: {', '.join(branch_info)}")
        
        if temp_info:
            self.reset_temperature()
        
        if result["tokens"] and result["final_prediction"] == result["tokens"][-1]:
            return f"Я не знаю, что сказать на '{user_input}'"
        
        return result["final_prediction"]


# ========== ИНТЕРАКТИВНЫЙ ЧАТ ==========
def print_help():
    print("\n" + "="*60)
    print("ДОСТУПНЫЕ КОМАНДЫ:")
    print("  !выход / !exit         - сохранить и выйти")
    print("  !стата / !stats        - статистика модели")
    print("  !помощь / !help        - эта справка")
    print("  !красная A B C         - исправить: A→B на A→C")
    print("  !обучи A B             - добавить ассоциацию A→B")
    print("  !похвала A B C ...     - укрепить цепочку A→B→C→...")
    print("  !молодец A B C ...     - то же самое")
    print("  !цепочка A             - показать всю цепочку от A")
    print("  !дерево A              - ПОКАЗАТЬ ДЕРЕВО ЦЕПОЧЕК (все связи)")
    print("  !почему A              - РЕФЛЕКСИЯ: как прийти к A")
    print("  !как достичь A         - ПЛАНИРОВАНИЕ: что нужно для A")
    print("  !память                - последние 10 событий")
    print("  !очистить              - очистить историю")
    print("  !вес X                 - изменить вес")
    print("  !темп X                - изменить базовую температуру")
    print("  !динамика on/off       - вкл/выкл динамическую температуру")
    print("  !ветвление on/off      - вкл/выкл показ ветвлений")
    print("  !боль слово            - добавить слово-триггер боли")
    print("  !сохранить             - принудительно сохранить")
    print("="*60 + "\n")

def main():
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    
    show_branching = True
    
    model_file = input(f"Введите имя файла модели [{GREEN}my_brain.mmr{RESET}]: ").strip()
    if not model_file:
        model_file = "my_brain.mmr"
    
    ai = Logic(weight=2.0, temperature=5.0, model_file=model_file, dynamic_temp=True)
    
    print("\n" + "="*60)
    print(f"{GREEN}🧠 ИИ ЗАПУЩЕН{RESET}")
    print(f"Модель: {model_file}")
    print(f"Динамическая температура: {'ВКЛ' if ai.dynamic_temp_enabled else 'ВЫКЛ'}")
    print(f"Режим ветвления: {'ВКЛ' if show_branching else 'ВЫКЛ'}")
    print(f"Избегание боли: АВТОМАТИЧЕСКИ")
    print(f"РЕФЛЕКСИЯ: !почему / !дерево / !как достичь")
    print("Просто пишите сообщения — ИИ отвечает последним словом цепочки")
    print("Введите !помощь для списка команд")
    print("="*60 + "\n")
    
    while True:
        try:
            user_input = input(f"{BLUE}Вы:{RESET} ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ["!выход", "!exit", "!quit"]:
                print(f"{GREEN}Сохраняю модель...{RESET}")
                ai.save()
                print(f"{GREEN}До свидания! 🧠{RESET}")
                break
            
            elif user_input.lower() in ["!помощь", "!help"]:
                print_help()
                continue
            
            elif user_input.lower() in ["!стата", "!stats"]:
                stats = ai.stats()
                print(f"\n{YELLOW}=== СТАТИСТИКА МОДЕЛИ ==={RESET}")
                for k, v in stats.items():
                    print(f"  {k}: {v}")
                print()
                continue
            
            elif user_input.lower() in ["!память", "!memory"]:
                print(f"\n{YELLOW}=== ПОСЛЕДНИЕ 10 СОБЫТИЙ ==={RESET}")
                for item in ai.memory[-10:]:
                    print(f"  {item}")
                print()
                continue
            
            elif user_input.lower() == "!очистить":
                ai.memory = []
                ai.error_log = []
                print(f"{GREEN}Память очищена{RESET}\n")
                ai.save()
                continue
            
            elif user_input.lower() == "!сохранить":
                ai.save()
                print(f"{GREEN}Сохранено{RESET}\n")
                continue
            
            elif user_input.lower().startswith("!ветвление"):
                parts = user_input.split()
                if len(parts) > 1:
                    if parts[1].lower() in ["on", "включить", "1", "true"]:
                        show_branching = True
                        print(f"{GREEN}Показ ветвлений ВКЛЮЧЁН{RESET}\n")
                    elif parts[1].lower() in ["off", "выключить", "0", "false"]:
                        show_branching = False
                        print(f"{GREEN}Показ ветвлений ВЫКЛЮЧЁН{RESET}\n")
                continue
            
            elif user_input.lower().startswith("!динамика"):
                parts = user_input.split()
                if len(parts) > 1:
                    if parts[1].lower() in ["on", "включить", "1", "true"]:
                        ai.dynamic_temp_enabled = True
                        print(f"{GREEN}Динамическая температура ВКЛЮЧЕНА{RESET}\n")
                    elif parts[1].lower() in ["off", "выключить", "0", "false"]:
                        ai.dynamic_temp_enabled = False
                        ai.reset_temperature()
                        print(f"{GREEN}Динамическая температура ВЫКЛЮЧЕНА. Температура фиксирована: {ai.temperature}{RESET}\n")
                continue
            
            elif user_input.lower().startswith("!боль"):
                parts = user_input.split()
                if len(parts) > 1:
                    word = parts[1]
                    ai.add_pain_word(word)
                    print(f"{GREEN}Слово '{word}' добавлено в триггеры боли{RESET}\n")
                else:
                    print(f"{RED}Формат: !боль слово{RESET}\n")
                continue
            
            elif user_input.startswith("!красная"):
                parts = user_input.split()
                if len(parts) >= 4:
                    _, inp, wrong, correct = parts[0], parts[1], parts[2], parts[3]
                    ai.correct(inp, wrong, correct)
                    print(f"{GREEN}✓ Исправлено: '{inp}' → '{wrong}' заменено на '{inp}' → '{correct}'{RESET}\n")
                else:
                    print(f"{RED}Формат: !красная A B C (исправить A→B на A→C){RESET}\n")
                continue
            
            elif user_input.startswith("!обучи") or user_input.startswith("!обучить"):
                parts = user_input.split()
                if len(parts) >= 3:
                    _, fr, to = parts[0], parts[1], parts[2]
                    ai.add_association(fr, to)
                    print(f"{GREEN}✓ Запомнено: '{fr}' → '{to}'{RESET}\n")
                else:
                    print(f"{RED}Формат: !обучи A B{RESET}\n")
                continue
            
            elif user_input.startswith("!похвала") or user_input.startswith("!молодец"):
                parts = user_input.split()
                if len(parts) >= 3:
                    chain = parts[1:]
                    result = ai.praise(chain)
                    if result["strengthened"]:
                        print(f"{GREEN}✓ Похвала! Укреплены связи:{RESET}")
                        for item in result["strengthened"]:
                            print(f"    '{item['from']}' → '{item['to']}': {item['old']:.2f} → {item['new']:.2f}")
                    else:
                        print(f"{RED}Не найдены связи в цепочке{RESET}")
                    print()
                else:
                    print(f"{RED}Формат: !похвала A B C ... (цепочка из 2+ слов){RESET}\n")
                continue
            
            elif user_input.startswith("!цепочка"):
                parts = user_input.split()
                if len(parts) >= 2:
                    _, start = parts[0], parts[1]
                    chain = ai.build_chain(start)
                    print(f"{YELLOW}Полная цепочка от '{start}':{RESET}")
                    print(f"  {' → '.join(chain)}")
                    if len(chain) > 1:
                        print(f"{GREEN}Последний элемент: {chain[-1]}{RESET}")
                    print()
                else:
                    print(f"{RED}Формат: !цепочка A{RESET}\n")
                continue
            
            elif user_input.startswith("!дерево"):
                parts = user_input.split()
                if len(parts) >= 2:
                    _, start = parts[0], parts[1]
                    depth = 3
                    if len(parts) >= 3:
                        try:
                            depth = int(parts[2])
                        except:
                            pass
                    tree = ai.build_tree(start, depth, "both")
                    ai.print_tree(tree, direction="both")
                    print()
                else:
                    print(f"{RED}Формат: !дерево A [глубина]{RESET}\n")
                continue
            
            elif user_input.startswith("!почему"):
                parts = user_input.split()
                if len(parts) >= 2:
                    _, target = parts[0], parts[1]
                    paths = ai.explain(target)
                    if paths:
                        print(f"{YELLOW}🔍 РЕФЛЕКСИЯ: Как прийти к '{target}':{RESET}")
                        for i, (path, strength) in enumerate(paths[:5]):
                            print(f"  {i+1}. {' → '.join(path)} (сила: {strength:.1f})")
                    else:
                        print(f"{RED}Нет известных путей к '{target}'{RESET}")
                    print()
                else:
                    print(f"{RED}Формат: !почему A (например, !почему деньги){RESET}\n")
                continue
            
            elif user_input.startswith("!как достичь") or user_input.startswith("!как_достичь"):
                parts = user_input.split()
                if len(parts) >= 2:
                    # Поддерживаем "!как достичь цель" и "!как_достичь цель"
                    if parts[0] == "!как" and len(parts) >= 3:
                        target = parts[2]
                    else:
                        target = parts[1]
                    
                    paths = ai.plan(target)
                    if paths:
                        print(f"{YELLOW}🎯 ПЛАНИРОВАНИЕ: Чтобы достичь '{target}', нужно:{RESET}")
                        for i, (path, strength) in enumerate(paths[:5]):
                            print(f"  {i+1}. {' → '.join(path)} (уверенность: {strength:.1f})")
                    else:
                        print(f"{RED}Нет известных способов достичь '{target}'{RESET}")
                    print()
                else:
                    print(f"{RED}Формат: !как достичь A (например, !как достичь деньги){RESET}\n")
                continue
            
            elif user_input.startswith("!вес"):
                parts = user_input.split()
                if len(parts) >= 2:
                    try:
                        new_weight = float(parts[1])
                        ai.weight = new_weight
                        ai.attention = ai.weight * ai.temperature
                        print(f"{GREEN}Вес изменён на {new_weight}. Внимание = {ai.attention}{RESET}\n")
                    except:
                        print(f"{RED}Ошибка: введите число{RESET}\n")
                continue
            
            elif user_input.startswith("!темп"):
                parts = user_input.split()
                if len(parts) >= 2:
                    try:
                        new_temp = float(parts[1])
                        ai.base_temperature = new_temp
                        ai.temperature = new_temp
                        ai.attention = ai.weight * ai.temperature
                        print(f"{GREEN}Базовая температура изменена на {new_temp}. Внимание = {ai.attention}{RESET}\n")
                    except:
                        print(f"{RED}Ошибка: введите число{RESET}\n")
                continue
            
            # Обычный диалог
            response = ai.respond(user_input, show_branching)
            
            print(f"{GREEN}ИИ:{RESET} {response}")
            
            if ai.active_chain and len(ai.active_chain) > 1:
                chain_str = ' → '.join(ai.active_chain)
                if len(ai.active_chain) > 2:
                    print(f"{YELLOW}  🔗 цепочка: {chain_str}{RESET}")
                else:
                    print(f"{YELLOW}  🔗 связь: {chain_str}{RESET}")
            print()
            
        except KeyboardInterrupt:
            print(f"\n{GREEN}Сохраняю модель...{RESET}")
            ai.save()
            print(f"{GREEN}До свидания! 🧠{RESET}")
            break
        except Exception as e:
            print(f"{RED}Ошибка: {e}{RESET}\n")

if __name__ == "__main__":
    main()
