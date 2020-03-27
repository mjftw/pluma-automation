#!/bin/bash
this_dir="$(dirname $0)"
farmcore_dir="$(pip3 show farm-core | awk -F': ' '/Location/ {print $2}')"

if [ -z "${farmcore_dir}" ]; then
    echo 'Cannot find pip3 package "farm-core". Is it installed?'
    exit 1
fi

pytest --cov=$farmcore_dir --cov-report=term-missing $this_dir $@