from machine import Pin, ADC
import time

'''due to world record highest hr'''
MAX_HISTORY = 200

class HeartRate:
    def __init__(self,adc_pin):
        self.adc = ADC(Pin(adc_pin))
        self.adc.atten(ADC.ATTN_11DB) 
        self.History = []
        self.count = 0
        self.beat = True
        self.beat_time = 0
        self.last_beat_time = 0
        
    def get_hr(self):
        
        Signal = self.adc.read()
        self.History.append(Signal)
        self.History = self.History[-MAX_HISTORY:]
        
        maxx, minn = (0,0)
        if len(self.History) >= 5:
            self.History[len(self.History) - 3] = (self.History[len(self.History) - 5] + self.History[len(self.History) - 4] +
                                                   self.History[len(self.History) - 3] +
                                                   self.History[len(self.History) - 2] + self.History[len(self.History) - 1]) / 5
            maxx = max(self.History[0:len(self.History) - 3])
            minn = min(self.History[0:len(self.History) - 3])
        else:
            maxx = max(self.History)
            minn = min(self.History)
            
        Threshold_on = (maxx * 3 + minn) / 4
        Threshold_off = (maxx + minn) / 2
        
        if (len(self.History) >= 5):
        
            if ((self.History[len(self.History) - 3] > Threshold_on) and (self.beat == False)):
                self.beat = True
                if self.count == 0:
                    self.beat_time = time.ticks_ms()
                self.count += 1
                if self.count == 6:
                    self.last_beat_time = time.ticks_ms()
                    self.count = 0

                #HR = 60000 / (beat_time - self.last_beat_time);
                    HR = (5 / (self.last_beat_time - self.beat_time)) * 60000
                    return int(HR)
            
            if ((self.History[len(self.History) - 3] < Threshold_off) and (self.beat == True)):
                self.beat = False
              
            '''
            if ((self.History[len(self.History) - 3] >= Threshold_off) and
                (self.History[len(self.History) - 3] <= Threshold_on) and
                (len(self.History) >= 10)):
                count = 0
                for k in range(1, 8):
                    if self.History[len(self.History) - 3 - k] <= Threshold_off: count += 1
                if count >= 5:
                    if self.beat == False:
                        self.beat = True
                        beat_time = time.ticks_ms()
                        HR = 60000 / (beat_time - self.last_beat_time);
                        self.last_beat_time = beat_time
                        return int(HR)
                '''
    



