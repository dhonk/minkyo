import os
import math
import gmaps

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
    def __init__ (self, name, address):
        self.name = name
        self.address = address

# rider (to track pick up status)
# use color to signify visit status
# white: not picked up: 0
# black: picked up: 1
class rider(human):
    def __init__ (self, name, address):
        super().__init__(name, address)
        self.color = 0
    
    def __str__(self):
        return f"rider {self.name} @ {self.address}"

# driver (to track capacity)
class driver(human):
    def __init__ (self, name, address, cap):
        super().__init__(name, address)
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
        # routes - stores the rider objects but can extract the addresses
        self.routes = {}
    
    # get distance between two nodes
    # for now, let's just implement distances as coordinates, use euclidean distance for simplicity atm
    # eventually, want to utilize the google maps to figure out distance
    def dist (self, a, b):
        # TODO: implement guardrails
        return abs(math.sqrt((a.address[0]-b.address[0]) ** 2 + (a.address[1]-b.address[1]) ** 2))        

    # initialize the distance matrix
    def init_dists (self):
        # currently both drivers and riders are included in the distance matrix, this might be good to change in the future
        comb = self.drivers + self.riders
        # use inf because distance matrix may contain adjacent 
        self.distances = [[math.inf for _ in range(len(comb))] for _ in range(len(comb))]
        for c in range(len(comb)):
            for r in range(len(comb)):
                # type check : make sure that distances between drivers aren't being registered in the matrix (that would be kinda bad lowk)
                if type(comb[r]) is driver:
                    self.distances[c][r] = math.inf
                else:
                    self.distances[c][r] = self.dist(comb[c], comb[r])
    
    # print out the distance matrix
    def show_distances (self):
        o = ""
        for r in self.distances:
            for c in r:
                o += (f"{c:.2f}, ")
            o += ("\n")
        print(o)

    # nearest neighbor approach
    def find_routes_NN (self):
        """ 
        - starting from each driver:
        - find nearest rider, start the route
        - each iter, find the next nearest rider, until capacity for car filled

        This heuristic is not the optimal solution, but should provide a "good enough" approach for most use cases in the projects' initial phase
        Eventually goal is to replace with more optimal algorithms
        """
        
        # initialize routes
        self.routes = {d : [d] for d in self.drivers}
        # initialize distance matrix
        self.init_dists()

        # create combined list access distance matrix easier
        # i really dislike this implementation thou let's maybe change it later?
        comb = self.drivers + self.riders
        # visit stack (technically a queue but whatevs)
        stack = self.riders
        # flag to check ride fillage
        cond = True
        # while there are people that haven't been visited yet OR while all drivers' capacity is not yet filled
        while stack and cond:
            cond = False
            for d in self.drivers:
                # current route
                croute = self.routes[d]
                # check if cap met yet
                if len(croute) > d.cap:
                    continue

                # distances from the last visited node
                cdists = self.distances[comb.index(croute[-1])]
                # getting the unvisited indices
                unvisited = [i for i, x in enumerate(comb) if x in stack and isinstance(x, rider)]
                # find next closest available node
                next = comb[cdists.index(min(cdists[i] for i in unvisited))]
                # add next closest node to the route
                croute.append(next)
                # remove from the stack
                stack.remove(next)
                # update cond
                cond = True
                

    # show routes
    def show_routes (self):
        o = ""
        for d in self.routes:
            o += f"{str(d)} : "
            for r in self.routes[d]:
                o += f"{str(r)} | "
            o += "\n"
        print(o)

    # show the total distance covered by all routes stored in a solution route
    def routes_dist (self):
        for i, d in enumerate(self.routes):
            print(f"{i}: " + str(d))
            # the distance 
            dist = 0
            # the previous address
            p_add = self.routes[d][0]
            for stop in self.routes[d][1:]:
                dist += self.dist(p_add, stop)
                p_add = stop
            print(dist)

        # Currently: this uses a nearest neighbors approach
        # Maybe implement a different algorithm, like clarke and wright, but let's run w this for now