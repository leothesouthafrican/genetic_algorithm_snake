import numpy as np
import math
import time
start_time = time.time()

from genetics import Individual, Environment, NN_Engine, Population
from crossover import *
from mutation import *
from selection import *



environment_1 = Environment(environment_size=10)

population_1 = Population(size = 1000, environment_used = environment_1, optim = "max")

population_1.evolve(
    gens=75,
    select=fps,
    crossover=pmx_co,
    mutate=inversion_mutation,
    co_p=0.9,
    mu_p=0.1, 
    elitism=True
)