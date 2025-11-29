import pytest

from locawise.errors import InvalidYamlConfigError
from locawise.localization.config import read_localization_config_yaml, LocalizationConfig
from tests.utils import get_absolute_path

DEFAULT_GLOSSARY = {'key1': 'value1', 'key2': 'value2'}


@pytest.mark.asyncio(loop_scope='module')
@pytest.mark.parametrize('file_path', [
    'resources/localizationconfigs/config_with_missing_values.yaml',
    'resources/localizationconfigs/config_with_all_values_except_file_path.yaml',
    'resources/localizationconfigs/invalid.yaml',
    'resources/localizationconfigs/invalid_lang_code.yaml'
])
async def test_read_localization_config_yaml_invalid_yaml(file_path: str):
    with pytest.raises(InvalidYamlConfigError):
        path = get_absolute_path(file_path)
        await read_localization_config_yaml(path)


@pytest.mark.asyncio(loop_scope='module')
@pytest.mark.parametrize('file_path, expected', [
    ('resources/localizationconfigs/config_with_file_name_pattern.yaml',
     LocalizationConfig(version='v1.0',
                        context='You work for a finance company',
                        glossary=DEFAULT_GLOSSARY,
                        tone='Be as kind as possible',
                        file_name_pattern='{language}.json',
                        source_lang_code='tr',
                        target_lang_codes={'fr', 'en'})
     ),

    ('resources/localizationconfigs/config_with_language_file_mapping.yaml',
     LocalizationConfig(version='v1.0',
                        context='You work for a finance company',
                        glossary=DEFAULT_GLOSSARY,
                        tone='Be as kind as possible',
                        source_lang_code='tr',
                        language_file_paths={
                            'en': 'en-US.json',
                            'tr': 'tr-TR.json',
                            'de': 'de.json'
                        })
     )
])
async def test_read_localization_config_yaml_valid_yaml(file_path: str, expected: LocalizationConfig):
    path = get_absolute_path(file_path)
    actual = await read_localization_config_yaml(path)
    assert actual == expected
