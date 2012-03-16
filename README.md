#Python interface for CONTEC AIO-160802AY-USB

I still have a lot of work to do on this to make it useful to others. Right now all it can do is send out a simple 50 ms TTL. Only works in windows but shouldn't be too difficult to modify to load the linux library instead.

## Instructions

The Contec driver must be installed.

```python
import CaioStim
mytrigbox=CaioStim.TriggerBox()
mytrigbox.trigger()
```

## Other information

Used by my [magstim module](https://github.com/cboulay/magstim-python).

In the help file see "Analog Input and Output Driver>Reference"