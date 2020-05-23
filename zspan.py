import os
import ROOT
import numpy as np
import sys
import math
from array import array


strawreallength=[1178.804, 1178.804, 1170.926, 1170.926, 1162.864, 1162.864, 1154.618, 1154.618, 1146.18, 1146.18, 1137.546, 1137.546, 1128.714, 1128.714, 1119.68, 1119.68, 1110.436, 1110.436, 1100.978, 1100.978, 1091.302, 1091.302, 1081.402, 1081.402, 1071.27, 1071.27, 1060.902, 1060.902, 1050.29, 1050.29, 1039.426, 1039.426, 1028.304, 1028.304, 1016.9159999999999, 1016.9159999999999, 1005.25, 1005.25, 993.3, 993.3, 981.052, 981.052, 968.5, 968.5, 955.63, 955.63, 942.428, 942.428, 928.884, 928.884, 914.978, 914.978, 900.7, 900.7, 886.028, 886.028, 870.942, 870.942, 855.426, 855.426, 839.454, 839.454, 822.998, 822.998, 806.034, 806.034, 788.528, 788.528, 770.444, 770.444, 751.744, 751.744, 732.382, 732.382, 712.304, 712.304, 691.454, 691.454, 669.76, 669.76, 647.142, 647.142, 623.504, 623.504, 598.732, 598.732, 572.688, 572.688, 545.196, 545.196, 516.038, 516.038, 496.93399999999997, 496.93399999999997, 477.508, 477.508]

if not os.path.exists('zcalibpdfs'):
    os.makedirs("zcalibpdfs")

ROOT.gSystem.Load("event/Dict.so")

from ROOT import StrawHit,Event

fn = sys.argv[1]
#entry = int(sys.argv[2])
#ntrigs = int(sys.argv[3])

ROOT.gStyle.SetTitleW(0.8);
ROOT.gStyle.SetTitleFontSize(0.15);

f = ROOT.TFile(fn);
tr = f.Get("T")
runtr = f.Get("Run")

outputfn = sys.argv[1].split(".")[0]+"zcal.root"
fout = ROOT.TFile(outputfn,'RECREATE');

tree=tr.CloneTree(0)
runtree=runtr.CloneTree(-1)

energycutoff = 50.
minimumcutoff = 350
nstraws = 96



hist_dt=[None]*96
strawlengths=[1]*96
strawcenters=[1]*96
for i in range(96):

    hist_dt[i] = ROOT.TH1F('ch'+str(i)+'_DeltaT','ch'+str(i)+'_DeltaT;#Delta T [ns];count',100,-12,12)




ientry = 0
while ientry < tr.GetEntries():

    tr.GetEntry(ientry)
    if ientry%10000==0:
        print ientry

    event=tr.events
    for hit in event.straws:

        if hit.peak-hit.pedestal>energycutoff and hit.minimum>minimumcutoff:
            hist_dt[hit.channel].Fill(hit.deltaT)
    ientry = ientry + 1

c0=ROOT.TCanvas("c0","c0", 1600, 600)

for i in range(96):
    lowside = 0
    highside = 0

    for j in range(hist_dt[i].GetMaximumBin(),1,-1):
        if hist_dt[i].GetBinContent(j)<hist_dt[i].GetMaximum()/20.:
            lowside = j
            break
    for j in range(hist_dt[i].GetMaximumBin(),hist_dt[i].GetNbinsX()):
        if hist_dt[i].GetBinContent(j)<hist_dt[i].GetMaximum()/20.:
            highside = j
            break

    l1=ROOT.TLine(hist_dt[i].GetBinCenter(lowside),0,hist_dt[i].GetBinCenter(lowside),hist_dt[i].GetMaximum())
    l2=ROOT.TLine(hist_dt[i].GetBinCenter(highside),0,hist_dt[i].GetBinCenter(highside),hist_dt[i].GetMaximum())
    hist_dt[i].Draw()
    l1.Draw()
    l2.Draw()
    

    
#    print (hist_dt[i].GetMaximum()),hist_dt[i].GetBinCenter(lowside),hist_dt[i].GetBinCenter(highside)
    strawlength = hist_dt[i].GetBinCenter(highside) - hist_dt[i].GetBinCenter(lowside)
    strawcenter = hist_dt[i].GetBinCenter(hist_dt[i].GetMaximumBin())

    if strawlength>0:
        strawlengths[i] = strawlength
        strawcenters[i] = strawcenter
    c0.Update()
    c0.SaveAs("zcalibpdfs/zcalibch"+str(i)+".pdf")
#    raw_input()


ientry=0

event = Event()
tree.SetBranchAddress("events",ROOT.AddressOf(event))

while ientry < tr.GetEntries():

    tr.GetEntry(ientry)
    if ientry%10000==0:
        print ientry



    event.nHits=tr.events.nHits
    event.fifosfull=tr.events.fifosfull
    event.warning=tr.events.warning

    event.straws.clear()
    for hit in tr.events.straws:
        zstr=strawreallength[hit.channel]*(hit.deltaT-strawcenters[hit.channel])/strawlengths[hit.channel]
        hit.zstraw=zstr
        event.straws.push_back(hit)

    tree.Fill()

    ientry = ientry + 1



#while ientry < runtr.GetEntries():
#    runtr.GetEntry(ientry)
#    runtree.Fill()

runtree.Write()    
tree.Write()
fout.Close()



