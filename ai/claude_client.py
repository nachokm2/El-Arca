import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from rich.console import Console
import config

console = Console()


class ClaudeClient:
    def __init__(self, api_key: str = ""):
        key = api_key or config.ANTHROPIC_API_KEY
        if not key:
            raise ValueError("ANTHROPIC_API_KEY no está configurado en .env")
        self.client = anthropic.Anthropic(api_key=key)
        self.model = config.MODEL_NAME
        self.max_tokens = config.MAX_TOKENS

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((anthropic.RateLimitError, anthropic.APIStatusError)),
    )
    def completar(self, system_prompt: str, user_prompt: str, temperatura: float = 0.8) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return response.content[0].text

    def completar_json(self, system_prompt: str, user_prompt: str) -> str:
        """Solicita respuesta en formato JSON."""
        system_con_json = (
            system_prompt
            + "\n\nIMPORTANTE: Responde ÚNICAMENTE con JSON válido, sin texto adicional, sin markdown."
        )
        return self.completar(system_con_json, user_prompt, temperatura=0.5)

    def ping(self) -> bool:
        try:
            self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hola"}],
            )
            return True
        except Exception as e:
            console.print(f"[red]Error conectando con Claude: {e}[/red]")
            return False
