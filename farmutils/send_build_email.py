#!/usr/bin/env python3
from doemail import doemail as de
import sys

if len(sys.argv) is not 3:
    print("Bad args")
    sys.exit(1)

subject = sys.argv[1]
body = sys.argv[2]

sys.exit(de(subject=subject, body=body))
