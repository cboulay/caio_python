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
```

My [magstim module](https://github.com/cboulay/magstim-python) is triggered via this triggerbox.
I also use a Digitimer DS5 but it is considerably simpler than the Magstim device so I have
created a VirtualStimulatorInterface (included in this package) that can be used in place of the Magstim interface.
This VirtualStimulatorInterface, like the Magstim interface, has a method trigger() which is
simply a proxy to self.trigbox.trigger()

```python
from Caio.VirtualStimulatorInterface import Virtual
stimulator=Virtual(trigbox=trigbox)
stimulator.trigger()
```

## Other information

Used by my [magstim module](https://github.com/cboulay/magstim-python).

In the help file see "Analog Input and Output Driver>Reference"