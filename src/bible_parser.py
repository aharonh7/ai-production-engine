"""
Bible Parser - מחלץ מידע מקובץ בייבל
"""
import re
import json

def parse_bible(bible_text: str) -> dict:
    """מחלץ את כל המידע מהבייבל"""
    
    result = {
        "title": "",
        "book_type": "novel",
        "target_audience": "",
        "language": "English",
        "min_words": 3000,
        "max_words": 5000,
        "chapter_count": 5,
        "words_per_chapter": 1000,
        "pov": "",
        "tense": "",
        "tone": "",
        "characters": [],
        "setting": "",
        "core_promise": "",
        "one_sentence_pitch": "",
        "description": ""
    }
    
    # === 1. כותרת ===
    match = re.search(r'title:\s*(.+)', bible_text, re.IGNORECASE)
    if match:
        result["title"] = match.group(1).strip()
    
    # === 2. סוג ספר ===
    if "novel" in bible_text.lower() or "fiction" in bible_text.lower():
        result["book_type"] = "novel"
    elif "children" in bible_text.lower():
        result["book_type"] = "childrens"
    elif "technical" in bible_text.lower() or "instructional" in bible_text.lower():
        result["book_type"] = "technical"
    elif "self-help" in bible_text.lower() or "personal development" in bible_text.lower():
        result["book_type"] = "selfhelp"
    
    # === 3. קהל יעד ===
    match = re.search(r'target_audience:\s*(.+)', bible_text, re.IGNORECASE)
    if match:
        result["target_audience"] = match.group(1).strip()
    
    # === 4. שפה ===
    match = re.search(r'language:\s*(.+)', bible_text, re.IGNORECASE)
    if match:
        result["language"] = match.group(1).strip()
    
    # === 5. טווח מילים לספר ===
    match = re.search(r'target_total_word_count:\s*(\d+)-(\d+)', bible_text, re.IGNORECASE)
    if match:
        result["min_words"] = int(match.group(1))
        result["max_words"] = int(match.group(2))
    
    # === 6. מספר פרקים ===
    match = re.search(r'target_chapter_count:\s*(\d+)', bible_text, re.IGNORECASE)
    if match:
        result["chapter_count"] = int(match.group(1))
    
    # === 7. מילים לפרק ===
    match = re.search(r'target_words_per_chapter:\s*(\d+)-?(\d+)?', bible_text, re.IGNORECASE)
    if match:
        if match.group(2):
            result["words_per_chapter"] = (int(match.group(1)) + int(match.group(2))) // 2
        else:
            result["words_per_chapter"] = int(match.group(1))
    
    # === 8. POV ===
    match = re.search(r'point_of_view:\s*(.+)', bible_text, re.IGNORECASE)
    if match:
        result["pov"] = match.group(1).strip()
    
    # === 9. Tense ===
    match = re.search(r'tense:\s*(.+)', bible_text, re.IGNORECASE)
    if match:
        result["tense"] = match.group(1).strip()
    
    # === 10. Tone ===
    match = re.search(r'tone:\s*(.+)', bible_text, re.IGNORECASE)
    if match:
        result["tone"] = match.group(1).strip()
    
    # === 11. Core Promise ===
    match = re.search(r'core_promise:\s*(.+)', bible_text, re.IGNORECASE)
    if match:
        result["core_promise"] = match.group(1).strip()
    
    # === 12. One Sentence Pitch ===
    match = re.search(r'one_sentence_pitch:\s*(.+)', bible_text, re.IGNORECASE)
    if match:
        result["one_sentence_pitch"] = match.group(1).strip()
    
    # === 13. דמויות ===
    char_pattern = r'\- name:\s*(.+)'
    characters = re.findall(char_pattern, bible_text, re.IGNORECASE)
    if characters:
        result["characters"] = [c.strip() for c in characters]
    
    # === 14. Setting ===
    match = re.search(r'time_period_and_place:\s*(.+)', bible_text, re.IGNORECASE)
    if match:
        result["setting"] = match.group(1).strip()
    else:
        match = re.search(r'setting:\s*(.+)', bible_text, re.IGNORECASE)
        if match:
            result["setting"] = match.group(1).strip()
    
    # === 15. Description (תיאור קצר) ===
    if result["one_sentence_pitch"]:
        result["description"] = result["one_sentence_pitch"]
    elif result["core_promise"]:
        result["description"] = result["core_promise"]
    
    return result