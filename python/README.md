# Peak Detector manual for python

## Requirement

* Python 3 ( Did not test in Python 2)
* numpy


## Usage

import:

```py
from PeakDetector import PeakDetector
```

It will return a object.

```py
peaks = PeakDetector(data, option = value)
```

* data
  * It can ignore, so add data later.
  * It must more then 3 elements.
  * It must be a one dimension list or array (It's will convert to numpy.narray).
* option
  * key = value format, see below table.

  

| Action                  | Key | Vaild format                       | Example              | Note           |
|-------------------------|-----|------------------------------------|----------------------|----------------|
| Distance of peak        | pd  | num                                | pd = 3               | pd >= 1        |
| Relative height of peak | ph  | all_low                            | ph = 2               | single num > 0 |
|                         | ph  | [all_low all_up]                   | ph = [-1, 1]         |                |
| Threshold               | th  | all_low                            | th = 3               |                |
|                         | th  | [all_low all_up]                   | th = [-1, 1]         |                |
|                         | th  | [[min_low,min_up][min_low,min_up]] | th = [[-3,-2],[3,4]] |                |


# to be continued
