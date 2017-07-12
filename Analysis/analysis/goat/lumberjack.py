''' Logger functions for plots in thefinalcountdown_TEST.py
'''
import numpy as np
import math as math
import ROOT as R
import logging

# Setup logging
def setup_logger(logger_name,log_file,level=logging.INFO):
    l = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(message)s')
    fileHandler = logging.FileHandler(log_file, mode='w')
    fileHandler.setFormatter(formatter)
    l.setLevel(level)
    l.addHandler(fileHandler)

# Occupancy logger
def occLogger(occLog,occHist,areaHist,digi,when,ec,ring,PU):
	BXtoSconv = 1./(25.*10**(-9))
	occLog.info('\n'+digi+' '+ec+ring+' '+when+(' PU norm' if PU else ''))
	occLog.info('Bin | wg/hs | area [cm2] | bx to s conv |     content | content err | content/cm2/s | content/cm2/s err')
	totalContent = 0.
	contentErrs = np.array([])
	totalArea = 0.
	nBins = occHist.GetNbinsX()
	for ibin in range(0,nBins+1):
		# include underflow bin 
		content = occHist.GetBinContent(ibin)
		totalContent += content
		contentErr = occHist.GetBinError(ibin)
		contentErrs = np.append(contentErrs,contentErr)
		digiarea = areaHist.GetBinContent(ibin)
		totalArea += digiarea
		if digiarea>0:
			contentScaled = content*BXtoSconv/digiarea
			contentScaledErr = contentErr*BXtoSconv/digiarea
		else:
			contentScaled = 0.
			contentScaledErr = 0.
		if occHist.GetBinLowEdge(ibin)==areaHist.GetBinLowEdge(ibin):
			wgorhs = occHist.GetBinLowEdge(ibin)
		else:
			wgorhs = 'WG or HS NOT EQUAL'
		printer = '{ibin:>3} | {wgorhs:>5} | {digiarea:>10.3f} | {BXtoSconv:12.1f} | {content:>11.9f} | {contentErr:>11.9f} | {contentScaled:>13.4f} | {contentScaledErr:>14.5f}'.format(**locals())
		occLog.info(printer)
	occLog.info('*'*len(printer))
	occLog.info('tot | wg/hs | area [cm2] | bx to s conv |     content | content err | content/cm2/s | content/cm2/s err')
	nWGorHS = nBins-1
	totalContentErr = math.sqrt(sum(contentErrs**2))
	totalContentScaled = totalContent*BXtoSconv/totalArea
	totalContentScaledErr = totalContentErr*BXtoSconv/totalArea
	totalPrinter = '{nBins:>3} | {nWGorHS:>5} | {totalArea:>10.3f} | {BXtoSconv:12.1f} | {totalContent:>11.9f} | {totalContentErr:>11.9f} | {totalContentScaled:>13.4f} | {totalContentScaledErr:>14.5f}'.format(**locals())
	occLog.info(totalPrinter)

# Luminosity Logger (full chamber)
def lumiLogger(lumiLog,lumiHist,chamAreaValue,digi,when,ec,ring,PU):
	BXtoSconv = 1./(25.*10**(-9))
	if not PU:
		fitHist = lumiHist.Clone()
		if fitHist.GetEntries()>2:
			fitHist.Scale(BXtoSconv)
			line = R.TF1('fitline_'+lumiHist.GetName(),'[0]*x',0,10**34)
			lumiHist.Fit('fitline_'+lumiHist.GetName())
			fit = lumiHist.GetFunction('fitline_'+lumiHist.GetName())
			slope,slopeErr,chiSq,nDOF = fit.GetParameter(0),fit.GetParError(0),fit.GetChisquare(),fit.GetNDF()
		else:
			slope,slopeErr,chiSq,nDOF = 0,0,0,0
	lumiLog.info('\n'+digi+' '+ec+ring+' '+when+' '+(' PU norm' if PU else ''))
	lumiLog.info('Bin | lumi [10^34 cm-2s-1] | area [cm2] | bx to s conv |     content | content err | content/cm2/s | content/cm2/s err')
	for ibin in range(0,lumiHist.GetNbinsX()+1):
		content = lumiHist.GetBinContent(ibin)
		contentErr = lumiHist.GetBinError(ibin)
		lumi = lumiHist.GetBinLowEdge(ibin)/(10**(34)) # convert to lumi per 10^34
		contentScaled = content*BXtoSconv/chamAreaValue
		contentScaledErr = contentErr*BXtoSconv/chamAreaValue
		printer = '{ibin:>3} | {lumi:>20.2f} | {chamAreaValue:>10.3f} | {BXtoSconv:12.1f} | {content:>11.9f} | {contentErr:>11.9f} | {contentScaled:>13.4f} | {contentScaledErr:>14.5f}'.format(**locals())
		lumiLog.info(printer)
	if not PU:
		lumiLog.info('*'*len(printer))
		ecring = ec+ring
		slopePrinter = 'ring {ecring:>3} | slope = {slope:>11.8e} | slope err = {slopeErr:>11.8e} | chi^2 = {chiSq:>11.5f} | nDOF = {nDOF:>3}'.format(**locals())
		lumiLog.info(slopePrinter)

