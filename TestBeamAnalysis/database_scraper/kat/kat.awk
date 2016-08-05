{
	if ($0 !~ /raid/)
		next

	maxm="0"
	if ($0 ~ /*/)
	{
		m = $1
		cmd="grep ^"m" modstar | awk '{print $2}'"
		cmd | getline maxm
	}

	cham=""
	test=""
	volt=$3
	beam=""
	source=""
	meas="m"$1
	time=""

	if ($2=="1")
		cham="ME11"
	else if ($2=="2")
		cham="ME21"
	else
		next

	if ($NF ~ /STEP_40/)
	{
		test="Test40"
	}
	else if ($NF ~ /STEP_27s/)
	{
		test="Test27s"
	}
	else if ($NF ~ /STEP_27/)
	{
		test="Test27"
	}
	else if ($NF ~ /Test_11/)
	{
		test="Test11"
	}
	else if ($NF ~ /Test_11c/)
	{
		test="Test11c"
	}
	else if ($NF ~ /Test_19/)
	{
		test="Test19"
	}
	else if ($NF ~ /Test_17b/)
	{
		test="Test17b"
	}
	else if ($NF ~ /Test_17/)
	{
		test="Test17"
	}
	else if ($NF ~ /Test_16/)
	{
		test="Test16"
	}
	else if ($NF ~ /Test_15/)
	{
		test="Test15"
	}
	else if ($NF ~ /Test_14/)
	{
		test="Test14"
	}
	else if ($NF ~ /Test_13/)
	{
		test="Test13"
	}

	if (volt !~ /V/)
		volt = volt "V"

	if ($5=="0")
		beam="bOff"
	else if ($5=="1")
		beam="bOn"

	if ($4=="0")
		source="uOff_dOff"
	else if ($4=="1")
		source="u"$6"_d"$7

	time=$NF
	sub(/emugif2.*EmuRUI01_.*_.*_.*_160/,"160",time)
	sub(/_UTC.raw/,"",time)
	sub(/_/,"",time)
	can="20"substr(time,1,2)"-"substr(time,3,2)"-"substr(time,5,2)"@"substr(time,7,2)":"substr(time,9,2)":"substr(time,11,2)
	#print can
	time="t"time

	if (maxm=="0")
		print "test_"$1".root", cham"_"test"_"volt"_"beam"_"source"_"meas"_"time".root"
	else
		for (i=0; i<=maxm; i++)
			print "test_"$1"_"i".root", cham"_"test"_"volt"_"beam"_"source"_"meas"_"time"_"i".root"
}
