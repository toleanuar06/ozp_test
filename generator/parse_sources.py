import os
import re
import json
import docx
import pypdf

SOURCE_FOLDER = r"c:\Users\tolea\Downloads\Telegram Desktop"

def clean_text(s):
    if not s:
        return ""
    # normalize spaces and quotes
    s = s.replace("«", "\"").replace("»", "\"").replace("”", "\"").replace("“", "\"")
    s = s.replace("’", "'").replace("`", "'")
    return re.sub(r"\s+", " ", s).strip()

def parse_shilde():
    path = os.path.join(SOURCE_FOLDER, "информатика шілде тест нұсқа (1).docx")
    if not os.path.exists(path):
        return []
    doc = docx.Document(path)
    
    answers = {}
    for t in doc.tables:
        for row in t.rows:
            cells = [clean_text(c.text) for c in row.cells]
            for i in range(0, len(cells)-1, 2):
                if cells[i].isdigit():
                    answers[int(cells[i])] = cells[i+1].upper()
                    
    paras = [clean_text(p.text) for p in doc.paragraphs if clean_text(p.text)]
    questions = []
    i = 0
    q_num = 1
    letter_map = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'Е': 4}
    
    while i < len(paras):
        p = paras[i]
        if i + 4 < len(paras):
            q_text = p
            opts = [paras[i+1], paras[i+2], paras[i+3], paras[i+4]]
            ans_letter = answers.get(q_num, 'A')
            corr_idx = letter_map.get(ans_letter, 0)
            if corr_idx >= len(opts):
                corr_idx = 0
            questions.append({
                "source": "информатика шілде тест нұсқа",
                "text": q_text,
                "options": opts,
                "correctIndex": corr_idx
            })
            q_num += 1
            i += 5
        else:
            i += 1
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
        p = paras[i]
        t = clean_text(p.text)
        m = re.match(r"^(\d+)[\.\)]\s*(.+)", t)
        if m:
            q_text = m.group(2)
            opts = []
            corr_idx = 0
            j = i + 1
            while j < len(paras) and len(opts) < 4:
                p_opt = paras[j]
                opt_t = clean_text(p_opt.text)
                if re.match(r"^\d+[\.\)]", opt_t):
                    break
                is_colored = any(r.font.color and r.font.color.rgb for r in p_opt.runs if r.text.strip())
                is_hl = any(r.font.highlight_color for r in p_opt.runs if r.text.strip())
                if is_colored or is_hl:
                    corr_idx = len(opts)
                # remove option letter prefix like A) or B.
                clean_opt = re.sub(r"^[A-Da-dА-Да-д][\.\)]\s*", "", opt_t)
                opts.append(clean_opt if clean_opt else opt_t)
                j += 1
            if len(opts) >= 2:
                while len(opts) < 4:
                    opts.append(f"Басқа нұсқа {len(opts)+1}")
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
    questions = []
    i = 0
    while i < len(paras):
        t = paras[i]
        if not re.match(r"^[A-Da-dА-Да-д][\.\)]", t):
            q_text = re.sub(r"^\d+[\.\)]\s*", "", t)
            opts = []
            corr_idx = 0
            j = i + 1
            while j < len(paras) and len(opts) < 4:
                opt_t = paras[j]
                m_opt = re.match(r"^[A-Da-dА-Да-д][\.\)]\s*(.+)", opt_t)
                if m_opt:
                    opt_val = m_opt.group(1).strip()
                    if "+" in opt_val or "дұрыс" in opt_val.lower():
                        corr_idx = len(opts)
                    clean_val = re.sub(r"[\+\-]\s*(қате|дұрыс)?", "", opt_val).strip()
                    opts.append(clean_val)
                    j += 1
                else:
                    break
            if len(opts) >= 2:
                while len(opts) < 4:
                    opts.append(f"Қосымша нұсқа {len(opts)+1}")
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
    # 1. информатика.docx
    p1 = os.path.join(SOURCE_FOLDER, "информатика.docx")
    if os.path.exists(p1):
        doc = docx.Document(p1)
        for p in doc.paragraphs:
            t = clean_text(p.text)
            if ":+" in t or ": +" in t:
                parts = re.split(r":\s*\+", t, maxsplit=1)
                if len(parts) == 2:
                    q = parts[0].strip()
                    a = parts[1].strip()
                    if "/" in a:
                        a = a.split("/")[0].strip()
                    if len(q) > 4 and len(a) > 0:
                        qa_list.append({"text": q, "answer": a, "source": "информатика.docx"})
                        
    # 2. Слив толықтырылған
    p2 = os.path.join(SOURCE_FOLDER, "Слив толықтырылған (1).docx")
    if os.path.exists(p2):
        doc = docx.Document(p2)
        for p in doc.paragraphs:
            t = clean_text(p.text)
            if "?" in t:
                pts = t.split("?", 1)
                q = pts[0].strip() + "?"
                a = pts[1].strip()
                if len(q) > 8 and len(a) > 0:
                    qa_list.append({"text": q, "answer": a, "source": "Слив толықтырылған"})
                    
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
                    q = pts[0].strip() + "?"
                    a = pts[1].strip()
                    if len(q) > 6 and len(a) > 0:
                        qa_list.append({"text": q, "answer": a, "source": "СЛИВ 2026 соңғысы"})
                elif ":" in line:
                    pts = line.split(":", 1)
                    q = pts[0].strip()
                    a = pts[1].strip()
                    if len(q) > 6 and len(a) > 0:
                        qa_list.append({"text": q, "answer": a, "source": "СЛИВ 2026 соңғысы"})
                        
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
                    a = pts[1].strip()
                    if len(q) > 8 and len(a) > 0:
                        qa_list.append({"text": q, "answer": a, "source": fname})
                elif ":" in t and not t.startswith("A\tB") and not t.startswith("http"):
                    pts = t.split(":", 1)
                    q = re.sub(r"^\d+[\.\)]\s*", "", pts[0].strip())
                    a = pts[1].strip()
                    if len(q) > 10 and len(a) > 0:
                        qa_list.append({"text": q, "answer": a, "source": fname})
                        
    return qa_list

