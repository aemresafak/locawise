import logging
import os
from typing import Self, Annotated

import yaml
from pydantic import BaseModel, ValidationError, model_validator, Field, ConfigDict

from locawise.envutils import generate_localization_file_name
from locawise.errors import InvalidYamlConfigError, InvalidLanguageCodeError, \
    InvalidTargetLanguageMappingCombinationError, LocalizationConfigValidationError
from locawise.fileutils import read_file
from locawise.langutils import is_valid_two_letter_lang_code

INVALID_TARGET_LANGUAGE_MAPPING_COMBINATION = ("Either language-file-paths or target-lang-codes with file-name-pattern "
                                               "must be provided")

LocalizationRootPath = Annotated[
    str,
    Field(serialization_alias="localization-root-path", validation_alias="localization-root-path")
]

SourceLangCode = Annotated[
    str,
    Field(serialization_alias="source-lang-code", validation_alias="source-lang-code")
]

TargetLangCodes = Annotated[
    set[str],
    Field(serialization_alias="target-lang-codes", validation_alias="target-lang-codes")
]

FileNamePattern = Annotated[
    str | None,
    Field(serialization_alias="file-name-pattern", validation_alias="file-name-pattern")
]

LanguageFilePaths = Annotated[
    dict[str, str],
    Field(
        serialization_alias="language-file-paths",
        validation_alias="language-file-paths",
        description="A mapping of language codes to their specific file paths. If provided, this mapping will be used "
                    "instead of generating file names based on a pattern. Paths should be relative to the "
                    "localization root path."
    )
]

LlmModel = Annotated[
    str | None,
    Field(serialization_alias="llm-model", validation_alias="llm-model")
]

LlmLocation = Annotated[
    str | None,
    Field(serialization_alias="llm-location", validation_alias="llm-location")
]


class LocalizationConfig(BaseModel):
    version: str
    localization_root_path: LocalizationRootPath = ''
    source_lang_code: SourceLangCode
    target_lang_codes: TargetLangCodes = set()
    file_name_pattern: FileNamePattern = None
    language_file_paths: LanguageFilePaths = dict()
    context: str = ""
    glossary: dict[str, str] = dict()
    tone: str = ""
    llm_model: LlmModel = None
    llm_location: LlmLocation = None

    model_config = ConfigDict(
        populate_by_name=True,
        validate_by_name=True,  # New name for 'allow_population_by_field_name'
    )

    @model_validator(mode='after')
    def validate_either_file_name_pattern_or_language_file_paths(self) -> Self:
        fnp = self.file_name_pattern
        lfp = self.language_file_paths
        tlc = self.target_lang_codes
        file_name_pattern_combination_provided = fnp and tlc and not lfp
        language_file_path_provided = lfp and not fnp and not tlc
        if not file_name_pattern_combination_provided and not language_file_path_provided:
            raise InvalidTargetLanguageMappingCombinationError(INVALID_TARGET_LANGUAGE_MAPPING_COMBINATION)
        return self

    @model_validator(mode='after')
    def validate_lang_codes(self) -> Self:
        if self.language_file_paths:
            for lang_code in self.language_file_paths.keys():
                if not is_valid_two_letter_lang_code(lang_code):
                    raise InvalidLanguageCodeError(f'{lang_code} is not a valid language code')
            return self

        if not is_valid_two_letter_lang_code(self.source_lang_code):
            raise InvalidLanguageCodeError(f'Invalid source language code {self.source_lang_code}')

        for lang_code in self.target_lang_codes:
            if not is_valid_two_letter_lang_code(lang_code):
                raise InvalidLanguageCodeError(f'{lang_code} is not a valid language code')

        return self


async def read_localization_config_yaml(file_path: str) -> LocalizationConfig:
    yaml_content = await read_file(file_path)
    yaml_dict = yaml.safe_load(yaml_content)
    if not isinstance(yaml_dict, dict):
        logging.error(f"Could not convert yaml file to config {yaml_dict}")
        raise InvalidYamlConfigError("Invalid YAML file")

    try:
        config = LocalizationConfig(**yaml_dict)
        return config
    except LocalizationConfigValidationError as e:
        logging.error(f"Could not convert yaml file to config {yaml_dict} {e}")
        raise InvalidYamlConfigError("Invalid YAML file")
    except ValidationError as e:
        logging.error(f"Could not convert yaml file to config {yaml_dict} {e}")
        raise InvalidYamlConfigError("Invalid YAML file")


def create_language_file_path_config(
        localization_root_path: str,
        source_lang_code: str,
        config_directory_absolute_path: str,
        target_lang_codes: set[str] | None,
        file_name_pattern: str | None,
        language_file_paths: dict[str, str] | None,
) -> dict[str, str]:
    base_path = os.path.join(config_directory_absolute_path, localization_root_path)
    if language_file_paths:
        return {lang_code: os.path.join(base_path, path) for lang_code, path in language_file_paths.items()}

    def generate_localization_absolute_file_path(lang_code: str) -> str:
        file_name = generate_localization_file_name(lang_code, file_name_pattern)
        return os.path.join(base_path, file_name)

    absolute_mapping = {lang_code: generate_localization_absolute_file_path(lang_code) for lang_code in
                        target_lang_codes}

    source_lang_file_path = calculate_source_lang_absolute_file_path(base_path, file_name_pattern, source_lang_code)
    absolute_mapping[source_lang_code] = source_lang_file_path

    return absolute_mapping


def calculate_source_lang_absolute_file_path(base_path: str, file_name_pattern: str, source_lang_code: str) -> str:
    source_lang_file_name = generate_localization_file_name(source_lang_code, file_name_pattern)
    source_lang_file_path = os.path.join(base_path, source_lang_file_name)
    if not os.path.exists(source_lang_file_path):
        if 'values-{language}' in file_name_pattern:
            new_fnp = file_name_pattern.replace('values-{language}', 'values')
        elif 'messages_{language}' in file_name_pattern:
            new_fnp = file_name_pattern.replace('messages_{language}', 'messages')
        else:
            raise FileNotFoundError(f"Source language file {source_lang_file_path} does not exist and no fallback "
                                    f"pattern found")

        source_lang_file_name = new_fnp.replace('{language}', source_lang_code)
        source_lang_file_path = os.path.join(base_path, source_lang_file_name)

    return source_lang_file_path
