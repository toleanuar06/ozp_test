import os
import re
import json
import random
from parse_sources import parse_shilde, parse_informatika_1, parse_probny_2, parse_qa_files, parse_pdf, clean_text
from build_contexts import CONTEXT_SCENARIOS
from curriculum_questions import get_curriculum_questions
from extra_curriculum import get_extra_questions

OUTPUT_FILE = r"d:\project_ozp\data\questions.json"
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

TOPICS = [
    {"id": "info_processes", "name": "Ақпаратты ұсыну және өлшеу. Ақпараттық процестер", "target": 5},
    {"id": "computer_systems", "name": "Компьютерлік жүйелер", "target": 4},
    {"id": "logic_operations", "name": "Логикалық операциялар", "target": 2},
    {"id": "networks_security", "name": "Компьютерлік желілер және қауіпсіздік", "target": 6},
    {"id": "computer_graphics", "name": "Компьютерлік графика", "target": 2},
    {"id": "spreadsheets", "name": "Есептерді электронды кестелердің көмегімен шешу, өңдеу", "target": 4},
    {"id": "databases", "name": "Мәліметтер қорымен жұмыс", "target": 4},
    {"id": "programming_ide", "name": "Программаларды құрудың кіріктірілген орталары", "target": 7},
    {"id": "web_design", "name": "Вебжобалау", "target": 4},
    {"id": "text_multimedia", "name": "Мәтіндік құжатпен жұмыс. Бейнеконтент", "target": 1},
    {"id": "ai", "name": "Жасанды интеллект", "target": 1},
    {"id": "context", "name": "Мәнмәтіндік тапсырмалар (Контекст)", "target": 10}
]

TOPIC_MAP = {t["id"]: t["name"] for t in TOPICS}

KEYWORD_MAP = {
    "info_processes": ["ақпарат", "өлшеу", "байт", "бит", "кбайт", "мбайт", "гбайт", "тбайт", "санау жүйе", "екілік", "сегіздік", "он алтылық", "ascii", "unicode", "кодтау", "шифр", "хартли", "шеннон", "дешифр", "виженер", "цезарь", "әліпби", "хабарлама"],
    "computer_systems": ["эем", "буын", "бэббидж", "лавлейс", "цузе", "нейман", "процессор", "микропроцессор", "транзистор", "шамдар", "интегралды", "ram", "rom", "bios", "cmos", "жедел жад", "сыртқы жад", "шина", "енгізу", "шығару", "операциялық жүйе", "unix", "linux", "windows", "драйвер", "аналық тақша", "кэш", "жады"],
    "logic_operations": ["конъюнкция", "дизъюнкция", "инверсия", "импликация", "эквиваленция", "ақиқат кесте", "логика", "немесе", "және", "емес", "xor", "and", "or", "not", "ақиқат", "жалған", "логикалық өрнек", "де морган"],
    "networks_security": ["желі", "топология", "lan", "wan", "man", "wlan", "osi", "tcp/ip", "ip-адрес", "ip-мекен", "ipv4", "ipv6", "маска", "хост", "маршрутизатор", "роутер", "коммутатор", "свитч", "домен", "dns", "vpn", "эцқ", "электрондық цифрлық", "сертификат", "симметриялық", "асимметриялық", "криптография", "вирус", "брандмауэр", "firewall", "қауіпсіздік", "хэш", "rsa", "сымсыз", "wi-fi", "фишинг", "ddos"],
    "computer_graphics": ["графика", "растрлық", "векторлық", "пиксель", "түс", "rgb", "cmyk", "hsb", "dpi", "ppi", "рұқсат", "bmp", "jpeg", "png", "gif", "tiff", "svg", "photoshop", "coreldraw", "paint", "қара-ақ", "түстер тереңдігі", "8k", "тұнықтылығы"],
    "spreadsheets": ["excel", "электронды кесте", "ұяшық", "сілтеме", "абсолюттік", "салыстырмалы", "аралас", "формула", "sum", "average", "count", "countif", "vlookup", "впр", "егер", "if", "диаграмма", "сүзгі", "фильтр", "жол мен баған", "calc", "$a$1", "a1"],
    "databases": ["деректер қоры", "мәліметтер қоры", "дқбж", "субд", "sql", "select", "where", "like", "from", "join", "group by", "order by", "insert", "update", "delete", "бастапқы кілт", "сыртқы кілт", "primary key", "реляциялық", "жазба", "өріс", "индекс", "таблица"],
    "programming_ide": ["python", "паскаль", "c++", "цикл", "for", "while", "if", "else", "elif", "массив", "тізім", "list", "append", "split", "def", "функция", "айнымалы", "жол", "string", "индекс", "range", "print", "input", "сұрыптау", "алгоритм", "фибоначчи", "факториал", "рекурсия", "код", "бағдарлама"],
    "web_design": ["html", "css", "тег", "href", "src", "style", "веб", "сайт", "web", "парақша", "браузер", "javascript", "сервер", "домен", "хостинг", "http", "https", "url", "гипермәтін", "форма", "table"],
    "text_multimedia": ["word", "мәтіндік", "құжат", "қаріп", "шрифт", "бейне", "бейнеконтент", "видео", "монтаж", "клип", "аудио", "mp4", "avi", "дыбыс", "кадр", "fps", "колонтитул", "абзац"],
    "ai": ["жасанды интеллект", "жи", "ai", "нейрон", "нейрондық", "машиналық оқыту", "синапс", "сигмоида", "терең оқыту", "үлгіні тану", "сараптамалық", "чат-бот", "nlp", "computer vision"]
}

