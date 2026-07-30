class PipelineEngine:
    def __init__(self, skill_registry):
        self.skills = skill_registry
    async def run_pipeline(self, steps, context):
        result = {}
        for skill_id in steps:
            skill = self.skills.get(skill_id)
            if skill:
                result[skill_id] = await skill.execute(result, context)
        return result
