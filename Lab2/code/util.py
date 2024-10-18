import pandas as pd 
from collections import Counter

from dataclasses import dataclass

def instance_as_df(filepath):
    """Converts the instance into a pandas DataFrame

    Parameter:
    filepath : str, in format r'filepath'
        path of the instance file
    Returns :
    pandas.core.frame.DataFrame
        Instance as dataframe
    """
    return pd.read_csv(filepath, encoding = 'latin', header=None, names=['ID', 'Position', 'Name', 'Club', 'Points', 'Price'])

# Define the Player data class
@dataclass(unsafe_hash=True)
class Player:
    id: int
    position: str
    name: str
    club: str
    points: int
    price: float
    ratio : float

def create_players_list(instance_df) :
     """Creates a list of all players from the instance

     Parameter:
     instance_df : pandas.core.frame.DataFrame
          instance DataFrame 
     Returns:
     list
          list players    
     """
     df = instance_df
     players = []
     for index, row in df.iterrows():
          player = Player(
               id = row['ID'],
               position = row['Position'],
               name = row['Name'],
               club = row['Club'],
               points = row['Points'],
               price = row['Price'],
               ratio = row['Points']/row['Price']
          )
          players.append(player)
     return players    

def save_solution_to_file(playing_11, substitutes, file_path):
    """Writes the solution in a .txt format checkable by validator.py

    Parameters:
    playing_11 : list
        List of 11 players on the field
    substitutes : list
        List of 4 players on the bench
    file_path : str
        String representing the file path where the solution is saved in.txt format
    Returns:
    Boolean
        True if the player position meets the constraint    
    """
    with open(file_path, 'w') as file:
        # Writing playing 11 to the file
        playing_11_line = ','.join(str(player.id) for player in playing_11)
        file.write(playing_11_line + '\n')

        # Writing substitutes to the file
        substitutes_line = ','.join(str(player.id) for player in substitutes)
        file.write(substitutes_line)



def fitness(solution): 
    """Evaluation of the solution to guide the search

    Parameters:
    solution : list
        A solution (list of 11 players) to the problem

    Returns:
    Int
        Sum of all points of the selected players  
    """
    sum_points = 0
    for player in solution:
        sum_points += player.points # sum of the points of the selected players
    return sum_points

def position_constraint(player, draft,n_gk=2,n_def=5,n_mid=5,n_fw=3):
    """Checks if the position constraint is met

    Parameters:
    player : Player
        The player to be checked
    draft : list
        List containing all drafted players

    Returns:
    Boolean
        True if the player position meets the constraint    
    """
    positions_count = Counter(player.position for player in draft)
    
    if player.position == 'GK':
        return positions_count['GK'] < n_gk
    elif player.position == 'DEF':
        return positions_count['DEF'] < n_def
    elif player.position == 'MID':
        return positions_count['MID'] < n_mid
    elif player.position == 'FW':
        return positions_count['FW'] < n_fw

    return False

def separate_by_position(players):
    """Separates players from the instance based on their position

    Parameters:
    player : list
        List of all players in the instance

    Returns:
    4 lists :
        List of all GKs, of all DEFs, of all MIDs, of all FWs    
    """
    goalkeepers = [player for player in players if player.position == 'GK']
    defenders = [player for player in players if player.position == 'DEF']
    midfielders = [player for player in players if player.position == 'MID']
    fowards = [player for player in players if player.position == 'FW']

    return goalkeepers,defenders,midfielders,fowards

def check_AC(solution,best_solution,quality_ratio):
    """Checks the aspiration criterion in tabu search

    Parameters :
    solution : list : List of 11 players to check  
    best_solution : list : List of best 11 players found so far

    Returns : Boolean : True if solution meets the criterion
    """
    return fitness(solution) >= quality_ratio * fitness(best_solution)
