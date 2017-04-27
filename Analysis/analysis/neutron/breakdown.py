import ROOT as R

R.gROOT.SetBatch(True)

TOTAL = 664
processes = {
	'neutron capture'  : {'' : (355, R.kRed)},
	'neutron inelastic': {'' : (59, R.kAzure+7)},
	'hadron elastic'   : {'n#rightarrowp' : (120, R.kMagenta), 'ion' : (13, R.kGreen)},
	'non-neutron'      : {'muon' : (42, R.kOrange+2), 'n*' : (4, R.kOrange), 'showers' : (71, R.kOrange-3)}
}

c = R.TCanvas('c', 'Canvas', 800, 500)
boxes = []
currentY = 0
i = 1
text = R.TLatex()
text.SetTextFont(42)
text.SetTextAlign(22)
text.SetTextSize(0.03)
for key, counter in processes.iteritems():
	value = sum([x[0] for x in counter.values()])

	height = float(value)/TOTAL
	boxes.append(R.TBox(0, currentY, 1, currentY + height))
	boxes[-1].SetFillColor(0 if len(counter)>1 else counter[''][1])
	boxes[-1].Draw()
	text.DrawLatexNDC(0.5, currentY+height/2., '#color[1]{{#splitline{{{KEY}}}{{{PCT:.0f}%}}}}'.format(KEY=key, PCT=height*100))
	i += 1

	if len(counter) > 1:
		currentX = 0
		for subKey, (subValue, color) in counter.iteritems():
			subWidth = float(subValue)/value
			boxes.append(R.TBox(currentX, currentY, currentX + subWidth, currentY + height))
			boxes[-1].SetFillColor(color)
			boxes[-1].Draw()
			text.DrawLatexNDC(currentX+subWidth/2., currentY+height/2., '#color[1]{{#splitline{{{KEY}}}{{{PCT:.0f}%}}}}'.format(KEY=subKey, PCT=float(subValue)/TOTAL*100))
			i += 1
			currentX += subWidth

	currentY += height

c.SaveAs('breakdown.pdf')
