import mesa
import random
import numpy as np
from .State import State
from .VirusAgent import VirusAgent

class ComputerAgent(mesa.Agent): # Crea las especificaciones del virus
    def __init__(
        self,
        unique_id,
        model,
        initial_state,
        check_frequency_antivirus,
        recovery_chance,
        gain_resistance_chance,
        computer_ages,
        memory,
        virus,
        ports,
    ):
        super().__init__(unique_id, model)

        self.state = initial_state
        self.check_frequency_antivirus = check_frequency_antivirus
        self.recovery_chance = recovery_chance
        self.gain_resistance_chance = gain_resistance_chance
        self.age = computer_ages
        self.memory = memory
        self.virus = virus
        self.ports = ports

    def try_to_infect_neighbors(self):
        neighbors_nodes = self.model.grid.get_neighbors(self.pos, include_center=False)
        susceptible_neighbors = [
            agent
            for agent in self.model.grid.get_cell_list_contents(neighbors_nodes)
            if agent.state is State.SUSCEPTIBLE
        ]
        
        for a in susceptible_neighbors:
            if self.recovery_chance< self.virus.virus_spread_chance:
                if(self.check_frequency_antivirus > self.virus.virus_spread_chance):
                    a.state = State.INFECTED
                    a.virus = self.virus
                else:
                    a.state = State.RESISTANT
                    a.virus = VirusAgent( #if is resistant, add a dead virus
                        a.unique_id,
                        self.model,
                        State.DEAD,
                        0,
                        0,
                        0,
                        a.ports,
                    ) 
                            
        antivirus_neighbors = [
            agent
            for agent in self.model.grid.get_cell_list_contents(neighbors_nodes)
            if agent.state is State.RESISTANT
        ]
        
        for a in antivirus_neighbors:
            if self.random.random() < a.recovery_chance:
                a.state = State.SUSCEPTIBLE
        

    def try_gain_resistance(self):
        ratio = 0.6
        if(self.state == State.INFECTED):
            VirusState = self.virus.state;
            if(VirusState == State.WEAK):
                ratio = self.gain_resistance_chance * 0.3
            elif(VirusState == State.REGULAR):
                ratio = self.gain_resistance_chance * 0.6
            elif(VirusState == State.MODERATE):
                ratio = self.gain_resistance_chance * 0.9
            elif(VirusState == State.MORTAL):
                ratio = self.gain_resistance_chance * 1.2
        self.recovery_chance = ratio
        m = self.memory
        q,n = m.shape
        r = self.random.random()
        noceros = np.count_nonzero(self.memory)
        if  (r) < ratio:          
            v = m.flatten()
            size = (q * n)
            maxElement = int(noceros * ratio)
            while((maxElement != 0)):
                i = random.randint(0, size - 1)
                if(v[i] == 1):
                    v[i] = 0
                maxElement-=1
            self.memory = v.reshape(self.memory.shape)
        if(np.count_nonzero(self.memory) > int((q * n) * 0.25)):
            return State.RESISTANT
        else:
            return State.INFECTED
        
    def try_remove_infection(self):
        ratio_virus = 0.2
        if (self.age < 3):
            ratio_virus = self.virus.virus_spread_chance * 0.4
        elif (self.age < 6):
            ratio_virus = self.virus.virus_spread_chance * 0.8
        elif (self.age < 10):
            ratio_virus = self.virus.virus_spread_chance * 1.2
        
        chance = (ratio_virus - self.recovery_chance)
                
        if self.random.random() < chance:
            # Success
            self.state = self.try_gain_resistance()
        else:
            # Failed
            self.state = State.INFECTED

    def try_check_situation(self):
        if self.virus.virus_check_frequency < self.check_frequency_antivirus:
            # Checking...
            if self.state is State.INFECTED:
                self.try_remove_infection()
                
        if self.state is State.RESISTANT:
            if self.virus.virus_check_frequency < self.check_frequency_antivirus:
                self.state = State.SUSCEPTIBLE
    
    # my methods
    def check_dead_computer(self):
        q, n = self.memory.shape
        if(np.count_nonzero(self.memory) > int((q*n) * 0.75)):
            self.state = State.DEAD
            
    def step(self):
        if self.state is State.INFECTED:
            self.try_to_infect_neighbors()
            self.virus.try_to_infect_computer(self)
            self.check_dead_computer()
            self.try_check_situation()
        if self.state is State.SUSCEPTIBLE:
            self.try_gain_resistance()
            if(self.random.random() > self.recovery_chance ):
                self.state = State.RESISTANT
