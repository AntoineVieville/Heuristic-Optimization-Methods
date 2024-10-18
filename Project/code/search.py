# Importing libraries
import time
from numpy.random import choice

# Importing secondary functions
from utils import *

# Greedy algorithm 
def greedy_search(customers,n_vehicles,capacity):
    """ Search a greedy solution to the problem
    Args: customers : (list) list of all customers, n_vehicles : (int) max number of vehicles allowed, capacity : (int) capacity of the vehicles
    Returns: (list) list of greedy routes 
    """
    depot = customers[0]
    distances = distance_matrix(customers)
    remaining_customers = customers[1:]
    routes = []
    i = 0
    truck = Vehicle(i,capacity,depot)

    while(len(remaining_customers) >= 0) :
      if len(remaining_customers) == 0:
        truck.add_customer(depot,customers,distances)
        routes.append(truck)
        break
      else:
        # Sorting remaining customers by distance to truck
        previous_customer_id = truck.route[-1][0]
        previous_customer = customer_by_id(previous_customer_id,customers)
        ordered_customers = [(customer,distance(previous_customer,customer,distances)) for customer in remaining_customers]
        ordered_customers.sort(key = lambda x: x[1])
        ordered_customers = [customer for customer, _ in ordered_customers]
        # Deliver nearest valid customer
        for cnt,customer in enumerate(ordered_customers):
          #print(f'Trying customer {customer.cust_no} for truck {i}')
          # waiting time allowed must be adapted for the instance, very high treshold allows feasible solutions for every instances
          if is_valid(customer,truck,depot,customers,distances) and truck.wait_time(customer,customers,distances) <=8000:
            truck.add_customer(customer,customers,distances)
            remaining_customers.remove(customer)
            break
          # no valid customer found, truck must head back to depot
          if cnt == len(ordered_customers)-1:
            truck.add_customer(depot,customers,distances)
            routes.append(truck)
            # initializing new truck
            i+=1
            if i < n_vehicles:
              truck = Vehicle(i,capacity,depot)
              #print(f'new truck {i} initialized')
            if i==n_vehicles:
              print('Max number of trucks reached, failed the task')
              return routes,remaining_customers
          else :
            continue

    return routes

# Ant Colony Optimization #

# Pheromone update :
# pheromone evaporation
def pheromone_evaporation(pheromone_matrix,evaporation_rate):
  """ evaporates the pheromones
  Args: pheromone_matrix : (numpy.array) matrix of pheromones, evaporation_rate (float) : evaporation rate
  Returns: (numpy.array) updated pheromone matrix
  """  
  N = np.shape(pheromone_matrix)[0]
  for i in range(N):
    for j in range(N):
      tau_ij = pheromone_matrix[i][j]
      if tau_ij == 0 :
        pheromone_matrix[i][j] = 0
      else :
        pheromone_matrix[i][j] = max(0,(1-evaporation_rate)*tau_ij)
  return pheromone_matrix

# pheromone reinforcement (offline, quality based)
def pheromone_reinforcement(pheromone_matrix,constructed_solutions,k_best,distances):
  """ reinforces the pheromones
  Args: pheromone_matrix : (numpy.array) matrix of pheromones, constructed_solutions : (list) list of constructed solutions,
  k_best : (int) number of solutions routes to reinforce, distances (numpy.array) : distance matrix of the instance
  Returns: (numpy.array) updated pheromone matrix
  """
  # out of n ants, select the best k to update pheromone
  N = np.shape(pheromone_matrix)[0]
  best_constructed_solutions = constructed_solutions[:k_best]
  for solution in best_constructed_solutions:
    fitness = total_distance(solution,distances) 
    delta = 1/fitness
    routes = [truck.route for truck in solution]
    for route in routes:
      for i in range(len(route)-1):
          current_node = route[i][0]
          next_node = route[i + 1][0]
          # quality based approach
          pheromone_matrix[current_node][next_node] += delta
  return pheromone_matrix  

