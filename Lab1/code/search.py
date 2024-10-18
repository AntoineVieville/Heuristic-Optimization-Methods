from util import Player, save_solution_to_file, fitness, position_constraint, separate_by_position
import random

# General greedy algorithm #
def general_greedy_search(players,solution_file) :
        """Finds a greedy solution to the draft problem

        Parameters:
        players : list
                List of all the players of the instance
        solution_file : str 
                solution file in format '.txt'
        Returns:
        2 lists
                list of the playing 11, list of 4 substitutes
        1 float
                budget spent of the draft    
        """   
        draft = []
        playing_11 = []
        substitutes = []
        budget = 0 
        max_budget = 100 

        # First, draft 4 cheapest player as substitutes 
        players.sort(key=lambda x: x.price)
        while(len(substitutes) < 4): # continue adding players meeting the constraints until the bench is full
                for player in players :
                        if len(substitutes) == 4: # we don't check all the remaining players if the bench is full
                                break
                        if position_constraint(player,substitutes,n_gk=1,n_def=2): # 1 GK, # 2 DEF
                                                                                   # the best scoring players are mostly FW and MID
                                                                                   # we want them on the playing field if we can
                                player_club = player.club
                                cpt_club = sum(player.club == player_club for player in substitutes) # number of already drafted players from this club
                                # checking club constraint
                                if cpt_club >=3 : 
                                        continue
                                else : 
                                        substitutes.append(player)
                                        draft.append(player)
                                        budget += player.price
                        else : 
                                continue   

        # Then, draft the remaining players based on best points/cost ratio
        players.sort(key=lambda x: x.ratio, reverse=True)

        while(len(draft) < 15):
                for player in players :
                        if len(draft) == 15: # we don't check all the remaining players if the draft is complete
                                break
                        if player not in draft: # the player hasn't already been selected
                                test_budget = budget + player.price
                                # checking budget constraint
                                if test_budget > max_budget : 
                                        continue

                                player_club = player.club
                                cpt_club = sum(player.club == player_club for player in draft) # number of already drafted players from this club
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
        save_solution_to_file(playing_11,substitutes,solution_file)                                  

        return playing_11, substitutes, budget    

# Best greedy algorithm #
def greedy_search(players,n_top_players,solution_file) :
        """Finds a greedy solution to the draft problem

        Parameters:
        players : list :List of all the players of the instance
        n_top_players : int : number of top players affordable per instance (<7 for #1 and <5 for #2)
        solution_file : str :solution file in format '.txt'
        Returns:
        2 lists
                list of the playing 11, list of 4 substitutes
        1 float
                budget spent of the draft    
        """   

        draft = []
        playing_11 = []
        substitutes = []
        budget = 0 
        max_budget = 100 

        # First, draft 4 cheapest player as substitutes 
        players.sort(key=lambda x: x.price)
        while(len(substitutes) < 4): 
                for player in players :
                        if len(substitutes) == 4: 
                                break
                        # checking position constraint
                        if position_constraint(player,substitutes,n_gk=1,n_def=2): 
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
        
        # Based on the instance, there is a certain number of top players (by points) that we can afford
        # before resorting to the less optimal but less restrictive ratio criterion
        players.sort(key=lambda x: x.points, reverse=True)
        # Draft the top players we can afford
        while (len(draft) < 4 + n_top_players) :
                for player in players :
                        if len(draft) == 4 + n_top_players :
                                break
                        
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

        # Then, draft the remaining players based on best points/cost ratio
        players.sort(key=lambda x: x.ratio, reverse=True)

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
        save_solution_to_file(playing_11,substitutes,solution_file)                                  

        return playing_11, substitutes, budget    

# Construction phase for the grasp algorithm
def construction_phase(players,alpha=0.2) :
        """Construction phase of the GRASP algorithm, generates a randomized greedy solution
        Parameters:
        players : list
                List of all the players of the instance
        Returns:
        2 lists
                list of the playing 11, list of 4 substitutes
        1 float
                budget spent of the draft    
        """   
        playing_11 = []
        substitutes = []
        draft = []
        budget = 0 
        max_budget = 100

        # First draft 4 cheapest players, with random positions (except for 1 GK)
        per_price = sorted(players,key=lambda x: x.price)
        cheapest_players =  [player for player in per_price if player.price <= 5.0]
        random.shuffle(cheapest_players)
        while(len(substitutes) < 4): 
                for player in cheapest_players  :
                        if len(substitutes) == 4: 
                                break
                        # checking position constraint
                        if position_constraint(player,substitutes,n_gk=1,n_def=2,n_mid=1,n_fw=0): 
                                player_club = player.club
                                cpt_club = sum(player.club == player_club for player in substitutes) 
                                # checking club constraint
                                if cpt_club >=3 : 
                                        continue
                                else : 
                                        substitutes.append(player)
                                        draft.append(player)
                                        budget += player.price  

        players.sort(key=lambda x: x.points, reverse=True)

        while(len(draft) < 15):
                if len(draft) == 15: 
                        break
                # constructing Restricted Candidate List
                c_min,c_max = players[-1].ratio, players[0].ratio
                threshold = c_min + alpha*(c_max-c_min)
                rcl = [player for player in players if player.ratio >= threshold]
                random.shuffle(rcl)
                for candidate in rcl :
                        test_budget = budget + candidate.price
                        # checking budget constraint
                        if test_budget > max_budget : 
                                continue
                        cpt_club = sum(player.club == candidate.club for player in draft) # number of already drafted players from this club
                        # checking club constraint
                        if cpt_club >= 3 : 
                                continue
                        # checking position constraint
                        if position_constraint(candidate,playing_11,n_gk=1,n_def=3,n_mid=4,n_fw=3) :
                                playing_11.append(candidate)
                                draft.append(candidate)
                                #print(f'player {candidate} added')
                                players.remove(candidate)
                                #print(f' nb of players left {len(players)}')
                                budget += candidate.price
                                break                                       
                                                       
        return playing_11, substitutes, budget    

