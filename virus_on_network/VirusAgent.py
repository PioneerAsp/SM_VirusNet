import mesa
import random
import numpy as np
from .State import State

class VirusAgent(mesa.Agent): # Crea las especificaciones del virus
    def __init__(
        self,
        unique_id,
        model,
        initial_state,
        virus_spread_chance,
        virus_check_frequency,
        gain_resistance_chance,
        ports,
    ):
        super().__init__(unique_id, model)

        self.state = initial_state
        self.virus_spread_chance = virus_spread_chance
        self.virus_check_frequency = virus_check_frequency
        self.gain_resistance_chance = gain_resistance_chance
        self.ports = ports
        
    def try_to_infect_computer(self, computer): #Intenta infectar la computador
        ratio_virus = 0.2
        if (computer.age < 3):
            ratio_virus = self.virus_spread_chance * 0.4
        elif (computer.age < 6):
            ratio_virus = self.virus_spread_chance * 0.8
        elif (computer.age < 10):
            ratio_virus = self.virus_spread_chance * 1.2
        
        b = self.virus_spread_chance * ratio_virus
        self.virus_spread_chance = b
        self.try_increse_size(computer, b)
        self.update_state(computer.memory)

    def update_state(self, memory):
        q,n = memory.shape
        size = int((q * n))
        if((size*0.25) < np.count_nonzero(memory)):
            self.state = State.WEAK
        elif((size*0.5) < np.count_nonzero(memory)):
            self.state = State.REGULAR
        elif((size*0.75) < np.count_nonzero(memory)):
            self.state = State.MODERATE
        elif ((size) < np.count_nonzero(memory)):
            self.state = State.MORTAL
    
    def try_increse_size(self, computer, b): #Incrementa su peso para abarcar mas
        q, n = computer.memory.shape
        m = computer.memory.flatten();
        size = q*n;

        VirusState = self.state;
        if(VirusState == State.WEAK):
            ones = int(size * 0.01 + b)
        elif(VirusState == State.REGULAR):
            ones = int(size * 0.10 + b)
        elif(VirusState == State.MODERATE):
            ones = int(size * 0.36 + b)
        elif(VirusState == State.MORTAL):
            ones = int(size * 0.51 + b)    
                
        while(ones != 0):
            i = random.randint(0, size - 1)
            if(m[i] != -1):
                m[i] = 1
            ones-=1
        computer.memory = m.reshape(computer.memory.shape)