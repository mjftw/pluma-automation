# Changelog
Notable changes to this project will be documented in this file.

## [Unreleased]
### Changed
- ConsoleBase.wait_for_quiet: 'quiet' is now the first argument, and 'timeout' the last
- farmcore module changed to pluma.core (can also just import as pluma)
- farmutils module changed to pluma.utils
- farmtest module changed to pluma.test
- farmcore.baseclasses.farmclass.Farmclass changed to pluma.core.baseclasses.hardwarebase.HardwareBase

### Deprecated
- ConsoleBase.send: Deprecated for 'send_nonblocking' and 'send_and_expect'
- ConsoleBase.flush: Deprecated for 'read_all'
- ConsoleBase._flush_get_size: Deprecated for 'read_all' and '_buffer_size'
- ConsoleBase.wait_for_data: Deprecated for 'wait_for_bytes' or 'wait_for_quiet'
- ConsoleBase._wait_for_match: Deprecated for 'wait_for_match'
