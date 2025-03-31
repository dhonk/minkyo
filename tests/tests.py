from minkyo.main import *

if __name__ == '__main__':
    drive1 = driver("1", (0, 0), 2)
    drive2 = driver("2", (10, 10), 3)

    drives = [drive1, drive2]
    rides = [
        rider("1", (0, 1)),
        rider("2", (0, 2)),
        rider("3", (9, 9)),
        rider("4", (9, 8)),
        rider("5", (1, 2)),
    ]

    soln = solve(drives, rides)
    soln.init_dists()
    soln.show_distances()

    soln.find_routes_NN()
    soln.show_routes()

    soln.routes_dist()
    