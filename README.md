#Python interface for CONTEC AIO-160802AY-USB

Only analog output implemented thus far. Pass a numpy array (samples by channels) to the buffer.

Only works in windows but shouldn't be too difficult to modify to load the linux library instead.

## Instructions

The Contec driver must be installed.

```python
from Caio.TriggerBox import TTL
trigbox=TTL()
trigbox._caio.fs=10000
trigbox.set_TTL(width=1, channel=2)
trigbox.trigger()

#This is to create an artificial stimulator device with an interface similar to the Magstim interface
from Caio.VirtualStimulatorInterface import Virtual
stimulator=Virtual(trigbox=trigbox)
stimulator.trigger() #this is just a proxy for self.trigbox.trigger()

```

## Other information

Used by my [magstim module](https://github.com/cboulay/magstim-python).

In the help file see "Analog Input and Output Driver>Reference"