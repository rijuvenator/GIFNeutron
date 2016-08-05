{
	test = ""
	end = ""
	url = ""

	# Not used in making the URL anymore, since they're symlinks
	# but it might be useful to leave it, if, say, you want URLs
	# only for a particular chamber, you can just "next" if it's
	# not the chamber you want.
	chamber = ""
	if ($2 == "1")
	{
		chamber = "ME+1.1.GIF"
	}
	else if ($2 == "2")
	{
		chamber = "ME+2.1._17_"
	}
	else if ($2 == "0")
	{
		chamber = ""
	}
	else
	{
		print "Error - I need to know whether this is ME1/1 or ME2/1."
		exit
	}
	# end chamber

	if ($1 ~ /STEP_40/)
	{
		test = "Test_40_Beam"
		end = "browse.html"
	}
	else if ($1 ~ /STEP_27/)
	{
		test = "Test_27_Cosmics"
		end = "browse.html"
	}
	else if ($1 ~ /Test_11/)
	{
		test = "Test_11_AFEBNoise"
	}
	else if ($1 ~ /Test_16/)
	{
		test = "Test_16_CFEBConnectivity"
	}
	else if ($1 ~ /Test_19/)
	{
		test = "Test_19_CFEBComparators"
	}
	else if ($1 ~ /Test_21/)
	{
		test = "Test_21_CFEBComparatorLogic"
	}
	else
	{
		print "Error - this isn't a test I know about."
		exit
	}

	url = $1
	sub(/^/,"http://",url)
	sub(/:\/raid/,"",url)
#	sub(/current/,"current/Tests_results/"chamber"/"test,url)
	sub(/current/,"current/Tests_results/"test,url)
	sub(/raw/,"plots/"end,url)

	# now that everything has been moved to backup
	sub(/data/,"backup/data",url)

	print url
}
