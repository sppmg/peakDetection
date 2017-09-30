import numpy as np
import matplotlib.pyplot as plt
import h5py
from PeakDetector import PeakDetector

### Read data .
# There are few test date. .mat has a variable named 'd',
# it's 2D array, time and value.
# hdf5 variable is 'd/value' , a 1D array.
###

file = '../data/md_1.mat'  # ph = 0.05 , pd = 1000
f = h5py.File(file,'r')
d01 = np.array( f.get(list(f.keys() )[0]) ) # data in d[1]
f.close()

file = '../data/matlab_mtlb_1001_1200.mat' # ph = 2, pd = 10
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

file = '../data/MIT-BIH-203_MLII_0s-30s.hdf5' # ph = 200 , pd = 5
f = h5py.File(file,'r')
d06 = np.array( f.get('d/value') ) 
f.close()


file = '../data/matlab_saturatedData.mat' # ph = 2, pd = 40
f = h5py.File(file,'r')
d07 = [[],np.array( f.get(list(f.keys() )[0]))[0]]
f.close()

# ------ Finish read data ---------

# Set variables for title of figure
dataname = 'd1'     # It's only for title of figure.
demo_pd = 1000
demo_ph = 0.05
demo_th = [[-1,-0.5],[-1,0.6]]
show_rm = False     # True / False

peaks = PeakDetector(d01[1], pd = demo_pd, ph = demo_ph, th = demo_th)

print('peak (max) numbers = ', len(peaks.orig_max_i))
print('removed number (min,max) = ', (len(peaks.rm_min_i) , len(peaks.rm_max_i) ) )
print('consume time = ', peaks.analyseTime)


# Plot peaks information .
fig = plt.figure()
plt.hold(True)

plt.title('data = '+ dataname +
    ', pd = ' + str(demo_pd)+
    ', ph = ' + str(demo_ph)+
    ', th = ' + str(demo_th))
    
plt.plot(peaks.data)
plt.plot(peaks.max_i, peaks.max_v,'+r',mew=2, ms=10)
plt.plot(peaks.min_i, peaks.min_v,'+g',mew=2, ms=10)
if show_rm :
    plt.plot(peaks.rm_max_i, peaks.rm_max_v,'^k',ms=5)
    plt.plot(peaks.rm_min_i, peaks.rm_min_v,'vk',ms=5)

plt.show()

print('Before clear, data lenght = :', len(peaks.data))
peaks.clear()
print('After clear, data lenght = :', len(peaks.data))
