import mesa
import random

from sklearn import tree

from .State import State

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
        virus,
        ports,
    ):
        super().__init__(unique_id, model)

        self.state = initial_state
        self.check_frequency_antivirus = check_frequency_antivirus
        self.recovery_chance = recovery_chance
        self.gain_resistance_chance = gain_resistance_chance
        self.range_age = computer_ages
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
            if self.random.random() < self.virus.virus_spread_chance:
                a.state = State.INFECTED
                a.state = self.virus
                
        antivirus_neighbors = [
            agent
            for agent in self.model.grid.get_cell_list_contents(neighbors_nodes)
            if agent.state is State.RESISTANT
        ]
        
        for a in antivirus_neighbors:
            if a.ports == self.ports:
                a.state = State.SUSCEPTIBLE
                self.ports=random.randint(0,50)
            else: 
                self.ports=random.randint(0,50)
        

    def try_gain_resistance(self):
        if self.random.random() < self.gain_resistance_chance:
            self.state = State.RESISTANT
            # self.virus.state = 

    def try_remove_infection(self):
        # Try to remove
        # Recovery chance puede ser que tan viejo es el equipo.
        if self.random.random() < self.recovery_chance:
            # Success
            self.state = State.SUSCEPTIBLE
            self.try_gain_resistance()
        else:
            # Failed
            self.state = State.INFECTED

    def try_check_situation(self):
        #Si ya paso un cierto tiempo intenta remover el virus
        if self.random.random() < self.check_frequency_antivirus:
            # Checking...
            if self.state is State.INFECTED:
                self.try_remove_infection()
        #Cuando pasa cierto tiempo el antivirus se desactualiza y vuelve a ser vulnerable        
        if self.state is State.RESISTANT:
            if self.random.random() < self.check_frequency_antivirus:
                self.state = State.SUSCEPTIBLE

    def step(self):
        if self.state is State.INFECTED:
            self.try_to_infect_neighbors()
        self.try_check_situation()