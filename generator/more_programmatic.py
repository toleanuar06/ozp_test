# -*- coding: utf-8 -*-
"""Қосымша есептелген (бағдарлама арқылы тексерілген) сұрақтар: санау жүйелері, Python, желі."""

def _four(correct, candidates):
    opts = [correct]
    for c in candidates:
        if c not in opts:
            opts.append(c)
        if len(opts) == 4:
            break
    k = 1
    while len(opts) < 4:
        opts.append(f"{correct}{k}")
        k += 1
    return opts


def get_more_questions():
    qs = []

    # ондық -> екілік
    for n in [22, 37, 41, 59, 66, 77, 85, 96, 103, 119, 127, 131, 144, 153, 171, 186, 203, 219, 236, 247, 29, 45, 58, 71, 94]:
        b = bin(n)[2:]
        cands = [f"{bin(n + d)[2:]}₂" for d in (1, -1, 2, 4, -2)]
        qs.append({
            "topicId": "info_processes",
            "text": f"{n}₁₀ санын екілік санау жүйесіне айналдырыңыз:",
            "options": _four(f"{b}₂", cands),
            "correctIndex": 0,
            "explanation": f"{n} санын 2-ге бөлу арқылы екілік жүйеге ауыстырсақ: {b}₂."
        })

    # екілік -> ондық
    for n in [23, 36, 52, 69, 81, 98, 112, 125, 138, 157, 174, 191, 205, 222, 238, 17, 39, 62, 87, 109]:
        b = bin(n)[2:]
        qs.append({
            "topicId": "info_processes",
            "text": f"{b}₂ екілік санының ондық санау жүйесіндегі мәнін табыңыз:",
            "options": _four(str(n), [str(n + d) for d in (2, -2, 4, -1, 8)]),
            "correctIndex": 0,
            "explanation": f"{b}₂ = {n}₁₀ (разрядтар салмағын 2-нің дәрежелерімен қосқанда)."
        })

    # он алтылық -> ондық
    for n in [43, 74, 101, 135, 168, 197, 226, 251, 58, 92, 120, 149]:
        h = hex(n)[2:].upper()
        qs.append({
            "topicId": "info_processes",
            "text": f"Он алтылық {h}₁₆ санының ондық жүйедегі мәні:",
            "options": _four(str(n), [str(n + d) for d in (1, -3, 16, 6)]),
            "correctIndex": 0,
            "explanation": f"{h}₁₆ = {n}₁₀."
        })

    # сегіздік -> ондық
    for n in [27, 46, 83, 110, 157, 204, 61, 98, 133]:
        o = oct(n)[2:]
        qs.append({
            "topicId": "info_processes",
            "text": f"Сегіздік {o}₈ санының ондық жүйедегі мәні:",
            "options": _four(str(n), [str(n + d) for d in (1, -2, 8, 5)]),
            "correctIndex": 0,
            "explanation": f"{o}₈ = {n}₁₀."
        })

    # Python: тізім / жол / цикл нәтижелері (барлығы есептелген)
    py_cases = []
    for lst in ([4, 9, 2, 7], [10, 3, 8, 5, 1], [6, 6, 2, 12], [15, 4, 9, 20, 11], [3, 18, 7, 5]):
        py_cases.append((f"a = {lst}\nprint(sum(a))", sum(lst)))
        py_cases.append((f"a = {lst}\nprint(max(a) - min(a))", max(lst) - min(lst)))
        py_cases.append((f"a = {lst}\nprint(len(a))", len(lst)))
    for n in (4, 6, 7, 8):
        py_cases.append((f"s = 0\nfor i in range(1, {n} + 1):\n    s += i * i\nprint(s)", sum(i * i for i in range(1, n + 1))))
    for a, b in ((14, 4), (29, 6), (38, 5), (47, 9)):
        py_cases.append((f"x = {a}\ny = {b}\nprint(x // y, x % y)", f"{a // b} {a % b}"))
    for code, res in py_cases:
        res_s = str(res)
        if " " in res_s:
            x, y = res_s.split()
            cands = [f"{int(x) + 1} {y}", f"{x} {int(y) + 1}", f"{int(x) - 1} {y}", f"{y} {x}"]
        else:
            cands = [str(res + d) for d in (1, -1, 3, 5, 2)]
        qs.append({
            "topicId": "programming_ide",
            "text": f"Python программасы орындалғанда экранға не шығады? `{code.replace(chr(10), ' ; ')}`",
            "options": _four(res_s, cands),
            "correctIndex": 0,
            "explanation": f"Кодты қадамдап орындасақ, нәтиже: {res_s}."
        })

    # Желі: IP + желі префиксі бойынша хост саны
    for prefix, hosts in ((16, 65534), (20, 4094), (22, 1022), (23, 510), (24, 254)):
        qs.append({
            "topicId": "networks_security",
            "text": f"IPv4 желісінің префиксі /{prefix} болса, онда қанша хостқа (компьютерге) адрес беруге болады?",
            "options": _four(str(hosts), [str(2 ** (32 - prefix)), str(hosts // 2), str(hosts + 2 + 2)]),
            "correctIndex": 0,
            "explanation": f"2^(32−{prefix}) − 2 = {hosts} хост (желі және тарату адрестері алынып тасталады)."
        })

    # Мәтін көлемі
    for k, bits_per, total in ((400, 8, 400), (1200, 16, 2400), (640, 8, 640), (2048, 16, 4096), (500, 16, 1000)):
        qs.append({
            "topicId": "info_processes",
            "text": f"Әр символы {bits_per} бит жадқа кодталатын {k} символдан тұратын мәтіннің ақпараттық көлемі қанша байт?",
            "options": _four(f"{total} байт", [f"{total * 8} байт", f"{total // 2} байт", f"{total * 2} байт"]),
            "correctIndex": 0,
            "explanation": f"I = {k} · {bits_per} бит = {k * bits_per} бит = {total} байт."
        })

    return qs