# Luminosity Logger (half chamber)
def lumiHalfLogger(lumiHalfLog,lumiHist,chamHalfAreaValue,digi,when,ec,ring,PU,half=''):
	BXtoSconv = 1./(25.*10**(-9))
	if not PU:
		fitHist = lumiHist.Clone()
		if fitHist.GetEntries()>2:
			fitHist.Scale(BXtoSconv)
			line = R.TF1('fitline_'+lumiHist.GetName(),'[0]*x',0,10**34)
			lumiHist.Fit('fitline_'+lumiHist.GetName())
			fit = lumiHist.GetFunction('fitline_'+lumiHist.GetName())
			slope,slopeErr,chiSq,nDOF = fit.GetParameter(0),fit.GetParError(0),fit.GetChisquare(),fit.GetNDF()
		else:
			slope,slopeErr,chiSq,nDOF = 0,0,0,0
	lumiHalfLog.info('\n'+digi+' '+ec+ring+' '+half+(' ' if half!='' else '')+when+' '+(' PU norm' if PU else ''))
	lumiHalfLog.info('Bin | lumi [10^34 cm-2s-1] | area [cm2] | bx to s conv |     content | content err | content/cm2/s | content/cm2/s err')
	for ibin in range(0,lumiHist.GetNbinsX()+1):
		content = lumiHist.GetBinContent(ibin)
		contentErr = lumiHist.GetBinError(ibin)
		lumi = lumiHist.GetBinLowEdge(ibin)/(10**(34)) # convert to lumi per 10^34
		contentScaled = content*BXtoSconv/chamHalfAreaValue
		contentScaledErr = contentErr*BXtoSconv/chamHalfAreaValue
		printer = '{ibin:>3} | {lumi:>20.2f} | {chamHalfAreaValue:>10.3f} | {BXtoSconv:12.1f} | {content:>11.9f} | {contentErr:>11.9f} | {contentScaled:>13.4f} | {contentScaledErr:>14.5f}'.format(**locals())
		lumiHalfLog.info(printer)
	if not PU:
		lumiHalfLog.info('*'*len(printer))
		ecring = ec+ring
		slopePrinter = 'ring {ecring:>3} | slope = {slope:>11.8e} | slope err = {slopeErr:>11.8e} | chi^2 = {chiSq:>11.5f} | nDOF = {nDOF:>3}'.format(**locals())
		lumiHalfLog.info(slopePrinter)

# Integral logger
def intLogger(intLog,intHist,chamAreaValues,digi,when,ectype,PU):
	BXtoSconv = 1./(25.*10**(-9))
	intLog.info('\n'+digi+' '+when+(' PU norm' if PU else ''))
	intLog.info('Bin | ring | area [cm2] | bx to s conv |     content | content err | content/cm2/s | content/cm2/s err')
	if ectype=='':
		rings = ['-','11','21','31','41','12','13','22','32','42']
	else:
		rings = ['-','+11','-11','+21','-21','+31','-31','+41','-41',
				'+12','-12','+13','-13','+22','-22','+32','-32','+42','-42']
	for ibin in range(0,intHist.GetNbinsX()+1):
		if ibin==0:
			content=0.
			contentErr=0.
			chamAreaValue=0.
			contentScaled=0.
			contentScaledErr=0.
			ring = '-'
			pring = '-'
		else:
			content = intHist.GetBinContent(ibin)
			contentErr = intHist.GetBinError(ibin)
			ring = rings[ibin] if ectype=='' else rings[ibin][1:3]
			pring = rings[ibin]
			chamAreaValue = chamAreaValues[ring]
			contentScaled = content*BXtoSconv/chamAreaValue
			contentScaledErr = contentErr*BXtoSconv/chamAreaValue
		printer = '{ibin:>3} | {pring:>4} | {chamAreaValue:10.3f} | {BXtoSconv:12.1f} | {content:>11.9f} | {contentErr:>11.9f} | {contentScaled:>13.4f} | {contentScaledErr:>14.5f}'.format(**locals())
		intLog.info(printer)

# Phi logger
def phiLogger(phiLog,hist,chamAreaValue,digi,when,ec,ring,PU):
	BXtoSconv = 1./(25.*10**(-9))
	phiLog.info('\n'+digi+' '+ec+ring+' '+when+' '+(' PU norm' if PU else ''))
	phiLog.info('Bin | cham | area [cm2] | bx to s conv |     content | content err | content/cm2/s | content/cm2/s err')
	chams = ['-']+range(1,37)
	for ibin in range(0,hist.GetNbinsX()+1):
		content = hist.GetBinContent(ibin)
		contentErr = hist.GetBinError(ibin)
		cham = chams[ibin]
		contentScaled = content*BXtoSconv/chamAreaValue
		contentScaledErr = contentErr*BXtoSconv/chamAreaValue
		printer = '{ibin:>3} | {cham:>4} | {chamAreaValue:>10.3f} | {BXtoSconv:12.1f} | {content:>11.9f} | {contentErr:>11.9f} | {contentScaled:>13.4f} | {contentScaledErr:>14.5f}'.format(**locals())
		phiLog.info(printer)
