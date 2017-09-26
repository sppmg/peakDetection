# Peak Detection

This is a peak detection program base on very simply but effective algorithm, only use maximum and minimum no any signal decomposition or transform, but you can do it by yourself.

The program write by python3, will port to other language if I have time :D .

## Example

When you use this program, you should specify two condition peak distance and
relative height of peak, detail in the wiki or document in project.

In all demos, blue line is data curve, red plus is local maximum,
green plus is local minimum, black triangle_up is removed max point by filter
and black triangle_down is removed min point (I don't show black triangles in here).

First use my data to demo. It's similar harmonic with a small 60 Hz power noise.

```py
p = PeakDetector(d1[1], pd = 100)
```
![d1](doc/img/d1_pd=100_ph=0.3.png)

It's can easy get small peak in left part.

![d1](doc/img/d1_pd=1000_ph=0.05.png)

![d1](doc/img/d1_pd=1000_ph=0.05_1.png)

2nd example use a little sharp wave.
It's an audio signal from MATLAB's mtlb(1001:1200).
MATLAB's findpeaks result in [findpeaks help page](https://www.mathworks.com/help/signal/ref/findpeaks.html#bufhyo1-2).

And my result:

![d2](doc/img/d2_pd=10_ph=2.png)

3rd and 4th example use a very sharp wave, ECG.

![d5](doc/img/d5_pd=5_ph=200.png)

4th is an arrhythmic ECG from MIT-BIH Arrhythmia Database. It's has nonstationary meaning, that's why I create this program.

![d6](doc/img/d6_pd=5_ph=250.png)

MATLAB use it to demo [how to use wavelet analyze ECG]
(https://www.mathworks.com/help/wavelet/ug/r-wave-detection-in-the-ecg.html)


## License

I use MIT license, free and no warranty, please use careful.

It you think it's nice, save your time. please share to another 3 guys.



