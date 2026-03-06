import google.generativeai as genai
from groq import Groq
from app.core.config import settings

class LLMService:
    def __init__(self):
        settings.validate()
        self.provider = settings.LLM_PROVIDER
        self.model_name = settings.MODEL_NAME
        
        if self.provider == "gemini":
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.client = genai.GenerativeModel(self.model_name)
        elif self.provider == "groq":
            self.client = Groq(api_key=settings.GROQ_API_KEY)

    def generate_text(self, prompt: str) -> str:
        """
        Generates text using the configured LLM.
        """
        try:
            if self.provider == "gemini":
                response = self.client.generate_content(prompt)
                if not response.text:
                     raise ValueError("Empty response from LLM")
                return response.text
                
            elif self.provider == "groq":
                chat_completion = self.client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=self.model_name,
                    max_tokens=500,
                    timeout=10.0  # 10 second timeout
                )
                return chat_completion.choices[0].message.content
                
        except Exception as e:
            print(f"LLM service error: {e}")
            return f"LLM_ERROR: {str(e)}"

llm_service = LLMService()
