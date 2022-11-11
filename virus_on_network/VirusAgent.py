import mesa
from sklearn import tree
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
        
        def try_to_infect_computer(self): #Intenta infectar la computadora
            return

        def try_increse_size(self): #Incrementa su peso para abarcar mas
            return
        
        def try_check_situation(self): #Verifica su situacion
            return
        
        def try_sneaking(self): #Tratata de ocultarse
            return

        def step(self):
            if self.state is State.INFECTED:
                self.try_to_infect_neighbors()
            self.try_check_situation()
        
        def try_evolution_virus(self): #trata de evolucionar
            return
