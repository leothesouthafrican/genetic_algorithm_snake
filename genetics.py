from dis import dis
from pickle import NONE
from random import shuffle, choice, sample, random
from operator import attrgetter
from copy import deepcopy
import numpy as np
import pandas as pd
from random import shuffle, choice, sample, random
from utils import da_informazione_a_conoscenza, df_to_excel
import math

class Environment:
    def __init__(self,apple_position = None, borders = [], environment_size = 20):
        self.apple_position = apple_position
        self.borders = borders
        self.environment_size = environment_size

        if self.apple_position is None:
            self.apple_position = list(np.random.randint(low=1, high=(self.environment_size - 1), size=2))
        
        if self.borders == []:
            for x in range(0,self.environment_size):
                if x == 0:
                    for y in range(0,self.environment_size):
                        self.borders.append([x,y])
                if x == (self.environment_size - 1) and y != 0:
                    for y in range(0,self.environment_size):
                        self.borders.append([x,y])
                for y in range(0,self.environment_size):
                    if y == (self.environment_size - 1) and x != 0:
                        self.borders.append([x,y])
                    elif y == 0 and x != 0:
                        self.borders.append([x,y])
    def __str__(self):
        return f"Apple Position: {self.apple_position})\nEnvironment Size: {self.environment_size}"

class Individual:
    def __init__(
        self,
        current_environment,
        matrix_weights_1 = None,
        matrix_weights_2 = None,
        matrix_weights_3 = None,
        matrix_weights_4 = None,
        bias_vector_1 = None,
        bias_vector_2 = None,
        bias_vector_3 = None,
        bias_vector_4 = None,
        representation = None,
        snake_head_coordinates = None,
        heading = "N",
        occupied_blocks = None,
        relative_position = [],
        available_epochs = 2000,
        fitness = None,
        fitness_function = "fitness_function_3",
    ):

        if matrix_weights_1 is None:
            self.matrix_weights_1 = np.random.uniform(low=-1, high=1, size=(4,10)).round(3)
        if matrix_weights_2 is None:
            self.matrix_weights_2 = np.random.uniform(low=-1, high=1, size=(10,15)).round(3)
        if matrix_weights_3 is None:
            self.matrix_weights_3 = np.random.uniform(low=-1, high=1, size=(15,10)).round(3)
        if matrix_weights_4 is None:
            self.matrix_weights_4 = np.random.uniform(low=-1, high=1, size=(10,3)).round(3)
        if bias_vector_1 is None:
            self.bias_vector_1 = np.random.uniform(low=-1, high=1, size=(1,10)).round(3)
        if bias_vector_2 is None:
            self.bias_vector_2 = np.random.uniform(low=-1, high=1, size=(1,15)).round(3)
        if bias_vector_3 is None:
            self.bias_vector_3 = np.random.uniform(low=-1, high=1, size=(1,10)).round(3)
        if bias_vector_4 is None:
            self.bias_vector_4 = np.random.uniform(low=-1, high=1, size=(1,3)).round(3)

        self.environment = current_environment
        self.snake_head_coordinates = snake_head_coordinates
        self.heading = heading
        self.occupied_blocks = occupied_blocks
        self.relative_position = relative_position
        self.initial_epochs = available_epochs
        self.available_epochs = available_epochs
        self.fitness = fitness
        self.representation = representation
        self.fitness_function = fitness_function

        if self.snake_head_coordinates is None:
            self.snake_head_coordinates = np.random.randint(low=2, high=(self.environment.environment_size - 1), size=2)
            self.occupied_blocks = [list(self.snake_head_coordinates- np.asarray([0,1])),list(self.snake_head_coordinates)]

    def distance_computer(self):

        #Loading environment into method for easier access
        environment = self.environment

        #Calculating sin angle from snake_head_coordinates (taking into account heading) to apple_position
        radians = math.atan2(np.abs(self.snake_head_coordinates[1]-environment.apple_position[1]), np.abs(self.snake_head_coordinates[0]- environment.apple_position[0]))
        degrees = math.degrees(radians)

        if self.heading == "N":
            distance_left = self.snake_head_coordinates[0]
            distance_right = (environment.environment_size - 1) - self.snake_head_coordinates[0]
            distance_forward = (environment.environment_size - 1) - self.snake_head_coordinates[1]

            self.relative_position = [distance_left,distance_forward,distance_right, round(np.sin(degrees),2)]
            
        elif self.heading == "E":
            distance_left = (environment.environment_size - 1) - self.snake_head_coordinates[1]
            distance_right = self.snake_head_coordinates[1]
            distance_forward = (environment.environment_size - 1) - self.snake_head_coordinates[0]

            #Adjusting angle for heading
            degrees += 270
            
            self.relative_position = [distance_left, distance_forward, distance_right, round(np.sin(degrees),2)]
            
        elif self.heading == "S":
            distance_left = (environment.environment_size - 1) - self.snake_head_coordinates[0]
            distance_right = self.snake_head_coordinates[0]
            distance_forward = self.snake_head_coordinates[1]

            #Adjusting angle for heading
            degrees += 180

            self.relative_position = [distance_left, distance_forward, distance_right, round(np.sin(degrees),2)]
            
        elif self.heading == "W":
            distance_left = self.snake_head_coordinates[1]
            distance_right = (environment.environment_size - 1) - self.snake_head_coordinates[1]
            distance_forward = self.snake_head_coordinates[0]

            #Adjusting angle for heading
            degrees += 90

            self.relative_position = [distance_left, distance_forward, distance_right, round(np.sin(degrees),2)]

    def create_representation(self):
        if self.representation == None:
            weights_1_vector = np.reshape(self.matrix_weights_1, (1,40))
            weights_2_vector = np.reshape(self.matrix_weights_2, (1,150))
            weights_3_vector = np.reshape(self.matrix_weights_3, (1,150))
            weights_4_vector = np.reshape(self.matrix_weights_4, (1,30))
            representation = np.hstack([weights_1_vector,self.bias_vector_1,weights_2_vector,self.bias_vector_2,weights_3_vector,self.bias_vector_3])
            representation = representation.tolist()[0]
            self.representation = representation

            return self.representation

    def __str__(self):
        return f"Av. Epoch: {self.available_epochs}\nCurrent relative position: {self.relative_position} \nCurrent Heading: {self.heading} \nCurrent Occupied Blocks: {self.occupied_blocks} \nSnake Fitness: {self.fitness}"
    
