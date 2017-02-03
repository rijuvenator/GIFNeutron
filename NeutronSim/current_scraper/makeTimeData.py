import math
import datetime

#measList = [3222,3223,3224,3225,3226,3227,3228,3229,3232,3233,3234,3235,3236,3237,3238,3239,3240,3241,3242,3243,3244,3245,3246,3247,3249,3250,3251,3252,3253,3254,3255,3256,3257,3284,3285,3286,3287,3288,3289,3290,3291,3295,3296,3297,3298,3299,3300,3301,3302,3303,3308,3309,3310,3311,3312,3313,3314,3315,3317,3318,3319,3320,3321,3322,3323,3324,3325,3339,3340,3341,3342,3343,3344,3345,3346,3347,3348,3349,3350,3351,3352,3353,3354,3384,3385,3386,3387,3388,3389,3390,3391]
measList = [3355,3356,3357,3358,3359,3360,3368,3369,3370,3371,3372,3373,3379,3380,3381,3382,3383,3404,3405,3406,3407,3409,3410,3411,3412,3413,3414,3415,3416,3417,3420,3421,3422,3423,3424,3425,3426,3427,3428,3429,3432,3433,3434,3435,3436,3437,3438,3439,3440,3441,3454,3455,3456,3457,3458,3459,3460]
# no 3367

for meas in measList:
	f = open('../database_scraper/tmb/'+str(meas)+'.tmb')
	T1Set = False
	P1Set = False
	for line in f:
		if 'Time:' in line:
			cols = line.strip('\n').split()
			if not T1Set:
				t1 = cols[-2] + ' ' + cols[-1]
				T1Set = True
			else:
				t2 = cols[-2] + ' ' + cols[-1]
		if 'Period [s]:' in line and not P1Set:
			cols = line.strip('\n').split()
			p1 = int(math.ceil(float(cols[-1])))

	T1 = datetime.datetime.strptime(t1, '%Y-%m-%d %H:%M:%S')
	T2 = datetime.datetime.strptime(t2, '%Y-%m-%d %H:%M:%S')

	P1        = datetime.timedelta(seconds = p1)
	TZCorrect = datetime.timedelta(seconds = 7200)
	MinRound  = datetime.timedelta(seconds = 60)

	T1 = T1 - TZCorrect - P1
	T2 = T2 - TZCorrect + MinRound
	print T1.strftime('%d.%m.%Y %H:%M'), T2.strftime('%d.%m.%Y %H:%M'), meas, "1"
	f.close()
