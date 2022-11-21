import math
import networkx as nx
import random
import mesa
import numpy as np

from .State import State
from .ComputerAgent import ComputerAgent
from .VirusAgent import VirusAgent

MEMORY_SIZE = 512
DIR_SIZE = 8

def number_state(model, state):
    return sum(1 for a in model.grid.get_all_cell_contents() if a.state is state)

def number_infected(model):
    return number_state(model, State.INFECTED)

def number_susceptible(model):
    return number_state(model, State.SUSCEPTIBLE)

def number_resistant(model):
    return number_state(model, State.RESISTANT)

def number_dead(model):
   return number_state(model, State.DEAD)

class VirusOnNetwork(mesa.Model):
    def __init__(
        self,
        num_nodes = 10,
        avg_node_degree = 3, #número máximo de conexiones
        initial_outbreak_size = 1, #Agentes contaminados en un inicio
        initial_antivirus_size = 1, #Agentes con antivirus en un inicio
        virus_spread_chance = 1.0,  #Suceptibilidad de los vecinos al virus
        virus_check_frequency = 0.3, #La probabilidad de que detecte su estado
        check_frequency_antivirus = 0.2, #Probabilidad de que se desactualice el antivirus
        recovery_chance = 0.3, #Probabilidad de que se recupere
        gain_resistance_chance_virus = 1, #Ganancia de resistencia al virus (antivirus)
        gain_resistance_chance_computer = 1, #Ganancia de resistencia al virus (antivirus)
        ports = random.randint(0, 50),
        computer_age = 2.5,
        initial_dead_computer = 3,
    ):

        #model parameters
        self.num_nodes = num_nodes
        prob = avg_node_degree / self.num_nodes
        self.G = nx.erdos_renyi_graph(n=self.num_nodes, p=prob)
        self.grid = mesa.space.NetworkGrid(self.G)
        self.schedule = mesa.time.RandomActivation(self)
        self.initial_dead_computer = initial_dead_computer
        self.ports = ports

        #virus parameters
        self.virus_spread_chance = virus_spread_chance
        self.virus_check_frequency = virus_check_frequency
        self.gain_resistance_chance_virus = gain_resistance_chance_virus
        self.initial_outbreak_size = (
            initial_outbreak_size if initial_outbreak_size <= num_nodes else num_nodes
        )
        
        #computer parameters
        self.check_frequency_antivirus = check_frequency_antivirus
        self.recovery_chance = recovery_chance
        self.gain_resistance_chance_computer = gain_resistance_chance_computer
        self.computer_age = computer_age
        self.initial_antivirus_size = (
            initial_antivirus_size if initial_antivirus_size <= num_nodes else num_nodes
        )
        
        #data collector computer state
        self.datacollector = mesa.DataCollector(
            {
                "Infected": number_infected,
                "Susceptible": number_susceptible,
                "Resistant": number_resistant,
                "Dead": number_dead,
            }
        )

        # Create agents
        for i, node in enumerate(self.G.nodes()):
            random.seed()
            a = ComputerAgent(  #paramter computer agent
                i,
                self,
                State.SUSCEPTIBLE,
                self.check_frequency_antivirus,
                self.recovery_chance,
                self.gain_resistance_chance_computer,
                random.randint(0, self.computer_age),
                np.zeros((MEMORY_SIZE, DIR_SIZE)),
                0,  #without virus 
                self.ports,
            )
            self.schedule.add(a)
            # Add the agent to the nodem
            self.grid.place_agent(a, node)

        # Infect some nodes
        infected_nodes = self.random.sample(list(self.G), self.initial_outbreak_size)
        i = 0
        for a in self.grid.get_cell_list_contents(infected_nodes):
            v = VirusAgent(     #Create virus agent
                a.unique_id,
                self,
                State.WEAK,     #start in state more low 
                self.virus_spread_chance,
                self.virus_check_frequency,
                self.gain_resistance_chance_virus,
                a.ports,
            )
            random.seed()
            a.state = State.INFECTED                        # If node is infected, add a virus
            a.memory = np.zeros((MEMORY_SIZE, DIR_SIZE))    # Initial state of memory
            
            m = a.memory.flatten()                          # For easy implementation
            for i in range((m.shape[0])):                   # Complete with random
                if(random.randint(0,10) == 5):
                    m[i] = random.randint(0,1)
            a.memory = m.reshape(a.memory.shape)            # Reshape update
            
            q,n = a.memory.shape
            if(int((q * n)*0.25) < np.count_nonzero(a.memory)):
                v.state = State.REGULAR
            elif(int((q * n)*0.5) < np.count_nonzero(a.memory)):
                v.state = State.REGULAR
            elif (int((q * n)*0.75) < np.count_nonzero(a.memory)):
                v.state = State.MODERATE
            elif (int((q * n)) < np.count_nonzero(a.memory)):
                v.state = State.MORTAL
            a.virus = v
            i+=1
            
        # Resistant some nodes
        i = 0
        antivirus_nodes = self.random.sample(list(self.G), self.initial_antivirus_size)
        for a in self.grid.get_cell_list_contents(antivirus_nodes):
            a.state = State.RESISTANT
            a.virus = VirusAgent( #if is resistant, add a dead virus
                a.unique_id,
                self,
                State.DEAD,
                0,
                0,
                0,
                a.ports,
            ) 
            a.memory = (np.ones((MEMORY_SIZE, DIR_SIZE))*-1)
            i+=1
        # Dead some nodes
        dead_nodes = self.random.sample(list(self.G), self.initial_dead_computer)
        for a in self.grid.get_cell_list_contents(dead_nodes):
            a.state = State.DEAD # dead node
            a.memory = np.ones((MEMORY_SIZE, DIR_SIZE))
            
        self.running = True
        self.datacollector.collect(self)

    def resistant_susceptible_ratio(self):
        try:
            return number_state(self, State.RESISTANT) / number_state(
                self, State.SUSCEPTIBLE
            )
        except ZeroDivisionError:
            return math.inf

    def step(self):
        if (number_infected(self) == 0):
            self.running = False
        self.schedule.step()
        # collect data
        self.datacollector.collect(self)

    def run_model(self, n):
        while(number_infected(self) != 0):
            self.step()