class NN_Engine:

    def __init__(self, individual, environment):
        self.individual = individual
        self.environment = environment

    def softmax(self,x):
        e_x = np.exp(x)
        return e_x/ e_x.sum()
    
    def sigmoid(self,x):
        return 1/(1 + np.exp(-x))

    def compute_layers(self):
        individual = self.individual

        hidden_layer_1 = np.dot(individual.relative_position, individual.matrix_weights_1) + individual.bias_vector_1

        activated_layer_1 = self.sigmoid(hidden_layer_1)

        hidden_layer_2 = np.dot(activated_layer_1,individual.matrix_weights_2) + individual.bias_vector_2

        activated_layer_2 = self.sigmoid(hidden_layer_2)

        hidden_layer_3 = np.dot(activated_layer_2,individual.matrix_weights_3) + individual.bias_vector_3

        activated_layer_3 = self.sigmoid(hidden_layer_3)

        pre_output = np.dot(activated_layer_3,individual.matrix_weights_4) + individual.bias_vector_4

        final_output = self.softmax(pre_output)

        return final_output

    def chosen_direction(self):
        output_vector = self.compute_layers()
        max_index = np.argmax(output_vector)

        return max_index

    def check_for_apple(self):
        environment = self.environment
        individual = self.individual
        if individual.snake_head_coordinates != environment.apple_position:
            return True
    
    def check_for_borders(self, new_head_position):
        environment = self.environment
        for border_block in environment.borders:
            if border_block == new_head_position:
                return True

    def check_for_occupied_block(self, new_head_position):
        individual = self.individual
        for block in individual.occupied_blocks[:-1]:
            if block == new_head_position:
                return True

    def update_individual_epoch(self):

        individual = self.individual
        environment = self.environment
        direction = self.chosen_direction()
        

        if (direction == 0 and individual.heading == "N") or (direction == 2 and individual.heading == "S") or (direction == 1 and individual.heading == "W"):
            new_snake_head = list(np.asarray(individual.snake_head_coordinates) - np.asarray([1,0]))
            individual.heading = "W"

        elif (direction == 0 and individual.heading == "E") or (direction == 2 and individual.heading == "W") or (direction == 1 and individual.heading == "N"):
            new_snake_head = list(np.asarray(individual.snake_head_coordinates) + np.asarray([0,1]))
            individual.heading = "N"
            
        elif (direction == 0 and individual.heading == "S") or (direction == 2 and individual.heading == "N") or (direction == 1 and individual.heading == "E"):
            new_snake_head = list(np.asarray(individual.snake_head_coordinates) + np.asarray([1,0]))
            individual.heading = "E"
            
        elif (direction == 0 and individual.heading == "W") or (direction == 2 and individual.heading == "E") or (direction == 1 and individual.heading == "S"):
            new_snake_head = list(np.asarray(individual.snake_head_coordinates) - np.asarray([0,1]))
            individual.heading = "S"

        individual.occupied_blocks.append(new_snake_head)
        individual.snake_head_coordinates = new_snake_head
        individual.available_epochs -= 1

        if self.check_for_apple():
            individual.occupied_blocks = individual.occupied_blocks[1:]
        else:
            new_random_coordinates = np.random.randint(low=1, high=(environment.environment_size - 1), size=2)
            environment.apple_position = list(new_random_coordinates)

        if self.check_for_borders(individual.snake_head_coordinates):
            self.counter = individual.available_epochs
            #Get fitness
            individual.available_epochs = 0            
            self.get_fitness()

        elif self.check_for_occupied_block(individual.snake_head_coordinates):
            self.counter = individual.available_epochs
            #Get fitness
            individual.available_epochs = 0
            self.get_fitness()

        elif individual.available_epochs == 0:
            self.counter = 0
            self.get_fitness()

        individual.distance_computer()

    def get_fitness(self):
        individual = self.individual
        steps = individual.initial_epochs - self.counter
        score = len(individual.occupied_blocks)

        if individual.fitness_function == "fitness_function_2":
            if score <= 4:
                fitness = 150*score 
            elif score <= 6:
                fitness = 250*score 
            elif score <= 8:
                fitness = 500*score 
            else:
                fitness = 1000*score 
            individual.fitness = fitness

        elif individual.fitness_function == "fitness_function_3":
            if score <= 4:
                fitness = 150*score + steps
            elif score <= 6:
                fitness = 250*score + steps
            elif score <= 8:
                fitness = 500*score + steps
            else:
                fitness = 1000*score + steps
            individual.fitness = fitness
        else:
            fitness = 150*score + steps
            individual.fitness = fitness

    def __str__(self):
        return f"Direction Chosen: {self.chosen_direction()} \nNew Snake: {self.individual.occupied_blocks} \nNew Heading: {self.individual.heading}"   

