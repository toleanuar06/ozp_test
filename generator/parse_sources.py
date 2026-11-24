import os
import re
import docx

SOURCE_FOLDER = r"c:\Users\tolea\Downloads\Telegram Desktop"

PEDAGOGY_STOPWORDS = [
    "сабақты жоспарлау", "оқу сабақтары", "метатанымдық", "сын тұрғысынан ойлау",
    "танымдық іс", "оқытудың қосымша", "педагогикалық технология", "мұғалімнің қолданған",
    "оқушының жеке дара", "конвергентті", "дивергентті", "оқу тәжірибесін",
    "білім алушылардың", "қалыптастырушы бағалау", "жиынтық бағалау", "критериалды бағалау",
    "тәрбие", "дидактика", "әдістемелік", "сабақ-конференция", "оқыту әдісі"
]

def clean_text(s):
    if not s:
        return ""
    s = s.replace("«", "\"").replace("»", "\"").replace("”", "\"").replace("“", "\"")
    s = s.replace("’", "'").replace("`", "'").replace("\u00a0", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s

def clean_option_text(s):
    s = clean_text(s)
    # Remove leading ++ or + or Ж:
    s = re.sub(r"^(\+\+|\+|Ж:|Жауабы:|Жауап:)\s*", "", s, flags=re.IGNORECASE)
    # Remove trailing қате / дұрыс / + / -
    s = re.sub(r"\s*[-–—+]?\s*(қате|дұрыс)\s*$", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\s*\+\s*$", "", s)
    return s.strip()

def is_pedagogy(text):
    tl = text.lower()
    return any(w in tl for w in PEDAGOGY_STOPWORDS)

def is_valid_mcq(q_text, opts):
    if not q_text or len(q_text) < 10:
        return False
    if q_text.startswith("</") or q_text.startswith("http"):
        return False
    if is_pedagogy(q_text):
        return False
    if len(opts) != 4:
        return False
    cleaned_set = set()
    for o in opts:
        if not o or len(o) > 160:
            return False
        # Reject placeholder or letter-only options (missing screenshots)
        if re.match(r"^[A-Ea-eАБВГДЕСДабвгдесд][\.\)]?$", o):
            return False
        if any(bad in o.lower() for bad in ["басқа нұсқа", "қосымша нұсқа", "балама нұсқа", "қате"]):
            return False
        if o.lower() in cleaned_set:
            return False
        cleaned_set.add(o.lower())
    return True

def parse_shilde():
    path = os.path.join(SOURCE_FOLDER, "информатика шілде тест нұсқа (1).docx")
    if not os.path.exists(path):
        return []
    doc = docx.Document(path)
    answers = {}
    for t in doc.tables:
        for row in t.rows:
            cells = [clean_text(c.text) for c in row.cells]
            for i in range(0, len(cells) - 1, 2):
                if cells[i].isdigit():
                    answers[int(cells[i])] = cells[i + 1].upper()

    paras = [clean_text(p.text) for p in doc.paragraphs if clean_text(p.text)]
    questions = []
    i = 0
    q_num = 1
    letter_map = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'А': 0, 'В': 1, 'С': 2, 'Д': 3}

    while i + 4 < len(paras) and q_num <= 50:
        q_text = paras[i]
        opts = [clean_option_text(paras[i + k]) for k in range(1, 5)]
        ans_letter = answers.get(q_num, 'A')
        corr_idx = letter_map.get(ans_letter, 0)
        if is_valid_mcq(q_text, opts):
            questions.append({
                "source": "информатика шілде тест нұсқа",
                "text": q_text,
                "options": opts,
                "correctIndex": corr_idx
            })
        q_num += 1
        i += 5
    return questions

def parse_informatika_1():
    path = os.path.join(SOURCE_FOLDER, "информатика 1(жауаптар) (1).docx")
    if not os.path.exists(path):
        return []
    doc = docx.Document(path)
    questions = []
    paras = [p for p in doc.paragraphs if clean_text(p.text)]

    i = 0
    while i < len(paras):
        t = clean_text(paras[i].text)
        m = re.match(r"^(\d+)[\.\)]\s*(.+)", t)
        if m:
            q_text = m.group(2).strip()
            opts = []
            corr_idx = None
            j = i + 1
            while j < len(paras) and len(opts) < 4:
                p_opt = paras[j]
                opt_t = clean_text(p_opt.text)
                if re.match(r"^\d+[\.\)]", opt_t):
                    break
                is_colored = any(r.font.color and r.font.color.rgb for r in p_opt.runs if r.text.strip())
                is_hl = any(r.font.highlight_color for r in p_opt.runs if r.text.strip())
                if (is_colored or is_hl) and corr_idx is None:
                    corr_idx = len(opts)
                opt_clean = re.sub(r"^[A-Ea-eАБВГДЕСДабвгдесд][\.\)]\s*", "", opt_t)
                opts.append(clean_option_text(opt_clean))
                j += 1
            if corr_idx is not None and is_valid_mcq(q_text, opts):
                questions.append({
                    "source": "информатика 1(жауаптар)",
                    "text": q_text,
                    "options": opts,
                    "correctIndex": corr_idx
                })
            i = j
        else:
            i += 1
    return questions

def parse_probny_2():
    path = os.path.join(SOURCE_FOLDER, "тест пробный информатика2.docx")
    if not os.path.exists(path):
        return []
    doc = docx.Document(path)
    paras = [clean_text(p.text) for p in doc.paragraphs if clean_text(p.text)]
    opt_re = re.compile(r"^[A-Ea-eАБВГДЕСДабвгдесд][\.\)]\s*(.+)")

    questions = []
    i = 0
    while i < len(paras):
        t = paras[i]
        if not opt_re.match(t):
            q_text = re.sub(r"^\d+[\.\)]\s*", "", t).strip()
            opts = []
            corr_idx = None
            j = i + 1
            while j < len(paras) and len(opts) < 4:
                m_opt = opt_re.match(paras[j])
                if m_opt:
                    raw_val = m_opt.group(1).strip()
                    if "+" in raw_val or "дұрыс" in raw_val.lower():
                        corr_idx = len(opts)
                    opts.append(clean_option_text(raw_val))
                    j += 1
                else:
                    break
            if corr_idx is not None and is_valid_mcq(q_text, opts):
                questions.append({
                    "source": "тест пробный информатика2",
                    "text": q_text,
                    "options": opts,
                    "correctIndex": corr_idx
                })
                i = j
            else:
                i += 1
        else:
            i += 1
    return questions

def parse_qa_files():
    qa_list = []

    def add_qa(q, a, src):
        q = clean_text(q)
        a = clean_option_text(a)
        if not q or not a:
            return
        if len(q) < 10 or len(a) < 1 or len(a) > 95:
            return
        if is_pedagogy(q) or is_pedagogy(a):
            return
        if "++" in q or "++" in a or "қате" in a.lower():
            return
        if q.startswith("</") or q.startswith("http"):
            return
        qa_list.append({"text": q, "answer": a, "source": src})

    # 1. информатика.docx
    p1 = os.path.join(SOURCE_FOLDER, "информатика.docx")
    if os.path.exists(p1):
        doc = docx.Document(p1)
        for p in doc.paragraphs:
            t = clean_text(p.text)
            if ":+" in t or ": +" in t:
                parts = re.split(r":\s*\+", t, maxsplit=1)
                if len(parts) == 2:
                    a = parts[1].split("/")[0].strip()
                    if not a.startswith("+"): # skip ++ multi-answer pedagogy lines
                        add_qa(parts[0], a, "информатика.docx")

    # 2. Слив толықтырылған
    p2 = os.path.join(SOURCE_FOLDER, "Слив толықтырылған (1).docx")
    if os.path.exists(p2):
        doc = docx.Document(p2)
        for p in doc.paragraphs:
            t = clean_text(p.text)
            if "?" in t:
                pts = t.split("?", 1)
                add_qa(pts[0].strip() + "?", pts[1], "Слив толықтырылған")

    # 3. СЛИВ 2026 соңғысы
    p3 = os.path.join(SOURCE_FOLDER, "СЛИВ 2026 соңғысы (1).docx")
    if os.path.exists(p3):
        doc = docx.Document(p3)
        for p in doc.paragraphs:
            t = clean_text(p.text)
            m = re.match(r"^\d+[\.\)]\s*(.+)", t)
            if m:
                line = m.group(1).strip()
                if "?" in line:
                    pts = line.split("?", 1)
                    add_qa(pts[0].strip() + "?", pts[1], "СЛИВ 2026 соңғысы")
                elif ":" in line:
                    pts = line.split(":", 1)
                    add_qa(pts[0], pts[1], "СЛИВ 2026 соңғысы")

    # 4. Daily files
    for fname in ["слив 17 ақпан (1).docx", "слив 18 ақпан (1).docx", "слив 20.02 (1).docx", "19 ақпан (1).docx", "19.02.2026Г-Информатика (1).docx"]:
        path = os.path.join(SOURCE_FOLDER, fname)
        if os.path.exists(path):
            doc = docx.Document(path)
            for p in doc.paragraphs:
                t = clean_text(p.text)
                if "?" in t:
                    pts = t.split("?", 1)
                    q = re.sub(r"^\d+[\.\)]\s*", "", pts[0].strip()) + "?"
                    add_qa(q, pts[1], fname)
                elif ":" in t and not t.startswith("A\tB") and not t.startswith("http"):
                    pts = t.split(":", 1)
                    q = re.sub(r"^\d+[\.\)]\s*", "", pts[0].strip())
                    add_qa(q, pts[1], fname)

    # Deduplicate by question text
    seen = set()
    unique_qa = []
    for item in qa_list:
        key = item["text"].lower()
        if key not in seen:
            seen.add(key)
            unique_qa.append(item)
    return unique_qa

if __name__ == "__main__":
    print("Shilde:", len(parse_shilde()))
    print("Info1:", len(parse_informatika_1()))
    print("Prob2:", len(parse_probny_2()))
    print("Clean QA:", len(parse_qa_files()))
