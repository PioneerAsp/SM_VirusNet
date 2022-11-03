import math
from enum import Enum
import networkx as nx
import random
import mesa

from sklearn import tree


class StateAntiVirus(Enum):
    SUSCEPTIBLE = 0
    INFECTED = 1
    RESISTANT = 2
    #DEAD = 3

class StateVirus(Enum):
    SUSCEPTIBLE = 0
    INFECTED = 1
    RESISTANT = 2
    #DEAD = 3


def number_state(model, state):
    return sum(1 for a in model.grid.get_all_cell_contents() if a.state is state)

def number_infected(model):
    return number_state(model, StateVirus.INFECTED)

def number_susceptible(model):
    return number_state(model, StateVirus.SUSCEPTIBLE)

def number_resistant(model):
    return number_state(model, StateVirus.RESISTANT)

#def number_dead(model):
 #   return number_state(model, State.RESISTANT)

class VirusOnNetwork(mesa.Model):
    def __init__(
        self,
        num_nodes=10,
        avg_node_degree=3, #número máximo de conexiones
        initial_outbreak_size=1, #Agentes contaminados en un inicio
        initial_antivirus_size=1, #Agentes con antivirus en un inicio
        virus_spread_chance=0.2,  #Suceptibilidad de los vecinos al virus
        virus_check_frequency=0.3, #La probabilidad de que detecte su estado
        check_frequency_antivirus=0.2, #Probabilidad de que se desactualice el antivirus
        recovery_chance=0.3, #Probabilidad de que se recupere
        gain_resistance_chance=1, #Ganancia de resistencia al virus (antivirus)
        ports=random.randint(0, 50),
        #Variable para representar la antiguedad del equipo, en caso de ser atacado ->DEAD
    ):

        self.num_nodes = num_nodes
        prob = avg_node_degree / self.num_nodes
        self.G = nx.erdos_renyi_graph(n=self.num_nodes, p=prob)
        self.grid = mesa.space.NetworkGrid(self.G)
        self.schedule = mesa.time.RandomActivation(self)
        self.initial_outbreak_size = (
            initial_outbreak_size if initial_outbreak_size <= num_nodes else num_nodes
        )
        self.initial_antivirus_size = (
            initial_antivirus_size if initial_antivirus_size <= num_nodes else num_nodes
        )
        self.virus_spread_chance = virus_spread_chance
        self.virus_check_frequency = virus_check_frequency
        self.check_frequency_antivirus = check_frequency_antivirus
        self.recovery_chance = recovery_chance
        self.gain_resistance_chance = gain_resistance_chance
        self.ports = ports
        

        self.datacollector = mesa.DataCollector(
            {
                "Infected": number_infected,
                "Susceptible": number_susceptible,
                "Resistant": number_resistant,
                #"Dead": number_dead,
            }
        )

        # Create agents
        for i, node in enumerate(self.G.nodes()):
            a = VirusAgent(
                i,
                self,
                StateVirus.SUSCEPTIBLE,
                self.virus_spread_chance,
                self.virus_check_frequency,
                self.check_frequency_antivirus,
                self.recovery_chance,
                self.gain_resistance_chance,
                self.ports,
            )
            self.schedule.add(a)
            # Add the agent to the nodem
            self.grid.place_agent(a, node)

        # Infect some nodes
        infected_nodes = self.random.sample(list(self.G), self.initial_outbreak_size)
        for a in self.grid.get_cell_list_contents(infected_nodes):
            a.state= StateVirus.INFECTED
            
        # Resistant some nodes
        antivirus_nodes = self.random.sample(list(self.G), self.initial_antivirus_size)
        for a in self.grid.get_cell_list_contents(antivirus_nodes):
            a.state = StateVirus.RESISTANT

        self.running = True
        self.datacollector.collect(self)

    def resistant_susceptible_ratio(self):
        try:
            return number_state(self, StateVirus.RESISTANT) / number_state(
                self, StateVirus.SUSCEPTIBLE
            )
        except ZeroDivisionError:
            return math.inf

    def step(self):
        self.schedule.step()
        # collect data
        self.datacollector.collect(self)

    def run_model(self, n):
        for i in range(n):
            self.step()


