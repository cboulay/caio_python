#Python interface for CONTEC AIO-160802AY-USB

I still have a lot of work to do on this to make it useful to others. Right now all it can do is send out a simple 50 ms TTL.

## Instructions

Thus far I am only using this to send out TTLs. I may modify it to send more complicated waveforms. I doubt I will ever use it for AD.

```python
import CaioStim
mytrigbox=CaioStim.TriggerBox()
mytrigbox.trigger()
```

## Other information

Used by my [magstim module](https://github.com/cboulay/magstim-python).