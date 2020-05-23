import ROOT
import numpy as np
import sys
import math 

strawreallength=[1178.804, 1178.804, 1170.926, 1170.926, 1162.864, 1162.864, 1154.618, 1154.618, 1146.18, 1146.18, 1137.546, 1137.546, 1128.714, 1128.714, 1119.68, 1119.68, 1110.436, 1110.436, 1100.978, 1100.978, 1091.302, 1091.302, 1081.402, 1081.402, 1071.27, 1071.27, 1060.902, 1060.902, 1050.29, 1050.29, 1039.426, 1039.426, 1028.304, 1028.304, 1016.9159999999999, 1016.9159999999999, 1005.25, 1005.25, 993.3, 993.3, 981.052, 981.052, 968.5, 968.5, 955.63, 955.63, 942.428, 942.428, 928.884, 928.884, 914.978, 914.978, 900.7, 900.7, 886.028, 886.028, 870.942, 870.942, 855.426, 855.426, 839.454, 839.454, 822.998, 822.998, 806.034, 806.034, 788.528, 788.528, 770.444, 770.444, 751.744, 751.744, 732.382, 732.382, 712.304, 712.304, 691.454, 691.454, 669.76, 669.76, 647.142, 647.142, 623.504, 623.504, 598.732, 598.732, 572.688, 572.688, 545.196, 545.196, 516.038, 516.038, 496.93399999999997, 496.93399999999997, 477.508, 477.508]

ROOT.gSystem.Load("event/Dict.so")

from ROOT import StrawHit,Event

energycut=10.

fn = sys.argv[1]
nhitcut=int(sys.argv[2])
#entry = int(sys.argv[2])
#ntrigs = int(sys.argv[3])

ROOT.gStyle.SetTitleW(0.8);
ROOT.gStyle.SetTitleFontSize(0.15);

f = ROOT.TFile(fn);
tr = f.Get("T")

nstraws = 96

ientry = 0
while ientry < tr.GetEntries():
  tr.GetEntry(ientry)
  entry_list = []

  


  event=tr.events
  
  for hit in event.straws:
    if hit.peak-hit.pedestal>energycut:
        entry_list.append(hit)


  
  
  ntrigs = len(entry_list)
  
  if ntrigs<nhitcut:
    ientry+=1
    continue


  g = []
  chs = [0 for i in range(nstraws)]
  zch = [0 for i in range(nstraws)]
  rech = [0 for i in range(nstraws)]
  colch = [0 for i in range(nstraws)]
  
  c1 = ROOT.TCanvas("c1","",800,600);
  c1.Draw();
  p1 = ROOT.TPad("p1","p1",0,0.93,1,1.);
  p1.Draw();
  
  c1.cd(0);
  p2 = ROOT.TPad("p1","p1",0.1,0.,0.9,0.93);
  p2.Draw();
#  p2.Divide(2,int(ntrigs/2)+ntrigs%2);
  
  for i in range(ntrigs):
    hit = entry_list[i]
    chs[i] = int(hit.channel)
    zch[chs[i]] = hit.zstraw
  
    if (i==0):
      dT=0;
    else:
      dT = hit.dT
  
#    cstr = "T=%7.3fns, #DeltaT=%7.3fns, %d" % (dT,tr.deltaT,tr.channel)
#    g[-1].SetTitle(cstr);
#    g[-1].SetLineColor(i+1);
#    g[-1].SetLineColor(2);
#    g[-1].SetLineWidth(3);
#    g[-1].Draw("al");
  
  
  
  
  lowstraw = nstraws/2-1;
  highstraw = nstraws/2;
  
  
  
  for i in range(ntrigs):
    print "channel:",chs[i]
    rech[chs[i]] = 1;

    colch[chs[i]] = i+1;
   
  el = []
  
  p1.cd();
  
  w = ROOT.gPad.GetWw()*ROOT.gPad.GetAbsWNDC();
  h = ROOT.gPad.GetWh()*ROOT.gPad.GetAbsHNDC();
  xmin = 0;
  xmax = 2;
  ymin = 0;
  ymax = xmax*h/w;
  
  
  ROOT.gPad.SetFixedAspectRatio(); 
  ROOT.gPad.Range(xmin,ymin,xmax,ymax);
  
  elrad = 0.015;
  spacing = 1.225*elrad;
  yspacing = 2*elrad+0.082*elrad;
  ypos = 0.03+yspacing;
  
  for i in range(nstraws):
    if i%2 == 0:
      el.append(ROOT.TEllipse(0.05+spacing*i,ypos,elrad,elrad))
    else:
      el.append(ROOT.TEllipse(0.05+spacing*i,ypos-yspacing,elrad,elrad))
     
    el[-1].SetLineStyle(1);

    if i==41 or i==43 or i==91:
      el[-1].SetFillStyle(1001);
#      el[-1].SetFillColor(colch[i]);
      el[-1].SetFillColor(1);
    if i==84 or i==85:
      el[-1].SetFillStyle(1001);
#      el[-1].SetFillColor(colch[i]);
      el[-1].SetFillColor(4);
      
    if (rech[i] == 1):
      el[-1].SetFillStyle(1001);
#      el[-1].SetFillColor(colch[i]);
      el[-1].SetFillColor(2);
    
  
       
    el[-1].Draw();
   
  
  
  el1 = ROOT.TEllipse(0.2,0.2,.1,.1);
  el1.Draw();


  p2.cd()
  rc = []
  rcz=[]
  w = ROOT.gPad.GetWw()*ROOT.gPad.GetAbsWNDC();
  h = ROOT.gPad.GetWh()*ROOT.gPad.GetAbsHNDC();
  xmin = 0;
  xmax = 2;
  ymin = 0;
  ymax = xmax*h/w;
  
  
  ROOT.gPad.SetFixedAspectRatio(); 
  ROOT.gPad.Range(xmin,ymin,xmax,ymax);
  
  rspacing = 0.01
  spacing = 0.015
  start = 0.1
  starty = 1.5
  factor=0.0005
  for i in range(nstraws):

    xstart = (xmax-xmin)/2. - strawreallength[i]/strawreallength[0]
    xend = (xmax-xmin)/2. + strawreallength[i]/strawreallength[0]
#    print xstart,xend
    rc.append(ROOT.TBox(xstart,starty-spacing*i,xend,starty-spacing*i-rspacing))



     
    rc[-1].SetLineStyle(1);
    rc[-1].Draw();
#    if i==41 or i==43 or i==91 or i==14:
#      rc[-1].SetFillStyle(1001);
#      rc[-1].SetFillColor(1);
      
    if (rech[i] == 1):
      rc[-1].SetFillStyle(1001);
      xstart = (xmax-xmin)/2. - zch[i]/strawreallength[0]
      xend = xstart+40.*0.5*(xmax-xmin)/strawreallength[0]
#      print "test",xstart,xend
    
      rcz.append(ROOT.TBox(xstart,starty-spacing*i,xend,starty-spacing*i-rspacing))
      rcz[-1].SetFillColor(2);
      rcz[-1].Draw("same")
      
#      el[-1].SetFillColor(colch[i]);
#      rc[-1].SetFillColor(2);
    
  
       
  ientry=ientry+1
    
  c1.Update();
  
  
  
  raw_input()


