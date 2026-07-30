import time
from src.core.interfaces import ProviderResponse
from src.providers.base import ProviderAdapter
from src.core.budget import BudgetManager

try:
    from openai import OpenAI
except:
    OpenAI = None

class DeepSeekAdapter(ProviderAdapter):
    def __init__(self, api_key, default_model="deepseek-chat", budget_limit=5.0):
        if OpenAI is None:
            raise ImportError("openai not installed")
        self.client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")
        self.default_model = default_model
        self.budget_manager = BudgetManager(budget_limit=budget_limit)
    
    def generate(self, prompt, system_prompt=None, temperature=0.7, max_tokens=4096, model=None, **kwargs):
        model = model or self.default_model
        
        estimated_prompt_tokens = int(len(prompt) * 1.3) + int(len(system_prompt or "") * 1.3)
        estimated_completion_tokens = max_tokens
        estimated_cost = self.estimate_cost(estimated_prompt_tokens, estimated_completion_tokens, model)
        
        if not self.budget_manager.can_afford(estimated_cost):
            raise Exception(f"תקציב חרג! (${self.budget_manager.budget_limit:.2f}) - עצור או הגדל תקציב")
        
        start = time.time()
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            actual_cost = self.estimate_cost(
                response.usage.prompt_tokens,
                response.usage.completion_tokens,
                model
            )
            
            self.budget_manager.record_cost(
                actual_cost,
                description=f"קריאה למודל {model} ({len(prompt)} תווים)"
            )
            
            return ProviderResponse(
                content=response.choices[0].message.content,
                provider="deepseek",
                model=model,
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens,
                cost=actual_cost
            )
        except Exception as e:
            raise Exception(f"DeepSeek error: {e}")
    
    def estimate_cost(self, prompt_tokens, completion_tokens, model=None):
        """מחשב עלות משוערת לפי מחירי DeepSeek"""
        input_cost = (prompt_tokens / 1_000_000) * 0.14
        output_cost = (completion_tokens / 1_000_000) * 0.28
        return input_cost + output_cost
    
    def get_status(self):
        """מחזיר את מצב התקציב"""
        return self.budget_manager.get_status()