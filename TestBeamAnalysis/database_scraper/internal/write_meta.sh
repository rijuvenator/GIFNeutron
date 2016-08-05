#!/bin/bash

meas=$1
file=$2

# if "on" is found after v_me1(2)1_state, set chamber
cham="0"
if [ "`grep -A 1 "v_me11_state" ${meas}.log | grep "on"`" ]; then
	cham="1"
fi
if [ "`grep -A 1 "v_me21_state" ${meas}.log | grep "on"`" ]; then
	cham="2"
fi

# exit if neither chamber
if [ "$cham" == "0" ]; then
	echo ${meas} ${cham} >> $2
	exit
fi

# if "equalized" is NOT found, grab the relevant HV value
# otherwise, if "ageing" is found, write HV1; otherwise, write HV0
hv=""
if [ "$cham" == "1" ]; then
	if [ "`grep -A 1 'v_hv_setting1' ${meas}.log | grep "equalized"`" == "" ]; then
		hv="$(grep 'v_hv_me11[^_]' ${meas}.log | sed -n -e 's/.*VALUE="//' -e 's/" onkeypress.*//p')"
	else
		if [ "`grep -A 1 'v_hv_setting1' ${meas}.log | grep "ageing"`" ]; then
			hv="HV1"
		else
			hv="HV0"
		fi
	fi
elif [ "$cham" == "2" ]; then
	if [ "`grep -A 1 'v_hv_setting2' ${meas}.log | grep "equalized"`" == "" ]; then
		hv="$(grep 'v_hv_me21[^_]' ${meas}.log | sed -n -e 's/.*VALUE="//' -e 's/" onkeypress.*//p')"
	else
		if [ "`grep -A 1 'v_hv_setting2' ${meas}.log | grep "ageing"`" ]; then
			hv="HV1"
		else
			hv="HV0"
		fi
	fi
fi

# catch HV errors
if [ $((`echo $hv | wc -c` > 5)) == "1" ]; then
	hv="X"
	if [ "$cham" == "1" ]; then
		exc=$(grep "v_hv_me11_except" ${meas}.log | sed -n -e 's/.*VALUE="//' -e 's/" onkeypress.*//p')
		if [ "$exc" == "HV0" ]; then
			#hv="HV0-E"
			hv="HV0"
		fi
	elif [ "$cham" == "2" ]; then
		exc=$(grep "v_hv_me21_except" ${meas}.log | sed -n -e 's/.*VALUE="//' -e 's/" onkeypress.*//p')
		if [ "$exc" == "HV0" ]; then
			#hv="HV0-E"
			hv="HV0"
		fi
	fi
fi

# if "on" or "off" is found after v_source_state, set source_state
sourcestate="X"
if [ "`grep -A 1 "v_source_state" ${meas}.log | grep "on"`" ]; then
	sourcestate="1"
fi
if [ "`grep -A 1 "v_source_state" ${meas}.log | grep "off"`" ]; then
	sourcestate="0"
fi

# if "on" or "off" is found after v_beam_state, set beamstate
beamstate="X"
if [ "`grep -A 1 "v_beam_state" ${meas}.log | grep "on"`" ]; then
	beamstate="1"
fi
if [ "`grep -A 1 "v_beam_state" ${meas}.log | grep "off"`" ]; then
	beamstate="0"
fi

# if source is on, grab attenuation upstream and downstream
attenup=""
attendown=""
if [ "$sourcestate" == "1" ]; then
	attenup="$(grep 'v_attenuat_up' ${meas}.log | sed -n -e 's/.*VALUE="//' -e 's/" onkeypress.*//p')"
	# BLEHHHHHHH -- some of the attenups are blank for source on
	if ! [ "`echo $attenup | grep "SIZE"`" == "" ]; then
		attenup="X"
	fi
	attendown="$(grep 'v_attenuat_down' ${meas}.log | sed -n -e 's/.*VALUE="//' -e 's/" onkeypress.*//p')"
fi

# get runs with "FastFilter" in them
ff="N"
if [ "`grep "FastFilter\|option " ${meas}.log`" ]; then
	#ff="`grep 'FastFilter' ${meas}.log | awk '{print $2}'`"
	#ff="`awk '/FastFilter/ {print $2}' ${meas}.log`"
	# idiot measurements!!
	ff="`awk '/\.\/FastFilter/ {print $2} /python Fast/ {print $NF} /option / {print $2}' ${meas}.log`"
fi
if [ -z "$ff" ]; then
	ff="X"
fi

echo ${meas} ${cham} ${hv} ${sourcestate} ${beamstate} ${attenup} ${attendown} ${ff} >> $2
