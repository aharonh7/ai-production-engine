from src.templates.base import BookTemplate
class NovelTemplate(BookTemplate):
    pipeline_steps = ["classify_project", "create_outline", "write_chapter", "assemble_manuscript"]
