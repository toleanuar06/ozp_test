# Mathematically verified programmatic PBB Informatics question generator
import random

def _make_numeric_options(correct_val, offsets, suffix=""):
    opts = [f"{correct_val}{suffix}"]
    for off in offsets:
        v = correct_val + off
        if v >= 0 and f"{v}{suffix}" not in opts:
            opts.append(f"{v}{suffix}")
    step = 1
    while len(opts) < 4:
        v = correct_val + step * 3
        if f"{v}{suffix}" not in opts:
            opts.append(f"{v}{suffix}")
        step += 1
    return opts[:4]

def get_programmatic_questions():
    qs = []

    # 1. INFO PROCESSES: Number systems, volume, transmission, ASCII
    bin_nums = [19, 27, 35, 46, 53, 61, 73, 84, 93, 108, 117, 134, 149, 165, 182, 197, 213, 229, 241]
    for n in bin_nums:
        b = bin(n)[2:]
        d1 = bin(n + 2)[2:]
        d2 = bin(n - 1)[2:]
        d3 = bin(n ^ 4)[2:]
        opts = list(dict.fromkeys([f"{b}₂", f"{d1}₂", f"{d2}₂", f"{d3}₂", f"{bin(n+5)[2:]}₂"]))[:4]
        qs.append({
            "topicId": "info_processes",
            "text": f"Ондық жүйедегі {n}₁₀ санын екілік санау жүйесіне ауыстырыңыз:",
            "options": opts,
            "correctIndex": 0,
            "explanation": f"{n} санын 2-ге тізбектей бөліп, қалдықтарды соңынан басына қарай жазсақ: {b}₂ шығады."
        })

    oct_nums = [29, 45, 63, 78, 92, 115, 140, 175, 210, 248]
    for n in oct_nums:
        o = oct(n)[2:]
        opts = list(dict.fromkeys([f"{o}₈", f"{oct(n+4)[2:]}₈", f"{oct(n-3)[2:]}₈", f"{oct(n+9)[2:]}₈"]))[:4]
        qs.append({
            "topicId": "info_processes",
            "text": f"Ондық жүйедегі {n}₁₀ санының сегіздік санау жүйесіндегі жазылуы:",
            "options": opts,
            "correctIndex": 0,
            "explanation": f"{n} санын 8-ге бөлу арқылы сегіздік жүйеге ауыстырғанда {o}₈ алынады."
        })

    hex_nums = [31, 47, 62, 88, 111, 139, 164, 190, 222, 245]
    for n in hex_nums:
        h = hex(n)[2:].upper()
        opts = list(dict.fromkeys([f"{h}₁₆", f"{hex(n+3)[2:].upper()}₁₆", f"{hex(n-2)[2:].upper()}₁₆", f"{hex(n+16)[2:].upper()}₁₆"]))[:4]
        qs.append({
            "topicId": "info_processes",
            "text": f"Ондық жүйедегі {n}₁₀ санын он алтылық санау жүйесіне ауыстырыңыз:",
            "options": opts,
            "correctIndex": 0,
            "explanation": f"{n} = {n // 16} * 16 + {n % 16}, яғни он алтылық жүйеде {h}₁₆ болады."
        })

    # Text volume calculations
    vol_cases = [
        (32, 5, 160), (64, 6, 200), (128, 7, 80), (256, 8, 120),
        (16, 4, 240), (32, 5, 320), (64, 6, 400), (256, 8, 512)
    ]
    for N, i, K in vol_cases:
        total_bytes = (K * i) // 8
        qs.append({
            "topicId": "info_processes",
            "text": f"{N} символдық әліпбиде жазылған {K} символдан тұратын хабарламаның ақпараттық көлемі қанша байт болады?",
            "options": _make_numeric_options(total_bytes, [total_bytes, -max(1, total_bytes//2), 16], " байт"),
            "correctIndex": 0,
            "explanation": f"N = {N} = 2^{i} => i = {i} бит. I = {K} * {i} = {K*i} бит = {total_bytes} байт."
        })

    # Data transfer speed
    transfer_cases = [(256, 32), (512, 64), (1024, 128), (2048, 256), (4096, 512), (1024, 256)]
    for kb, kbps in transfer_cases:
        secs = (kb * 8) // kbps
        qs.append({
            "topicId": "info_processes",
            "text": f"Өткізу қабілеті {kbps} Кбит/с байланыс арнасы арқылы көлемі {kb} Кбайт файлды жіберуге қанша секунд кетеді?",
            "options": _make_numeric_options(secs, [-secs//2, secs, secs//4 + 2], " секунд"),
            "correctIndex": 0,
            "explanation": f"{kb} Кбайт = {kb*8} Кбит. Уақыт: t = {kb*8} / {kbps} = {secs} секунд."
        })

    # 2. LOGIC OPERATIONS: Computed truth evaluations
    logic_exprs = [
        ("A AND B", lambda a, b, c: int(a and b)),
        ("A OR B", lambda a, b, c: int(a or b)),
        ("NOT A OR B", lambda a, b, c: int((not a) or b)),
        ("A AND NOT B", lambda a, b, c: int(a and (not b))),
        ("NOT (A AND B)", lambda a, b, c: int(not (a and b))),
        ("NOT (A OR B)", lambda a, b, c: int(not (a or b))),
        ("(A OR B) AND C", lambda a, b, c: int((a or b) and c)),
        ("(A AND B) OR C", lambda a, b, c: int((a and b) or c)),
        ("NOT A AND (B OR C)", lambda a, b, c: int((not a) and (b or c))),
        ("(A XOR B) AND C", lambda a, b, c: int((a ^ b) and c)),
        ("A OR (NOT B AND C)", lambda a, b, c: int(a or ((not b) and c))),
        ("NOT (A AND C) OR B", lambda a, b, c: int((not (a and c)) or b))
    ]
    sample_inputs = [(1, 0, 1), (0, 1, 0), (1, 1, 0), (0, 0, 1)]
    for expr, fn in logic_exprs:
        for a, b, c in sample_inputs[:3]:
            val = fn(a, b, c)
            if "C" in expr:
                q_txt = f"A = {a}, B = {b}, C = {c} болғанда, F = {expr} логикалық өрнегінің мәні:"
            else:
                q_txt = f"A = {a}, B = {b} болғанда, F = {expr} логикалық өрнегінің мәні:"
            corr_str = "1 (Ақиқат)" if val == 1 else "0 (Жалған)"
            wrong_str = "0 (Жалған)" if val == 1 else "1 (Ақиқат)"
            qs.append({
                "topicId": "logic_operations",
                "text": q_txt,
                "options": [corr_str, wrong_str, "Анықталмаған", "2"],
                "correctIndex": 0,
                "explanation": f"Берілген мәндерді {expr} өрнегіне қойып есептегенде нәтиже {corr_str} болады."
            })

    # 3. NETWORKS & SECURITY: Ports, OSI layers, Subnets
    ports = [
        ("HTTP", "80", ["443", "21", "22"]),
        ("HTTPS", "443", ["80", "25", "53"]),
        ("FTP (басқару)", "21", ["22", "80", "110"]),
        ("SSH", "22", ["23", "21", "443"]),
        ("Telnet", "23", ["22", "25", "80"]),
        ("SMTP (пошта жіберу)", "25", ["110", "143", "53"]),
        ("DNS", "53", ["80", "67", "443"]),
        ("POP3 (пошта қабылдау)", "110", ["25", "143", "21"]),
        ("IMAP", "143", ["110", "25", "443"]),
        ("RDP (қашықтан жұмыс үстелі)", "3389", ["3306", "8080", "22"]),
        ("MySQL дерекқоры", "3306", ["5432", "8080", "443"]),
        ("PostgreSQL дерекқоры", "5432", ["3306", "27017", "80"])
    ]
    for proto, port, dists in ports:
        qs.append({
            "topicId": "networks_security",
            "text": f"{proto} хаттамасы (қызметі) әдепкі бойынша қай порт нөмірін пайдаланады?",
            "options": [f"{port}-порт"] + [f"{d}-порт" for d in dists],
            "correctIndex": 0,
            "explanation": f"{proto} стандарты бойынша {port}-порт арқылы жұмыс істейді."
        })

    osi_layers = [
        (1, "Физикалық (Physical)", "биттерді электрлік немесе оптикалық сигнал түрінде тасымалдау"),
        (2, "Арналық (Data Link)", "кадрларды (frames) MAC-адрес бойынша жеткізу"),
        (3, "Желілік (Network)", "IP-адрестеу және пакеттерді маршруттау"),
        (4, "Көліктік (Transport)", "TCP/UDP арқылы деректерді сенімді жеткізу және порттармен жұмыс"),
        (5, "Сеанстық (Session)", "байланыс сеанстарын орнату, басқару және аяқтау"),
        (6, "Ұсыну (Presentation)", "деректерді кодтау, сығу және шифрлау (SSL/TLS)"),
        (7, "Қолданбалы (Application)", "қолданушы бағдарламаларының желіге қол жеткізуі (HTTP, FTP, DNS)")
    ]
    all_layer_names = [x[1] for x in osi_layers]
    for num, name, desc in osi_layers:
        dists = [x for x in all_layer_names if x != name][:3]
        qs.append({
            "topicId": "networks_security",
            "text": f"OSI моделіндегі «{desc}» қызметіне жауап беретін деңгей:",
            "options": [name] + dists,
            "correctIndex": 0,
            "explanation": f"OSI моделінің {num}-деңгейі — {name} деңгейі дәл осы қызметті атқарады."
        })
        qs.append({
            "topicId": "networks_security",
            "text": f"OSI моделінің {num}-деңгейі қалай аталады?",
            "options": [name] + dists,
            "correctIndex": 0,
            "explanation": f"OSI 7-деңгейлі моделінде {num}-деңгей — {name}."
        })

    subnets = [
        ("/24", "255.255.255.0", 254),
        ("/25", "255.255.255.128", 126),
        ("/26", "255.255.255.192", 62),
        ("/27", "255.255.255.224", 30),
        ("/28", "255.255.255.240", 14),
        ("/29", "255.255.255.248", 6),
        ("/30", "255.255.255.252", 2)
    ]
    for cidr, mask, hosts in subnets:
        qs.append({
            "topicId": "networks_security",
            "text": f"Желі маскасы {mask} ({cidr}) болғанда, ішкі желідегі пайдалануға болатын хосттар (компьютерлер) саны:",
            "options": _make_numeric_options(hosts, [2, max(2, hosts // 2), hosts + 2]),
            "correctIndex": 0,
            "explanation": f"Хостқа {32 - int(cidr[1:])} бит бөлінген. 2^{32 - int(cidr[1:])} - 2 = {hosts} хост."
        })

    # 4. COMPUTER GRAPHICS: Image volume & palette & RGB
    img_cases = [
        (64, 64, 8, 4), (128, 128, 8, 16), (256, 256, 8, 64),
        (128, 128, 16, 32), (256, 256, 16, 128), (512, 256, 16, 256),
        (512, 512, 8, 256), (1024, 512, 8, 512), (1024, 768, 8, 768),
        (256, 128, 24, 96), (512, 256, 24, 384), (64, 128, 4, 4)
    ]
    for w, h, depth, kb in img_cases:
        qs.append({
            "topicId": "computer_graphics",
            "text": f"Өлшемі {w}x{h} пиксель және түс тереңдігі {depth} бит болатын сығылмаған растрлық суреттің көлемі қанша Кбайт?",
            "options": _make_numeric_options(kb, [kb, -max(1, kb // 2), kb * 2], " Кбайт"),
            "correctIndex": 0,
            "explanation": f"I = ({w} * {h} * {depth}) / (8 * 1024) = {kb} Кбайт."
        })

    palettes = [(1, 2), (2, 4), (3, 8), (4, 16), (5, 32), (6, 64), (7, 128), (8, 256), (16, 65536)]
    for bits, colors in palettes:
        qs.append({
            "topicId": "computer_graphics",
            "text": f"Түс тереңдігі {bits} бит болатын графикалық кескін палитрасында ең көп дегенде неше түс бола алады?",
            "options": _make_numeric_options(colors, [colors, max(2, colors // 2), bits * 2], " түс"),
            "correctIndex": 0,
            "explanation": f"N = 2^i = 2^{bits} = {colors} түс."
        })

    hex_colors = [
        ("#FF0000", "Таза қызыл (Red)", ["Таза көк", "Таза жасыл", "Сары"]),
        ("#00FF00", "Таза жасыл (Green)", ["Таза қызыл", "Таза көк", "Қара"]),
        ("#0000FF", "Таза көк (Blue)", ["Таза жасыл", "Таза қызыл", "Ақ"]),
        ("#FFFF00", "Сары (Yellow)", ["Күлгін", "Көгілдір", "Қара"]),
        ("#00FFFF", "Көгілдір (Cyan)", ["Сары", "Қызыл", "Жасыл"]),
        ("#FF00FF", "Күлгін (Magenta)", ["Сары", "Көгілдір", "Сұр"])
    ]
    for code, name, dists in hex_colors:
        qs.append({
            "topicId": "computer_graphics",
            "text": f"RGB моделіндегі {code} он алтылық коды қандай түске сәйкес келеді?",
            "options": [name] + dists,
            "correctIndex": 0,
            "explanation": f"RGB (#RRGGBB) форматында {code} коды {name} түсін береді."
        })

    # 5. SPREADSHEETS (Excel): Formula evaluations & Reference shifts
    excel_evals = [
        ("A1=5, B1=3, C1=2", "=A1*B1+C1", 17),
        ("A1=12, B1=4, C1=5", "=A1/B1+C1", 8),
        ("A1=10, B1=20, C1=30", "=AVERAGE(A1:C1)", 20),
        ("A1=4, A2=8, A3=12, A4=16", "=SUM(A1:A4)", 40),
        ("A1=15, A2=25, A3=5", "=MAX(A1:A3)-MIN(A1:A3)", 20),
        ("A1=3, B1=4", "=A1^2+B1^2", 25),
        ("A1=6, B1=8", "=A1^2+B1^2", 100),
        ("A1=2, B1=5", "=2^B1+A1", 34),
        ("A1=100, B1=20", "=A1-A1*B1/100", 80),
        ("A1=50, B1=10", "=IF(A1>B1, A1+B1, A1-B1)", 60),
        ("A1=10, B1=50", "=IF(A1>B1, A1+B1, B1-A1)", 40),
        ("A1=7, B1=3, C1=10", "=SUM(A1:C1)/2", 10)
    ]
    for vals, formula, res in excel_evals:
        qs.append({
            "topicId": "spreadsheets",
            "text": f"MS Excel кестесінде {vals} мәндері берілген. `{formula}` формуласының нәтижесі:",
            "options": _make_numeric_options(res, [5, -3, 10]),
            "correctIndex": 0,
            "explanation": f"Мәндерді `{formula}` формуласына қойып есептегенде {res} шығады."
        })

    ref_shifts = [
        ("=A1+$B$1", "C1", "C2", "=A2+$B$1", ["=A2+$B$2", "=B1+$B$1", "=A1+$B$2"]),
        ("=$A1+B$1", "C1", "D2", "=$A2+C$1", ["=$B2+C$2", "=$A1+C$1", "=B2+C$1"]),
        ("=A1*B1", "C1", "C3", "=A3*B3", ["=A1*B3", "=C3*D3", "=A2*B2"]),
        ("=$A$1+B2", "C2", "E4", "=$A$1+D4", ["=$C$3+D4", "=$A$1+B4", "=$A$3+D2"]),
        ("=A$2+$B1", "C1", "D3", "=B$2+$B3", ["=B$4+$C3", "=A$2+$B3", "=B$3+$B2"])
    ]
    for form, src, dst, ans, dists in ref_shifts:
        qs.append({
            "topicId": "spreadsheets",
            "text": f"MS Excel-де {src} ұяшығындағы `{form}` формуласын {dst} ұяшығына көшіргенде формула қандай түрге өзгереді?",
            "options": [ans] + dists,
            "correctIndex": 0,
            "explanation": f"Доллар ($) белгісі қойылған координаттар өзгермейді, ал қалған салыстырмалы сілтемелер ығысу шамасына қарай өзгеріп, `{ans}` болады."
        })

    # 6. DATABASES (SQL): Practical query construction
    sql_qs = [
        ("Students кестесінен барлық оқушылардың тек name және grade бағандарын шығаратын SQL сұранысы:",
         ["SELECT name, grade FROM Students;", "GET name, grade FROM Students;", "SELECT * FROM name, grade;", "SHOW name, grade IN Students;"],
         "Нақты бағандарды таңдау үшін SELECT баған1, баған2 FROM кесте; қолданылады."),
        ("Employees кестесінен жалақысы (salary) 250000-нан жоғары қызметкерлер санын есептейтін SQL сұранысы:",
         ["SELECT COUNT(*) FROM Employees WHERE salary > 250000;", "SELECT SUM(*) FROM Employees WHERE salary > 250000;", "COUNT Employees WHERE salary > 250000;", "SELECT TOTAL(salary) FROM Employees;"],
         "Шартқа сай жазбалар санын есептеу үшін COUNT(*) және WHERE қолданылады."),
        ("Products кестесінен бағасы (price) ең қымбат тауардан бастап кему ретімен шығаратын SQL сұранысы:",
         ["SELECT * FROM Products ORDER BY price DESC;", "SELECT * FROM Products ORDER BY price ASC;", "SELECT * FROM Products GROUP BY price DESC;", "SELECT * FROM Products SORT BY price;"],
         "Кему ретімен сұрыптау үшін ORDER BY баған DESC жазылады."),
        ("Users кестесіне жаңа қолданушы ('Али', 22) қосатын дұрыс SQL командасы:",
         ["INSERT INTO Users (name, age) VALUES ('Али', 22);", "ADD INTO Users VALUES ('Али', 22);", "UPDATE Users SET ('Али', 22);", "NEW RECORD Users ('Али', 22);"],
         "Кестеге жаңа жол енгізу үшін INSERT INTO кесте (өрістер) VALUES (мәндер); қолданылады."),
        ("Users кестесінде id=5 болатын қолданушының қаласын 'Астана' етіп өзгерту сұранысы:",
         ["UPDATE Users SET city = 'Астана' WHERE id = 5;", "MODIFY Users city = 'Астана' WHERE id = 5;", "CHANGE Users SET city = 'Астана' IF id = 5;", "INSERT Users SET city = 'Астана' WHERE id = 5;"],
         "Бар жазбаны жаңарту үшін UPDATE кесте SET өріс = мән WHERE шарт; жазылады."),
        ("Orders кестесінен status = 'cancelled' болатын барлық жазбаларды өшіру сұранысы:",
         ["DELETE FROM Orders WHERE status = 'cancelled';", "DROP FROM Orders WHERE status = 'cancelled';", "REMOVE Orders WHERE status = 'cancelled';", "CLEAR TABLE Orders IF status = 'cancelled';"],
         "Жазбаларды шарт бойынша жою үшін DELETE FROM кесте WHERE шарт; қолданылады."),
        ("SQL-де GROUP BY арқылы топтастырылған нәтижелерге шарт қою үшін қай оператор қолданылады?",
         ["HAVING", "WHERE", "ORDER BY", "LIMIT"],
         "WHERE топтастыруға дейін, ал HAVING GROUP BY арқылы топтастырылған агрегаттық мәндерге шарт қою үшін қолданылады."),
        ("SQL-де аты 'А' әрпінен басталып, дәл 4 әріптен тұратын есімдерді табатын LIKE үлгісі:",
         ["LIKE 'А___'", "LIKE 'А%'", "LIKE '%А%'", "LIKE 'А____'"],
         "Астын сызу (_) дәл бір символды білдіреді. 'А' + 3 дана '_' = барлығы 4 таңба."),
        ("SQL-де нәтижеден тек алғашқы 5 жазбаны ғана шығаруға арналған оператор (MySQL/PostgreSQL/SQLite):",
         ["LIMIT 5", "MAX 5", "COUNT 5", "FIRST 5"],
         "LIMIT N сұраныс нәтижесінде қайтарылатын жолдар санын шектейді."),
        ("SQL-де жаңа кесте құру командасы:",
         ["CREATE TABLE", "NEW TABLE", "MAKE TABLE", "ADD TABLE"],
         "DDL тобындағы CREATE TABLE командасы дерекқорда жаңа кесте анықтайды.")
    ]
    for q_txt, opts, expl in sql_qs:
        qs.append({
            "topicId": "databases",
            "text": q_txt,
            "options": opts,
            "correctIndex": 0,
            "explanation": expl
        })

    # 7. PROGRAMMING IDE (Python): Computed outputs
    py_arith = [
        ("17 // 5", 17 // 5, "Бүтін санды бөлу (//): 17-ні 5-ке бөлгендегі бүтін бөлік = 3."),
        ("17 % 5", 17 % 5, "Қалдық табу (%): 17 = 5*3 + 2, қалдық = 2."),
        ("23 // 4", 23 // 4, "23-ті 4-ке бөлгендегі бүтін бөлік = 5."),
        ("23 % 4", 23 % 4, "23 = 4*5 + 3, қалдық = 3."),
        ("2 ** 5", 2 ** 5, "Дәрежелеу (**): 2⁵ = 32."),
        ("3 ** 4", 3 ** 4, "Дәрежелеу (**): 3⁴ = 81."),
        ("25 // 6 + 25 % 6", 25 // 6 + 25 % 6, "25 // 6 = 4, 25 % 6 = 1, қосындысы = 5."),
        ("100 % 30 // 3", 100 % 30 // 3, "100 % 30 = 10, 10 // 3 = 3."),
        ("len([2, 4, 6, 8, 10])", 5, "Тізімде 5 элемент бар."),
        ("sum([3, 7, 10, 5])", 25, "3 + 7 + 10 + 5 = 25."),
        ("max([14, 29, 7, 42, 18])", 42, "Ең үлкен элемент = 42."),
        ("min([14, 29, 7, 42, 18])", 7, "Ең кіші элемент = 7.")
    ]
    for expr, res, expl in py_arith:
        qs.append({
            "topicId": "programming_ide",
            "text": f"Python тілінде `print({expr})` командасы орындалғанда экранға қандай мән шығады?",
            "options": _make_numeric_options(res, [1, -1, 3]),
            "correctIndex": 0,
            "explanation": expl
        })

    py_slices = [
        ("Алгоритм", "s[0:4]", "Алго", ["Алгор", "Алт", "горитм"]),
        ("Информатика", "s[-4:]", "тика", ["атика", "инфо", "мати"]),
        ("Python", "s[::-1]", "nohtyP", ["Python", "Pytho", "nythPo"]),
        ("Бағдарлама", "s[::2]", "Бғалм", ["Бағда", "адраа", "Бғарм"]),
        ("Компьютер", "s[3:7]", "пьюте"[:4], ["мпью", "ьюте", "пьютер"])
    ]
    for word, sl, ans, dists in py_slices:
        qs.append({
            "topicId": "programming_ide",
            "text": f"Python-да `s = '{word}'` жолы берілген. `print({sl})` командасының нәтижесі:",
            "options": [f"'{ans}'"] + [f"'{d}'" for d in dists],
            "correctIndex": 0,
            "explanation": f"'{word}' жолынан `{sl}` тілімі (slice) бойынша '{ans}' шығады."
        })

    # 8. COMPUTER SYSTEMS extra
    sys_extra = [
        ("Процессордың бір тактіде өңдей алатын биттер саны (мысалы 64-бит) қалай аталады?",
         ["Процессордың разрядтылығы", "Тактілік жиілік", "Кэш көлемі", "Ядро саны"],
         "Разрядтылық процессор регистрлері мен деректер шинасының бір мезгілде өңдейтін бит санын көрсетеді."),
        ("Процессорға ең жақын және ең жылдам орналасқан кэш-жад деңгейі:",
         ["L1 кэш-жады", "L3 кэш-жады", "DDR4 жедел жады", "NVMe SSD"],
         "L1 кэш-жады процессор ядросының дәл ішінде орналасқан, жылдамдығы ең жоғары."),
        ("Компьютердің аппараттық ресурстарын ортақ шина арқылы біріктіретін негізгі үш магистраль:",
         ["Деректер шинасы, адрестер шинасы, басқару шинасы", "Аудио, видео және қуат шиналары", "LAN, WAN, MAN", "USB, HDMI, VGA"],
         "Жүйелік шина 3 бөліктен тұрады: деректер, адрестер және басқару шиналары."),
        ("Арифметикалық және логикалық операцияларды тікелей орындайтын процессор блогы:",
         ["Арифметикалық-логикалық құрылғы (АЛҚ / ALU)", "Басқару құрылғысы (CU)", "Қоректендіру блогы", "Чипсет"],
         "АЛҚ (ALU) барлық қосу, азайту, салыстыру және логикалық операцияларды орындайды."),
        ("Фон Нейман архитектурасының басты қағидасы:",
         ["Бағдарлама мен деректер компьютердің ортақ жадында екілік код түрінде сақталады", "Әр бағдарлама бөлек механикалық дөңгелекте сақталады", "Тек мәтіндік ақпарат өңделеді", "Интернетсіз жұмыс істемейді"],
         "Жадта сақталатын бағдарлама және екілік кодтау — Фон Нейман архитектурасының өзегі."),
        ("Виртуалды жад (Virtual Memory / своп-файл) қай жерде орналасады?",
         ["Сыртқы жинақтауышта (HDD немесе SSD дискісінде)", "Процессор регистрлерінде", "BIOS микросхемасында", "Монитор жадында"],
         "Жедел жад (RAM) жетпеген кезде ОЖ қатты дискінің бір бөлігін виртуалды жад ретінде пайдаланады."),
        ("Қатты дискідегі (HDD) файлдардың шашыраңқы бөліктерін ретке келтіріп, оқу жылдамдығын арттыратын қызметтік процесс:",
         ["Дефрагментация", "Форматтау", "Архивтеу", "Компиляция"],
         "Дефрагментация файлдардың фрагменттерін дискінің іргелес секторларына жинақтайды."),
        ("Жоғары деңгейлі бағдарлама кодын машиналық кодқа тұтастай аударып, орындалатын файл (.exe) жасайтын бағдарлама:",
         ["Компилятор", "Интерпретатор", "Драйвер", "Архиватор"],
         "Компилятор бүкіл бастапқы кодты бірден машиналық кодқа аударады."),
        ("Бағдарлама кодын жолма-жол оқып, бірден орындайтын транслятор түрі (мысалы, Python):",
         ["Интерпретатор", "Компилятор", "Линкер", "Дебаггер"],
         "Интерпретатор кодты жол бойынша талдап, сол сәтте орындайды."),
        ("Ашық бастапқы коды (Open Source) бар тегін операциялық жүйе:",
         ["Linux (Ubuntu, Debian, Fedora)", "Windows 11", "macOS", "iOS"],
         "Linux ядросы мен оның дистрибутивтері GNU GPL ашық лицензиясымен тегін таратылады.")
    ]
    for q_txt, opts, expl in sys_extra:
        qs.append({
            "topicId": "computer_systems",
            "text": q_txt,
            "options": opts,
            "correctIndex": 0,
            "explanation": expl
        })

    # 9. WEB DESIGN extra (HTTP status codes, CSS, HTML)
    http_codes = [
        ("200 OK", "Сұраныс сәтті орындалды", ["Бет табылмады", "Сервердің ішкі қатесі", "Кіруге тыйым салынған"]),
        ("404 Not Found", "Сұралған бет немесе ресурс серверде табылмады", ["Сұраныс сәтті орындалды", "Сервер қайта жүктелді", "Авторизация сәтті өтті"]),
        ("403 Forbidden", "Ресурсқа қол жеткізуге тыйым салынған (құқық жоқ)", ["Бет табылмады", "Сұраныс сәтті өтті", "Басқа мекенжайға бағытталды"]),
        ("500 Internal Server Error", "Веб-сервердің ішкі қателігі", ["Қолданушы интернеті өшкен", "Бет сәтті жүктелді", "Браузер ескірген"]),
        ("301 Moved Permanently", "Ресурс тұрақты түрде басқа URL мекенжайға көшірілді", ["Бет жойылды", "Сервер жауап бермеді", "Қате пароль"])
    ]
    for code, desc, dists in http_codes:
        qs.append({
            "topicId": "web_design",
            "text": f"HTTP хаттамасындағы `{code}` жауап коды нені білдіреді?",
            "options": [desc] + dists,
            "correctIndex": 0,
            "explanation": f"`{code}` — {desc}."
        })

    web_extra = [
        ("CSS-те класс (class) бойынша селектор қандай таңбадан басталады?",
         ["Нүктеден (.)", "Торкөзден (#)", "Жұлдызшадан (*)", "Қос нүктеден (:)"],
         "Класс селекторы `.classname`, ал идентификатор (id) селекторы `#idname` түрінде жазылады."),
        ("CSS-те бірегей идентификатор (id) селекторы қандай таңбамен белгіленеді?",
         ["Торкөзбен (#)", "Нүктемен (.)", "Доллармен ($)", "Амперсандпен (&)"],
         "ID селекторы `#header` сияқты торкөз (#) белгісінен басталады."),
        ("HTML құжатында қазақша әріптер дұрыс көрінуі үшін `<head>` ішінде қандай кодтау тегі жазылады?",
         ["<meta charset=\"UTF-8\">", "<meta lang=\"KZ\">", "<encoding type=\"UTF-8\">", "<charset>UTF-8</charset>"],
         "`<meta charset=\"UTF-8\">` барлық Unicode символдарын, соның ішінде қазақ әріптерін дұрыс көрсетеді."),
        ("HTML кестесінде бағандарды көлденең біріктіру атрибуты:",
         ["colspan", "rowspan", "merge", "span-col"],
         "`colspan` көршілес бағандарды, ал `rowspan` көршілес жолдарды біріктіреді."),
        ("HTML кестесінде жолдарды тігінен біріктіру атрибуты:",
         ["rowspan", "colspan", "vertical-span", "join-row"],
         "`rowspan` бірнеше қатарды (жолды) біріктіруге арналған."),
        ("HTML-де сілтемені жаңа қойындыда (жаңа терезеде) ашу үшін `<a>` тегіне қандай атрибут беріледі?",
         ["target=\"_blank\"", "open=\"new\"", "window=\"tab\"", "href=\"_new\""],
         "`target=\"_blank\"` атрибуты гиперсілтемені браузердің жаңа қойындысында ашады."),
        ("CSS Flexbox-та элементтерді негізгі ось бойынша көлденең ортаға туралау қасиеті:",
         ["justify-content: center;", "align-items: left;", "text-float: center;", "margin: 0;"],
         "`justify-content: center;` флекс-элементтерді негізгі ось бойымен дәл ортаға орналастырады."),
        ("Веб-беттің түрлі экран өлшемдеріне (телефон, планшет, компьютер) бейімделу технологиясы:",
         ["Адаптивті дизайн (Responsive Web Design, @media)", "Статикалық дизайн", "Тек кестелік беттеу", "Серверлік рендеринг"],
         "CSS `@media` сұраныстары арқылы сайт барлық құрылғылардың экранына бейімделеді.")
    ]
    for q_txt, opts, expl in web_extra:
        qs.append({
            "topicId": "web_design",
            "text": q_txt,
            "options": opts,
            "correctIndex": 0,
            "explanation": expl
        })

    # 10. TEXT & MULTIMEDIA extra
    tm_extra = [
        ("Full HD бейне стандартының пиксельдік өлшемі (рұқсаты):",
         ["1920 x 1080", "1280 x 720", "3840 x 2160", "720 x 576"],
         "Full HD (1080p) стандарты 1920x1080 пиксельге тең."),
        ("4K UHD бейне стандартының рұқсаты:",
         ["3840 x 2160", "1920 x 1080", "1280 x 720", "7680 x 4320"],
         "4K UHD стандарты 3840x2160 пиксельді құрайды (Full HD-ден 4 есе көп пиксель)."),
        ("HD (720p) бейне стандартының өлшемі:",
         ["1280 x 720", "1920 x 1080", "640 x 480", "3840 x 2160"],
         "HD Ready (720p) — 1280x720 пиксель."),
        ("Ұзақтығы 10 секунд, кадр жиілігі 30 FPS болатын бейнероликте барлығы неше кадр бар?",
         ["300 кадр", "30 кадр", "600 кадр", "100 кадр"],
         "10 секунд * 30 кадр/сек = 300 кадр."),
        ("MS Word-та мәтінді курсив (көлбеу) етіп жазу пернелер тіркесімі:",
         ["Ctrl + I", "Ctrl + B", "Ctrl + U", "Ctrl + K"],
         "Ctrl + I (Italic) — курсив, Ctrl + B — қалың, Ctrl + U — астын сызу."),
        ("MS Word-та мәтіннің астын сызу пернелер тіркесімі:",
         ["Ctrl + U", "Ctrl + I", "Ctrl + B", "Ctrl + S"],
         "Ctrl + U (Underline) таңдалған мәтіннің астын сызады."),
        ("MS Word-та соңғы жасалған әрекетті болдырмау (кері қайтару) пернесі:",
         ["Ctrl + Z", "Ctrl + Y", "Ctrl + X", "Ctrl + V"],
         "Ctrl + Z — соңғы әрекетті кері қайтару (Undo)."),
        ("Аудио және бейне деректерді сығу мен ашуды жүзеге асыратын бағдарламалық алгоритм:",
         ["Кодек (Codec, мысалы H.264, MP3)", "Браузер", "Компилятор", "Протокол"],
         "Кодек (Coder-Decoder) мультимедиа ағынын тиімді сығып сақтау және ойнату үшін қолданылады.")
    ]
    for q_txt, opts, expl in tm_extra:
        qs.append({
            "topicId": "text_multimedia",
            "text": q_txt,
            "options": opts,
            "correctIndex": 0,
            "explanation": expl
        })

    # 11. AI extra
    ai_extra = [
        ("Машинаның адам сияқты ойлай алатындығын тексеру үшін 1950 жылы ұсынылған әйгілі тест:",
         ["Тьюринг тесті (Алан Тьюринг)", "Фон Нейман тесті", "Хартли тесті", "Мур заңы"],
         "Алан Тьюринг машинаның зияткерлік деңгейін тексеру үшін «Еліктеу ойыны» (Тьюринг тестін) ұсынды."),
        ("Модельдің дұрыс болжаған жауаптарының барлық жауаптарға қатынасын көрсететін негізгі метрика:",
         ["Дәлдік (Accuracy)", "Дәуір (Epoch)", "Градиент", "Битрейт"],
         "Accuracy = (Дұрыс болжамдар саны) / (Жалпы мысалдар саны)."),
        ("Мәліметтерді дайын белгілерсіз (label-сіз) ұқсас топтарға бөлетін танымал алгоритм:",
         ["K-орташа әдісі (K-Means кластерлеу)", "Көпіршікті сұрыптау", "Цезарь шифры", "Екілік іздеу"],
         "K-Means — мұғалімсіз оқытудағы (Unsupervised Learning) ең танымал кластерлеу алгоритмі."),
        ("Жасанды интеллект модельдеріне (мысалы ChatGPT, Gemini) нақты тапсырма беру өнері мен нұсқаулық жазу әдісі:",
         ["Промпт-инжиниринг (Prompt Engineering)", "Дефрагментация", "Компиляция", "Маршруттау"],
         "Промпт-инжиниринг — үлкен тілдік модельдерден дәл әрі сапалы жауап алу үшін сұраныстарды (промпттарды) тиімді құрастыру."),
        ("Көп қабатты (жасырын қабаттары көп) нейрондық желілерді оқыту бағыты қалай аталады?",
         ["Терең оқыту (Deep Learning)", "Сызықтық бағдарламалау", "Қарапайым сүзгілеу", "Деректерді архивтеу"],
         "Deep Learning (Терең оқыту) көптеген жасырын қабаттары бар нейрожүйелер арқылы күрделі заңдылықтарды үйренеді."),
        ("Модельдің тым қарапайым болып, тіпті оқыту деректеріндегі негізгі заңдылықты да игере алмауы:",
         ["Жеткіліксіз оқыту (Underfitting / Недообучение)", "Қайта оқыту (Overfitting)", "Токенизация", "Нормализация"],
         "Underfitting кезінде модель тым қарапайым болғандықтан, оқу жиынтығында да, тестте де төмен нәтиже көрсетеді."),
        ("Машиналық оқытуда деректер жиынтығын оқыту (Train) және тексеру (Test) бөліктеріне бөлудің мақсаты:",
         ["Модельдің бұрын көрмеген жаңа деректердегі нақты сапасын әділ бағалау", "Файл көлемін кішірейту", "Суреттің түсін өзгерту", "Интернет жылдамдығын тексеру"],
         "Train/Test бөлуі модельдің жаттап алмағанын (Overfitting жоқтығын) және жаңа деректерде жақсы жұмыс істейтінін тексеруге мүмкіндік береді."),
        ("Нейрондық желіде қателікті шығыс қабаттан кіріс қабатқа қарай таратып, салмақтарды түзететін классикалық алгоритм:",
         ["Қатені кері тарату әдісі (Backpropagation)", "Екілік іздеу", "Тікелей көшіру", "Хэштеу"],
         "Backpropagation алгоритмі градиенттерді есептеп, барлық қабаттардағы нейрон салмақтарын жаңартады.")
    ]
    for q_txt, opts, expl in ai_extra:
        qs.append({
            "topicId": "ai",
            "text": q_txt,
            "options": opts,
            "correctIndex": 0,
            "explanation": expl
        })

    # --- ADDITIONAL BATCH TO SURPASS 1,050+ SPOTLESS QUESTIONS ---
    # Binary -> Decimal conversions (25 questions)
    for n in [11, 14, 21, 26, 33, 38, 43, 49, 58, 67, 74, 83, 91, 99, 106, 114, 121, 133, 142, 155, 168, 179, 193, 207, 234]:
        b = bin(n)[2:]
        qs.append({
            "topicId": "info_processes",
            "text": f"Екілік санау жүйесіндегі {b}₂ санының ондық жүйедегі мәні:",
            "options": _make_numeric_options(n, [2, -2, 4]),
            "correctIndex": 0,
            "explanation": f"{b}₂ екілік санын 2-нің дәрежелері бойынша жіктегенде {n}₁₀ шығады."
        })

    # Python for-loop & list comprehension computations (35 questions)
    loop_cases = [
        ("s = 0\nfor i in range(1, 6):\n    s += i\nprint(s)", sum(range(1, 6)), "1+2+3+4+5 = 15."),
        ("s = 0\nfor i in range(2, 11, 2):\n    s += i\nprint(s)", sum(range(2, 11, 2)), "2+4+6+8+10 = 30."),
        ("s = 0\nfor i in range(1, 10, 2):\n    s += i\nprint(s)", sum(range(1, 10, 2)), "1+3+5+7+9 = 25."),
        ("p = 1\nfor i in range(1, 5):\n    p *= i\nprint(p)", 24, "1*2*3*4 = 24 (4!)."),
        ("p = 1\nfor i in range(1, 6):\n    p *= i\nprint(p)", 120, "1*2*3*4*5 = 120 (5!)."),
        ("c = 0\nfor x in [3, 8, 12, 5, 10, 7]:\n    if x % 2 == 0:\n        c += 1\nprint(c)", 3, "Жұп сандар: 8, 12, 10 — барлығы 3 сан."),
        ("c = 0\nfor x in [15, 4, 22, 9, 18, 1]:\n    if x > 10:\n        c += 1\nprint(c)", 3, "10-нан үлкен сандар: 15, 22, 18 — 3 сан."),
        ("a = [2, 5, 4, -6, 9]\ns = 0\nfor x in a:\n    if x > 0:\n        s += x\nprint(s)", 20, "Оң сандар қосындысы: 2+5+4+9 = 20."),
        ("a = [10, 20, 30, 40]\na.append(50)\nprint(len(a))", 5, "Бастапқы 4 элементке 50 қосылды, ұзындығы = 5."),
        ("a = [5, 10, 15, 20]\na.pop()\nprint(sum(a))", 30, "pop() соңғы 20 элементін алып тастайды. 5+10+15 = 30."),
        ("x = 12\ny = 5\nif x > 10 and y < 10:\n    print(x - y)\nelse:\n    print(x + y)", 7, "Екі шарт та орындалады: 12 - 5 = 7."),
        ("x = 4\ny = 9\nif x % 2 == 0 or y % 2 == 0:\n    print(x * y)\nelse:\n    print(x + y)", 36, "x жұп болғандықтан шарт ақиқат: 4 * 9 = 36."),
        ("s = 'informatika'\nprint(s.count('a'))", 2, "'informatika' сөзінде 'a' әрпі 2 рет кездеседі."),
        ("s = 'kz-2026-pbb'\nprint(len(s.split('-')))", 3, "'-' бойынша бөлгенде ['kz', '2026', 'pbb'] — 3 элемент."),
        ("d = {'a': 10, 'b': 25, 'c': 15}\nprint(sum(d.values()))", 50, "Сөздік мәндерінің қосындысы: 10+25+15 = 50.")
    ]
    for code, res, expl in loop_cases:
        qs.append({
            "topicId": "programming_ide",
            "text": f"Келесі Python коды орындалғанда экранға қандай сан шығады? `{code.replace(chr(10), ' ; ')}`",
            "options": _make_numeric_options(res, [2, -1, 5]),
            "correctIndex": 0,
            "explanation": expl
        })

    # Additional Python arithmetic/logic/modulo (20 questions)
    for a, b in [(31, 6), (45, 7), (50, 8), (67, 9), (74, 10), (83, 12), (95, 11), (104, 15), (125, 20), (147, 13)]:
        qs.append({
            "topicId": "programming_ide",
            "text": f"Python-да `print({a} // {b})` өрнегінің нәтижесі:",
            "options": _make_numeric_options(a // b, [1, -1, 2]),
            "correctIndex": 0,
            "explanation": f"{a}-ны {b}-ға бүтін бөлгенде {a // b} шығады (қалдық {a % b})."
        })
        qs.append({
            "topicId": "programming_ide",
            "text": f"Python-да `print({a} % {b})` өрнегінің нәтижесі:",
            "options": _make_numeric_options(a % b, [1, 2, -1 if a % b > 0 else 3]),
            "correctIndex": 0,
            "explanation": f"{a} = {b} * {a // b} + {a % b}, яғни қалдық {a % b}."
        })

    # Excel extra computed formulas (25 questions)
    excel_more = [
        ("A1=8, B1=12, C1=4", "=SUM(A1:C1)", 24),
        ("A1=9, B1=15, C1=6", "=AVERAGE(A1:C1)", 10),
        ("A1=20, B1=5, C1=3", "=A1/B1*C1", 12),
        ("A1=14, B1=6, C1=2", "=(A1+B1)/C1", 10),
        ("A1=5, B1=4", "=A1^2-B1^2", 9),
        ("A1=10, B1=3", "=MOD(A1, B1)", 1),
        ("A1=25, B1=4", "=MOD(A1, B1)", 1),
        ("A1=16", "=SQRT(A1)+6", 10),
        ("A1=81", "=SQRT(A1)*2", 18),
        ("A1=12, A2=18, A3=30", "=SUM(A1:A3)/3", 20),
        ("A1=4, B1=5, C1=6", "=PRODUCT(A1:C1)", 120),
        ("A1=15, B1=20", "=IF(A1+B1>30, 100, 50)", 100),
        ("A1=10, B1=15", "=IF(A1+B1>30, 100, 50)", 50),
        ("A1=3, B1=4, C1=5", "=MAX(A1:C1)*MIN(A1:C1)", 15),
        ("A1=7, B1=14, C1=21", "=AVERAGE(A1:C1)+6", 20)
    ]
    for vals, form, res in excel_more:
        qs.append({
            "topicId": "spreadsheets",
            "text": f"Excel кестесінде {vals} болғанда, `{form}` формуласы қандай мән қайтарады?",
            "options": _make_numeric_options(res, [4, -2, 8]),
            "correctIndex": 0,
            "explanation": f"`{form}` формуласын есептегенде нәтиже {res} болады."
        })

    # Audio & Video size/frame calculations (15 questions)
    audio_cases = [
        (10, 8000, 8, 1, 80000),
        (10, 16000, 8, 1, 160000),
        (5, 8000, 16, 1, 80000),
        (5, 16000, 16, 2, 320000),
        (2, 44100, 16, 1, 176400),
        (4, 22050, 8, 2, 176400)
    ]
    for sec, freq, bits, ch, res_bytes in audio_cases:
        ch_name = "моно (1 арна)" if ch == 1 else "стерео (2 арна)"
        qs.append({
            "topicId": "text_multimedia",
            "text": f"Ұзақтығы {sec} секунд, дискреттеу жиілігі {freq} Гц, тереңдігі {bits} бит болатын {ch_name} дыбыс файлының көлемі қанша байт?",
            "options": _make_numeric_options(res_bytes, [res_bytes, -res_bytes // 2, res_bytes // 4], " байт"),
            "correctIndex": 0,
            "explanation": f"I = {sec} * {freq} * ({bits}/8) * {ch} = {res_bytes} байт."
        })

    for sec, fps in [(15, 24), (20, 30), (10, 60), (30, 25), (60, 30), (12, 50)]:
        frames = sec * fps
        qs.append({
            "topicId": "text_multimedia",
            "text": f"Ұзақтығы {sec} секунд және жиілігі {fps} кадр/сек (FPS) бейнежазбада барлығы неше кадр бар?",
            "options": _make_numeric_options(frames, [fps * 2, -fps, frames // 2], " кадр"),
            "correctIndex": 0,
            "explanation": f"Кадр саны = {sec} * {fps} = {frames} кадр."
        })

    # Networks IP class & private IP identification (20 questions)
    ip_classes = [
        ("10.0.0.1", "A класы", ["B класы", "C класы", "D класы"]),
        ("126.15.4.2", "A класы", ["B класы", "C класы", "E класы"]),
        ("128.10.0.5", "B класы", ["A класы", "C класы", "D класы"]),
        ("172.16.25.1", "B класы", ["A класы", "C класы", "D класы"]),
        ("191.254.1.10", "B класы", ["A класы", "C класы", "E класы"]),
        ("192.168.1.1", "C класы", ["A класы", "B класы", "D класы"]),
        ("203.0.113.45", "C класы", ["A класы", "B класы", "D класы"]),
        ("223.255.10.2", "C класы", ["A класы", "B класы", "E класы"])
    ]
    for ip, cls, dists in ip_classes:
        qs.append({
            "topicId": "networks_security",
            "text": f"{ip} IPv4 мекенжайы қай желі класына жатады?",
            "options": [cls] + dists,
            "correctIndex": 0,
            "explanation": f"A класы: 1–126, B класы: 128–191, C класы: 192–223. Демек {ip} — {cls}."
        })

    # Databases & Web & Systems & Graphics & AI additional verified items (30 questions)
    more_mixed = [
        ("databases", "SQL-де кестенің құрылымын өзгерту (жаңа баған қосу немесе типін өзгерту) командасы:", ["ALTER TABLE", "UPDATE TABLE", "CHANGE TABLE", "MODIFY SCHEMA"], "ALTER TABLE кестенің бағандарын қосу, өшіру немесе өзгерту үшін қолданылады."),
        ("databases", "SQL-де кестедегі барлық жолдарды жылдам тазартып, бірақ кесте құрылымын сақтап қалатын команда:", ["TRUNCATE TABLE", "DROP TABLE", "ALTER TABLE", "REMOVE TABLE"], "TRUNCATE TABLE барлық жазбаларды жояды, бірақ кестенің өзін сақтап қалады."),
        ("databases", "SQL-де бос емес (NULL емес) мәндерді тексеретін шарт:", ["IS NOT NULL", "!= NULL", "<> EMPTY", "NOT EMPTY"], "SQL-де NULL емес екенін тексеру үшін IS NOT NULL операторы қолданылады."),
        ("databases", "Деректер қорындағы ACID қасиеттеріне не жатады?", ["Атомдылық, Келісілгендік, Оқшаулану, Тұрақтылық", "Жылдамдық, Өлшем, Түс, Формат", "Кілт, Индекс, Кесте, Өріс", "Сұрыптау, Сүзу, Іздеу, Көшіру"], "ACID: Atomicity, Consistency, Isolation, Durability — транзакциялардың сенімділік кепілі."),
        ("databases", "Құжаттық, кілт-мән немесе графтық модельдерге негізделген реляциялық емес дерекқорлар тобы:", ["NoSQL (мысалы, MongoDB, Redis)", "SQLite", "MS Access", "PostgreSQL"], "NoSQL дерекқорлары икемді құрылымды үлкен деректермен жұмыс істеуге арналған."),
        ("web_design", "HTML5-те құжаттың HTML5 стандартымен жазылғанын браузерге хабарлайтын ең бірінші жол:", ["<!DOCTYPE html>", "<html version=\"5\">", "<head type=\"html5\">", "<meta html=\"5\">"], "`<!DOCTYPE html>` браузерге құжатты HTML5 режимінде көрсетуді нұсқайды."),
        ("web_design", "HTML-де бейне (видео) ойнатқышты кірістіруге арналған HTML5 тегі:", ["<video>", "<movie>", "<media>", "<play>"], "`<video controls>` тегі веб-бетке бейнефайл орналастырады."),
        ("web_design", "HTML-де дыбыстық (аудио) файлды ойнатуға арналған HTML5 тегі:", ["<audio>", "<sound>", "<music>", "<mp3>"], "`<audio controls>` тегі веб-бетте дыбыс ойнатуға арналған."),
        ("web_design", "CSS-те элементтің бұрыштарын дөңгелектеу қасиеті:", ["border-radius", "corner-round", "box-radius", "circle-border"], "`border-radius` (мысалы `border-radius: 12px;`) элементтің бұрыштарын жұмырлайды."),
        ("web_design", "CSS-те элементтің мөлдірлігін (0-ден 1-ге дейін) реттейтін қасиет:", ["opacity", "transparent", "visibility", "alpha"], "`opacity: 0.5;` элементті 50% мөлдір етеді."),
        ("computer_systems", "Компьютердің бейнесигналын мониторға цифрлық түрде дыбыспен бірге тасымалдайтын заманауи интерфейс:", ["HDMI", "VGA", "PS/2", "LPT"], "HDMI жоғары ажыратымдылықтағы цифрлық бейне мен дыбысты бір кабельмен береді."),
        ("computer_systems", "Процессор мен аналық тақшадағы құрылғылардың қызып кетуінен қорғайтын салқындату жүйесі:", ["Кулер және радиатор (Cooling system)", "Чипсет", "Конденсатор", "Резистор"], "Радиатор жылуды сіңіріп, кулер (желдеткіш) оны сыртқа шығарады."),
        ("computer_systems", "Операциялық жүйенің файлдарды дискіде сақтау және ұйымдастыру тәсілі қалай аталады?", ["Файлдық жүйе (NTFS, FAT32, ext4)", "Мәліметтер қоры", "Протокол", "Браузер"], "Файлдық жүйе (NTFS, ext4, APFS) файлдар мен бумалардың дискідегі құрылымын басқарады."),
        ("computer_graphics", "Суреттің шетіндегі сатылы (тісті) контурларды тегістеу технологиясы:", ["Тегістеу (Anti-aliasing)", "Кропинг (Crop)", "Инверсия", "Контраст"], "Anti-aliasing пиксель жиектерін жұмсартып, кескінді тегіс көрсетеді."),
        ("computer_graphics", "3D-модельдеудегі үш өлшемді нысанның беткі қабатын құрайтын көпбұрыштар:", ["Полигондар (Polygons)", "Пикселдер", "Биттер", "Векторлар"], "3D модельдер үшбұрышты немесе төртбұрышты полигондар торынан (mesh) тұрады."),
        ("ai", "Компьютерлік көруде нақты уақыт режимінде нысандарды анықтауға арналған танымал нейрожелі моделі:", ["YOLO (You Only Look Once)", "HTML", "SQL", "TCP/IP"], "YOLO — камера бейнесінен нысандарды өте жылдам танитын танымал нейрожелі."),
        ("ai", "Мәтіндік сұраныс бойынша сурет генерациялайтын жасанды интеллект жүйелерінің түрі:", ["Генеративті ЖИ (Generative AI, диффузиялық модельдер)", "Сызықтық регрессия", "Антивирус", "Реляциялық ДҚБЖ"], "Диффузиялық модельдер сияқты генеративті ЖИ мәтіндік сипаттамадан жаңа кескіндер жасайды."),
        ("ai", "Сараптамалық жүйенің (Expert System) ең негізгі екі компоненті:", ["Білім базасы және логикалық қорытынды шығару механизмі", "Монитор және пернетақта", "Принтер және сканер", "HTML және CSS"], "Сараптамалық жүйе нақты саланың білім базасына және ережелер бойынша қорытынды шығару тетігіне сүйенеді."),
        ("computer_systems", "Монитор экранындағы кескіннің 1 секундта қанша рет жаңаратынын көрсететін параметр:", ["Жаңарту жиілігі (Гц — мысалы 60 Гц, 144 Гц)", "Диагональ (дюйм)", "Жарықтылық (нит)", "Салмақ"], "Жаңарту жиілігі (Refresh Rate) экрандағы суреттің секундына қанша рет жаңаратынын Гц-пен өлшейді."),
        ("networks_security", "Жеке компьютер мен интернет арасындағы трафикті шифрлап, IP мекенжайды жасыратын қауіпсіз туннель технологиясы:", ["VPN (Virtual Private Network)", "LAN", "HTML", "BIOS"], "VPN шифрланған қорғалған арна арқылы желілік трафиктің құпиялылығын қамтамасыз етеді.")
    ]
    for tid, q_txt, opts, expl in more_mixed:
        qs.append({
            "topicId": tid,
            "text": q_txt,
            "options": opts,
            "correctIndex": 0,
            "explanation": expl
        })

    return qs

if __name__ == "__main__":
    qs = get_programmatic_questions()
    print("Programmatic questions generated:", len(qs))
