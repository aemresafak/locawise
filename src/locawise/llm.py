import json
import logging
import re
from abc import ABC, abstractmethod

import httpx
import openai
from google import genai
from google.genai import types
from google.genai.errors import APIError
from openai import APIStatusError, OpenAIError
from tenacity import retry, stop_after_attempt, retry_if_exception_type, \
    wait_random_exponential

from locawise.envutils import retrieve_openai_api_key
from locawise.errors import InvalidLLMOutputError, LLMApiError, TransientLLMApiError

_NON_RETRYABLE_ERROR_STATUS_CODES = [400, 401, 403, 404, 409, 422]


class LLMStrategy(ABC):
    @retry(stop=stop_after_attempt(8),
           wait=wait_random_exponential(multiplier=5, exp_base=3, max=300, min=15),
           retry=retry_if_exception_type(TransientLLMApiError))
    @abstractmethod
    async def call(self, system_prompt: str, user_prompt: str) -> dict[str, str]:
        pass


class LLMContext:
    def __init__(self, strategy: LLMStrategy):
        self.strategy = strategy

    async def call(self, system_prompt: str, user_prompt: str) -> dict[str, str]:
        """
        :raise LLMApiError
         """
        return await self.strategy.call(system_prompt, user_prompt)


class MockLLMStrategy(LLMStrategy):
    def __init__(self):
        self.regex = r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}'

    def _extract_pairs_from_prompt(self, prompt: str) -> dict[str, str]:
        input_match = re.search(self.regex, prompt, re.DOTALL)
        if not input_match:
            return {}

        pairs_str = input_match.group(0).strip()

        try:
            pairs = json.loads(pairs_str)
            return {str(k): str(v) for k, v in pairs.items()}
        except json.JSONDecodeError:
            return {}

    async def call(self, system_prompt: str, user_prompt: str) -> dict[str, str]:
        if "THROW_LLM_API_ERROR" in user_prompt:
            raise LLMApiError
        if "THROW_INVALID_LLM_OUTPUT_ERROR" in user_prompt:
            raise InvalidLLMOutputError

        pairs = self._extract_pairs_from_prompt(user_prompt)
        output = {}
        for k, v in pairs.items():
            output[k] = f"TRANSLATED_{v}"

        return output


class GeminiLLMStrategy(LLMStrategy):
    def __init__(self, model: str | None = None, location: str | None = None):
        if not model:
            self.model = 'gemini-2.0-flash'
        else:
            self.model = model

        self.temperature = 0

        if not location:
            self.location = 'europe-west1'
        else:
            self.location = location

        self.client = genai.Client(vertexai=True, location=self.location)

    async def call(self, system_prompt: str, user_prompt: str) -> dict[str, str]:
        config = self._create_config(system_prompt)
        try:
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=user_prompt,
                config=config
            )
        except APIError as e:
            if e.code in _NON_RETRYABLE_ERROR_STATUS_CODES:
                raise LLMApiError
            else:
                raise TransientLLMApiError
        except Exception as e:
            raise LLMApiError from e

        return _parse_json_text(response.text)

    def _create_config(self, system_prompt):
        return types.GenerateContentConfig(temperature=self.temperature,
                                           system_instruction=system_prompt,
                                           automatic_function_calling=types.AutomaticFunctionCallingConfig(
                                               disable=True))


class OpenAiLLMStrategy(LLMStrategy):
    def __init__(self, model: str | None = None):
        self.client = openai.AsyncClient(api_key=retrieve_openai_api_key(), max_retries=0,
                                         timeout=httpx.Timeout(600, connect=10))
        if not model:
            self.model = 'gpt-4.1-mini'
        else:
            self.model = model
        self.temperature = 0

    async def call(self, system_prompt: str, user_prompt: str) -> dict[str, str]:
        try:
            response = await self.client.responses.create(
                model=self.model,
                instructions=system_prompt,
                input=user_prompt,
                temperature=self.temperature,
            )
        except APIStatusError as e:
            if e.status_code in _NON_RETRYABLE_ERROR_STATUS_CODES:
                raise LLMApiError from e
            else:
                logging.warning(f"Transient llm api error occurred. status={e.status_code}")
                raise TransientLLMApiError from e
        except OpenAIError as e:
            raise TransientLLMApiError from e
        except Exception as e:
            raise LLMApiError from e

        return _parse_json_text(response.output_text)


def _extract_json_text(text) -> str:
    pattern = r"```json\s*([\s\S]*?)\s*```"
    match = re.search(pattern, text)
    if match:
        return match.group(1)
    return text


def _parse_json_text(text: str) -> dict[str, str]:
    try:
        json_text: str = text
        if text.strip().startswith('```json'):
            json_text: str = _extract_json_text(text)
        return json.loads(json_text)
    except Exception as e:
        logging.warning('Invalid LLM output. This generally happens when you use a "dumber" LLM model or '
                        'a model with low maximum output tokens. Please change '
                        'the LLM model.')
        raise InvalidLLMOutputError from e


def create_strategy(model: str | None, location: str | None) -> LLMStrategy:
    if model == 'mock':
        return MockLLMStrategy()

    openai_key = retrieve_openai_api_key()
    if openai_key:
        return OpenAiLLMStrategy(model=model)

    try:
        return GeminiLLMStrategy(model=model, location=location)
    except (Exception,):
        logging.error("No environment variables found for any supported LLM providers. Please add the necessary "
                      "environment variables.")
        raise ValueError('No environment variables found for LLM providers.')
