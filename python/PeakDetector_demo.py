import numpy as np
import matplotlib.pyplot as plt
import h5py
from PeakDetector import PeakDetector

####

file = '../data/md_1.mat'  # mph_r = 0.01, mpd = 100/55  mpd = int(len(d[1])/100) , ph = 0.05 , pd = 1000 (連前面都找到)
f = h5py.File(file,'r')
d01 = np.array( f.get(list(f.keys() )[0]) ) # data in d[1]
f.close()

file = '../data/matlab_mtlb_1001_1200.mat' # mph_r = 2, mpd = 10 
f = h5py.File(file,'r')
d02 = np.array( f.get(list(f.keys() )[0]) )
f.close()

# ph = 0 , pd = 2
d03 = [[],np.array([0, 6, 25, 20, 15, 8, 15, 6, 0, 6, 0, -5, -15, -3, 4, 10, 8, 13, 8, 10, 3, 1, 20, 7, 3, 0 ])]

d04 = [[],np.array([1, 1, 1.1, 1, 0.9, 1, 1, 1.1, 1, 0.9, 1, 1.1, 1, 1, 0.9, 1, 1, 1.1, 1, 1, 1, 1, 1.1, 0.9, 1, 1.1, 1, 1, 0.9, 1, 1.1, 1, 1, 1.1, 1, 0.8, 0.9, 1, 1.2, 0.9, 1, 1, 1.1, 1.2, 1, 1.5, 1, 3, 2, 5, 3, 2, 1, 1, 1, 0.9, 1, 1, 3, 2.6, 4, 3, 3.2, 2, 1, 1, 0.8, 4, 4, 2, 2.5, 1, 1, 1])]


file = '../data/MIT-BIH-200_MLII_0s-30s.hdf5' # ph = 2, pd = 10
f = h5py.File(file,'r')
d05 = np.array( f.get('d/value') ) # ph = 200 , pd = 5
f.close()

file = '../data/MIT-BIH-203_MLII_0s-30s.hdf5' # ph = 2, pd = 10
f = h5py.File(file,'r')
d06 = np.array( f.get('d/value') ) # ph = 200 , pd = 5
f.close()


file = '../data/matlab_saturatedData.mat' # ph = 2, pd = 40
f = h5py.File(file,'r')
d07 = [[],np.array( f.get(list(f.keys() )[0]))[0]]
f.close()

####

dataname = 'd7'
demo_pd = 2
demo_ph = 40
show_rm = False

fp = PeakDetector(d07[1], pd = demo_pd, ph = demo_ph)
print('peak (max) numbers = ', len(fp.extr['max']))
print('removed number (min,max) = ', (len(fp.get('rm.min')) , len(fp.get('rm.max')) ) )
print('used time = ', fp.analyseTime)

fig = plt.figure()
plt.hold(True)

# use time(d[0]) for x
#plt.plot(d[0],fp.data)
#plt.plot(d[0][fp.localMax],fp.data[fp.localMax],'+r',markersize=15)
#plt.plot(d[0][fp.localMin],fp.data[fp.localMin],'+g',markersize=15)

# use id for x
#plt.plot(fp.data)
#plt.plot(fp.localMax,fp.data[fp.localMax],'+r',markersize=15)
#plt.plot(fp.localMin,fp.data[fp.localMin],'+g',markersize=15)
#plt.plot(fp.localMin_rm,fp.data[fp.localMin_rm],'^k',markersize=5)

# use get() api
#print(fp.get('orig.max.i'))
#print(fp.get('max.v'))
#plt.subplot('311')
plt.title('data = '+ dataname +', pd = ' + str(demo_pd)+', ph = '+str(demo_ph))
plt.plot(fp.data)
plt.plot(fp.get('max.i'),fp.get('max.v'),'+r',mew=2, ms=10)
plt.plot(fp.get('min.i'),fp.get('min.v'),'+g',mew=2, ms=10)
if show_rm :
    plt.plot(fp.get('rm.max'),fp.data[fp.get('rm.max')],'^k',ms=5)
    plt.plot(fp.get('rm.min'),fp.data[fp.get('rm.min')],'vk',ms=5)

#plt.show()
if len(fp.log_flt_ph) > 0 :
    plt.subplot('312')
    plt.plot(fp.log_rs[0],fp.log_rs[1] ) # np.log((1/fp.rs_log[1])))
    plt.subplot('313')
    plt.plot(fp.log_flt_pd)
plt.show()


#fp.clear()
#print('after clear, data lenght = :', len(fp.data))

#print('len = ',len(fp.localMax_rm))
#tmp=[]
#for n in range(1,len(fp.localMax_rm)) :
    ##print(fp.localMax_rm[n-1])
    #tmp.append(fp.localMax_rm[n] - fp.localMax_rm[n-1])
#tmp.sort()
#print(tmp)
