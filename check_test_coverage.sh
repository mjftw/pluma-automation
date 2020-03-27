#!/bin/bash
thisdir="$(dirname $0)"
pytest $thisdir --cov=$thisdir --cov-report=term-missing $@