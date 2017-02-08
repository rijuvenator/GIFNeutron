def Pattern(id_, hs):
	if id_ == 2:
		x = [hs-5, hs-4, hs-3, hs-4, hs-3, hs-2, hs-2, hs-1, hs  , hs  , hs+1, hs+2, hs+3, hs+4, hs+5]
		y = [6   , 6   , 6   , 5   , 5   , 5   , 4   , 4   , 4   , 3   , 2   , 2   , 1   , 1   , 1   ]
	elif id_ == 3:
		x = [hs-5, hs-4, hs-3, hs-2, hs-1, hs  , hs  , hs+1, hs+2, hs+2, hs+3, hs+4, hs+3, hs+4, hs+5]
		y = [1   , 1   , 1   , 2   , 2   , 3   , 4   , 4   , 4   , 5   , 5   , 5   , 6   , 6   , 6   ]
	elif id_ == 4:
		x = [hs-4, hs-3, hs-2, hs-4, hs-3, hs-2, hs-2, hs-1, hs  , hs+1, hs+2, hs+2, hs+3, hs+4]
		y = [6   , 6   , 6   , 5   , 5   , 5   , 4   , 4   , 3   , 2   , 2   , 1   , 1   , 1   ]
	elif id_ == 5:
		x = [hs-4, hs-3, hs-2, hs-2, hs-1, hs  , hs+1, hs+2, hs+2, hs+3, hs+4, hs+2, hs+3, hs+4]
		y = [1   , 1   , 1   , 2   , 2   , 3   , 4   , 4   , 5   , 5   , 5   , 6   , 6   , 6   ]
	elif id_ == 6:
		x = [hs-3, hs-2, hs-1, hs-2, hs-1, hs-1, hs  , hs  , hs  , hs+1, hs+1, hs+2, hs+3] 
		y = [6   , 6   , 6   , 5   , 5   , 4   , 4   , 3   , 2   , 2   , 1   , 1   , 1   ]
	elif id_ == 7:
		x = [hs-3, hs-2, hs-1, hs-1, hs  , hs  , hs  , hs+1, hs+1, hs+2, hs+1, hs+2, hs+3] 
		y = [1   , 1   , 1   , 2   , 2   , 3   , 4   , 4   , 5   , 5   , 6   , 6   , 6   ]
	elif id_ == 8:
		x = [hs-2, hs-1, hs  , hs-2, hs-1, hs  , hs-1, hs  , hs  , hs  , hs+1, hs  , hs+1, hs+2] 
		y = [6   , 6   , 6   , 5   , 5   , 5   , 4   , 4   , 3   , 2   , 2   , 1   , 1   , 1   ]
	elif id_ == 9:
		x = [hs-2, hs-1, hs  , hs-1, hs  , hs  , hs  , hs+1, hs  , hs+1, hs+2, hs  , hs+1, hs+2] 
		y = [1   , 1   , 1   , 2   , 2   , 3   , 4   , 4   , 5   , 5   , 5   , 6   , 6   , 6   ]
	elif id_ == 10:
		x = [hs-1, hs  , hs+1, hs-1, hs  , hs+1, hs  , hs  , hs  , hs-1, hs  , hs+1] 
		y = [6   , 6   , 6   , 5   , 5   , 5   , 4   , 3   , 2   , 1   , 1   , 1   ]

	X1 = [float(i) + 2     for i in x]
	X2 = [float(i) + 2 + 1 for i in x]
	Y1 = [float(i)         for i in y]
	Y2 = [float(i)     + 1 for i in y]
	return X1, Y1, X2, Y2
