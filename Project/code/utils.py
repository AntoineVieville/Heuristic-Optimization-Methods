# Importing libraries
from dataclasses import dataclass
import pandas as pd
import numpy as np
import math

# Processing instance data # 

# Reading instance file
def read_cvrptw_instance(file_path):
    """ Loads instance data 
    Args: file_path : (str) path of the instance file
    Returns: (pandas.core.frame.DataFrame) dataframe of the instance
    """
    num_vehicles = 0
    capacity = 0
    customer_data = []

    with open(file_path, 'r') as file:
        lines = file.readlines()

        for i, line in enumerate(lines):
            tokens = line.split()

            if i == 2 :
                num_vehicles = int(tokens[0])
                capacity = int(tokens[1])

            if i>=7 :
                customer_data.append(tokens[:])

    customers_df = pd.DataFrame(customer_data, columns=['CUST NO.', 'XCOORD.', 'YCOORD.', 'DEMAND', 'READY TIME', 'DUE DATE', 'SERVICE TIME'])

    return num_vehicles, capacity, customers_df

# Customer class
@dataclass(unsafe_hash=True)
class Customer:
    """Customer class
    """
    cust_no: int
    position: (int,int)
    demand: int
    ready_time: int
    due_date: int
    service_time : int
# Create customer list from instance
def create_customers_list(customer_df) :
    """Creates a list of all customers from the instance
    Params: instance_df : (pandas.core.frame.DataFrame) instance DataFrame
    Returns: (list) list of all customers
    """
    df = customer_df
    customers = []
    for index, row in df.iterrows():
        customer = Customer(
            cust_no = int(row['CUST NO.']),
            position= (int(row['XCOORD.']), int(row['YCOORD.'])),
            demand = int(row['DEMAND']),
            ready_time = int(row['READY TIME']),
            due_date = int(row['DUE DATE']),
            service_time = int(row['SERVICE TIME']))
        customers.append(customer)
    return customers

# Intermediate functions #

# Get customer by its id
def customer_by_id(id,customers):
    """Finds a customer using its id
    Params: id : (int) customer id, customers : (list) list of all customers
    Returns: (Customer) customer 
    """
    for customer in customers:
        if customer.cust_no == id:
                return customer
    
# Distance matrix
def distance_matrix(customers):
    """Computes the distance between each customers
     Params: customers : (list) list of all customers
     Returns: (numpy.array) distance matrix
    """
    N = len(customers)
    res = np.zeros((N,N))
    customers_coordinates = [customer.position for customer in customers]
    for i in range(N):
        for j in range(N):
            x1,y1 = customers_coordinates[i][0],customers_coordinates[i][1]
            x2,y2 = customers_coordinates[j][0],customers_coordinates[j][1]
            res[i, j] = np.sqrt((x2 - x1)**2 + (y2 - y1)**2) # math.ceil(np.sqrt((x2 - x1)**2 + (y2 - y1)**2))
    return(res)

# Inverse distance matrix
def inverse_distance_matrix(customers):
    """Computes the inverse of the distance between each customers
    Params: customers : (list) list of all customers
    Returns: (numpy.array) inverse distance matrix
    """
    N = len(customers)
    res = np.zeros((N,N))
    customers_coordinates = [customer.position for customer in customers]
    for i in range(N):
        for j in range(N):
            x1,y1 = customers_coordinates[i][0],customers_coordinates[i][1]
            x2,y2 = customers_coordinates[j][0],customers_coordinates[j][1]
            if i==j :
              res[i,j] == 0.000001
            else :
              res[i, j] = 1/np.sqrt((x2 - x1)**2 + (y2 - y1)**2) # 1/math.ceil((np.sqrt((x2 - x1)**2 + (y2 - y1)**2)))
    return(res)

# Distance between 2 nodes (customers)
def distance(customer_1,customer_2,distances):
    """Gets the distance of two customers from the distance matrix
    Params: customer_1,customer_1 : (Customer) customers, distances : (numpy.array) distance matrix of the instance
    Returns: (int) ceiled distance between the two customers
    """
    id_1 = customer_1.cust_no
    id_2 = customer_2.cust_no
    return math.ceil(distances[id_1,id_2])

