import math
import mesa
from .State import State
from .model import VirusOnNetwork, number_infected

def network_portrayal(G):
    # The model ensures there is always 1 agent per node

    def node_color(agent):
        return {State.INFECTED: "#BC2E0F", State.SUSCEPTIBLE: "#42F50E", State.DEAD : "#FFFFFFF"}.get(
            agent.state, "#3498DB"
        )

    def edge_color(agent1, agent2):
        if State.RESISTANT in (agent1.state, agent2.state):
            return "#3498DB"
        return "#000000"

    def edge_width(agent1, agent2):
        if State.RESISTANT in (agent1.state, agent2.state):
            return 4
        return 2

    def get_agents(source, target):
        return G.nodes[source]["agent"][0], G.nodes[target]["agent"][0]

    portrayal = dict()
    portrayal["nodes"] = [
        {
            "size": 7,
            "color": node_color(agents[0]),
            "tooltip": f"id: {agents[0].unique_id}<br>state: {agents[0].state}",
        }
        for (_, agents) in G.nodes.data("agent")
    ]

    portrayal["edges"] = [
        {
            "source": source,
            "target": target,
            "color": edge_color(*get_agents(source, target)),
            "width": edge_width(*get_agents(source, target)),
        }
        for (source, target) in G.edges
    ]

    return portrayal


network = mesa.visualization.NetworkModule(network_portrayal, 500, 500)
chart = mesa.visualization.ChartModule(
    [
        {"Label": "Infected", "Color": "#BC2E0F"},
        {"Label": "Susceptible", "Color": "#42F50E"},
        {"Label": "Resistant", "Color": "#3498DB"},
        {"Label": "Dead", "Color": "#FFFFFFF"},
    ]
)

def get_resistant_susceptible_ratio(model):
    ratio = model.resistant_susceptible_ratio()
    ratio_text = "&infin;" if ratio is math.inf else f"{ratio:.2f}"
    infected_text = str(number_infected(model))

    return "Resistant/Susceptible Ratio: {}<br>Infected Remaining: {}".format(
        ratio_text, infected_text
    )

model_params = {
    "num_nodes": mesa.visualization.Slider(
        "Number of agents",
        20,
        10,
        100,
        1,
        description="Choose how many agents to include in the model",
    ),
    "initial_outbreak_size": mesa.visualization.Slider(
        "Initial Outbreak Size",
        5,
        1,
        10,
        1,
        description="Initial Outbreak Size",
    ),
    "initial_antivirus_size": mesa.visualization.Slider(
        "Initial Antivirus Size",
        4,
        1,
        10,
        1,
        description="Initial Resistan Size",
    ),
    "gain_resistance_chance_virus": mesa.visualization.Slider(
        "Gain Resistance Chance Virus",
        1.0,
        0.0,
        1.0,
        0.1,
        description="Probability that a recovered agent will become "
        "resistant to this virus in the future",
    ),
    "gain_resistance_chance_computer": mesa.visualization.Slider(
        "Gain Resistance Chance Computer",
        1.0,
        0.0,
        1.0,
        0.1,
        description="Probability that a recovered agent will become "
        "resistant to this virus in the future",
    ),
    "check_frequency_antivirus": mesa.visualization.Slider(
        "Outdated",
        0.2,
        0.0,
        1.0,
        0.1,
        description="Frecuency check antivirus "
    ),
    "computer_age": mesa.visualization.Slider(
        "Computer Ages",
        0.1,
        0.0,
        10.0,
        0.1,
        description="Computer age"
    ),
    "initial_dead_computer": mesa.visualization.Slider(
        "Initial Dead Computer",
        2,
        1,
        10,
        1,
        description="Initial computer with state dead"
    ),
}

server = mesa.visualization.ModularServer(
    VirusOnNetwork,
    [network, get_resistant_susceptible_ratio, chart],
    "Virus Model",
    model_params,
)
server.port = 8521