def classify(text):
    text_lower = text.lower()
    scores = {}
    for tid, kws in KEYWORD_MAP.items():
        s = 0
        for kw in kws:
            if kw in text_lower:
                s += len(kw)
        scores[tid] = s
    best = max(scores, key=scores.get)
    if scores[best] > 0:
        return best
    return "programming_ide"

# Pool of answers per topic to build good distractors
TOPIC_ANSWERS_POOL = {t["id"]: [] for t in TOPICS}

all_questions = []
q_counter = 1

# 1. Add direct MCQs from parsed sources
raw_sources = [
    parse_shilde(),
    parse_informatika_1(),
    parse_probny_2(),
    parse_pdf()
]

for src_list in raw_sources:
    for q in src_list:
        tid = classify(q["text"])
        corr_opt = q["options"][q["correctIndex"]]
        TOPIC_ANSWERS_POOL[tid].append(corr_opt)
        all_questions.append({
            "id": f"q_{q_counter:04d}",
            "topicId": tid,
            "topicName": TOPIC_MAP[tid],
            "text": q["text"],
            "options": q["options"],
            "correctIndex": q["correctIndex"],
            "explanation": f"Дұрыс жауабы: {corr_opt}. ПББ стандартына сәйкес нақты анықтама.",
            "source": q.get("source", "ресми жинақ"),
            "contextId": None,
            "contextTitle": None,
            "contextText": None
        })
        q_counter += 1

print(f"Added {len(all_questions)} direct source MCQs.")

# 2. Add QA pairs with synthesized distractors
qa_list = parse_qa_files()
print(f"Processing {len(qa_list)} QA pairs...")

for item in qa_list:
    text = item["text"]
    ans = item["answer"]
    tid = classify(text + " " + ans)
    TOPIC_ANSWERS_POOL[tid].append(ans)

for item in qa_list:
    text = item["text"]
    ans = item["answer"]
    tid = classify(text + " " + ans)
    
    # Pick 3 distractors from same topic or generic
    pool = [a for a in set(TOPIC_ANSWERS_POOL[tid]) if a != ans and len(a) > 0 and len(a) < 90]
    random.shuffle(pool)
    distractors = pool[:3]
    while len(distractors) < 3:
        distractors.append(f"Балама нұсқа {len(distractors)+1}")
        
    options = [ans] + distractors
    # Shuffle options randomly
    corr_idx = random.randint(0, 3)
    options[0], options[corr_idx] = options[corr_idx], options[0]
    
    all_questions.append({
        "id": f"q_{q_counter:04d}",
        "topicId": tid,
        "topicName": TOPIC_MAP[tid],
        "text": text,
        "options": options,
        "correctIndex": corr_idx,
        "explanation": f"Дұрыс жауабы: {ans}.",
        "source": item.get("source", "сұрақтар жинағы"),
        "contextId": None,
        "contextTitle": None,
        "contextText": None
    })
    q_counter += 1

print(f"Total questions after QA conversion: {len(all_questions)}")

# 3. Add Context Scenarios (Topic 12)
for ctx in CONTEXT_SCENARIOS:
    cid = ctx["id"]
    ctitle = ctx["title"]
    ctext = ctx["text"]
    for cq in ctx["questions"]:
        all_questions.append({
            "id": f"q_{q_counter:04d}",
            "topicId": "context",
            "topicName": TOPIC_MAP["context"],
            "text": cq["text"],
            "options": cq["options"],
            "correctIndex": cq["correctIndex"],
            "explanation": cq["explanation"],
            "source": f"Контекст: {ctitle}",
            "contextId": cid,
            "contextTitle": ctitle,
            "contextText": ctext
        })
        q_counter += 1

# 4. Add Curriculum base questions
curr_qs = get_curriculum_questions()
for cq in curr_qs:
    tid = cq["topicId"]
    all_questions.append({
        "id": f"q_{q_counter:04d}",
        "topicId": tid,
        "topicName": TOPIC_MAP[tid],
        "text": cq["text"],
        "options": cq["options"],
        "correctIndex": cq["correctIndex"],
        "explanation": cq["explanation"],
        "source": "ПББ оқу бағдарламасы",
        "contextId": None,
        "contextTitle": None,
        "contextText": None
    })
    q_counter += 1

# 5. Add Extra curriculum questions
extra_qs = get_extra_questions()
for eq in extra_qs:
    tid = eq["topicId"]
    all_questions.append({
        "id": f"q_{q_counter:04d}",
        "topicId": tid,
        "topicName": TOPIC_MAP[tid],
        "text": eq["text"],
        "options": eq["options"],
        "correctIndex": eq["correctIndex"],
        "explanation": eq["explanation"],
        "source": "ПББ стандарты",
        "contextId": None,
        "contextTitle": None,
        "contextText": None
    })
    q_counter += 1

print(f"Total questions after extra curriculum: {len(all_questions)}")

# Check counts per topic
topic_counts = {t["id"]: 0 for t in TOPICS}
for q in all_questions:
    topic_counts[q["topicId"]] += 1

print("Current distribution:", topic_counts)

# Save to questions.json
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump({
        "topics": TOPICS,
        "totalCount": len(all_questions),
        "questions": all_questions
    }, f, ensure_ascii=False, indent=2)

print(f"Successfully wrote {len(all_questions)} questions to {OUTPUT_FILE}!")
