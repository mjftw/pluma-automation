#!/usr/bin/env python3

import random as r
import dbdata as d
from datetime import datetime as dt
import sys
import pandas as pd

pd.options.display.max_rows = 10
pd.options.display.max_columns = 0
pd.options.display.column_space = 20

ses = d.sf()

q = ses.query( d.data ).filter( d.data.test == 'quad' )

print("Query count is {}".format(  q.count()   ))

dfo = pd.read_sql( q.statement, q.session.bind )
dfo = dfo[['major','minor','revision','idle']]

df = dfo
df = df.groupby( ['major','minor','revision'] ).agg(['mean','max','min'])
#df.index = df.index.to_series().str.join(' ')

#df['test'] = df.index.to_series().astype(str).str.join( '.' )
#df['test'] = df['index']['major']

df = df.reset_index()
df['test'] = df['major'].astype(str) + '.' + df['minor'].astype(str) + '.' + df['revision'].astype(str).str.zfill(4) 

df = df[ ['test', 'idle']  ]

print(df)

sys.exit(0)


for _ in range(100):
    n = d.data()
    n.date = dt.now()
    n.idle = r.uniform(20.0,70.0)
    n.test = r.choice( [ 'quad', 'sd1', 'sd1-4', 'hd' ])
    n.major = 1
    n.minor = r.randrange(10)
    n.revision = r.randrange(100)
    n.filename = "Delete me"
    ses.add(n)

ses.commit()
ses.close()

