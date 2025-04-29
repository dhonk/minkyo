import os
import math
import minkyo.gmaps
import pickle

"""
Current thought process:

For set of drivers:
    1. Find closest rider
    2. If rider isn't already in a car, pick up in car
    3. Continue until seats filled / riders exhausted

okie googlemaps kinda hard     

lets start w the actual alg

lets start with a rider object
-- should driver be a separate object??
-- ye

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
    
    def capacity(self):
        return self.cap

    def __str__(self):
        return f"driver {self.name} @ {self.address} [{self.cap}]"

# utilizing inheritance has the added benefit of simplifying the distance calculation for the distance matrix

"""
Yo this joint is a CVRP problem, lit
"""

class solve:
    def __init__ (self, drivers, riders):
        self.drivers = drivers
        self.riders = riders
        # distance matrix
        self.distances = []
        # eventually add time matrix for time output...?

        # routes - stores the rider objects but can extract the addresses
        self.routes = {}
    
    # get distance between two nodes
    # for now, let's just implement distances as coordinates, use euclidean distance for simplicity atm
    # eventually, want to utilize the google maps to figure out distance
    def dist (self, a, b):
        # TODO: implement guardrails
        # coordinate / L2 distance
        '''
        return abs(math.sqrt((a.address[0]-b.address[0]) ** 2 + (a.address[1]-b.address[1]) ** 2))        
        '''

        # google maps distance
        route = minkyo.gmaps.get_route(a.placeId, b.placeId)
        d, _ = minkyo.gmaps.extract_from_route(route)
        return d

    # initialize the distance matrix
    def init_dists (self):
        # currently both drivers and riders are included in the distance matrix, this might be good to change in the future
        comb = self.drivers + self.riders
        # use inf because distance matrix may contain adjacent 
        self.distances = [[math.inf for _ in range(len(comb))] for _ in range(len(comb))]
        for c in range(len(comb)):
            for r in range(len(comb)):
                if c != r and type(comb[r]) is rider:
                    self.distances[c][r] = self.dist(comb[c], comb[r])
    
    # print out the distance matrix
    def show_distances (self):
        o = ""
        for r in self.distances:
            for c in r:
                o += (f"{c:.2f}, ")
            o += ("\n")
        print(o)

    # show routes
    def show_routes (self):
        print('routes:')
        o = ''
        for d in self.routes:
            o += f'{str(d)} : '
            for r in self.routes[d]:
                o += f'{str(r)} | '
            o += '\n'
        print(o)

    # show the total distance covered by all routes stored in a solution route
    def routes_dist (self):
        print('Distances: ')
        dists = []
        for i, d in enumerate(self.routes):
            print(f'{i}: ' + str(d))

            comb = self.drivers + self.riders
            # the distance 
            dist = 0
            # the previous address
            p_add = self.routes[d][0]
            for stop in self.routes[d][1:]:
                dist += self.distances[comb.index(p_add)][comb.index(stop)]
                p_add = stop
            print(dist)
            dists.append(dist)
        print(f'Average: {sum(dists)/len(dists)}')


    # nearest neighbor approach
    def find_routes_NN (self):
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

                # iterate over the riders (entire comb list in order to get indexing for the distance matrix):
                min_dist = math.inf
                min_r = None
                for i, r in enumerate(comb):
                    cdist = self.distances[comb.index(croute[-1])][comb.index(r)]
                    if type(r) == rider and r.color == 0 and cdist < min_dist:
                        min_dist = cdist
                        min_r = r

                # add next closest node to the route
                print(f'adding: {min_r}')
                croute.append(min_r)
                min_r.color = 1
                num_picked += 1
                cond = True

    # Currently: this uses a nearest neighbors approach
    # Maybe implement a different algorithm, like clarke and wright, but let's run w this for now