#Python interface for CONTEC AIO-160802AY-USB

Only analog output implemented thus far. Pass a numpy array (samples by channels) to the buffer.

Only works in windows but shouldn't be too difficult to modify to load the linux library instead.

## Instructions

The Contec driver must be installed.

```python
from Caio import CaioStim
mytrigbox=CaioStim.TriggerBox()
mytrigbox.trigger()
```

## Other information

Used by my [magstim module](https://github.com/cboulay/magstim-python).

In the help file see "Analog Input and Output Driver>Reference"