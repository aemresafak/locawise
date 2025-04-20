from threepio import parsing
from threepio.dictutils import unsafe_subdict
from threepio.diffutils import retrieve_keys_to_be_localized, retrieve_nom_source_keys
from threepio.langutils import is_valid_two_letter_lang_code, retrieve_lang_full_name
from threepio.llm import LLMContext
from threepio.localization import localize
from threepio.lockfile import read_lock_file
from threepio.parsing import parse
from threepio.serialization import serialize_and_save


class SourceProcessor:
    """
    Processes source files, i.e. localizes the source language into target languages
    """

    def __init__(self,
                 llm_context: LLMContext,
                 source_dict: dict[str, str],
                 nom_keys: set[str],
                 context: str = '',
                 tone: str = '',
                 glossary: dict[str, str] | None = None):
        self.llm_context = llm_context
        self.context = context
        self.tone = tone
        self.glossary = glossary
        self.source_dict = source_dict
        self.nom_keys = nom_keys

    async def localize_to_target_language(self, target_path: str, target_lang_code: str):
        """
        :param target_path:
        :param target_lang_code:
        :return:
        :raises ValueError: Programming errors or unsupported features
        :raises ParsingError: Target file could not be parsed
        :raises LocalizationFailedError:
        :raises FileSaveError: error while saving to the target file
        """
        if not target_path.strip():
            raise ValueError("Target path cannot be empty")

        if not is_valid_two_letter_lang_code(target_lang_code):
            raise ValueError(f'Language Code={target_lang_code} is not a valid two letter language code.')

        target_lang_full_name = retrieve_lang_full_name(target_lang_code)

        target_dict = await generate_localized_dictionary(self.llm_context,
                                                          source_dict=self.source_dict,
                                                          nom_keys=self.nom_keys,
                                                          target_dict_path=target_path,
                                                          target_language_full_name=target_lang_full_name,
                                                          context=self.context,
                                                          tone=self.tone,
                                                          glossary=self.glossary)

        await serialize_and_save(target_dict, target_path)


async def create_source_processor(llm_context: LLMContext,
                                  source_file_path: str,
                                  lock_file_path: str,
                                  context: str = '',
                                  tone: str = '',
                                  glossary: dict[str, str] | None = None) -> SourceProcessor:
    """
    :param llm_context:
    :param source_file_path:
    :param lock_file_path:
    :param context:
    :param tone:
    :param glossary:
    :return:
    :raises ParseError:
    :raises ValueError:
    """
    source_dict = await parse(source_file_path)
    key_value_hashes: set[str] = await read_lock_file(lock_file_path)
    nom_keys = retrieve_nom_source_keys(key_value_hashes, source_dict=source_dict)
    return SourceProcessor(llm_context,
                           source_dict,
                           nom_keys=nom_keys,
                           context=context,
                           tone=tone,
                           glossary=glossary)


async def generate_localized_dictionary(
        llm_context: LLMContext,
        source_dict: dict[str, str],
        nom_keys: set[str],
        target_dict_path: str,
        target_language_full_name: str,
        context: str = '',
        tone: str = '',
        glossary: dict[str, str] | None = None,
) -> dict[str, str]:
    """
        Reads the target file, finds the keys that need localization, localizes them and returns the final target dict.

        Raises:
            ParsingError: If the target dictionary file cannot be parsed
            LocalizationFailedError: If the localization process fails
        """
    try:
        target_dict: dict[str, str] = await parsing.parse(file_path=target_dict_path)
    except FileNotFoundError:
        target_dict: dict[str, str] = {}
    keys_to_be_localized: set[str] = retrieve_keys_to_be_localized(source_dict, target_dict, nom_keys)
    pairs_to_be_localized: dict[str, str] = unsafe_subdict(source_dict, keys_to_be_localized)
    localized_pairs = await localize(llm_context=llm_context,
                                     pairs=pairs_to_be_localized,
                                     target_language=target_language_full_name,
                                     context=context,
                                     tone=tone,
                                     glossary=glossary)

    target_dict.update(localized_pairs)

    return target_dict
