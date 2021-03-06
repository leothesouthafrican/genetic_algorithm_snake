
from audioop import avg
import os
import numpy as np
import pandas as pd
from openpyxl import load_workbook
from operator import attrgetter
import time
start_time = time.time()

def da_informazione_a_conoscenza(population, gens,select, cross, mutate,co_p,mu_p,elitism,fitness_function):
    """Convert all necessary population meta-data into a dictionary that stores
     a pair of the input data, parameters and the generation by generation results.

    Args:
        population (list): a list containing individuals (object) in the population with all their attributes
    """
    
    #preprocessing
    select = str(select).split(" ")[1]
    cross = str(cross).split(" ")[1]
    mutate = str(mutate).split(" ")[1]
    
    #Create dictionary
    temp_dictionary = {"meta_data":{
        "gens":gens,
        "select":select,
        "cross":cross,
        "mutate":mutate,
        "co_p":co_p,
        "mu_p":mu_p,
        "elitism": elitism,
        "fitness_function": fitness_function
        }}
    
    #Fetching variables
    best_fitness = max(population, key=attrgetter("fitness")).fitness
    best_fit_repr = max(population, key=attrgetter("fitness")).representation

    best_fit_length = len(max(population, key=attrgetter("fitness")).occupied_blocks)
    best_fit_steps = population[0].initial_epochs - max(population, key=attrgetter("fitness")).available_epochs

    total = 0
    for individual in population:
        total += individual.fitness
    average_fitness = total / len(population)

    #Calculating phenotypic variance
    variance = 0
    for individual in population:
        variance += (individual.fitness - average_fitness)**2
    prefix = 1/(len(population)-1)
    phenotypic_variance = round(prefix * variance)

    #Calculating genotypic variance
    origin = population[0].representation

    distances = []
    for individual in population:
        distances.append(np.linalg.norm(np.asarray(origin) - np.asarray(individual.representation)))

    average_distance = np.mean(distances)

    variance = 0
    for distance in distances:
        variance += (distance - average_distance)**2
    genotypic_variance = round(prefix * variance,5)

    #Time per generation
    time_elapsed = time.time() - start_time


    print(f"Time Elapsed: {round(time_elapsed, 3)}")

    #Create a dataframe
    column_names = ["best_fitness","best_fitness_representation","best_fit_length","best_fit_steps", "average_fitness", "phenotypic_variance", "genotypic_variance", "time"]
    series_to_append = pd.Series([best_fitness, best_fit_repr, best_fit_length, best_fit_steps,average_fitness, phenotypic_variance, genotypic_variance, time_elapsed], index = column_names)
    
    return temp_dictionary, series_to_append

def df_to_excel(dataframe, dictionary, runs):
    
    dir_list = os.listdir("./results")

    sub_dict = dictionary["meta_data"]
    name = str(str(sub_dict["gens"]) +"_"+ sub_dict["select"] +"_"+ sub_dict["cross"] +"_"+ sub_dict["mutate"] +"_"+ str(sub_dict["co_p"]) +"_"+ str(sub_dict["mu_p"]) +"_"+ str(int(sub_dict["elitism"])) +"_"+ sub_dict["fitness_function"])
    
    dataframe.to_excel(r'./results/' + name + '.xlsx', sheet_name = str(runs))

def excel_concat(dictionary, gens,output_file_name,runs):
    
    sub_dict = dictionary["meta_data"]
    name = str(str(sub_dict["gens"]) +"_"+ sub_dict["select"] +"_"+ sub_dict["cross"] +"_"+ sub_dict["mutate"] +"_"+ str(sub_dict["co_p"]) +"_"+ str(sub_dict["mu_p"]) +"_"+ str(int(sub_dict["elitism"])) +"_"+ sub_dict["fitness_function"])

    df = pd.read_excel(r'./results/' + name + '.xlsx')
    GROUP_LENGTH = gens + 1 # set nr of rows to slice df

    with pd.ExcelWriter(r'./results/' + output_file_name + '.xlsx') as writer:
        for i, count in zip(range(0, len(df), GROUP_LENGTH),range(runs)):
            df[i : i+GROUP_LENGTH].to_excel(writer, sheet_name='Run_{}'.format(count), index=False, header=True)
    
    #remove excel file with no sheets
    os.remove(r'./results/' + name + '.xlsx')

