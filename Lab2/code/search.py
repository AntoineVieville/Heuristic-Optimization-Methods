from util import Player, save_solution_to_file, fitness, position_constraint, separate_by_position, check_AC
import random
import numpy as np

# Random search algorithm #
def random_search(players):

    draft = []
    playing_11 = []
    substitutes = []
    budget = 0 
    max_budget = 100 

    players.sort(key = lambda x: x.price)

    # picking 4 subsitutes (cheapest players)
    while(len(substitutes) < 4): 
            for player in players :
                    if len(substitutes) == 4: 
                            break
                    if position_constraint(player,substitutes,n_gk=1,n_def=1,n_mid=1,n_fw=1):                                               
                            player_club = player.club
                            cpt_club = sum(player.club == player_club for player in substitutes) 
                            # checking club constraint
                            if cpt_club >=3 : 
                                    continue
                            else : 
                                    substitutes.append(player)
                                    draft.append(player)
                                    budget += player.price
                    else : 
                            continue   
    random.shuffle(players)

    # pick remaining players (meeting constraints) randomly
    while(len(draft) < 15):
            for player in players :
                    if len(draft) == 15: 
                            break
                    if player not in draft: 
                            test_budget = budget + player.price
                            # checking budget constraint
                            if test_budget > max_budget : 
                                    continue

                            player_club = player.club
                            cpt_club = sum(player.club == player_club for player in draft)
                            # checking club constraint
                            if cpt_club == 3 : 
                                    continue
                            # checking position constraint
                            if position_constraint(player,draft) :
                                    playing_11.append(player)
                                    draft.append(player)
                                    budget += player.price
                            else : 
                                    continue 
                           
    return playing_11, substitutes, budget    

# Greedy search algorithm #
def greedy_search(players):
    draft = []
    playing_11 = []
    substitutes = []
    budget = 0 
    max_budget = 100 

    # picking 4 subsitutes (cheapest players) 
    players.sort(key=lambda x: x.price)
    while(len(substitutes) < 4): 
            for player in players :
                    if len(substitutes) == 4: 
                            break
                    if position_constraint(player,substitutes,n_gk=1,n_def=1,n_mid=1): 
                            player_club = player.club
                            cpt_club = sum(player.club == player_club for player in substitutes) 
                            # checking club constraint
                            if cpt_club >=3 : 
                                    continue
                            else : 
                                    substitutes.append(player)
                                    draft.append(player)
                                    budget += player.price
                    else : 
                            continue   

    # draft remaining players based on best points**3/cost ratio
    players.sort(key=lambda x: (x.points)**3/x.price, reverse=True)

    while(len(draft) < 15):
            for player in players :
                    if len(draft) == 15:
                            break
                    if player not in draft: 
                            test_budget = budget + player.price
                            # checking budget constraint
                            if test_budget > max_budget : 
                                    continue

                            player_club = player.club
                            cpt_club = sum(player.club == player_club for player in draft) 
                            # checking club constraint
                            if cpt_club == 3 : 
                                    continue
                            # checking position constraint
                            if position_constraint(player,draft) :
                                    playing_11.append(player)
                                    draft.append(player)
                                    budget += player.price
                            else : 
                                    continue 

    return playing_11, substitutes, budget    

