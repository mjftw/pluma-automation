from farmcore import farm

apc1 = farm.APC('10.103.3.40', 'apc','apc')
apc2 = farm.APC('10.103.3.41', 'apc','apc')

ur1 = farm.USBRelay( '1-1.1.4.1')
ur2 = farm.USBRelay( '1-1.1.4.3')
ur3 = farm.USBRelay( '1-1.1.4.2.2' )

sdm1 = farm.SDMux( ur2[0], apc2[2])
sdm2 = farm.SDMux( ur2[3], apc2[7])
sdm3 = farm.SDMux( ur2[2], apc2[8])
sdm4 = farm.SDMux( ur3[3], apc2[1])


bbb = farm.Board('bbb', apc1[7], '1-1.1.1', sdm1)
fb42 = farm.Board('fb42', apc1[4], '1-1.1.2', sdm2)
fb43 = farm.Board('fb43', apc1[6], '1-1.1.3', sdm3)
ab4 = farm.Board('ab4', apc1[1], '1-1.1.4.2.4', sdm4 )
