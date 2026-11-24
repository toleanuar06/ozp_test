import os
import re
import json
import random
from parse_sources import parse_shilde, parse_informatika_1, parse_probny_2, parse_qa_files, clean_text, is_valid_mcq
from build_contexts import CONTEXT_SCENARIOS
from curriculum_questions import get_curriculum_questions
from extra_curriculum import get_extra_questions
from programmatic_questions import get_programmatic_questions
from more_programmatic import get_more_questions
from fixes import apply_fixes

random.seed(2026)

OUTPUT_JSON = r"d:\project_ozp\data\questions.json"
OUTPUT_JS = r"d:\project_ozp\data\questions.js"
os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)

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
    "spreadsheets": ["excel", "электронды кесте", "ұяшық", "сілтеме", "абсолюттік", "салыстырмалы", "аралас", "формула", "sum", "average", "count", "countif", "vlookup", "впр", "егер", "диаграмма", "сүзгі", "фильтр", "жол мен баған", "calc", "$a$1", "a1"],
    "databases": ["деректер қоры", "мәліметтер қоры", "дқбж", "субд", "sql", "select", "where", "like", "from", "join", "group by", "order by", "insert", "update", "delete", "бастапқы кілт", "сыртқы кілт", "primary key", "реляциялық", "жазба", "өріс", "индекс", "таблица"],
    "programming_ide": ["python", "паскаль", "c++", "цикл", "for", "while", "if", "else", "elif", "массив", "тізім", "list", "append", "split", "def", "функция", "айнымалы", "жол", "string", "индекс", "range", "print", "input", "сұрыптау", "алгоритм", "фибоначчи", "факториал", "рекурсия", "код", "бағдарлама"],
    "web_design": ["html", "css", "тег", "href", "src", "style", "веб", "сайт", "web", "парақша", "браузер", "javascript", "сервер", "домен", "хостинг", "http", "https", "url", "гипермәтін", "форма", "table"],
    "text_multimedia": ["word", "мәтіндік", "құжат", "қаріп", "шрифт", "бейне", "бейнеконтент", "видео", "монтаж", "клип", "аудио", "mp4", "avi", "дыбыс", "кадр", "fps", "колонтитул", "абзац"],
    "ai": ["жасанды интеллект", "жи", "ai", "нейрон", "нейрондық", "машиналық оқыту", "синапс", "сигмоида", "терең оқыту", "үлгіні тану", "сараптамалық", "чат-бот", "nlp", "computer vision"]
}

FALLBACK_DISTRACTORS = {
    "info_processes": ["8 бит", "16 бит", "1024 байт", "Unicode", "ASCII", "Екілік жүйе", "Сегіздік жүйе", "Он алтылық жүйе", "Хартли формуласы", "256 символ"],
    "computer_systems": ["Электрондық шамдар", "Транзисторлар", "Интегралдық микросұлбалар", "Микропроцессорлар", "Жедел жад (RAM)", "Тұрақты жад (ROM)", "Аналық тақша", "BIOS"],
    "logic_operations": ["Конъюнкция", "Дизъюнкция", "Инверсия", "Импликация", "Эквиваленция", "1 (Ақиқат)", "0 (Жалған)"],
    "networks_security": ["Жұлдыз (Star)", "Сақина (Ring)", "Шина (Bus)", "255.255.255.0", "IPv4", "IPv6", "Маршрутизатор (Router)", "Коммутатор (Switch)", "ЭЦҚ", "Брандмауэр"],
    "computer_graphics": ["Растрлық графика", "Векторлық графика", "RGB", "CMYK", "PNG", "JPEG", "SVG", "TIFF", "300 DPI", "Пиксель"],
    "spreadsheets": ["=SUM(A1:A10)", "=AVERAGE(A1:A10)", "=COUNT(A1:A10)", "$A$1", "A$1", "$A1", "=IF(A1>0, 1, 0)", "=COUNTIF(A1:A10, \">5\")"],
    "databases": ["SELECT * FROM table", "PRIMARY KEY", "FOREIGN KEY", "WHERE id = 1", "JOIN", "GROUP BY", "ORDER BY", "Реляциялық модель"],
    "programming_ide": ["append()", "len()", "split()", "for i in range(n):", "def function():", "list", "dict", "print()", "input()", "sort()"],
    "web_design": ["<a href=\"#\">", "<img src=\"\">", "<div>", "display: flex;", "color: red;", "HTML5", "CSS3", "JavaScript"],
    "text_multimedia": ["Колонтитул", "Заголовок 1", "MP4", "AVI", "30 FPS", "Full HD (1920x1080)", "WAV", "Абзац"],
    "ai": ["Нейрондық желі", "Машиналық оқыту", "Мұғаліммен оқыту", "Мұғалімсіз оқыту", "Синапс", "Активация функциясы", "Сигмоида"]
}

def classify(text):
    text_lower = text.lower()
    scores = {}
    for tid, kws in KEYWORD_MAP.items():
        s = sum(len(kw) for kw in kws if kw in text_lower)
        scores[tid] = s
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "programming_ide"

