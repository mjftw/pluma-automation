import os


def test_temp_file_can_create_empty(temp_file):
    filename = temp_file()

    with open(filename, 'r') as f:
        content_read = f.read()
        assert content_read == ''


def test_temp_file_can_write_no_dedent(temp_file):
    content = '''

        Hello
        World
        123
            456
    '''

    filename = temp_file(content, dedent=False)

    with open(filename, 'r') as f:
        content_read = f.read()
        assert content == content_read


def test_temp_file_can_write_dedent(temp_file):
    content = '''

        Hello
        World
        123
            456
    '''

    content_dedented = '''\
Hello
World
123
    456
'''

    filename = temp_file(content)

    with open(filename, 'r') as f:
        content_read = f.read()
        assert content_dedented == content_read