class Population:
    def __init__(self, size, optim, environment_used, informazione_df = None, informazione_meta = None):

        self.environment = environment_used
        self.individuals = []
        self.size = size
        self.optim = optim
        for new_individual in range(size):
            self.individuals.append(
                Individual(
                    self.environment
                )
            )
            self.individuals[new_individual].distance_computer()
            self.individuals[new_individual].create_representation()
            engine = NN_Engine(self.individuals[new_individual], environment_used)
            
            while self.individuals[new_individual].available_epochs > 0:
                engine.update_individual_epoch()
        self.informazione_df = informazione_df
        self.informazione_meta = informazione_meta

        column_names = ["best_fitness","best_fitness_representation","best_fit_length","best_fit_steps","average_fitness","phenotypic_variance", "genotypic_variance"]
        self.informazione_df = pd.DataFrame(columns=column_names)

    def evolve(self, gens, select, crossover, mutate, co_p, mu_p, elitism):
    
        for gen in range(gens):
            new_pop = []

            if elitism == True:
                if self.optim == "max":
                    elite = deepcopy(max(self.individuals, key=attrgetter("fitness")))
                elif self.optim == "min":
                    elite = deepcopy(min(self.individuals, key=attrgetter("fitness")))

            while len(new_pop) < self.size:
                parent1, parent2 = select(self), select(self)
                # Crossover
                if random() < co_p:
                    offspring1, offspring2 = crossover(parent1, parent2)
                else:
                    offspring1, offspring2 = parent1, parent2
                # Mutation
                if random() < mu_p:
                    offspring1 = mutate(offspring1)
                if random() < mu_p:
                    offspring2 = mutate(offspring2)

                #create new_offspring_1
                new_offspring_1 = Individual(self.environment, representation=offspring1)
                #make him play
                new_offspring_1.distance_computer()
                engine = NN_Engine(new_offspring_1, self.environment)
                while new_offspring_1.available_epochs > 0:
                    engine.update_individual_epoch()
                new_pop.append(new_offspring_1)

                if len(new_pop) < self.size:
                    #create new_offspring_2
                    new_offspring_2 = Individual(self.environment, representation=offspring2)
                    #make him play
                    new_offspring_2.distance_computer()
                    engine = NN_Engine(new_offspring_2, self.environment)
                    while new_offspring_2.available_epochs > 0:
                        engine.update_individual_epoch()

                    new_pop.append(new_offspring_2)
                

            if elitism == True:
                if self.optim == "max":
                    least = min(new_pop, key=attrgetter("fitness")).representation
                elif self.optim == "min":
                    least = max(new_pop, key=attrgetter("fitness")).representation
                
                new_pop_representations = []
                for individual in new_pop:
                    new_pop_representations.append(individual.representation)
                index_to_drop = new_pop_representations.index(least)
                new_pop.pop(index_to_drop)
                new_pop.append(elite)

            self.individuals = new_pop
            
            #Calculating all of the necessary metrics for storage and further
            print(f"Current Generation: {gen}")
            result = da_informazione_a_conoscenza(self.individuals, gens,select, crossover, mutate,co_p,mu_p,elitism,self.individuals[0].fitness_function)

            #Appending new row to df
            self.informazione_df = self.informazione_df.append(result[1], ignore_index=True)


        self.informazione_meta = result[0]
        self.informazione_df = self.informazione_df.append(result[0], ignore_index=True)
        df_to_excel(self.informazione_df, self.informazione_meta)