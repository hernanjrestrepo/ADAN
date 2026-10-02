"""Dobles de prueba compartidos."""
from app.ai.base import LLMAdapter, LLMResponse

VALID_VOTE = (
    '{"analysis":"A","justification":"J","vote":"PROCEED","confidence":80,'
    '"key_strengths":["s"],"key_concerns":["c"],"questions":["q"]}'
)


class FakeLLM(LLMAdapter):
    """LLM de prueba: respuestas configurables y conteo de llamadas."""

    def __init__(self, chat_replies=None, generate_reply="Documento generado", stream_tokens=None):
        self.chat_replies = list(chat_replies or [VALID_VOTE])
        self.generate_reply = generate_reply
        self.stream_tokens = stream_tokens or ["Hola", "\nmundo"]
        self.chat_calls = 0
        self.generate_calls = 0
        self.last_messages = None

    async def chat(self, messages, model=None, temperature=0.7, max_tokens=2048):
        self.chat_calls += 1
        self.last_messages = messages
        reply = self.chat_replies[(self.chat_calls - 1) % len(self.chat_replies)]
        return LLMResponse(content=reply, model="fake")

    async def chat_stream(self, messages, model=None, temperature=0.7, max_tokens=2048):
        self.last_messages = messages
        for token in self.stream_tokens:
            yield token

    async def generate(self, prompt, model=None, system=None, temperature=0.7, max_tokens=2048):
        self.generate_calls += 1
        return LLMResponse(content=self.generate_reply, model="fake")

    async def health_check(self):
        return True

    def list_models(self):
        return []