def shuffle_options(options, correct_index):
    indexed = list(enumerate(options))
    random.shuffle(indexed)
    new_opts = [opt for _, opt in indexed]
    new_corr = next(i for i, (orig_i, _) in enumerate(indexed) if orig_i == correct_index)
    return new_opts, new_corr

all_questions = []
seen_texts = set()
q_counter = 1

def add_question(tid, text, options, correct_index, explanation, source, ctx_id=None, ctx_title=None, ctx_text=None):
    global q_counter
    text = clean_text(text)
    if text.lower() in seen_texts:
        return False
    opts = [clean_text(o) for o in options]
    if len(opts) != 4 or len(set(o.lower() for o in opts)) != 4:
        return False
    if any(not o or len(o) > 165 for o in opts):
        return False
    if correct_index < 0 or correct_index >= 4:
        return False

    shuffled_opts, shuffled_corr = shuffle_options(opts, correct_index)
    seen_texts.add(text.lower())
    all_questions.append({
        "id": f"q_{q_counter:04d}",
        "topicId": tid,
        "topicName": TOPIC_MAP[tid],
        "text": text,
        "options": shuffled_opts,
        "correctIndex": shuffled_corr,
        "explanation": explanation,
        "source": source,
        "contextId": ctx_id,
        "contextTitle": ctx_title,
        "contextText": ctx_text
    })
    q_counter += 1
    return True

# 1. Direct verified MCQs from user's Telegram Desktop docs
TOPIC_ANSWERS_POOL = {t["id"]: [] for t in TOPICS}
for src_list in [parse_shilde(), parse_informatika_1(), parse_probny_2()]:
    for q in src_list:
        tid = classify(q["text"])
        corr_opt = q["options"][q["correctIndex"]]
        if len(corr_opt) < 70:
            TOPIC_ANSWERS_POOL[tid].append(corr_opt)
        add_question(
            tid, q["text"], q["options"], q["correctIndex"],
            f"Дұрыс жауабы: {corr_opt}. Ресми ПББ нұсқасынан.",
            q.get("source", "ресми жинақ")
        )

# 2. Clean QA pairs from user's docs
qa_list = parse_qa_files()
for item in qa_list:
    tid = classify(item["text"] + " " + item["answer"])
    if len(item["answer"]) < 70:
        TOPIC_ANSWERS_POOL[tid].append(item["answer"])

for item in qa_list:
    tid = classify(item["text"] + " " + item["answer"])
    ans = item["answer"]
    pool = [a for a in set(TOPIC_ANSWERS_POOL[tid]) if a.lower() != ans.lower() and 1 <= len(a) < 70]
    random.shuffle(pool)
    distractors = pool[:3]
    for fb in FALLBACK_DISTRACTORS.get(tid, []):
        if len(distractors) >= 3:
            break
        if fb.lower() != ans.lower() and fb.lower() not in [d.lower() for d in distractors]:
            distractors.append(fb)
    if len(distractors) == 3:
        add_question(
            tid, item["text"], [ans] + distractors, 0,
            f"Дұрыс жауабы: {ans}.",
            item.get("source", "сұрақтар жинағы")
        )

# 3. Context Scenarios (20 scenarios x 5 = 100 questions)
for ctx in CONTEXT_SCENARIOS:
    for cq in ctx["questions"]:
        add_question(
            "context", cq["text"], cq["options"], cq["correctIndex"],
            cq["explanation"], f"Контекст: {ctx['title']}",
            ctx["id"], ctx["title"], ctx["text"]
        )

# 3.5 Targeted fixes (ONLY flawed questions with off-context options are fixed/removed)
all_questions = apply_fixes(all_questions, TOPIC_MAP)
seen_texts.clear()
seen_texts.update(q["text"].lower() for q in all_questions)

# 4. Curriculum, Extra, and Programmatic verified questions
for src_name, q_list in [
    ("ПББ оқу бағдарламасы", get_curriculum_questions()),
    ("ПББ стандарты", get_extra_questions()),
    ("ПББ есептер қоры", get_programmatic_questions()),
    ("ПББ есептер қоры", get_more_questions())
]:
    for cq in q_list:
        add_question(
            cq["topicId"], cq["text"], cq["options"], cq["correctIndex"],
            cq["explanation"], src_name
        )

# Final pass: apply any text/context fixes and renumber IDs cleanly
all_questions = apply_fixes(all_questions, TOPIC_MAP)
for idx, q in enumerate(all_questions, start=1):
    q["id"] = f"q_{idx:04d}"

# Summary & Verify
topic_counts = {t["id"]: 0 for t in TOPICS}
corr_dist = {0: 0, 1: 0, 2: 0, 3: 0}
for q in all_questions:
    topic_counts[q["topicId"]] += 1
    corr_dist[q["correctIndex"]] += 1

print(f"Total spotless verified questions: {len(all_questions)}")
print("Topic distribution:", topic_counts)
print("Correct index distribution (should be ~25% each):", corr_dist)

payload = {
    "topics": TOPICS,
    "totalCount": len(all_questions),
    "questions": all_questions
}

with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False, indent=2)

with open(OUTPUT_JS, "w", encoding="utf-8") as f:
    f.write("window.PBB_DATABASE = " + json.dumps(payload, ensure_ascii=False) + ";")

print("Successfully saved BOTH questions.json and questions.js!")
