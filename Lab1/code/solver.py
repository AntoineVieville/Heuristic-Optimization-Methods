from util import instance_as_df, create_players_list 
from search import *

# Loading the data
df_1 = instance_as_df(r'Lab1\2023_instance1.txt')
df_2 = instance_as_df(r'Lab1\2023_instance2.txt')

players_1 = create_players_list(df_1) # Instance 1
players_2 = create_players_list(df_2) # Instance 2

# General greedy algorithm solutions 
general_greedy_11_1,general_greedy_sub_1,general_greedy_budget_1 = general_greedy_search(players_1,'general_greedy_1.txt')
general_greedy_11_2,general_greedy_sub_2,general_greedy_budget_2 = general_greedy_search(players_2,'general_greedy_2.txt')

# Best greedy algorithm solutions
n_top_players_1 = 7
n_top_players_2 = 5 
greedy_11_1,greedy_sub_1,greedy_budget_1 = greedy_search(players_1,7,'greedy_1.txt')
greedy_11_2,greedy_sub_2,greedy_budget_2 = greedy_search(players_2,5,'greedy_2.txt')

# GRASP algorithm solutions
grasp_11_1,grasp_sub_1,grasp_budget_1,n_iter_1 = grasp(players_1,10,'grasp_1.txt')
grasp_11_2,grasp_sub_2,grasp_budget_2,n_iter_2 = grasp(players_2,10,'grasp_2.txt')

print(f' Instance 1: nb of iterations needed by local search to reach a local (or potentially global) optimum : {n_iter_1}')
print(f' Instance 2: nb of iterations needed by local search to reach a local (or potentially global) optimum : {n_iter_2}')

