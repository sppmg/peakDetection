import numpy as np
import time
#from scipy import stats

class PeakDetector():
    """ A peak detect object base on local maximum and local minimum.

    This module will analyse extrema (local maximum and local minimum) from
    input data, you can apply filters by give vaild argument.
    
    
    Args:
        *args   - for data, a 1D array/list (Only use args[0] for data).
        pd      - Peak Distance. The minimum distance of same type extrema (eg.
                max with max).
        ph      - Peak Height relatively. It's difference height of neighboring
                opposite extrema (eg. max with min).
                Ignore or set to False to turn off this option.
        th      - Threshold. It's absolute height of peak. Can be a number,
                2 element array/list or 2D array/list with 4 element.
                Ignore or set to False to turn off this option.
                
    Args, didn't finish(for developer):
        adp     - Adaptive, Adapt pd, ph ,etc.

    Attributes (public):
        analyseTime - log time of peak detection with filters consumption.

    Attributes (private):
        flt_*   - * can be pd, ph, th, etc. record all filter.
        
    """
    
    def __init__(self, *args, pd = 2, ph = False, th= False, adp = False ,
        measureTime = True ):
            
        self.time = []     # a narray
        self.data = np.array(args[0]) if len(args) > 0 else np.array([])
        
        self.extr = {'min': [] , 'max': []} # index of data for extrema
        self.extr_rm = {'min':[] ,'max':[]} # index of data for removed extrema
        
        self.analyseTime = 0  # analyse() consume time.
        self.measureTime = measureTime
        
        self.adp = adp

        # filter - pd - Peak Distance (minimum)
        self.flt_pd = int(pd) if pd > 0 else 1

        # Filter - ph - relative Peak Height
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

        # Filter - th - Threshold
        try :
            if not th :
                self.flt_th = False
            elif np.ndim(th) == 0 :
                # only one number, so min of all extrema
                self.flt_th = [
                    [th, np.Inf],
                    [th, np.Inf]]
            elif np.ndim(th) == 1:
                # min and max of all extrema
                self.flt_th = [
                    [th[0], th[1]],
                    [th[0], th[1]]]
            elif np.ndim(th) == 2:
                # min and max of each type extrema
                self.flt_th = [
                    [th[0][0], th[0][1]],
                    [th[0][1], th[1][1]]]
        except:
            self.flt_th = False
            print("Threshold dimension error!")
        
        # logs
        self.log_flt_pd = []
        self.log_flt_ph = []
        self.log_rs = [[],[]]
        self.log_std=[[],[]]
        
        self.loop_count=0
        
        #if measureTime :
            ##import time
            #time = __import__('time')
            #print('hi',time.monotonic())
        
        if len(self.data) >= 3 :
            self.analyse()
    
    def analyse(self, n=0):
        """ Peak detect function. only call from class members.

        Args:
            n   - Start scan location of .data .
        """
        
        if self.measureTime :
            self.analyseTime = time.monotonic()
        if self.adp :
            self.flt_ph = 1
            self.log_flt_pd = []
            self.log_flt_ph = []

        #if self.preExtr['i'] == 0 :     # && self.tmpLocal.max.v.length == 0
            #self.preExtr['v'] = self.data[0]  # tmp_local_max
            #self.preExtr['i'] = 0        # tmp_local_max

            #self.blkExtr['v'] = self.data[0]  # block_local_max
            #self.blkExtr['i'] = 0        # block_local_max
        preExtr = { 'i': 0, 'v': 0}
        blkExtr = { 'i': 0, 'v': 0}
            
        # Determine first is max or min
        dataBlock = self.data[0:self.flt_pd]  # should check boundary in other language.
        find_max = True if np.argmax(dataBlock) > np.argmin(dataBlock) else False
        
        
        
        lastExtr = {'min': 0, 'max' : 0}
        
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
                dataBlock = self.data[n: n + self.flt_pd ]

            self.log_std[0].append(n)
            self.log_std[1].append(np.std(self.data[n: n +10]))
            
            # Get extrema
            blkExtr['i'] = np.argmax(dataBlock) if find_max else np.argmin(dataBlock)
            blkExtr['v'] = dataBlock[blkExtr['i']]

            # Compare last block, move on or save extrema then find opposite extrema.
            if (blkExtr['v'] >= preExtr['v'] if find_max else
                blkExtr['v'] <= preExtr['v'] ):
                preExtr['i'] = blkExtr['i'] + n
                preExtr['v'] = blkExtr['v']
                n += self.flt_pd
            elif preExtr['i'] - lastExtr['max' if find_max else 'min'] < self.flt_pd :
                # If extrema near last opposite extrema may case two opposite
                # extrema short then min distance (flt_pd), so check it.
                preExtr['i'] = blkExtr['i'] + n
                preExtr['v'] = blkExtr['v']
                n += self.flt_pd
            else :
                self.extr['max' if find_max else 'min'].append(preExtr['i'])
                n = preExtr['i']
                lastExtr['max' if find_max else 'min'] = preExtr['i']

                #if loop_count > 5000 :
                    #break
                
                if self.adp :
                    self.adaptive(find_max,n)
                    
                find_max = not find_max
        # while data seq
        #self.extr['max' if find_max else 'min'].append(preExtr['i'])

        
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
        if self.flt_th :
            # flt_th should be 2D array: [[min_low,min_up], [min_low,min_up]] .
            for extrType in range(2) :
                extrTypeStr = 'max' if extrType else 'min'
                extr = np.array(self.extr[extrTypeStr])
                extr_rm = np.array(self.extr_rm[extrTypeStr],
                    np.int32)
                extrData = np.array( self.data[extr] )
                th_extr_rm = extr[ np.flatnonzero( np.logical_or(
                    extrData < self.flt_th[extrType][0],
                    extrData > self.flt_th[extrType][1])
                )]
                self.extr_rm[extrTypeStr] = (
                    np.unique(np.concatenate((extr_rm,th_extr_rm)))  )
            
        # the last line of analyse(), record used time
        if self.measureTime :
            self.analyseTime = time.monotonic() - self.analyseTime

    def adaptive(self, find_max,n) :
        """ adapt pd, ph ,etc. """
        
        return # didn't finish
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
        """ Renew data and call analyse. """
        
        # check data type
        if len(data) > 0 :
            self.data = np.array(data)
            self.analyse()
            
    def append(self, data) :
        """ Append new data to original data.

        This method didn't finish, so disibled.
        """
        if len(data) > 0 :
            pass

    def clear(self) :
        """ clear data in object.

        Actually, it's reinitialize object to default setting,
        include .data and filters.
        """
        self.__init__()

    def get(self, act='max.v') :
        """ Get peak detection result.

        Arg :       A string. Vaild string please check code or manual.
        Return :    1D numpy array. Content depend on arg.
        """

        case = {
            'orig.max.i' : lambda : self.extr['max'] ,
            'orig.min.i' : lambda : self.extr['min'] ,
            'rm.max.i'   : lambda : self.extr_rm['max'] ,
            'rm.max.v'   : lambda : self.data[self.extr_rm['max']] ,
            'rm.min.i'   : lambda : self.extr_rm['min'] ,
            'rm.min.v'   : lambda : self.data[self.extr_rm['min']] ,
            'max.i'      : lambda : np.setdiff1d(self.extr['max'], self.extr_rm['max']),
            'max.v'      : lambda : self.data[np.setdiff1d(self.extr['max'], self.extr_rm['max'])],
            'min.i'      : lambda : np.setdiff1d(self.extr['min'], self.extr_rm['min']),
            'min.v'      : lambda : self.data[np.setdiff1d(self.extr['min'], self.extr_rm['min'])]
            }
        return case.get(act, lambda : [])()

    # i,v == max.i , max.v
    @property
    def i(self) :
        return np.setdiff1d(self.extr['max'], self.extr_rm['max'])
    @property
    def v(self) :
        return self.data[np.setdiff1d(self.extr['max'], self.extr_rm['max'])]

    # max i,v
    @property
    def max_i(self) :
        return np.setdiff1d(self.extr['max'], self.extr_rm['max'])
    @property
    def max_v(self) :
        return self.data[np.setdiff1d(self.extr['max'], self.extr_rm['max'])]

    # min i,v
    @property
    def min_i(self) :
        return np.setdiff1d(self.extr['min'], self.extr_rm['min'])
    @property
    def min_v(self) :
        return self.data[np.setdiff1d(self.extr['min'], self.extr_rm['min'])]

    # orig i for min, max
    @property
    def orig_max_i(self) :
        return self.extr['max']
    @property
    def orig_min_i(self) :
        return self.extr['min']

    # rm_max i,v
    @property
    def rm_max_i(self) :
        return self.extr_rm['max']
    @property
    def rm_max_v(self) :
        return self.data[self.extr_rm['max']]

    # rm_min i,v
    @property
    def rm_min_i(self) :
        return self.extr_rm['min']
    @property
    def rm_min_v(self) :
        return self.data[self.extr_rm['min']]

    