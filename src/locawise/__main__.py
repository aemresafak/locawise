import argparse
import asyncio
import logging
import os

from locawise.envutils import generate_localization_file_name
from locawise.llm import LLMContext, create_strategy
from locawise.localization.config import read_localization_config_yaml
from locawise.lockfile import write_lock_file
from locawise.processor import create_source_processor


async def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.getLogger("httpx").setLevel(logging.WARNING)

    parser = argparse.ArgumentParser(
        description='Process localization files based on configuration.',
        epilog='Example: python3 main.py config.yaml'
    )
    parser.add_argument("config_path", help="Path to the YAML configuration file")
    args = parser.parse_args()

    # Run the async main function
    config_path = args.config_path

    config = await read_localization_config_yaml(config_path)
    config_directory = os.path.dirname(os.path.abspath(config_path))
    logging.info(f'Setting current working directory to {config_directory}')
    os.chdir(config_directory)

    source_lang_file_name = generate_localization_file_name(config.source_lang_code, config.file_name_pattern)
    source_lang_file_path = os.path.join(config_directory, config.localization_root_path, source_lang_file_name)

    if not os.path.exists(source_lang_file_path):
        if 'values-{language}' in config.file_name_pattern:
            source_lang_file_path = os.path.join(config_directory, config.localization_root_path,
                                                 config.file_name_pattern.replace('values-{language}', 'values'))
        elif 'messages' in config.file_name_pattern:
            source_lang_file_path = os.path.join(config_directory, config.localization_root_path,
                                                 config.file_name_pattern.replace('messages_{language}',
                                                                                  'messages'))

    logging.info(f'Localizing {source_lang_file_path}')

    llm_strategy = create_strategy(model=config.llm_model, location=config.llm_location)
    llm_context = LLMContext(llm_strategy)
    lock_file_name = 'i18n.lock'
    lock_file_path = os.path.join(config_directory, config.localization_root_path, lock_file_name)
    processor = await create_source_processor(llm_context,
                                              source_file_path=source_lang_file_path,
                                              lock_file_path=lock_file_path,
                                              context=config.context,
                                              tone=config.tone,
                                              glossary=config.glossary)

    async with asyncio.TaskGroup() as tg:
        for target_lang_code in config.target_lang_codes:
            logging.info(f'Creating task for {target_lang_code}')
            target_file_name = generate_localization_file_name(target_lang_code, config.file_name_pattern)
            target_path = os.path.join(config_directory, config.localization_root_path, target_file_name)
            tg.create_task(processor.localize_to_target_language(target_path, target_lang_code))

        tg.create_task(write_lock_file(lock_file_path, processor.source_dict))
    logging.info('All tasks have finished.')


if __name__ == "__main__":
    asyncio.run(main())
