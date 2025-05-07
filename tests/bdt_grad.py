from minkyo.distance import *

''' 
Real world case example, from rides back home from BDT grad
Toby: Alex, Aya, Ephram : 4.6 miles
Clara: Sofa, Brandon, Luke : 2.6 miles
Andy: MoiMoi, Jacob, Eric : 4.5 miles
John: Mindy, Dylan, Taewoo : 0.2 miles
avg : 2.98 miles

Minimum possible solution:

nn + cluster:

avg:  miles
min dist increased by  miles
max dist increased by  miles
avg dist increased by  miles

bruteish approach:
Toebie: Taewoo, : 0.00 miles
Clara: SofaCho, Mindy, Alex, Aya, : 3.44 miles
John: Dylan, Bdon, Luke, Ephram, : 4.43 miles
Andy: MoiMoi, Jacob, Eric, : 4.54 miles
avg: 3.10 miles
min dist increased by -0.2 miles
max dist increased by -0.06 miles
avg dist increased by 0.12 miles

'''

# driver('me', '416 poplar', 'ChIJKdRoaxpAjoARKfkOmL50Uq4', 4),
# driver('toebie', '243 chico', 'ChIJiT24a25qjoARQ0U8cZDdZmw', 4),  
# rider('noah', '698 Nobel Drive, Santa Cruz, CA, USA', 'EiQxMjIgTm9iZWwgRHJpdmUsIFNhbnRhIENydXosIENBLCBVU0EiMBIuChQKEgkrAw5ExUGOgBElcSBwRGPKCRB6KhQKEgnZhPHdxEGOgBG9kVblpM7MWw'),
# rider('jeff', '122 Robinson Lane, Santa Cruz, CA, USA', 'EiQxMjIgTm9iZWwgRHJpdmUsIFNhbnRhIENydXosIENBLCBVU0EiMBIuChQKEgkrAw5ExUGOgBElcSBwRGPKCRB6KhQKEgnZhPHdxEGOgBG9kVblpM7MWw'),
            

if __name__ == '__main__':

    drivers = [
        driver('Toebie', '243 chico', 'ChIJiT24a25qjoARQ0U8cZDdZmw', 4),  
        driver('Clara', '139 Alamo Ave', 'ChIJI65yLN9BjoARDF2Df2tIPLM', 4),
        driver('John', '292 Swanton Blvd', 'ChIJtSSP4HFqjoARKBOB7kCaK7Q', 4),
        driver('Andy', '292 Swanton Blvd', 'ChIJtSSP4HFqjoARKBOB7kCaK7Q', 4),
        ]

    rides = [
        # Toby
        rider('Alex', 'UCSC Village', 'ChIJr5zBCrxBjoARwaNDorG0B6c'),
        rider('Aya', 'College Nine', 'ChIJg5nvWgpBjoARREJcQDkWM6o'),
        rider('Ephram', 'College Nine', 'ChIJg5nvWgpBjoARREJcQDkWM6o'),

        # Clara
        rider('SofaCho', '139 Alamo Ave', 'ChIJI65yLN9BjoARDF2Df2tIPLM'),
        rider('Bdon', 'RCC', 'ChIJMXtLEZlBjoARkq5QnGwk-C8'),
        rider('Luke', 'RCC', 'ChIJMXtLEZlBjoARkq5QnGwk-C8'),

        # Andy
        rider('MoiMoi', 'Merrill College', 'ChIJrQECDKdBjoARj3WQx5XV3nU'),
        rider('Jacob', 'C9 Apartments', 'ChIJg5nvWgpBjoARREJcQDkWM6o'),
        rider('Eric', 'College Nine', 'ChIJg5nvWgpBjoARREJcQDkWM6o'),

        # John
        rider('Mindy', '139 Alamo Ave', 'ChIJI65yLN9BjoARDF2Df2tIPLM'),
        rider('Taewoo', '243 Chico', 'ChIJiT24a25qjoARQ0U8cZDdZmw'),
        rider('Dylan', '292 Swanton Blvd', 'ChIJtSSP4HFqjoARKBOB7kCaK7Q'),
    ]

    soln = solve(drivers, rides)
    soln.init_dists()
    soln.show_distances()

    print('NN approach:')
    soln.find_routes_NN()
    soln.show_routes()
    soln.print_dist()

    print('\nGreedy approach:')
    soln.find_routes_greedy()
    soln.show_routes()
    soln.print_dist()

    