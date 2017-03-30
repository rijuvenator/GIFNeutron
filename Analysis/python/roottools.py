import sys
import subprocess as bash
import ROOT as R
import array as array

CMSSW_PATH  = bash.check_output('echo $CMSSW_BASE',shell=True).strip('\n') + '/src/'
GITLAB_PATH = CMSSW_PATH + 'Gif/Analysis/'

def DrawOverflow(hist):
    # Function to paint the histogram hist with an extra bin for overflows
    nx = hist.GetNbinsX()+1
    xbins = array.array('d',[])
    for ibin in range(nx+1):
        if ibin==nx+1: xbins.append(xbins[nx-1]+hist.GetBinWidth(nx))
        else: xbins.append(hist.GetBinLowEdge(ibin+1))
    # Book a temporary histogram having extra bins for overflows
    htmp = R.TH1F(hist.GetName(), hist.GetTitle(), nx, xbins)
    htmp.Sumw2()
    # Fill the new histogram including the overflows
    for ibin in range(1,nx+1):
        htmp.SetBinContent(htmp.FindBin(htmp.GetBinCenter(ibin)),hist.GetBinContent(ibin))
        htmp.SetBinError(htmp.FindBin(htmp.GetBinCenter(ibin)),hist.GetBinError(ibin))
    htmp.SetBinContent(htmp.FindBin(htmp.GetBinCenter(1)-1),hist.GetBinContent(0))
    htmp.SetBinError(htmp.FindBin(htmp.GetBinCenter(1)-1),hist.GetBinError(0))
    # Restore the number of entries
    htmp.SetEntries(hist.GetEffectiveEntries())
    return htmp

def poisson_interval(nobs, alpha=(1-0.6827)/2, beta=(1-0.6827)/2):
    lower = 0
    if nobs > 0:
        lower = 0.5 * R.Math.chisquared_quantile_c(1-alpha, 2*nobs)
    elif nobs == 0:
        beta *= 2
    upper = 0.5 * R.Math.chisquared_quantile_c(beta, 2*(nobs+1))
    return lower, upper

def clopper_pearson(n_on, n_tot, alpha=1-0.6827, equal_tailed=True):
    if equal_tailed:
        alpha_min = alpha/2
    else:
        alpha_min = alpha

    lower = 0
    upper = 1

    if n_on > 0:
        lower = R.Math.beta_quantile(alpha_min, n_on, n_tot - n_on + 1)
    if n_tot - n_on > 0:
        upper = R.Math.beta_quantile_c(alpha_min, n_on + 1, n_tot - n_on)

    if n_on == 0 and n_tot == 0:
        return 0, lower, upper
    else:
        return float(n_on)/n_tot, lower, upper

def clopper_pearson_poisson_means(x, y, alpha=1-0.6827):
	r, rl, rh = clopper_pearson(x, x+y, alpha)
	return r/(1 - r), rl/(1 - rl), rh/(1 - rh)

# For getting the output of TTree::Scan as a dictionary
# No arguments gets you the entire tree
# scanarg is exactly what you want to pass to TTree::Scan
#    it should be of the form '"ID", "CUTS"'
# num is the event number
def getTreeDict(scanarg=None,num=None):
	if scanarg is None:
		SCANARG = r'"ID"'
	else:
		SCANARG = scanarg

	if num is None:
		print 'No tree given.'
		return

	SCANARG = '\'' + SCANARG + '\''

	COMMAND = GITLAB_PATH+'analysis/neutron/scanTree.sh '+str(num)+' '+SCANARG
	scan = bash.check_output(COMMAND,shell=True)

	scan = scan.split('\n')
	dic = {}
	for line in scan:
		if '**' in line or 'Row' in line or 'selected' in line or line == '':
			continue
		l = line.split()
		dic[l[3]] = int(l[1])
	return dic

def cumulative_histogram(h, type='ge'):
    """Construct the cumulative histogram in which the value of each
    bin is the tail integral of the given histogram.
    """
    
    nb = h.GetNbinsX()
    hc = R.TH1F(h.GetName() + '_cumulative_' + type, '', nb, h.GetXaxis().GetXmin(), h.GetXaxis().GetXmax())
    hc.Sumw2()
    if type == 'ge':
        first, last, step = nb+1, 0, -1
    elif type == 'le':
        first, last, step = 0, nb+1, 1
    else:
        raise ValueError('type %s not recognized' % type)
    for i in xrange(first, last, step):
        prev = 0 if i == first else hc.GetBinContent(i-step)
        c = h.GetBinContent(i) + prev
        hc.SetBinContent(i, c)
        if c > 0:
            hc.SetBinError(i, c**0.5)
        else:
            hc.SetBinError(i, 0.)
    return hc