# Ant construction phase
def ant_search(customers,capacity,depot,distances,inverse_distances,pheromone_matrix,alpha,beta):
  """ each ant constructs a solution
  Args : customers : (list) list of all customers, capacity : (int) capacity of vehicles, depot : (Customer) depot, distances (numpy.array) distance matrix of instance
  inverse_distance : (numpy.array) inverse distance matrix of instance, pheromone_matrix : (numpy.array) matrix of pheromones, alpha : (float) pheromone's influence
  beta : (float) distances influence
  Returns : (list) list of constructed solutions
  """
  remaining_customers = customers[1:]
  routes = []
  i = 0
  truck = Vehicle(i,capacity,depot)
  #while(time.time() < remaining_time):
  while(len(remaining_customers) > 0) :
    if len(remaining_customers) == 0:
      break
    else:
      # Selection of next customer based on ant behavior
      previous_customer_id = truck.route[-1][0]
      probabilities = []
      customers_to_remove = []
      for customer in remaining_customers :
        if is_valid(customer,truck,depot,customers,distances):

          pheromone_value = pheromone_matrix[previous_customer_id][customer.cust_no]
          heuristic_dist_info = inverse_distances[previous_customer_id][customer.cust_no]
          heuristic_time_info = truck.heuristic_wait_time(customer,customers,distances)

          proba = pheromone_value**alpha * heuristic_dist_info**beta * heuristic_time_info
          probabilities.append((customer,proba))

      normalization_factor = sum(proba[1] for proba in probabilities)
      normalized_probabilities = [(customer, proba/normalization_factor) for customer,proba in probabilities]

      # no valid customers were found
      if len(normalized_probabilities) == 0:
        truck.add_customer(depot, customers,distances)
        routes.append(truck)
        i+= 1
        truck = Vehicle(i, capacity, depot)

      else:
      # Choose the next valid customer based on the computed probabilities
        chosen_customer_idx = np.random.choice(len(normalized_probabilities), p=[prob for _, prob in normalized_probabilities])
        chosen_customer = normalized_probabilities[chosen_customer_idx][0]
        truck.add_customer(chosen_customer,customers,distances)
        customers_to_remove.append(chosen_customer)

      # Remove the processed customers after the loop
      for customer in customers_to_remove:
          remaining_customers.remove(customer)

      if len(remaining_customers) == 0 :
        truck.add_customer(depot,customers,distances)
        routes.append(truck)

  return routes

# ACO algorithm 
def ant_colony_optimization(customers,n_vehicles,capacity,alpha,beta,rho,n_ants,greedy_routes,minutes):
  """ finds a solution in given time
  Args : customers : (list) list of all customers, n_vehicles : (int) maximum number of vehicles, capacity : (int) capacity of vehicles
  alpha : (float) pheromone's influence, beta : (float) distances influence, rho : (float) evaporation rate, n_ants : (int) number of ants per iteration,
  greedy_routes : (list) greedy solution, minutes (int) : number of minutes to run algo
  Returns : (list) best found solution
  """
  depot = customers[0]
  distances = distance_matrix(customers)
  inverse_distances = inverse_distance_matrix(customers)
  N_customers = len(customers)
  tau_0 = 1/total_distance(greedy_routes,distances)
  pheromone_matrix = tau_0 * np.ones((N_customers,N_customers))
  best_solution = greedy_routes
  iterations = 0
  best_iteration_nr = 0
  t_end = time.time() + 60 * minutes

  while time.time() < t_end:
    iterations += 1
    solutions = []
    # For each ant, construct a solution based on ant behavior and pheromone trail
    for ant in range(n_ants):
      remaining_time = t_end - time.time()
      solution = ant_search(customers,capacity,depot,distances,inverse_distances,pheromone_matrix,alpha=alpha,beta=beta)
      solutions.append(solution)

    # Assessing fitness of the solutions:
    # for each solution, compute number of trucks and total distance
    # [(solution, number of trucks, total distance travelled)]
    fitnesses = [(solution,len(solution),total_distance(solution,distances)) for solution in solutions]

    # Sorting by number of trucks required
    fitnesses.sort(key = lambda x: x[1])
    min_nb_trucks = fitnesses[0][1]

    # Sorting by distance using minimum number of trucks
    # [(solution with minimum nb of trucks,total distance travelled)]
    min_truck_solutions = [(fitness[0],fitness[2]) for fitness in fitnesses if fitness[1] == min_nb_trucks]
    min_truck_solutions.sort(key = lambda x: x[1])
    best_constructed_solution = min_truck_solutions[0][0]

    # Updating pheromone trails :
    # evaporation of the pheromones (offline)
    pheromone_matrix = pheromone_evaporation(pheromone_matrix,evaporation_rate=rho)
    # reinforcement (offline)
    sorted_solutions = [solution for solution, _, _ in fitnesses]
    pheromone_matrix = pheromone_reinforcement(pheromone_matrix,sorted_solutions,k_best=3,distances=distances)

    # Update best solution
    if len(best_constructed_solution) < len(best_solution):
      #print(f'better solution found : {len(best_constructed_solution)} instead of {len(best_solution)}')
      #print(time.localtime())
      best_solution = best_constructed_solution
      best_iteration_nr = iterations
    elif len(best_constructed_solution) == len(best_solution):
      if total_distance(best_constructed_solution,distances) < total_distance(best_solution,distances):
        best_solution = best_constructed_solution
        best_iteration_nr = iterations

  print("Best solution found after this many iterations: " + str(best_iteration_nr))
  print("Number of iterations: " + str(iterations) + " for " + str(n_vehicles) + " Vehicles.")
  return best_solution
