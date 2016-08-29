from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import *
#from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import sys
import time

globDet = True

# file format:
# stopdate stoptime startdate starttime cham endmeas startmeas
# dates: dd.mm.yyyy
# times: 24-hour hh:mm
# see test data dictionaries below
f = open(sys.argv[1])
rawdata = []
for line in f:
	arr = line.strip("\n").split()
	dic = {}
	dic["startdate"] = arr[2]
	dic["starttime"] = arr[3]
	dic["stopdate"] = arr[0]
	dic["stoptime"] = arr[1]
	dic["cham"] = arr[4]
	dic["detailed"] = globDet
	dic["startm"] = arr[6]
	dic["endm"] = arr[5]
	rawdata.append(dic)

# test data dictionaries
dataTest1 = {
		"startdate" : "10.5.2016",
		"starttime" : "00:00",
		"stopdate" : "10.5.2016",
		"stoptime" : "04:00",
		"cham" : "1",
		"detailed" : True,
		"startm" : "0",
		"endm" : "0"
		}
dataTest2 = {
		"startdate" : "9.5.2016",
		"starttime" : "00:00",
		"stopdate" : "9.5.2016",
		"stoptime" : "04:00",
		"cham" : "2",
		"detailed" : True,
		"startm" : "0",
		"endm" : "0"
		}
dataTest3 = {
		"startdate" : "8.5.2016",
		"starttime" : "00:00",
		"stopdate" : "8.5.2016",
		"stoptime" : "04:00",
		"cham" : "1",
		"detailed" : False,
		"startm" : "0",
		"endm" : "0"
		}

# For modern desktops, i.e. Firefox 45+, Marionette is required;
# Add path to wires (the gecko webdriver renamed) to PATH and make executable
#firefox_capabilities = DesiredCapabilities.FIREFOX
#firefox_capabilities['marionette'] = True
#b = webdriver.Firefox(capabilities=firefox_capabilities)
#b = webdriver.Firefox()
#b.get("http://emugif1.cern.ch:8080/CSC")

# two functions for turning on if off and turning off if on
def turnOn(elem):
	if not elem.is_selected():
		elem.click()

def turnOff(elem):
	if elem.is_selected():
		elem.click()

# the main engine
def getCurrents(data):
	# if using a single browser, instead of destroying and recreating,
	# make "out" global and move it outside the function
	out = "output here"
	# declare browser, get address, switch to left frame
	b = webdriver.Firefox()
	#b.set_window_size(1400,900) # when I was trying to get screenshots; I've given up
	b.get("http://emugif1.cern.ch:8080/CSC")
	b.switch_to_frame(b.find_element_by_name("navigation"))

	# I've conveniently named the keys to correspond to the relevant entry in data
	# so that I can loop over them to fill them
	times = {}
	times["startdate"] = b.find_element_by_id("datepicker1")
	times["starttime"] = b.find_element_by_id("starttime")
	times["stopdate" ] = b.find_element_by_id("datepicker2")
	times["stoptime" ] = b.find_element_by_id("stoptime")

	for key in times.keys():
		times[key].clear()
		times[key].send_keys(data[key])

	# This is to prevent "Other element would receive the click" errors;
	# I expect it is because of the date picker pop-up covering the buttons
	# so click and unclick elsewhere on the form
	turnOff(b.find_element_by_id("section1"))
	turnOn(b.find_element_by_id("section1"))
	turnOff(b.find_element_by_id("section1"))
	turnOn(b.find_element_by_id("section1"))
	turnOff(b.find_element_by_id("section1"))
	turnOn(b.find_element_by_id("section1"))

	# Click chamber and turn on section 2 and 3 for ME2/1
	if data["cham"] == "1":
		turnOn(b.find_element_by_id("chamber1"))
		turnOff(b.find_element_by_id("section2"))
		turnOff(b.find_element_by_id("section3"))
	elif data["cham"] == "2":
		# For unknown reasons, the turnOn(chamber2) here gets "Other element would receive the click" errors sometimes;
		# For this action only I put in an action chain; radio buttons are idempotent, so it doesn't matter
		action = ActionChains(b)
		action.move_to_element(b.find_element_by_id("chamber2")).click().perform()
		#turnOn(b.find_element_by_id("chamber2"))
		turnOn(b.find_element_by_id("section2"))
		turnOn(b.find_element_by_id("section3"))

	# Turn on detailed if True -- it's always true
	if data["detailed"] == True:
		turnOn(b.find_element_by_id("detailed"))
	elif data["detailed"] == False:
		turnOff(b.find_element_by_id("detailed"))

	# Click Submit!
	b.find_element_by_id("submit").click()

	# Go back to parent page
	b.switch_to_default_content()

	# Switch to right frame
	b.switch_to_frame(b.find_element_by_id("outputtxt"))

	# A while loop for checking if the data has arrived yet.
	# Checks against "out", which is either "output here"
	# or the previous output. If it's different, the data has arrived;
	# save it and move on.
	waitingForData = True
	while waitingForData:
		# For unknown reasons, a few of the measurements give Unresponsive Script errors.
		# I've tried switching to the alert, but to no avail. Better to just get out
		# and move on; do the ones that fail manually, so record them.
		# I'd meant to print the "didn't work" to stderr, but you know, putting them in curr works pretty well
		try:
			thisOut = b.find_element_by_id("printout").get_attribute("innerHTML")
		except:
			print "#%s-%s didn't work." % (data["startm"], data["endm"])
			b.quit()
			return
		if thisOut == out:
			pass
		else:
			waitingForData = False
			out = thisOut

	# Everything has worked well. Print out the measurement range and the data,
	# replacing all the <br> tags with real linebreaks.
	print "#%s-%s" % (data["startm"], data["endm"])
	print out.replace("<br>","\n")

	# Go back to parent page. It was more important when I was trying to save screenshots, and/or
	# if using a single browser window, as opposed to this heavy create-destroy nonsense.
	b.switch_to_default_content()
	#b.save_screenshot("test.png")
	b.quit()

# Test data
#getCurrents(dataTest1)
#getCurrents(dataTest2)
#getCurrents(dataTest3)

# The count is just for progress report purposes while the script runs.
# It gets printed to stderr and is lost.
c = 0
for data in rawdata:
	getCurrents(data)
	c = c + 1
	print >> sys.stderr, c
