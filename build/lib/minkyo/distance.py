import os
import math
import minkyo.gmaps
import pickle
import random

"""
Note: solution functions require for total capacity to be greater than or equal to the number of riders.
"""

# human class super
class human:
    def __init__ (self, name, address, placeId):
        self.name = name
        self.address = address
        self.placeId = placeId # google maps place id

# rider (to track pick up status)
# color to track visitation bcs stack didn't work
class rider(human):
    def __init__ (self, name, address, placeId):
        super().__init__(name, address, placeId)
        self.color = 0
    
    def __str__(self):
        return f"rider {self.name} @ {self.address}"

# driver (to track capacity)
class driver(human):
    def __init__ (self, name, address, placeId, cap):
        super().__init__(name, address, placeId)
        self.cap = cap # driver capacity
        self.load = 0 # current riders
    
    def get_cap(self):
        return self.cap

    def get_load(self):
        return self.load

    def __str__(self):
        return f"driver {self.name} @ {self.address} [{self.cap}]"

# utilizing inheritance has the added benefit of simplifying the distance calculation for the distance matrix

"""
Yo this joint is a CVRP problem, lit
"""

class solve:
    def __init__(self, drivers=[], riders=[]):
        self.drivers = drivers
        self.riders = riders
        # distance matrix
        self.distances = []
        # distance storage
        self.dist_data = {}
        # eventually add time matrix for time output...?

        # routes - stores the rider objects but can extract the addresses
        self.routes = {}

    # add a driver
    def add_driver(self, driver):
        self.drivers.append(driver)

    # add a rider
    def add_rider(self, rider):
        self.riders.append(rider)
    
    # get distance between two nodes
    # for now, let's just implement distances as coordinates, use euclidean distance for simplicity atm
    # eventually, want to utilize the google maps to figure out distance
    def dist(self, a, b):
        # TODO: implement guardrails
        # coordinate / L2 distance
        '''
        return abs(math.sqrt((a.address[0]-b.address[0]) ** 2 + (a.address[1]-b.address[1]) ** 2))        
        '''

        # google maps distance
        
        # if the pids identical, return 0
        if a.placeId == b.placeId:
            return 0

        # check the distance storage if the id exists
        key = a.placeId + ' ' + b.placeId
        if key in self.dist_data:
            return self.dist_data[key]

        # else, call API and add the distance to the storage
        route = minkyo.gmaps.get_route(a.placeId, b.placeId)
        d, _ = minkyo.gmaps.extract_from_route(route)
        self.dist_data[key] = d
        return d

    # initialize the distance matrix
    def init_dists(self):
        # open the distance storage
        # TODO: later modify to try {placeId : {placeId : distance}}
        # TODO: later transition to sqlite?
        # structure: {placeId placeId : distance}
        with open('data.pickle', 'ab') as file:
            pickle.dump({}, file)

        with open('data.pickle', 'rb') as file:
            self.dist_data = pickle.load(file)

        # currently both drivers and riders are included in the distance matrix, this might be good to change in the future
        comb = self.drivers + self.riders
        # use inf because distance matrix may contain adjacent 
        self.distances = [[math.inf for _ in range(len(comb))] for _ in range(len(comb))]
        for c in range(len(comb)):
            for r in range(len(comb)):
                if c != r and type(comb[r]) is rider:
                    self.distances[c][r] = self.dist(comb[c], comb[r])
        
        # save the distance storage
        # structure: {placeId placeId : distance}
        with open('data.pickle', 'wb') as file:
            pickle.dump(self.dist_data, file)

    # print out the distance matrix
    def show_distances(self):
        o = ""
        for r in self.distances:
            for c in r:
                o += (f"{c:.2f}, ")
            o += ("\n")
        print(o)

    # get string of routes
    def route_to_str(self):
        o = ''
        for d in self.routes:
            skip = True 
            o += f'{d.name}: '
            for r in self.routes[d]:
                if skip:
                    skip = False
                    continue
                o += f'{r.name}, '
            o += '\n'
        return o

    # show routes
    def show_routes(self):
        print('routes:')
        print(self.route_to_str())

    def show_routes_verbose(self):
        print('routes:')
        o = ''
        for d in self.routes:
            skip = True
            o += f'{str(d)} : '
            for r in self.routes[d]:
                if skip:
                    skip = False
                    continue
                o += f'{str(r)} | '
            o += '\n'
        print(o)

    # find the distance covered by a route
    def route_dist(self, route):
        comb = self.drivers + self.riders
        prev = route[0]
        dist = 0
        for i in range(1, len(route)):
            dist += self.distances[comb.index(prev)][comb.index(route[i])]
            prev = route[i]
        return dist

    def routes_dist(self):
        dists = []
        for i, d in enumerate(self.routes):
            dist = self.route_dist(self.routes[d])
            dists.append(dist)
        return sum(dists)

    # show the total distance covered by all routes stored in a solution route
    def print_dist(self):
        print('Distances: ')
        dists = []
        for i, d in enumerate(self.routes):
            dist = self.route_dist(self.routes[d])
            print(f'{i}. {d} : {dist/1609:0.2f} miles')
            dists.append(dist)
        print(f'Average: {0.00 if len(dists) == 0 else sum(dists)/len(dists)/1609:0.2f} miles')

    # check if total cap >= # riders
    def solveable(self):
        if len(self.riders) > sum(d.cap for d in self.drivers):
            return False
        return True

    # brute force approach
    # permute through every single rider/driver combination possible
    # considerations:
    # easy part is to permute through every ordering of rider (O(m!))
    # -> find every permutation of the riders array
    # difficult part is to figure out with the different sizings as well
    # -> working through:
    # ---> eg driver with 4 available seats, there are 5 possible arrangements, 0, 1, 2, 3, 4
    # ---> also need to consider the total number of riders in order for every rider to be seated
    # ---> so eg for 2 drivers, 3 riders:
    # -----> 3 : 0, 2 : 1, 1 : 2, 0 : 3 are all valid combinations
    # ---> alg : consider total capacity
    # ---> recursively, permute through each driver allocation

    def find_routes_brute(self):
        # initialize distance matrix
        self.init_dists()

        # initialize routes
        self.routes = {d : [d] for d in self.drivers}

        # initalize colors
        for r in self.riders:
            r.color = 0

        # comb matrix for indexing objects to the distance matrix
        comb = self.drivers + self.riders

        # setting up the 
        

    # brute force ish approach
    # no GREEDY APPROACH
    # algorithm: find driver : rider pair that minimizes the distance
    # O(m^2*n), m = # of riders, n = # of drivers
    def find_routes_greedy(self):
        # initialize distance matrix
        self.init_dists()

        # initialize routes
        self.routes = {d : [d] for d in self.drivers}

        # initalize colors to all not put in a car
        for r in self.riders:
            r.color = 0

        # comb matrix for indexing to the distance matrix
        comb = self.drivers + self.riders

        for _ in range(len(self.riders)):
            # find smallest increase to the global distance
            min_dist = math.inf
            min_rte = None # store the key val for the route with the min dist addition
            min_rte_idx = 0 # store the actual minimum index for ease of access
            min_rider_idx = 0 # store the minimum next rider index

            for d in self.routes:
                if len(self.routes[d]) > d.cap:
                    continue

                last_stop_idx = comb.index(self.routes[d][-1])
                for i, dist in enumerate(self.distances[last_stop_idx]):
                    if dist < min_dist and comb[i].color == 0:
                        min_dist = dist
                        min_rte = d
                        min_rte_idx = last_stop_idx
                        min_rider_idx = i
                        
            self.routes[min_rte].append(comb[min_rider_idx])
            comb[min_rider_idx].color = 1

    # nearest neighbor approach
    def find_routes_NN(self):
        """ 
        - starting from each driver:
        - find nearest rider, start the route
        - each iter, find the next nearest rider, until capacity for car filled

        This heuristic is not the optimal solution, but should provide a "good enough" approach for most use cases in the projects' initial phase
        Eventually goal is to replace with more optimal algorithms
        """
        
        # this code is so hideous but idc anymore i just want this to work

        # initialize routes
        self.routes = {d : [d] for d in self.drivers}
        # initialize distance matrix
        self.init_dists()
        # initialize colors to all not put in a car
        for r in self.riders:
            r.color = 0

        # num_picked
        num_picked = 0

        # iter counter to keep balanced loading
        iters = 0

        # create combined list access distance matrix easier
        # i really dislike this implementation thou let's maybe change it later?
        comb = self.drivers + self.riders
        # flag to check ride fillage
        cond = True
        # while there are people that haven't been visited yet OR while all drivers' capacity is not yet filled
        while cond:
            cond = False
            for d in self.drivers:
                # check if there are riders that need to be picked up
                if num_picked >= len(self.riders):
                    break

                # current route
                croute = self.routes[d]
                # check if cap met yet
                if len(croute) > d.cap:
                    continue
                # balancer
                if d.load > iters:
                    continue

                # iterate over the riders (entire comb list in order to get indexing for the distance matrix):
                min_dist = math.inf
                min_r = None
                min_i = 0
                for i, r in enumerate(comb):
                    cdist = self.distances[comb.index(croute[-1])][comb.index(r)]
                    if type(r) == rider and r.color == 0 and cdist < min_dist:
                        min_dist = cdist
                        min_r = r
                        min_i = i

                # add next closest rider(s) to the route
                print(f'adding: {min_r}')

                # begin by adding initial rider:
                croute.append(min_r)
                min_r.color = 1
                num_picked += 1
                d.load += 1

                # SAME STOP OPTIMIZATION
                # also keeping balanced car loads
                # for tests.basic, this optimization saves an average distance of 0.67 miles
                # single furthest distance reduced by 1.67 miles

                # now check for others from same location:
                for i in range(len(self.distances[min_i])):
                    if self.distances[min_i][i] == 0 and len(croute) < d.cap:
                        croute.append(comb[i])
                        comb[i].color = 1
                        num_picked += 1
                        d.load += 1
                cond = True
                iters += 1

    # Currently: this uses a nearest neighbors approach
    # Maybe implement a different algorithm, like clarke and wright, but let's run w this for now

