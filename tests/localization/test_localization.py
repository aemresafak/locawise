import pytest

from src.threepio import llm
from src.threepio.errors import LocalizationError
from src.threepio.llm import LLMContext
from src.threepio.localization import localize


@pytest.mark.asyncio
@pytest.mark.parametrize("chunk_size", [
    1,
    2,
    3,
    4,
    10,
    50,
    100
])
async def test_localize_with_mock_strategy_and_valid_pairs(chunk_size):
    strategy = llm.MockLLMStrategy()
    context = LLMContext(strategy)
    pairs = {
        'key1': 'value1',
        'key2': 'value2',
        'key3': 'value3',
        'key4': 'value4',
        'key5': 'value5',
        'key6': 'value6',
        'key7': 'value7',
    }
    target_language = 'en'

    result = await localize(context, pairs, target_language, chunk_size=chunk_size)

    assert result == {
        'key1': 'TRANSLATED_value1',
        'key2': 'TRANSLATED_value2',
        'key3': 'TRANSLATED_value3',
        'key4': 'TRANSLATED_value4',
        'key5': 'TRANSLATED_value5',
        'key6': 'TRANSLATED_value6',
        'key7': 'TRANSLATED_value7',
    }


@pytest.mark.asyncio
async def test_localize_with_mock_strategy_and_llm_api_error():
    strategy = llm.MockLLMStrategy()
    context = LLMContext(strategy)
    pairs = {
        'key1': 'THROW_LLM_API_ERROR',
        'key2': 'value2',
        'key3': 'value3',
        'key4': 'value4',
        'key5': 'THROW_LLM_API_ERROR',
        'key6': 'value6',
        'key7': 'value7',
    }
    target_language = 'en'

    with pytest.raises(LocalizationError):
        await localize(context, pairs, target_language, chunk_size=1)


@pytest.mark.asyncio
async def test_localize_with_mock_strategy_and_invalid_llm_output_error():
    strategy = llm.MockLLMStrategy()
    context = LLMContext(strategy)
    pairs = {
        'key1': 'THROW_INVALID_LLM_OUTPUT_ERROR',
        'key2': 'value2',
        'key3': 'value3',
        'key4': 'value4',
        'key5': 'value5',
        'key6': 'value6',
        'key7': 'value7',
    }
    target_language = 'en'

    with pytest.raises(LocalizationError):
        await localize(context, pairs, target_language, chunk_size=2)
