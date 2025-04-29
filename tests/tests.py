from minkyo.distance import *

if __name__ == '__main__':
    '''
    drive1 = driver("1", (0, 0), '', 2)
    drive2 = driver("2", (10, 10), '', 3)

    drives = [drive1, drive2]
    rides = [
        rider("1", (0, 1), ''),
        rider("2", (0, 2), ''),
        rider("3", (9, 9), ''),
        rider("4", (9, 8), ''),
        rider("5", (0, 1), ''),
    ]

    '''
    
    drives = [
        driver('toebie', '243 chico', 'ChIJiT24a25qjoARQ0U8cZDdZmw', 3),
        driver('not toebie', '243 chico', 'ChIJiT24a25qjoARQ0U8cZDdZmw', 3),
    ]

    rides = [
        rider('noah', '122 Nobel Drive, Santa Cruz, CA, USA', 'EiQxMjIgTm9iZWwgRHJpdmUsIFNhbnRhIENydXosIENBLCBVU0EiMBIuChQKEgkrAw5ExUGOgBElcSBwRGPKCRB6KhQKEgnZhPHdxEGOgBG9kVblpM7MWw'),
        rider('jeff', '122 Nobel Drive, Santa Cruz, CA, USA', 'EiQxMjIgTm9iZWwgRHJpdmUsIFNhbnRhIENydXosIENBLCBVU0EiMBIuChQKEgkrAw5ExUGOgBElcSBwRGPKCRB6KhQKEgnZhPHdxEGOgBG9kVblpM7MWw'),
        rider('bdon', 'rcc', 'ChIJMXtLEZlBjoARkq5QnGwk-C8'),
    ]

    soln = solve(drives, rides)
    soln.init_dists()
    soln.show_distances()

    soln.find_routes_NN()
    soln.show_routes()
    soln.routes_dist()
    