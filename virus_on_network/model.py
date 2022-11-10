import math
import networkx as nx
import random
import mesa

from .State import State
from .ComputerAgent import ComputerAgent

def number_state(model, state):
    return sum(1 for a in model.grid.get_all_cell_contents() if a.state is state)

def number_infected(model):
    return number_state(model, State.INFECTED)

def number_susceptible(model):
    return number_state(model, State.SUSCEPTIBLE)

def number_resistant(model):
    return number_state(model, State.RESISTANT)

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
            a = ComputerAgent(
                i,
                self,
                State.SUSCEPTIBLE,
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
            a.state= State.INFECTED
            
        # Resistant some nodes
        antivirus_nodes = self.random.sample(list(self.G), self.initial_antivirus_size)
        for a in self.grid.get_cell_list_contents(antivirus_nodes):
            a.state = State.RESISTANT

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
        self.schedule.step()
        # collect data
        self.datacollector.collect(self)

    def run_model(self, n):
        for i in range(n):
            self.step()