from pluma.utils import random_dir_name


def test_random_folder_name_should_be_unique():
    folder_names = set()
    count = 50
    for i in range(count):
        folder_names.add(random_dir_name())

    assert len(folder_names) == count
