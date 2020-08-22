# Changelog
Notable changes to this project will be documented in this file.

## [Unreleased]
### Changed
- ConsoleBase.wait_for_quiet: 'quiet' is now the first argument, and 'timeout' the last

### Deprecated
- ConsoleBase.send: Deprecated for 'send_nonblocking' and 'send_and_expect'
- ConsoleBase.flush: Deprecated for 'read_all'
- ConsoleBase._flush_get_size: Deprecated for 'read_all' and '_buffer_size'
- ConsoleBase.wait_for_data: Deprecated for 'wait_for_bytes' or 'wait_for_quiet'
- ConsoleBase._wait_for_match: Deprecated for 'wait_for_match'
