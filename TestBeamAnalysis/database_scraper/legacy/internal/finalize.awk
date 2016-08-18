{
	printf $1;
	if ($2=="TMB" || $2=="Missing_file")
	{
		print " "$2
		next
	}
	x=0;
	x += sub(/.*raid/,"raid",$0);
	x += sub(/raw.*/,"raw",$0);
	gsub(/ /,"",$0)
	if (x==2)
	{
		printf " ";
		print $0;
	}
	else
		print ""
}
