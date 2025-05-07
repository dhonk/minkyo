import os
import math
from dotenv import load_dotenv

load_dotenv()

gmap_api_key = os.getenv("GMAP_API_KEY")

# Don't actually do this later
print(gmap_api_key)

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
    def __init__ (self, address):
        self.address = address

# rider (to track pick up status)
# use color to signify visit status
# white: not picked up: 0
# black: picked up: 1
class rider(human):
    def __init__ (self, address):
        super().__init__(address)
        self.color = 0
    
    def __str__(self):
        return f"rider {self.address}"

# driver (to track capacity)
class driver(human):
    def __init__ (self, address, cap):
        super().__init__(address)
        self.cap = cap # driver capacity
    
    def capacity(self):
        return self.cap

    def __str__(self):
        return f"driver {self.address} [{self.cap}]"

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
        comb = self.drivers + self.riders
        # use inf because distance matrix may contain adjacent 
        self.distances = [[math.inf for _ in range(len(comb))] for _ in range(len(comb))]
        for c in range(len(comb)):
            for r in range(len(comb)):
                # type check : make sure that distances between drivers aren't being registered in the matrix (that would be kinda bad lowk)
                if type(comb[c]) is driver and type(comb[r]) is driver:
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

    # show routes
    def show_routes (self):
        o = ""
        for d in self.routes:
            o += f"{str(d)} : "
            for r in self.routes[d]:
                o += f"{str(r)} | "
            o += "\n"
        print(o)

    # solve for the routs
    def find_routes(self):
        self.routes = {d: [d] for d in self.drivers}

        # initial route discovery
        # solve by getting the nearest rider and kinda shoving onto the route
        # iteratively until riders run out or driver runs out of space
        
        # need to use this ugly lil comb thingy in order to get index access from the distance matrix
        comb = self.drivers + self.riders
        
        # wait what the frick
        # idk anymore but make a set of the riders (remove the one that is found to be closest)
        ride_set = set(self.riders)

        cond = True
        while ride_set and cond:
            cond = False
            for driver in self.routes:
                # current route list
                clist = self.routes[driver]

                # check if car is full, if there are still riders
                if len(clist) >= driver.capacity():
                    continue

                # get most last node in route
                cnode = clist[-1]
                # get row of distances from last node in the route
                t = self.distances[comb.index(cnode)]
                # isolate unvisited nodes only
                unvisit = [i for i, node in enumerate(comb) if isinstance(node, rider) and node in ride_set]
                if not unvisit: 
                    continue

                # find the nearest rider
                nearest = comb[t.index(min(t[i] for i in unvisit))]
                # append to the current route list
                clist.append(nearest)
                
                # remove the nearest rider from the ride_set
                ride_set.remove(nearest)
                cond = True

        # Currently: this uses a nearest neighbors approach
        # Maybe implement a different algorithm, like clarke and wright, but let's run w this for now


