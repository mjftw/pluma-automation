from pluma.plugins.testsuite import filesystem


def test_filesystem_FileExists_should_pass_on_existing_file(pluma_cli, temp_file, pluma_config_file):
    filename = temp_file()

    test_config = pluma_config_file([
        (filesystem.FileExists, {
            'path': filename,
            'run_on_host': 'true'
        })
    ])
    target_config = temp_file()

    pluma_cli(['-c', test_config, '-t', target_config])
