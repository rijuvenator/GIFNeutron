import ROOT as r
import array as array

def DrawOverflow(hist):
    # Function to paint the histogram hist with an extra bin for overflows
    nx = hist.GetNbinsX()+1
    xbins = array.array('d',[])
    for ibin in range(nx+1):
        if ibin==nx+1: xbins.append(xbins[nx-1]+hist.GetBinWidth(nx))
        else: xbins.append(hist.GetBinLowEdge(ibin+1))
    # Book a temporary histogram having extra bins for overflows
    htmp = r.TH1F(hist.GetName(), hist.GetTitle(), nx, xbins)
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
