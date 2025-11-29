import pytest

from locawise.lockfile import read_lock_file
from tests.utils import get_absolute_path


@pytest.mark.asyncio(loop_scope="module")
@pytest.mark.parametrize('file_path, expected_output', [
    ('resources/lockfiles/valid_lockfile.lock', {
        'a1b2c3d4',
        'e1b2c3d5',
        'd1b2c3d3',
        'c1b2c3d1',
    }),
    ('resources/lockfiles/empty_lockfile.lock', set()),
    ('resources/lockfiles/partially_valid.lock', {
        'abcd1234',
        'abcd1235',
        'abcdef11'
    })
])
async def test_read_lock_file(file_path, expected_output):
    file_path = get_absolute_path(file_path)
    content = await read_lock_file(file_path)

    assert content == expected_output


async def test_read_lock_file_with_non_existent_file():
    file_path = get_absolute_path('resources/lockfiles/non_existent.lock')
    with pytest.raises(FileNotFoundError):
        await read_lock_file(file_path)
