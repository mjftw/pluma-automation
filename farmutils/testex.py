#!/usr/bin/env python3

try:
    raise RuntimeError('Error with omething....')
except RuntimeError as e:
    print(e)