# Distance travelled
def total_distance(routes,distances):
    """Computes the total distance travelled in a solution
    Params: routes : (list) list of Vehicles forming the solution, distances : (numpy.array) distance matrix of the instance
    Returns: (double) total distance rounded to 2 decimals
    """
    res = 0
    for truck in routes:
        route = truck.route
        dist_per_route = 0

        for i in range(len(route)-1):
            previous_customer_id = route[i][0]
            current_customer_id = route[i+1][0]
            dist_per_route += distances[previous_customer_id][current_customer_id]

        res += dist_per_route

    return round(res,2)

import os

# Writing solution to .txt file for validator.py
def write_solution_to_file(solution, time, instance, distances):
    """Writes solution to the correct format for validator.py
    Params: solution : (list) solution, time : (str) time [1m,5m,un] in which the solution was obtained, instance : (str) instance [i1,i2...]
            distances : (numpy.array) distance matrix of the instance
    Returns: (double) .txt solution file
    """
    file_name = f"res-{time}-{instance}.txt"

    with open(file_name, "w") as file:
        # Write the number of routes
        file.write(f"{len(solution)}\n")

        # Write each route
        for i, truck in enumerate(solution, start=1):
            route_info = [f"{customer[0]}({customer[1]})" for customer in truck.route]
            route_str = "->".join(route_info)
            file.write(f"{i}: {route_str}\n")

        # Write the total distance
        total_distance_value = total_distance(solution, distances)
        file.write(f"{total_distance_value}\n")

    print(f"Solution written to {file_name}")

# Vehicle class 
class Vehicle:
    """Vehicle class
    """
    def __init__(self, id, cargo, depot):
        """Constructor
        """
        self.id = id # id of vehicle/route
        self.cargo= cargo # cargo carried by the vehicle
        self.position = depot.position # depot position
        self.time = 0 # time of start of service of the current customer
        self.route = [(0,0)] # (id of customer visited, time at which the service for the customer starts)

    def add_customer(self, customer, customers,distances):
        """Adds a customer on the vehicle's route
        """
        previous_customer = customer_by_id(self.route[-1][0],customers)
        # Update vehicle's cargo
        self.cargo -= customer.demand
        # Update time of the vehicle
        if self.time + previous_customer.service_time + distance(previous_customer,customer,distances) < customer.ready_time :
          # service starts when customer is ready
          self.time = customer.ready_time
        else:
          self.time += previous_customer.service_time + distance(previous_customer,customer,distances)
        # Update vehicle's position
        self.position = customer.position
        # Update vehicle's route
        self.route.append((customer.cust_no,self.time))

    def wait_time(self,customer,customers,distances):
      """Computes the time a vehicle will have to wait for a customer to open
      """
      previous_customer = customer_by_id(self.route[-1][0],customers)
      time_to_wait = customer.ready_time - self.time
      if time_to_wait <= 0:
        return 0
      else :
        return time_to_wait

    def heuristic_wait_time(self,customer,customers,distances):
      """Computes the inverse of the time a vehicle will have to wait for a customer to open
      """
      previous_customer = customer_by_id(self.route[-1][0],customers)
      time_to_wait = customer.ready_time - self.time
      if time_to_wait <= 0:
        return 1
      else :
        return 1/time_to_wait
      
# Constraints
def is_valid(customer,truck,depot,customers,distances):
    """Checks if the vehicle can visit a customer or not
    Params: customer : (Customer) customer to visit, truck : (Vehicle) vehicle, depot : (Customer) depot, customers : (list) list of all customers
            distances : (nump.array) distance matrix of the instance
    Returns: (boolean) True if the vehicle can visit the customer, False else
    """
    visited_customers_ids = [truck.route[i][0] for i in range(1,len(truck.route))] # depot excluded
    if len(visited_customers_ids) > 0: # not empty
        # each customer must be visited only once
        if customer.cust_no != 0 and customer.cust_no in visited_customers_ids :
        # print('Customer already visited')
            return False
    # customer's demand must be met
    if truck.cargo < customer.demand :
        # print('Not enough cargo')
        return False
    # customer's time window constraint
    previous_customer_id = truck.route[-1][0]
    previous_customer = customer_by_id(previous_customer_id,customers)
    # customer must be delivered before due date
    if truck.time + previous_customer.service_time + distance(previous_customer,customer,distances) > customer.due_date : # truck will not make it in time
        # print('Customer due time surpassed')
        return False
    # truck must be able to make it back on time to the depot
    if truck.time + previous_customer.service_time + distance(previous_customer,customer,distances) + customer.service_time + distance(customer,depot,distances) > depot.due_date :
        # print('Truck cannot make it back in time to depot')
        return False
    else :
        # print('Valid customer')
        return True