# Local search algorithm, used for grasp #
def local_search(players,playing_11,substitutes,budget, neighborhood_size=10):
    """Finds a locally optimal solution from a starting solution using local search algorithm

    Parameters:
    players : list
            List of all the players of the instance
    playing_11 : list : list of 11 players on the field
    substitutes : list : list of 4 substitutes players
    neighbordhood_size : int : size of the neighborhood to be explored during the search     
    Returns:
    2 lists
            list of the better playing 11, list of 4 substitutes
    1 float
            budget spent of the improved draft    
    """  
    draft = playing_11 + substitutes
    improved_11 = playing_11.copy() 
    better_solution = True # boolean tested throughout the iterations of the algorithm
    max_budget = 100
    current_budget = budget
    n_iter = 0 
    gks,defs,mids,fws = separate_by_position(players)

    while (better_solution) :
        better_solution = False
        # We search better players to replace our current players on the field
        for i in range(11) : 
            player = improved_11[i]
            if player.position == "GK" :
                neighborhood = gks
            elif player.position == 'DEF':
                neighborhood = defs
            elif player.position == 'MID':
                neighborhood = mids
            elif player.position == 'FW':
                neighborhood = fws

            random.shuffle(neighborhood) 
            player_neighborhood = neighborhood[:neighborhood_size]  # reduced random neighborhood : N=neighborhood_size players of the same position

            # We check all the neighbors and store the ones that improve the solution
            # Then we replace the player by the most improving neighbor
            potential_switches = [] 

            for neighbor in player_neighborhood:
                if neighbor in draft : 
                    continue 
                # checking budget constraint
                if current_budget - player.price + neighbor.price > max_budget:  
                    continue
                cpt_neighbor_club = sum(player.club == neighbor.club for player in draft)
                # checking club constraint
                if player.club == neighbor.club or cpt_neighbor_club <=2 : 
                    # evaluating "quality" of the neighbor
                    if neighbor.points > player.points:
                        potential_switches.append(neighbor)
                                
            if len(potential_switches) > 0: # we have found neighbors that improve the solution
                better_solution = True
                potential_switches.sort(key=lambda x: x.points, reverse=True)
                best_neighbor = potential_switches[0] # best improving neighbor
                improved_11[i] = best_neighbor # replacing player by the most improving candidate
                draft[i] = best_neighbor 
                current_budget = sum(p.price for p in draft) 
                n_iter += 1
            else : 
                continue    
                            
    return improved_11,substitutes,current_budget,n_iter

# GRASP algorithm #
def grasp(players, max_iter, solution_file):
    """Finds a solution to the problem using GRASP algorithm

    Parameters:
    players : list
            List of all the players of the instance
    max_iter : int : maximum number of iterations for the GRASP algorithm
    solution_file : str : solution file in format '.txt'
    Returns:
    2 lists
            list of the best playing 11 found, list of 4 substitutes
    1 float, 1 int
            budget spent of the draft, number of iterations needed for the local search to find the best solution    
    """ 
    random.seed(1)
    best_fitness = 0
    best_11 = []
    best_substitutes = []
    best_budget = []
    n_iter_best = 0 

    for i in range(max_iter):
        # Construction phase 
        initial_playing_11, initial_substitutes, initial_budget = construction_phase(players)
        # Local search phase
        improved_playing_11, substitutes, new_budget,n_iter_search = local_search(players, initial_playing_11, initial_substitutes, initial_budget)
        new_fitness = fitness(improved_playing_11)

        if new_fitness > best_fitness:
            # Update the best solution
            best_fitness = new_fitness
            best_11 = improved_playing_11
            best_budget = new_budget
            n_iter_best = n_iter_search
            
    save_solution_to_file(best_11,substitutes,solution_file)                                  

    return best_11, substitutes, best_budget,n_iter_best
