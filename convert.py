import ROOT
import json
import os
from array import array

ROOT.gSystem.Load("event/Dict.so")

from ROOT import StrawHit,Event

channel_map = [
    [91,85,79,73,67,61,55,49,
      43,37,31,25,19,13,7,1,
      90,84,78,72,66,60,54,48,
      42,36,30,24,18,12,6,0,
      93,87,81,75,69,63,57,51,
      45,39,33,27,21,15,9,3],
    [94,88,82,76,70,64,58,52,
      46,40,34,28,22,16,10,4,
      95,89,83,77,71,65,59,53,
      44,38,32,26,20,14,8,2,
      92,86,80,74,68,62,56,50,
      47,41,35,29,23,17,11,5]]

def read_chunk(f,chunk_size=5000):
  while True:
    data = f.read(chunk_size)
    if not data:
      break
    yield data


def parse_straws(filename,outfile):
  fout = ROOT.TFile(outfile,"UPDATE")
  
  totalTime = array( 'd', [ 0 ] )
  threshHV = array( 'i', 8*[0])
  threshCal = array('i', 8*[0])
  gainHV = array('i',8*[0])
  gainCal = array('i',8*[0])
  calDAC = array('i',8*[0])
  runMode = array('i',[0])
  adcMode = array('i',[0])
  tdcMode = array('i',[0])
  samples = array('i',[0])
  lookback = array('i',[0])
  triggers = array('i',[0])
  chanMask = array('i',[0])
  message = array('B',100*[0])
  afilename = array('B',100*[0])
  runNumber = array('i',[0])
  runtree = ROOT.TTree('Run','Run')
  runtree.Branch('totalTime',totalTime,'totalTime/D')
  runtree.Branch('threshHV',threshHV,'threshHV[8]/I')
  runtree.Branch('threshCal',threshCal,'threshCal[8]/I')
  runtree.Branch('gainHV',gainHV,'gainHV[8]/I')
  runtree.Branch('gainCal',gainCal,'gainCal[8]/I')
  runtree.Branch('calDAC',calDAC,'calDAC[8]/I')
  runtree.Branch('runMode',runMode,'runMode/I')
  runtree.Branch('adcMode',adcMode,'adcMode/I')
  runtree.Branch('tdcMode',tdcMode,'tdcMode/I')
  runtree.Branch('samples',samples,'samples/I')
  runtree.Branch('lookback',lookback,'lookback/I')
  runtree.Branch('triggers',triggers,'triggers/I')
  runtree.Branch('chanMask',chanMask,'chanMask/I')
  runtree.Branch('message',message,'message/C')
  runtree.Branch('filename',afilename,'filename/C')
  runtree.Branch('runNumber',runNumber,'runNumber/I')

  tree = ROOT.TTree( 'T', 'Tree' )
  branchev = Event()
  tree.Branch('events',branchev,32000,0)
 
  for filename in filenames:
    print(filename)
    runno = int(filename.split("_")[-1].split(".txt")[0])
    f = open(filename)
    settings = json.loads(f.readline())
    meta = json.loads(f.readline())
    #for i in range(len(meta['filename'])):
    #  afilename[i] = str(meta['filename'])[i]
    #runNumber[0] = int(meta['filename'].split("_")[1].split(".txt")[0])
    #for i in range(len(meta['message'])):
    #  message[i] = str(meta['message'])[i]
    #chanMask[0] = meta['chan_mask']
    #triggers[0] = meta['triggers']
    lookback[0] = meta['lookback']
    samples[0] = meta['samples']*3
    #tdcMode[0] = meta['tdc_mode']
    #adcMode[0] = meta['adc_mode']
    #runMode[0] = meta['mode']
    #for i in range(8):
    #  threshHV[i] = int(settings['thresh'][i])
    #  threshCal[i] = int(settings['thresh'][i+8])
    #  gainHV[i] = int(settings['gain'][i])
    #  gainCal[i] = int(settings['gain'][i+8])
    #  calDAC[i] = int(settings['caldac'][i])
    runtree.Fill()
  
    num_words = (4 + int(samples[0]/3))*2
  
    filesize = os.path.getsize(filename)
    index = 0
    print("PARSING...")
  
    allhits = []
  #  trees = [ROOT.TTree( 'straw%d' % (i), 'Tree %d' % (i) ) for i in range(96)]
  #  for i in range(96):
  #    trees[i].Branch('hits',branchhits[i],32000,0)
   
   
    last_data = ''
    num_chunks = 0
  
    gtime = 0
    htime = 0
    ctime = 0
    for chunk in read_chunk(f):
      if num_chunks % 1000 == 0:
        print(num_chunks * 5000,"/",filesize,":",(gtime*2**28+htime)*24.414625*10**-12)
  #    if num_chunks > 5000:
  #      break
      num_chunks += 1
      data = last_data + chunk
      last_data = ''
      data = data.split('\n')
      if (len(data)-1) % num_words != 0:
        for j in range((len(data)-1) % num_words):
          last_data += data[-((len(data)-1) % num_words) + j - 1] + '\n'
      last_data += data[-1]
      data = data[:-((len(data)-1) % num_words)-1]
      data = list(map(lambda x: int(x,16) & 0xFFFF, data))
      for i in range(int(len(data) / num_words)):
        if data[i*num_words] & 0x8000 != 0x8000:
          import pdb;pdb.set_trace()
        tdata = data[i*num_words:(i+1)*num_words]
        fifo_was_full = (tdata[1] & 0x80) != 0x0
        diginum = (tdata[1] & 0x40) >> 6
        tempchannel = (tdata[1] & 0x3F)
        if tempchannel >= 48:
          import pdb;pdb.set_trace()
        channel = channel_map[diginum][tempchannel]
        
        gtime = ((tdata[2] & 0x7FFF) << 16) + tdata[3]
        htime = ((tdata[4]&0xFF)<<16) + tdata[5]
        ctime = ((tdata[6]&0xFF)<<16) + tdata[7]
        htime = (htime & 0x3FFFFF00) + (0xFF - (htime&0xFF));
        ctime = (ctime & 0x3FFFFF00) + (0xFF - (ctime&0xFF));
        htot = ((tdata[4]&0xF00)>>8)
        ctot = ((tdata[6]&0xF00)>>8)
        
        deltat = (ctime-htime)*24.414625*10**-3 # in ns
        
        hit = StrawHit()
        hit.channel = channel
        hit.run = runno
        hit.timeGlobal = gtime
        hit.timeHV = htime
        hit.timeCal = ctime
        hit.deltaT = deltat
        hit.totHV = htot
        hit.totCal = ctot
        hit.trigHV = True
        hit.trigCal = True
        hit.warning = fifo_was_full
        hit.samples.clear()
  
        for j in range(int(samples[0]/3)):
          sample0 = (tdata[8+j*2+1] & 0x3FF)
          sample1 = ((tdata[8+j*2] & 0xF)<<6) + ((tdata[8+j*2+1] & 0xFC00) >> 10)
          sample2 = ((tdata[8+j*2] & 0x3FF0)>>4)
          hit.samples.push_back(sample0)
          hit.samples.push_back(sample1)
          hit.samples.push_back(sample2)
        if samples[0] > 1:
          hit.pedestal = sum(hit.samples[0:lookback[0]])/lookback[0]
          hit.peak = max(hit.samples)
          hit.minimum = min(hit.samples)
        else:
          hit.pedestal = 0
          hit.peak = 0
          hit.minimum = 0
        
        allhits.append(hit)
  #      trees[channel].Fill()
      
        i += 1
  #  for i in range(95):
  #    trees[i].Write()
    print("DONE! Now sorting...",len(allhits),)
    f.close()
  
   
    #FIXME ewm is not 2**28
    allhits = sorted(allhits,key = lambda x: x.timeGlobal*2**28 + x.timeCal)
    timeGlobalOld = 0
    timeCalOld = 0
    branchev.nHits = 0
    branchev.straws.clear()
    for i in range(len(allhits)):
      if i != len(allhits)-1:
        timesincelast = ((allhits[i+1].timeGlobal-allhits[i].timeGlobal)*2**28+(allhits[i+1].timeCal-allhits[i].timeCal))*24.414625*10**-12 # in s
      else:
        timesincelast = 9999
      if i == 0:
        timeGlobalOld = allhits[0].timeGlobal
        timeCalOld = allhits[0].timeCal
        branchev.straws.push_back(allhits[0])
        branchev.nHits += 1
      else:
        deltat  = (allhits[i].timeGlobal-timeGlobalOld)*2**28*24.414625*10**-3
        deltat += (allhits[i].timeCal-timeCalOld)*24.414625*10**-3
        if deltat > 250:
          for j in range(branchev.straws.size()):
            if branchev.straws[j].warning:
              branchev.warning = True
            
          tree.Fill()
          timeGlobalOld = allhits[i].timeGlobal
          timeCalOld = allhits[i].timeCal
          branchev.straws.clear()
          branchev.nHits = 0
          branchev.warning = False
          if timesincelast >= 0.0005:
            branchev.fifosfull = True
          else:
            branchev.fifosfull = False
        else:
          if timesincelast >= 0.0005:
            branchev.fifosfull = True
        branchev.straws.push_back(allhits[i])
        branchev.nHits += 1
    if branchev.straws.size() > 0:
      branchev.fifosfull = True
      for j in range(branchev.straws.size()):
        if branchev.straws[j].warning:
          branchev.warning = True
      tree.Fill() 
    #totalTime[0] = tdc0*2**28*10**-12*24.414625
    #totalTime[0] += tdc1*10**-12*24.414625
    #runtree.Fill()
 
  tree.Write()
  runtree.Write()
  fout.Write()
  fout.Close()



if __name__ == "__main__":
  import sys
  import glob
  filenames = glob.glob(sys.argv[1])
  outfilename = sys.argv[2]
  f = ROOT.TFile(outfilename,"RECREATE")
  f.Close()
  parse_straws(filenames,outfilename)
