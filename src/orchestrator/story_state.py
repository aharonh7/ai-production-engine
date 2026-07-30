"""
Story State Manager - ניהול מצב הדמויות, העלילה והעובדות
"""
import json
from typing import Dict, List, Optional

class StoryState:
    """
    מנהל את ה-Story State של הפרויקט
    """
    
    def __init__(self, project_id: str, story_state_json: Optional[str] = None):
        self.project_id = project_id
        self.data = self._init_state()
        if story_state_json:
            try:
                self.data = json.loads(story_state_json)
            except:
                pass
    
    def _init_state(self) -> Dict:
        """אתחול מבנה ה-Story State"""
        return {
            "characters": {},      # {name: {location, emotional_state, knowledge, physical_state, relationships}}
            "locations": {},       # {name: {description, established_facts}}
            "objects": {},         # {name: {description, location, importance}}
            "timeline": [],        # [{event, chapter, characters_involved}]
            "open_threads": [],    # [{thread, introduced_in_chapter, status}]
            "glossary": {},        # {term: spelling_rule}
            "established_facts": {} # {fact: chapter_established}
        }
    
    def get_character(self, name: str) -> Dict:
        """מחזיר מצב של דמות"""
        return self.data["characters"].get(name, {})
    
    def update_character(self, name: str, updates: Dict):
        """מעדכן מצב של דמות"""
        if name not in self.data["characters"]:
            self.data["characters"][name] = {}
        self.data["characters"][name].update(updates)
    
    def add_open_thread(self, thread: str, chapter: int):
        """מוסיף חוט עלילה חדש"""
        self.data["open_threads"].append({
            "thread": thread,
            "introduced_in_chapter": chapter,
            "status": "open"
        })
    
    def close_thread(self, thread: str, chapter: int):
        """סוגר חוט עלילה"""
        for t in self.data["open_threads"]:
            if t["thread"] == thread:
                t["status"] = "closed"
                t["closed_in_chapter"] = chapter
    
    def add_established_fact(self, fact: str, chapter: int):
        """מוסיף עובדה חדשה"""
        self.data["established_facts"][fact] = chapter
    
    def add_glossary_term(self, term: str, rule: str):
        """מוסיף מונח למילון"""
        self.data["glossary"][term] = rule
    
    def get_timeline(self) -> List:
        """מחזיר את ציר הזמן"""
        return self.data["timeline"]
    
    def add_timeline_event(self, event: str, chapter: int, characters: List[str] = None):
        """מוסיף אירוע לציר הזמן"""
        self.data["timeline"].append({
            "event": event,
            "chapter": chapter,
            "characters": characters or []
        })
    
    def to_json(self) -> str:
        """מחזיר את המצב כ-JSON"""
        return json.dumps(self.data, ensure_ascii=False, indent=2)
    
    def get_open_threads_summary(self) -> str:
        """מחזיר סיכום של חוטי עלילה פתוחים"""
        open_threads = [t["thread"] for t in self.data["open_threads"] if t["status"] == "open"]
        if not open_threads:
            return "No open threads"
        return ", ".join(open_threads)
    
    def get_characters_summary(self) -> str:
        """מחזיר סיכום של כל הדמויות ומצבן"""
        summary = []
        for name, data in self.data["characters"].items():
            loc = data.get("location", "unknown")
            state = data.get("emotional_state", "unknown")
            summary.append(f"{name}: {loc} ({state})")
        return "\n".join(summary) if summary else "No characters established"