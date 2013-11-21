class Virtual(object):
    def __init__(self, trigbox = None, mychan = 2, V2mA = 1.0):
        """
        This is a simple interface to a virtual stimulator.
        It is meant to mimic the MagstimInterface thus the same properties
        and methods must be exposed.
        We may want to also set the channel and width of the TTL but those
        must be accessed through stim_instance.trigbox
        If I weren't so lazy I would turn this into a DS5 ctypes interface
        Methods:
            stim_instance.trigger()
                Sends a trigger through trigbox.
                If this is instantiated without a trigbox, it uses Caio by default.
                
        Properties:
            stim_instance.stim_intensity
                Set the stimulator intensity. Units are in V
            stim_instance.stim_ready = True
                Always true since there is no way to know if it is not ready.
        """
        if not trigbox:
            from Caio import TriggerBox
            trigbox = TriggerBox.TTL()
        self.trigbox = trigbox
        self.my_chan = mychan-1 #Base 0.
        self.V2mA = float(V2mA) #5.0 = 10V:50mA
        self.intensity = 0
        
    def _get_stimi(self):
        return self.trigbox._attributes[self.my_chan]['amplitude'] * self.V2mA
    def _set_stimi(self, mamps): #Passed in intensity is mA
        vamps = float(mamps) / self.V2mA #Convert to DIO V
        vamps = min(vamps, 10.0) #Can't output more than 10.0 V
        #vamps = max([vamps, 0.05]) #Digitimer has a minimum V before it triggers, around 50mV
        self.trigbox._attributes[self.my_chan]['amplitude'] = vamps
        self.trigbox.set_TTL()
    intensity = property(_get_stimi, _set_stimi)
    
    def _get_stim_ready(self): return True
    def _set_stim_ready(self): pass #Always True
    ready = property(_get_stim_ready, _set_stim_ready)
    
    def trigger(self):
        self.trigbox.trigger()