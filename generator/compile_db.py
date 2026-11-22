import os
import re
import json
import random
from parse_sources import parse_shilde, parse_informatika_1, parse_probny_2, parse_qa_files, parse_pdf, clean_text
from build_contexts import CONTEXT_SCENARIOS

TOPICS = [
    {
        "id": "info_processes",
        "name": "Ақпаратты ұсыну және өлшеу. Ақпараттық процестер",
        "target": 5,
        "keywords": ["ақпарат", "өлшеу", "байт", "бит", "кбайт", "мбайт", "гбайт", "тбайт", "санау жүйе", "екілік", "сегіздік", "он алтылық", "ascii", "unicode", "кодтау", "шифр", "хартли", "шеннон", "дешифр", "виженер", "цезарь", "әліпби"]
    },
    {
        "id": "computer_systems",
        "name": "Компьютерлік жүйелер",
        "target": 4,
        "keywords": ["эем", "буын", "бэббидж", "лавлейс", "цузе", "нейман", "процессор", "микропроцессор", "транзистор", "шамдар", "интегралды", "ram", "rom", "bios", "cmos", "жедел жад", "сыртқы жад", "шина", "енгізу", "шығару", "операциялық жүйе", "unix", "linux", "windows", "драйвер"]
    },
    {
        "id": "logic_operations",
        "name": "Логикалық операциялар",
        "target": 2,
        "keywords": ["конъюнкция", "дизъюнкция", "инверсия", "импликация", "эквиваленция", "ақиқат кесте", "логика", "немесе", "және", "емес", "xor", "and", "or", "not", "ақиқат", "жалған", "логикалық өрнек", "де морган"]
    },
    {
        "id": "networks_security",
        "name": "Компьютерлік желілер және қауіпсіздік",
        "target": 6,
        "keywords": ["желі", "топология", "lan", "wan", "man", "wlan", "osi", "tcp/ip", "ip-адрес", "ip-мекен", "ipv4", "ipv6", "маска", "хост", "маршрутизатор", "роутер", "коммутатор", "свитч", "домен", "dns", "vpn", "эцқ", "электрондық цифрлық", "сертификат", "симметриялық", "асимметриялық", "криптография", "вирус", "брандмауэр", "firewall", "қауіпсіздік", "хэш", "rsa"]
    },
    {
        "id": "computer_graphics",
        "name": "Компьютерлік графика",
        "target": 2,
        "keywords": ["графика", "растрлық", "векторлық", "пиксель", "түс", "rgb", "cmyk", "hsb", "dpi", "ppi", "рұқсат", "bmp", "jpeg", "png", "gif", "tiff", "svg", "photoshop", "coreldraw", "paint", "қара-ақ", "түстер тереңдігі", "8k"]
    },
    {
        "id": "spreadsheets",
        "name": "Есептерді электронды кестелердің көмегімен шешу, өңдеу",
        "target": 4,
        "keywords": ["excel", "электронды кесте", "ұяшық", "сілтеме", "абсолюттік", "салыстырмалы", "аралас", "формула", "sum", "average", "count", "countif", "vlookup", "впр", "егер", "if", "диаграмма", "сүзгі", "фильтр", "жол мен баған", "calc"]
    },
    {
        "id": "databases",
        "name": "Мәліметтер қорымен жұмыс",
        "target": 4,
        "keywords": ["деректер қоры", "мәліметтер қоры", "дқбж", "субд", "sql", "select", "where", "like", "from", "join", "group by", "order by", "insert", "update", "delete", "бастапқы кілт", "сыртқы кілт", "primary key", "реляциялық", "жазба", "өріс", "индекс"]
    },
    {
        "id": "programming_ide",
        "name": "Программаларды құрудың кіріктірілген орталары",
        "target": 7,
        "keywords": ["python", "паскаль", "c++", "цикл", "for", "while", "if", "else", "elif", "массив", "тізім", "list", "append", "split", "def", "функция", "айнымалы", "жол", "string", "индекс", "range", "print", "input", "сұрыптау", "алгоритм", "фибоначчи", "факториал", "рекурсия"]
    },
    {
        "id": "web_design",
        "name": "Вебжобалау",
        "target": 4,
        "keywords": ["html", "css", "тег", "href", "src", "style", "веб", "сайт", "web", "парақша", "браузер", "javascript", "сервер", "домен", "хостинг", "http", "https", "url", "гипермәтін", "форма", "table"]
    },
    {
        "id": "text_multimedia",
        "name": "Мәтіндік құжатпен жұмыс. Бейнеконтент",
        "target": 1,
        "keywords": ["word", "мәтіндік", "құжат", "қаріп", "шрифт", "бейне", "бейнеконтент", "видео", "монтаж", "клип", "аудио", "mp4", "avi", "дыбыс", "кадр", "fps", "колонтитул", "абзац"]
    },
    {
        "id": "ai",
        "name": "Жасанды интеллект",
        "target": 1,
        "keywords": ["жасанды интеллект", "жи", "ai", "нейрон", "нейрондық", "машиналық оқыту", "синапс", "сигмоида", "терең оқыту", "үлгіні тану", "сараптамалық", "чат-бот", "nlp", "computer vision"]
    },
    {
        "id": "context",
        "name": "Мәнмәтіндік тапсырмалар (Контекст)",
        "target": 10,
        "keywords": ["мәнмәтін", "контекст", "жағдаят", "мәтінге сәйкес", "кестеге сәйкес"]
    }
]

TOPIC_MAP = {t["id"]: t["name"] for t in TOPICS}

def classify(text):
    text_lower = text.lower()
    scores = {}
    for t in TOPICS[:-1]: # exclude context from keyword classification
        s = 0
        for kw in t["keywords"]:
            if kw in text_lower:
                s += len(kw)
        scores[t["id"]] = s
    best = max(scores, key=scores.get)
    if scores[best] > 0:
        return best
    return "programming_ide"

# Pool of generic plausible distractors per topic if needed
TOPIC_DISTRACTORS = {
    "info_processes": ["8 бит", "16 бит", "1024 байт", "Unicode", "ASCII", "Екілік жүйе", "Сегіздік жүйе", "Он алтылық жүйе", "Хартли формуласы", "Шеннон формуласы"],
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

def make_distractors(topic_id, correct_ans, all_answers_in_topic):
    candidates = [a for a in all_answers_in_topic if a != correct_ans and len(a) > 0 and len(a) < 80]
    random.shuffle(candidates)
    distractors = candidates[:3]
    # Fallback to topic distractors if not enough
    pool = TOPIC_DISTRACTORS.get(topic_id, TOPIC_DISTRACTORS["programming_ide"])
    for p in pool:
        if len(distractors) >= 3:
            break
        if p != correct_ans and p not in distractors:
            distractors.append(p)
    while len(distractors) < 3:
        distractors.append(f"Басқа нұсқа {len(distractors)+1}")
    return distractors

print("Base setup ready.")
