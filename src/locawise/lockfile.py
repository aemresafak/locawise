import logging
import os.path

import aiofiles
import xxhash

from locawise.fileutils import write_to_file

_KEY_VALUE_HASH_LENGTH = 8

_HASH_SEED = 123

_LOCK_FILE_NAME = 'i18n.lock'


async def read_lock_file(file_path: str) -> set[str]:
    key_value_hashes = set()
    try:
        async with aiofiles.open(file_path, 'r', encoding='UTF-8') as f:
            async for line in f:
                line = line.rstrip('\n\r')
                if not line:
                    continue

                if len(line) != _KEY_VALUE_HASH_LENGTH:
                    logging.warning(f"Invalid key value hash length. line={line} length={len(line)}")
                    continue

                key_value_hashes.add(line)
    except FileNotFoundError as e:
        logging.warning("Lock file not found. Ignore this if it's the first time you are running this application.")
        raise e
    except (Exception,):
        logging.warning(f"Unknown error while reading the lock file {file_path}")

    return key_value_hashes


async def write_lock_file(file_path: str, key_value_pairs: dict[str, str]):
    content = create_lock_file_content(key_value_pairs)
    await write_to_file(file_path, content)


def create_lock_file_content(key_value_pairs: dict[str, str]):
    content = ""
    for k, v in key_value_pairs.items():
        hashed_value = hash_key_value_pair(k, v)
        content += hashed_value + "\n"
    return content


def hash_key_value_pair(key: str, value: str) -> str:
    return xxhash.xxh32_hexdigest(f"{key}={value}", _HASH_SEED)


def create_lock_file_path(base_folder: str) -> str:
    return str(os.path.join(base_folder, _LOCK_FILE_NAME))
