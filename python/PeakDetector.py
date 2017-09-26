import numpy as np
from scipy import stats
import time


class PeakDetector():
            
    def __init__(self, *args, pd = 10, ph = False, th= False, adp = False ,
        measureTime = True ):
        #if th :
        try :
            if not th :
                self.threshold = False
            elif np.ndim(th) == 0 :
                # only one number, so min of all extrema
                self.threshold = [
                    [th, np.Inf],
                    [th, np.Inf]]
            elif np.ndim(th) == 1:
                # min and max of all extrema
                self.threshold = [
                    [th[0], th[1]],
                    [th[0], th[1]]]
            elif np.ndim(th) == 2:
                # min and max of each type extrema
                self.threshold = [
                    [th[0][0], th[0][1]],
                    [th[0][1], th[1][1]]]
        except:
            self.threshold = False
            print("Threshold dimension error!")
        #else :
            #self.threshold = []

        #if ph :
        try :
            if not ph :
                self.flt_ph = False
            if np.ndim(ph) == 0 :
                self.flt_ph = [ph, 0]
            elif np.ndim(ph) == 1 and len(ph) == 2 :
                self.flt_ph = [ph[0], ph[1]]
        except :
            self.flt_ph = False
            print("Relatively height setting error!")
        #else
            
        self.flt_pd = pd # minimum distance of peak round(0.1*rate)
        ##self.flt_ph = np.array(ph) # relatively height of peak and around local minimum
        self.time = []     # a narray
        self.data = np.array(args[0]) if len(args) > 0 else np.array([])     # a narray
        self.extr = {'min': [] , 'max': []} # local_max (peaks) only index
        
        self.extr_rm = {'min':[] ,'max':[]}
        
        self.analyseTime = 0  # for dev , analyse() used time
        self.adp = adp
        self.log_flt_pd = []
        self.log_flt_ph = []
        self.log_rs = [[],[]]
        #self.threshold = th if len(th)>0 else []
        self.cv=[]
        self.log_std=[[],[]]
        self.measureTime = measureTime
        self.loop_count=0
        
        self.preExtr = { 'i': 0, 'v': 0}
        self.blkExtr = { 'i': 0, 'v': 0}
        #if measureTime :
            ##import time
            #time = __import__('time')
            #print('hi',time.monotonic())
        
        if len(self.data) >= 3 :
            self.analyse()
    
    def analyse(self):
        if self.measureTime :
            self.analyseTime = time.monotonic()
        if self.adp :
            self.flt_ph = 1
            self.log_flt_pd = []
            self.log_flt_ph = []

        if self.preExtr['i'] == 0 :     # && self.tmpLocal.max.v.length == 0
            self.preExtr['v'] = self.data[0]  # tmp_local_max
            self.preExtr['i'] = 0        # tmp_local_max

            self.blkExtr['v'] = self.data[0]  # block_local_max
            self.blkExtr['i'] = 0        # block_local_max

            
        # Determine first is max or min
        dataBlock = self.data[0:self.flt_pd]  # should check boundary in other language.
        find_max = True if np.argmax(dataBlock) > np.argmin(dataBlock) else False
        
        
        
        lastExtr = {'min': 0, 'max' : 0}
        n=0                 # for index of self.data
        dataLen = len(self.data)
        #find_max = True    # find min first may ignore code for first max and flt_ph
        while n < dataLen -1 :
            self.loop_count += 1
            #print('loop count = ', loop_count,
                #'\tn = ' ,n, '\tmax' if find_max else '\tmin',
                #)
            # record flt_pd when adp
            if self.adp :
                self.log_flt_pd.append(self.flt_pd)
                self.log_flt_ph.append(self.flt_ph)

            # Load a part data to find extrema
            if n + self.flt_pd > dataLen :
                dataBlock = self.data[n:]
            else :
                #print('block from ', n , ' to ',n+ self.flt_pd)
                dataBlock = self.data[n: n + self.flt_pd ]
                #print('block len = ', len(dataBlock))

            self.log_std[0].append(n)
            self.log_std[1].append(np.std(self.data[n: n +10]))
            
            # Get extrema
            self.blkExtr['i'] = np.argmax(dataBlock) if find_max else np.argmin(dataBlock)
            self.blkExtr['v'] = dataBlock[self.blkExtr['i']]

            # Compare last block, move on or save extrema then find opposite extrema.
            if (self.blkExtr['v'] >= self.preExtr['v'] if find_max else
                self.blkExtr['v'] <= self.preExtr['v'] ):
                self.preExtr['i'] = self.blkExtr['i'] + n 
                self.preExtr['v'] = self.blkExtr['v']
                n += self.flt_pd
            elif self.preExtr['i'] - lastExtr['max' if find_max else 'min'] < self.flt_pd :
                # If extrema near last opposite extrema may case two opposite
                # extrema short then min distance (flt_pd), so check it.
                self.preExtr['i'] = self.blkExtr['i'] + n
                self.preExtr['v'] = self.blkExtr['v']
                n += self.flt_pd
            else :
                self.extr['max' if find_max else 'min'].append(self.preExtr['i'])
                n = self.preExtr['i']
                lastExtr['max' if find_max else 'min'] = self.preExtr['i']

                #if loop_count > 5000 :
                    #break
                
                if self.adp :
                    self.adaptive(find_max,n)
                    
                find_max = not find_max
        # while data seq
        #self.extr['max' if find_max else 'min'].append(self.preExtr['i'])

        
        # filters
        extrLen = {
            'max' : len(self.extr['max']),
            'min' : len(self.extr['min'])
        }
        
        # filter for flt_ph (relatively height of peak and around local minimum)
        if self.flt_ph :
            flt_ph_lower = True if self.flt_ph[0] > 0 else False
            flt_ph_upper = True if self.flt_ph[1] > 0 else False

            #self.flt_ph.sort()  # make sure [0] < [1]
            
            # 2nd extrema type should start from 2nd data
            if self.extr['max'][0] > self.extr['min'][0] :
                shift = {'max': 0, 'min': 1}
            else :
                shift = {'max': 1, 'min': 0}
            
            for mm in ['max', 'min'] :
                if mm == 'max' :    # current extrema
                    mmo = 'min'     # opposite extrema
                    tmp_sign = 1
                else :
                    mmo = 'max'
                    tmp_sign = -1

                # compare extrema with surround opposite extrema
                for n in range(extrLen[mm]-shift[mm]) :
                    tmp_targetPV = self.data[self.extr[mm][n+shift[mm]]]
                    tmp_surrPV = self.data[self.extr[mmo][n:n+2]]
                    if len(tmp_surrPV) == 2 :
                        # lower limit of relative peak height.
                        if ( flt_ph_lower and
                            (tmp_sign * (tmp_targetPV - tmp_surrPV[0]) < self.flt_ph[0] or
                            tmp_sign * (tmp_targetPV - tmp_surrPV[1]) < self.flt_ph[0]
                        )):
                            self.extr_rm[mm].append(self.extr[mm][n+shift[mm]])

                        # upper limit of relative peak height.
                        # difference is ">" and "and" because it's for noise.
                        if (flt_ph_upper and
                            tmp_sign * (tmp_targetPV - tmp_surrPV[0]) > self.flt_ph[1] and
                            tmp_sign * (tmp_targetPV - tmp_surrPV[1]) > self.flt_ph[1] 
                        ):
                            self.extr_rm[mm].append(self.extr[mm][n+shift[mm]])

        # filter for threshold
        if self.threshold :
            for extrType in range(2) : # use ['min', 'max'] ?
                #for mm in range(2) :
                    #if self.threshold[extrType][mm]:
                extr = np.array(self.extr['min' if extrType == 0 else 'max'])
                extr_rm = np.array(self.extr_rm['min' if extrType == 0 else 'max'], np.int32)
                extrData = np.array( self.data[extr] )
                th_extr_rm = extr[ np.flatnonzero( np.logical_or(
                    extrData < self.threshold[extrType][0],
                    extrData > self.threshold[extrType][1])
                )]
                self.extr_rm['min' if extrType == 0 else 'max'] = (
                    np.unique(np.concatenate((extr_rm,th_extr_rm)))  )
            
        # the last line of analyse(), record used time
        if self.measureTime :
            self.analyseTime = time.monotonic() - self.analyseTime

    def adaptive(self, find_max,n) :
        #pass
        # may use ordinary least squares
        
        
        y = self.data[n:n+10]
        x = np.array(range(len(y)))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        r_2 = r_value**2
        self.log_rs[0].append(n)
        self.log_rs[1].append(r_2)
        
        #self.flt_pd = r_2* len(self.data)*0.1
        #if self.flt_pd < 3 :
            #self.flt_pd = 3
        #else :
            #self.flt_pd = int(self.flt_pd)

        #self.log_flt_pd.append(self.flt_pd)
        
        #if self.std[1][-1] > 0 :
            ## ok 
            ## self.flt_pd = np.log( 1/ self.log_std[-1]) * len(self.data)*0.01
            #if len(self.extr['max' if find_max else 'min']) > 2 :
                #peak_dst_avg = np.mean(np.diff((self.extr['max' if find_max else 'min'][-4:])))
            #else :
                #peak_dst_avg = 0
                
            #self.flt_pd = np.log( 1/ np.mean(self.log_std[1][-3:]))# * peak_dst_avg * 0.5
            #if self.flt_pd < 3 :
                #self.flt_pd = 3
            #else :
                #self.flt_pd = int(self.flt_pd)
        
        #self.log_flt_pd.append(self.flt_pd)
        
        #def cv(d) :
            #return np.std(d)/np.mean(d)
            
        #if len(self.localMax) > 1 :
            #tmp_cond = cv(self.data[self.localMax[-5:-1]])
            #if self.data[self.localMax[-1]] > tmp_cond :
                #self.flt_ph *= 1.5
            #else :
                #self.flt_ph *= 0.5
            
        
    def update(self, data) :
        # 
        # check data type
        if len(data) > 0 :
            self.data = data
            self.analyse()
    def append(self, data) :
        # append new data
        if len(data) > 0 :
            pass

    def clear(self) :
        # clear data in object
        self.__init__()

    def get(self, act='max.v') :
        # Get peaks api
        case = {
            'orig.max.i' : lambda : self.extr['max'] ,
            'orig.min.i' : lambda : self.extr['min'] ,
            'rm.max'     : lambda : self.extr_rm['max'] ,
            'rm.min'     : lambda : self.extr_rm['min'] ,
            'max.i'      : lambda : np.setdiff1d(self.extr['max'], self.extr_rm['max']),
            'max.v'      : lambda : self.data[np.setdiff1d(self.extr['max'], self.extr_rm['max'])],
            'min.i'      : lambda : np.setdiff1d(self.extr['min'], self.extr_rm['min']),
            'min.v'      : lambda : self.data[np.setdiff1d(self.extr['min'], self.extr_rm['min'])]
            }
        return case.get(act, lambda : [])()
