from farmcore import farm

apc1 = farm.APC('10.103.3.40', 'apc','apc')

ur1 = farm.USBRelay( '1-1.1.4.1')
ur2 = farm.USBRelay( '1-1.1.4.3')

sdm1 = farm.SDMux( ur2[0], apc1[2])
sdm2 = farm.SDMux( ur2[3], apc1[1])
sdm3 = farm.SDMux( ur2[2], apc1[3])

bbb = farm.Board('bbb', apc1[7], '1-1.1.1', sdm1)
fb42 = farm.Board('fb42', apc1[4], '1-1.1.2', sdm2)
fb43 = farm.Board('fb43', apc1[6], '1-1.1.3', sdm3)

