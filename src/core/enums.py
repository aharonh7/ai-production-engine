from enum import Enum
class ProjectState(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
class BookType(str, Enum):
    NOVEL = "novel"
    NON_FICTION = "non_fiction"
