import osmnx
from smart_mobility_utilities.common import Node, cost, randomized_search
from smart_mobility_utilities.viz import draw_route
from smart_mobility_utilities.problem import cross_over
import random
import itertools
from tqdm.notebook import tqdm
import matplotlib.pyplot as plt

reference = (43.661667, -79.395)

G = osmnx.graph_from_point(reference, dist=300, clean_periphery=True, simplify=True)

origin = Node(graph=G, osmid=55808290)
destination = Node(graph=G, osmid=389677909)

highlighted = [389677909, 55808290]

# marking both the source and destination node

nc = ['red' if node in highlighted else '#336699' for node in G.nodes()]
ns = [50 if node in highlighted else 8 for node in G.nodes()]
fig, ax = osmnx.plot_graph(G, node_size=ns, node_color=nc, node_zorder=2)


# Initialize the swarm
n = 200
particles = [randomized_search(G,origin.osmid, destination.osmid) for _ in range(n)]
num_swarms = 4
num_iterations = 100

# Used to track the costs for analysis
swarm_costs = []

for iteration in tqdm(range(num_iterations)):
    particles.sort(key=lambda p: cost(G,p))
    pps = n // num_swarms # particles per swarm

    # We select the best particles in each swarm to lead
    leaders = particles[:pps][:]

    for i in range(num_swarms):
        particles[i] , particles[i * (pps) - 1] = particles[i * (pps) - 1], particles[i]
    
    swarms = list()
    for i in range(num_swarms):
        swarms.append(particles[i * (pps): i*(pps) + pps])

    # For each swam, we need to follow the leader of that swarm

    # follow the leader of the local swarm
    def local_follow(population):
        for i in range(1, len(population)):
            population[i] = cross_over(population[0],population[i])

    # follow the global leader
    def global_follow():
        for u, v in itertools.product(range(0, len(leaders)), range(0, len(leaders))):
            to_be_mutated = random.choice([u, v])
            leaders[to_be_mutated] = cross_over(leaders[u], leaders[v])
    
    for swarm in swarms:
        local_follow(swarm)
    
    global_follow()

    # Add the new leaders
    particles[i*(pps-1)] = leaders[i]

    # Track the lowest cost in each swarm
    swarms = list()
    for i in range(num_swarms):
        swarms.append(particles[i * (pps): i*(pps) + pps])

    cost_set = []
    for swarm in swarms:
        lowest =min([cost(G,p) for p in swarm])
        cost_set.append(lowest)
    swarm_costs.append(cost_set)


route = min(particles, key=lambda p: cost(G,p))
print("Cost:",cost(G,route))
draw_route(G, route)


plt.plot(swarm_costs)
plt.xlabel('Iterations')
plt.ylabel('Cost (m)')
plt.show()