class VirusAgent(mesa.Agent): # Crea las especificaciones del virus
    def __init__(
        self,
        unique_id,
        model,
        initial_state,
        virus_spread_chance,
        virus_check_frequency,
        check_frequency_antivirus,
        recovery_chance,
        gain_resistance_chance,
        ports,
    ):
        super().__init__(unique_id, model)

        self.state = initial_state
        self.virus_spread_chance = virus_spread_chance
        self.virus_check_frequency = virus_check_frequency
        self.check_frequency_antivirus=check_frequency_antivirus
        self.recovery_chance = recovery_chance
        self.gain_resistance_chance = gain_resistance_chance
        self.ports = ports

    def try_to_infect_neighbors(self):
        neighbors_nodes = self.model.grid.get_neighbors(self.pos, include_center=False)
        susceptible_neighbors = [
            agent
            for agent in self.model.grid.get_cell_list_contents(neighbors_nodes)
            if agent.state is StateVirus.SUSCEPTIBLE
        ]
        for a in susceptible_neighbors:
            if self.random.random() < self.virus_spread_chance:
                a.state = StateVirus.INFECTED
                
        #El virus intenta decifrar el puerto libre.
        antivirus_neighbors = [
            agent
            for agent in self.model.grid.get_cell_list_contents(neighbors_nodes)
            if agent.state is StateVirus.RESISTANT
        ]
        for a in antivirus_neighbors:
            if a.ports == self.ports:
                a.state = StateVirus.SUSCEPTIBLE
                self.ports=random.randint(0,50)
            else: 
                self.ports=random.randint(0,50)
        

    def try_gain_resistance(self):
        if self.random.random() < self.gain_resistance_chance:
            self.state = StateVirus.RESISTANT

    def try_remove_infection(self):
        # Try to remove
        # Recovery chance puede ser que tan viejo es el equipo.
        if self.random.random() < self.recovery_chance:
            # Success
            self.state = StateVirus.SUSCEPTIBLE
            self.try_gain_resistance()
        else:
            # Failed
            self.state = StateVirus.INFECTED

    def try_check_situation(self):
        #Si ya paso un cierto tiempo intenta remover el virus
        if self.random.random() < self.virus_check_frequency:
            # Checking...
            if self.state is StateVirus.INFECTED:
                self.try_remove_infection()
        #Cuando pasa cierto tiempo el antivirus se desactualiza y vuelve a ser vulnerable        
        if self.state is StateVirus.RESISTANT:
            if self.random.random() < self.check_frequency_antivirus:
                self.state = StateVirus.SUSCEPTIBLE

    def step(self):
        if self.state is StateVirus.INFECTED:
            self.try_to_infect_neighbors()
        self.try_check_situation()
    
    def try_evolution_virus(self):
        self.virus_check_frequency
        self.gain_resistance_chance
        self.recovery_chance
        self.virus_check_frequency
        self.virus_spread_chance
        
    def clasification_situation(self, X, y):
        clf = tree.DecisionTreeClassifier()
        clf = clf.fit(X, y)
        return clf

class AntivirusVirusAgent(mesa.Agent): # Crea las especificaciones del virus
    def __init__(
        self,
        unique_id,
        model,
        initial_state,
        virus_spread_chance,
        virus_check_frequency,
        check_frequency_antivirus,
        recovery_chance,
        gain_resistance_chance,
        ports,
    ):
        super().__init__(unique_id, model)

        self.state = initial_state
        self.virus_spread_chance = virus_spread_chance
        self.virus_check_frequency = virus_check_frequency
        self.check_frequency_antivirus=check_frequency_antivirus
        self.recovery_chance = recovery_chance
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
            if self.state is StateVirus.INFECTED:
                self.try_to_infect_neighbors()
            self.try_check_situation()
        
        def try_evolution_virus(self): #trata de evolucionar
            return
            
        def clasification_situation(self, X, y):
            clf = tree.DecisionTreeClassifier()
            clf = clf.fit(X, y)
            return clf