def parse_pdf():
    pdf_path = os.path.join(SOURCE_FOLDER, "Информатика тест жинақ.pdf")
    if not os.path.exists(pdf_path):
        return []
    reader = pypdf.PdfReader(pdf_path)
    full_text = "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
    
    questions = []
    # split into blocks by question marks or double asterisks
    lines = [clean_text(l) for l in full_text.split("\n") if clean_text(l)]
    
    current_q = None
    for l in lines:
        if l.startswith("**"):
            opt_text = l.replace("**", "").strip()
            if current_q and len(current_q["options"]) < 4 and opt_text:
                current_q["options"].append(opt_text)
        elif l.endswith(":") or l.endswith("?"):
            if current_q and len(current_q.get("options", [])) >= 2:
                while len(current_q["options"]) < 4:
                    current_q["options"].append("Басқа анықтама")
                questions.append(current_q)
            current_q = {
                "source": "Информатика тест жинақ.pdf",
                "text": l,
                "options": [],
                "correctIndex": 0
            }
    if current_q and len(current_q.get("options", [])) >= 2:
        while len(current_q["options"]) < 4:
            current_q["options"].append("Басқа анықтама")
        questions.append(current_q)
    return questions

if __name__ == "__main__":
    q_shilde = parse_shilde()
    q_info1 = parse_informatika_1()
    q_prob2 = parse_probny_2()
    qa_list = parse_qa_files()
    q_pdf = parse_pdf()
    print(f"Direct MCQ questions: Shilde={len(q_shilde)}, Info1={len(q_info1)}, Prob2={len(q_prob2)}, PDF={len(q_pdf)}")
    print(f"QA pairs: {len(qa_list)}")
