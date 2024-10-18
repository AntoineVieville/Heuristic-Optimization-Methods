from util import instance_as_df, create_players_list 
from search import *
random.seed(0)
# Loading the data
df_1 = instance_as_df(r'Lab2\2023_Lab2_instance1.txt')
df_2 = instance_as_df(r'Lab2\2023_Lab2_instance2.txt')

players_1 = create_players_list(df_1) # Instance 1
players_2 = create_players_list(df_2) # Instance 2

# greedy search solutions 
greedy_11_1,greedy_sub_1,greedy_budget_1 = greedy_search(players_1)
greedy_11_2,greedy_sub_2,greedy_budget_2 = greedy_search(players_2)

# random search solutions 
random_11_1,random_sub_1,random_budget_1 = random_search(players_1)
random_11_2,random_sub_2,random_budget_2 = random_search(players_2)

# Tabu search solutions
## with initial greedy solution
tabu_greedy_11_1,tabu_greedy_sub_1,tabu_greedy_budget_1 = tabu_search(players_1,greedy_11_1,greedy_sub_1,greedy_budget_1,5,'tabu_greedy_1.txt',max_iter=200)
tabu_greedy_11_2,tabu_greedy_sub_2,tabu_greedy_budget_2 = tabu_search(players_2,greedy_11_2,greedy_sub_2,greedy_budget_2,5,'tabu_greedy_2.txt',max_iter=200)
## with initial random solution
tabu_random_11_1,tabu_random_sub_1,tabu_random_budget_1 = tabu_search(players_1,random_11_1,random_sub_1,random_budget_1,1,'tabu_random_1.txt',max_iter=600)
tabu_random_11_2,tabu_random_sub_2,tabu_random_budget_2 = tabu_search(players_2,random_11_2,random_sub_2,random_budget_2,1,'tabu_random_2.txt',max_iter=600)

# Simulated annealing solutions
## with initial greedy solution
SA_greedy_11_1,SA_greedy_sub_1,SA_greedy_budget_1 = simulated_annealing(players_1,greedy_11_1,greedy_sub_1,greedy_budget_1,108,0.01,'geometric','SA_greedy_1.txt',alpha=0.95)
SA_greedy_11_2,SA_greedy_sub_2,SA_greedy_budget_2 = simulated_annealing(players_2,greedy_11_2,greedy_sub_2,greedy_budget_2,88,0.01,'geometric','SA_greedy_2.txt',alpha=0.95)
## with initial random solution
SA_random_11_1,SA_random_sub_1,SA_random_budget_1 = simulated_annealing(players_1,random_11_1,random_sub_1,random_budget_1,108,0.01,'geometric','SA_random_1.txt',alpha=0.95)
SA_random_11_2,SA_random_sub_2,SA_random_budget_2 = simulated_annealing(players_2,random_11_2,random_sub_2,random_budget_2,88,0.01,'geometric','SA_random_2.txt',alpha=0.95)





