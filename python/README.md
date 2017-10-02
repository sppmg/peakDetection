# Peak Detector manual for python

## Requirement

* Python 3 ( Did not test in Python 2)
* numpy

## Install

Save `PeakDetector.py` to your search path of python.

The `PeakDetector_demo.py` just a demo, it will read demo data and plot result.

## Usage

### Example: get index of local maximum

```py
from PeakDetector import PeakDetector           # import PeakDetector
peaks = PeakDetector(data, pd = 100, ph = 0.1)  # get PeakDetector object and analyse
peaks.i                                         # get index of local maximum

# Plot data with local maximum marker.
import matplotlib.pyplot as plt
plt.hold(True)
plt.plot(peaks.data)
plt.plot(peaks.i, peaks.v,'+r',mew=2, ms=10)
plt.show()
```

Note: Peak will detect after input data immediately, not at `.get()` command.


### PeakDetector argument

```py
peaks = PeakDetector(data, option = value)
```
It will return a object. If you give data, the result will save in it's attributes.

* data
  * It can ignore, so add data later.
  * It must more then 3 elements.
  * It must be a one dimension list or array (It's will convert to numpy.narray).
* option
  * key = value format, see below table.
  * `Distance of peak` : Recommend less then 60% of peak distance or peak width.
    for sharp wave , use small value.
  * `Relative height of peak`: It's difference height of neighboring
    local maximum and local minimum. **It's differed with MATLAB's `MinPeakHeight`** .
  * `Threshold`: It's absolute height of peak, same as MATLAB's `MinPeakHeight`.
    If set a array(or list in python), it's means only in this range can output.
    2D array means separate set range of local maximum and local minimum.
  

| Action                  | Key | Vaild format                       | Example              | Note           |
|-------------------------|-----|------------------------------------|----------------------|----------------|
| Distance of peak        | pd  | all_low                            | pd = 3               | pd > 0        |
| Relative height of peak | ph  | all_low                            | ph = 2               | this style must ph > 0 |
|                         | ph  | [all_low all_up]                   | ph = [-1, 1]         |                |
| Threshold               | th  | all_low                            | th = 3               |                |
|                         | th  | [all_low all_up]                   | th = [-1, 1]         |                |
|                         | th  | [[min_low,min_up],[min_low,min_up]] | th = [[-3,-2],[3,4]] |                |


### Get result

Use dot syntax. For example, below will get local maximum location.

```py
peaks.i
```
Vaild attributes:

| Vaild attr. | Return                                            |
|-------------|---------------------------------------------------|
| .i          | Index of max with filter. (short for .max_i)      |
| .v          | Value of max with filter. (short for .max_v)      |
| .max_i      | Index of max with filter.                         |
| .max_v      | Value of max with filter.                         |
| .min_i      | Index of min with filter.                         |
| .min_v      | Value of min with filter.                         |
| .orig_max_i | Non-filter (but apply pd) index of original data. |
| .orig_max_v | Non-filter (but apply pd) value of original data. |
| .rm_max_i   | Filter index of original data for max.            |
| .rm_max_v   | Filter value of original data for max.            |
| .rm_min_i   | Filter index of original data for min.            |
| .rm_min_v   | Filter value of original data for min.            |


### Method list

| Method        | Describe                                                                   |
|---------------|----------------------------------------------------------------------------|
| .update(data) | Update data in PeakDetector object. It's will detect new data immediately. |
| .clear()      | Clear all information in the PeakDetector object.                          |


# Setting suggestion

If you see a clear local maximum but `PeakDetector` can't grab it, try to
decrease `pd`.

# Demo: threshold

## Without threshold

![d1 Without threshold](../doc/img/d01_pd=1000_ph=0.05.png)

## Minimum for max and min

![d1 with threshold](../doc/img/d01_pd=1000_ph=0.05_th_1.png)

## Range for max and min

![d1 with threshold](../doc/img/d01_pd=1000_ph=0.05_th_2.png)

## Separate Range for max and min

![d1 with threshold](../doc/img/d01_pd=1000_ph=0.05_th_3.png)