# Neighborhood generation function (used for tabu search and SA)
def generate_neighborhood(solution, draft, budget, players):
    gks, defs, mids, fws = separate_by_position(players)
    max_budget = 100
    neighborhood = []  # list of neighbor solutions

    for i, player in enumerate(solution):
        neighbor_solution = solution.copy()  
        if player.position == "GK":
            switches = gks
        elif player.position == 'DEF':
            switches = defs
        elif player.position == 'MID':
            switches = mids
        elif player.position == 'FW':
            switches = fws
        
        #switches.sort(key= lambda x : x.points, reverse=True)
        random.shuffle(switches)
        valid_switches =[]
        while (len(valid_switches) < len(switches)//2):
            if len(valid_switches) == len(switches)//2 : 
                  break 
            for candidate in switches:
                if candidate not in draft:
                    # checking budget constraint
                    if budget - player.price + candidate.price > max_budget:  
                        continue
                    cpt_neighbor_club = sum(player.club == candidate.club for player in draft)
                    # checking club constraint
                    if player.club == candidate.club or cpt_neighbor_club <=2 : 
                        # valid switch 
                        valid_switches.append(candidate)
                    else : continue
                else : 
                      continue
        random.shuffle(valid_switches)
        neighbor_solution[i] = valid_switches[0]
        neighborhood.append((neighbor_solution, fitness(neighbor_solution), i))
    
    sorted_neighborhood = sorted(neighborhood, key=lambda x: x[1], reverse=True)
    return sorted_neighborhood


# Tabu search algorithm #
def tabu_search(players,playing_11,substitutes,budget,tenure,solution_file,max_iter=300): 

    current_draft = playing_11 + substitutes
    tabu_list = [0] * 11
    current_budget = budget
    current_solution = playing_11
    best_solution = current_solution
    best_draft = best_solution + substitutes
    
    for iter in range(max_iter):

        # generate neighborhood from the current solution
        current_neighborhood = generate_neighborhood(current_solution,current_draft,current_budget,players)

        for i in range(len(current_neighborhood)):
            idx_switch = current_neighborhood[i][2]

            # check if solution is tabu or not
            # (is not tabu) or (is tabu but meets the AC)
            if tabu_list[idx_switch] == 0 or check_AC(current_neighborhood[i][0],best_solution,1.2): 
                # select this solution to test
                best_neighbor = current_neighborhood[i][0]
                best_neighbor_fitness = current_neighborhood[i][1]
                # make the solution tabu for future iterations
                tabu_list[idx_switch]+=(tenure+1) 
                break
            # is tabu 
            else : 
                continue

        # search always goes forward    
        current_solution = best_neighbor
        current_draft = current_solution + substitutes
        current_budget = sum(player.price for player in current_draft)
        # update best solution only if best neighbor is improving
        if best_neighbor_fitness > fitness(best_solution):
            best_solution = best_neighbor
            best_draft = best_solution + substitutes
            
        # update the tabu list at the end of iteration
        for i in range(len(tabu_list)):
            if tabu_list[i] > 0: 
                tabu_list[i] -= 1

    best_budget = sum(player.price for player in best_draft)
    #print(f'tabu_list {tabu_list} at iter {iter}')  

    save_solution_to_file(best_solution,substitutes,solution_file)                                  

    return best_solution,substitutes,best_budget  

# Simulated annealing algorithm #
def simulated_annealing(players,playing_11,substitutes,budget,initial_temp,final_temp,decrement_temp,solution_file,alpha=0.9,beta=0.1):

    T = initial_temp
    T_f = final_temp
    current_solution = playing_11
    current_draft = playing_11 + substitutes
    current_budget = budget
    best_solution = current_solution
    best_draft = best_solution + substitutes

    if decrement_temp == 'geometric':
        n_iter = int((np.log(T_f)-np.log(T))/np.log(alpha)) 
    elif decrement_temp == 'slow':
        n_iter = int((T-T_f)/(beta*T*T_f))    

    for iter in range(n_iter):
        idx = random.randint(0, 10)
        # select a random neighbor in the neighborhood of the current solution
        neighbor_solution = generate_neighborhood(current_solution,current_draft,current_budget,players)[idx][0] 

        # improving neighbor
        if fitness(neighbor_solution) > fitness(current_solution) :
            current_solution = neighbor_solution # always accept 
            current_draft = current_solution + substitutes
            current_budget = sum(player.price for player in current_draft)

        # non improving neighbor
        else : 
            delta_f = fitness(current_solution) - fitness(neighbor_solution)
            p = np.exp(-delta_f/T)
            if random.random() < p : # accept with proba of p
                current_solution = neighbor_solution
                current_draft = current_solution + substitutes
                current_budget = sum(player.price for player in current_draft)

        # update best solution 
        if fitness(current_solution) > fitness(best_solution):
            best_solution = current_solution
            best_draft = best_solution + substitutes

        # update temperature
        if decrement_temp == 'geometric':
            T = alpha*T # alpha = 0.9
        elif decrement_temp == 'slow' :
            T = T / (1+beta*T) # beta = 0.1

    best_budget = sum(player.price for player in best_draft)
    save_solution_to_file(best_solution,substitutes,solution_file) 
        
    return best_solution,substitutes,best_budget                  

