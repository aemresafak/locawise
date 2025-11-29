# should throw when invalid combinations for target languages are provided

import pytest

from locawise.errors import InvalidLanguageCodeError, InvalidTargetLanguageMappingCombinationError
from locawise.localization.config import LocalizationConfig


@pytest.mark.parametrize('target_lang_codes', [
    {'treq'},
    {'tr', 'fr', 'es', '11'},
    {'tr', 'es', 'Tr-tr'}
])
def test_localization_config_invalid_target_lang_codes(target_lang_codes):
    with pytest.raises(InvalidLanguageCodeError):
        LocalizationConfig(
            version='1.0',
            source_lang_code='en',
            target_lang_codes=target_lang_codes,
            file_name_pattern='messages_{language}.properties'
        )


@pytest.mark.parametrize('language_file_paths', [
    {
        'en': 'en.json',
        'tr': 'tr.json',
        'deg': 'de.json'
    },
    {
        'frq': 'fr.json'
    }
])
def test_localization_config_with_invalid_target_lang_code_in_language_file_paths(language_file_paths):
    with pytest.raises(InvalidLanguageCodeError):
        LocalizationConfig(
            version='1.0',
            source_lang_code='en',
            language_file_paths=language_file_paths
        )


@pytest.mark.parametrize(['file_name_pattern', 'target_language_codes', 'language_file_paths'], [
    (None, None, None),
    (None, {'en'}, None),
    (None, {'en'}, {'en': 'en.json'}),
    ('{language}.json', None, None),
    ('{language}.json', None, {'en': 'en.json'}),
    ('{language}.json', {'en'}, {'en': 'en.json'}),
])
def test_localization_config_with_invalid_combinations_for_target_language_mappings(file_name_pattern,
                                                                                    target_language_codes,
                                                                                    language_file_paths):
    with pytest.raises(InvalidTargetLanguageMappingCombinationError):
        LocalizationConfig(
            version='1.0',
            source_lang_code='en',
            language_file_paths=language_file_paths,
            file_name_pattern=file_name_pattern,
            target_lang_codes=target_language_codes
        )
