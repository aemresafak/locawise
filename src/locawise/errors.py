class ParseError(Exception):
    pass


class InvalidYamlConfigError(Exception):
    pass


class LLMApiError(Exception):
    pass


# retryable
class TransientLLMApiError(LLMApiError):
    pass


class InvalidLLMOutputError(TransientLLMApiError):
    pass


class LocalizationError(Exception):
    pass


class FileSaveError(Exception):
    pass


class LocalizationFormatError(Exception):
    pass


class SerializationError(Exception):
    pass


class UnsupportedLocalizationKeyError(Exception):
    pass


class LocalizationFileAlreadyUpToDateError(Exception):
    pass


class MalformedAndroidStringsXMLError(Exception):
    pass


class LocalizationConfigValidationError(Exception):
    pass


class InvalidLanguageCodeError(LocalizationConfigValidationError):
    pass


class InvalidTargetLanguageMappingCombinationError(LocalizationConfigValidationError):
    pass
