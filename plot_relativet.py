import ROOT
import numpy as np
import sys

ROOT.gSystem.Load("event/Dict.so")
from ROOT import StrawHit,Event

energycut=10.
fn = sys.argv[1]

#current_calibration = [0, 4.104590896238184, -9.840137416296168, 3.9227602390996488, -10.567058178106489, -6.544705757701402, 3.8300694130233355, 4.682170508175938, -7.149393395624793, 5.247334928827449, -8.553771516328489, -5.569002196530992, 2.5253486135013037, 4.167162761128765, 3.9480358548531473, 3.9480358548531473, -9.666402459465, -4.906731066885791, 3.292173909414168, 4.658610532674562, -9.891363710049669, 3.7064530340284723, -9.47747135926139, -6.067798406359641, 2.8188644310718516, 2.130359988270829, -8.364398407877761, 3.75225071816579, -9.310764614151237, -5.875722665211868, 3.607964221547065, 5.6733404803247485, -7.599947145283743, 4.600489238956891, -8.848892368247398, -4.1001524981677, 3.88342030434654, 7.423666582398102, -6.903629629195844, 5.632116239467964, -7.787805372242197, 5.011584985291551, 5.011584985291551, -4.433021787494241, -4.433021787494241, 9.77685118852532, -4.2302367577406494, 0.4723746873908672, 7.259192093166655, 8.38753461059845, -2.374289125868847, 9.588992781050857, -4.998679071108203, -2.2987863753872, 6.661352188396149, 9.27444741542606, -1.9577280689231813, 10.100047668291419, -2.8562635596412282, -0.7350831014770236, 8.900731428111918, 9.303840603238273, -0.8158495252828288, 8.490255098957999, -3.508657129703287, -3.05581137849666, 7.474057671240535, 10.859676335474445, -2.531608937178662, 9.954912655083225, -6.129655011001661, -2.762059798307181, 8.693465224833194, 8.506489424394909, -2.86066421648988, 8.50646917985991, -3.8144862142225686, -1.6514899924709514, 8.482075269660111, 8.900118652148226, -1.6196486763235036, 8.650099184744825, -3.7385217808678846, -2.698108912155995, 0.21870633659400873, 0.21870633659400873, 0.21870633659400873, 11.284267373676123, -2.4210768976864427, -1.19727577564269, 6.709596450437562, 1.4312266868907635, 1.4312266868907635, 12.416414408066547, -0.6599126223587491, 0]
#current_calibration = np.zeros(96)
#
#pairs = {j: j+1 for j in range(95)}
#del pairs[0]
#del pairs[14]
#pairs[13] = 15
#del pairs[41]
#pairs[40] = 42
#del pairs[43]
#pairs[42] = 44
#del pairs[84]
#del pairs[85]
#pairs[83] = 86
#del pairs[91]
#pairs[90] = 92

#from try3calib import *
badchannels = [0,14,41,43,69,84,85,91]

pairs = {}
strawi = 0
while strawi < 95:
  if strawi in badchannels:
    strawi += 1
    continue
  strawj = strawi + 1
  while strawj < 95:
    if strawj in badchannels:
      strawj += 1
      continue
    break
  if strawj in badchannels:
    break
  pairs[strawi] = strawj
  strawi += 1



hs = [ROOT.TH1F("h_%d" % i,"h_%d" % i,200,-100,100) for i in range(96)]

f = ROOT.TFile(fn);
t = f.Get("T")
for i in range(t.GetEntries()):
    t.GetEntry(i)
    indexi = -1
    indexj = -1
    failed = False
    straws = []
    for j in range(t.events.straws.size()):
        if t.events.straws[j].peak-t.events.straws[j].pedestal < energycut:
            failed = True
            break
        if t.events.straws[j].warning or t.events.straws[j].trigHV:
          continue
        straws.append(t.events.straws[j].channel)
#        if t.events.straws[j].channel == strawi:
#            indexi = j
#        elif t.events.straws[j].channel == strawj:
#            indexj = j
    if failed:
        continue
#    if indexi == -1 or indexj == -1:
#        continue
    for j in range(95):
        if not j in pairs:
          continue
        try:
            indexi = straws.index(j)
            indexj = straws.index(pairs[j])
        except:
            continue
        timei = (t.events.straws[indexi].timeCal+t.events.straws[indexi].timeHV)/2.*0.024414625# + current_calibration[j]
        timej = (t.events.straws[indexj].timeCal+t.events.straws[indexj].timeHV)/2.*0.024414625# + current_calibration[pairs[j]]
#        deltaT = ((t.events.straws[indexi].timeCal+t.events.straws[indexi].timeHV)/2. - (t.events.straws[indexj].timeCal+t.events.straws[indexj].timeHV)/2.)*0.024414625
        deltaT = timei - timej
        hs[j].Fill(deltaT)

offsets = [0 for i in range(96)]
for j in range(96):
    if not j in pairs:
        continue
    if hs[j].Integral() > 100:
        offsets[j] = hs[j].GetMean()
        print(j,pairs[j],hs[j].GetMean(),hs[j].GetRMS())
    else:
        print(j,pairs[j],"NOT ENOUGH HITS")

total_offsets = [0 for i in range(96)]

index = 0
while index < 95:
  if not index in pairs:
    index += 1
    continue
  total_offsets[pairs[index]] += offsets[index]
  index += 1



#index = 94
#total_offsets = [0 for i in range(96)]
#while index > 0:
#    total_offsets[index] = total_offsets[index+1] - offsets[index]
#    index -= 1
    
for i in range(96):
    print(i,total_offsets[i])
print(total_offsets)

import matplotlib.pyplot as plt
plt.plot(np.linspace(0,95,96)[::2],total_offsets[::2],label="even")
plt.plot(np.linspace(0,95,96)[1::2],total_offsets[1::2],label="odd")
plt.xlabel("channel")
plt.ylabel("offset (ns)")
plt.legend()
plt.show()



for j in range(95):
    if not j in pairs:
        continue
    hs[j].Draw()
    input()


