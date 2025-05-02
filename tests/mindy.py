from minkyo.distance import *

''' 
Real world case example, from rides back home 4/30/2025
John : Alex, Danny, MoiMoi, Sandee : 5.4 miles
Andy: Sofacho, Clara, Mindy : 1.1 miles
Jason: Dylan, Toby, Taewoo : 0.2 miles
Annie: Jacob, Eric, Victoria, Natalie : 4.2 miles 
Ashley: Amelia, Aya, Brandon : 5.9 miles
avg: 3.36 miles

Minimum possible solution:


nn + cluster:
John: Dylan, Bdon, Victoria : 4.42 miles
Andy: Toebie, Taewoo, Danny, Natalie : 4.77 miles
Jason: SofaCho, Clara, Mindy, MoiMoi : 4.30 miles
Annie: Alex, Sandee, Jacob : 4.06 miles
Ashley: Amelia, Eric, Sandee : 5.11 miles
avg: 4.53 miles
min dist increased by 3.86 miles
max dist increased by 0.21 miles
avg dist increased by 1.17 miles

bruteish approach:
John: Dylan, Toebie, Taewoo, : 0.27 miles
Andy: Bdon, Danny, Victoria, Natalie, : 4.45 miles
Jason: MoiMoi, Sandee, Jacob, Eric, : 4.54 miles
Annie: SofaCho, Clara, Mindy, Alex, : 2.95 miles
Ashley: Amelia, Aya, : 5.11 miles
avg: 3.46 miles
min dist increased by 0.10 miles
max dist increased by -1.36 miles
avg dist increased by 0.07 miles

'''

# driver('me', '416 poplar', 'ChIJKdRoaxpAjoARKfkOmL50Uq4', 4),
# driver('toebie', '243 chico', 'ChIJiT24a25qjoARQ0U8cZDdZmw', 4),  
# rider('noah', '698 Nobel Drive, Santa Cruz, CA, USA', 'EiQxMjIgTm9iZWwgRHJpdmUsIFNhbnRhIENydXosIENBLCBVU0EiMBIuChQKEgkrAw5ExUGOgBElcSBwRGPKCRB6KhQKEgnZhPHdxEGOgBG9kVblpM7MWw'),
# rider('jeff', '122 Robinson Lane, Santa Cruz, CA, USA', 'EiQxMjIgTm9iZWwgRHJpdmUsIFNhbnRhIENydXosIENBLCBVU0EiMBIuChQKEgkrAw5ExUGOgBElcSBwRGPKCRB6KhQKEgnZhPHdxEGOgBG9kVblpM7MWw'),
            
def test():
    drivers = [
        driver('John', '292 Swanton Blvd', 'ChIJtSSP4HFqjoARKBOB7kCaK7Q', 4),
        driver('Andy', '292 Swanton Blvd', 'ChIJtSSP4HFqjoARKBOB7kCaK7Q', 4),
        driver('Jason', '292 Swanton Blvd', 'ChIJtSSP4HFqjoARKBOB7kCaK7Q', 4),
        driver('Annie', 'Pacific Shores', 'ChIJyX2IHeBBjoARcRY-sQBSx68', 4),
        driver('Ashley', '127 Pearl Street', 'ChIJIXO7W59qjoARzhOjjU499cI', 4),
    ]

    rides = [
        # John
        rider('Alex', 'UCSC Village', 'ChIJr5zBCrxBjoARwaNDorG0B6c'),
        rider('Danny', 'UCSC Core West Parking Structure', 'ChIJlczXdHVBjoARwqjoyseHkfw'),
        rider('MoiMoi', 'Merrill College', 'ChIJrQECDKdBjoARj3WQx5XV3nU'),
        rider('Sandee', 'College Nine', 'ChIJg5nvWgpBjoARREJcQDkWM6o'),
        

        # Jason
        rider('Dylan', '292 Swanton Blvd', 'ChIJtSSP4HFqjoARKBOB7kCaK7Q'),
        rider('Toebie', '243 Chico', 'ChIJiT24a25qjoARQ0U8cZDdZmw'),
        rider('Taewoo', '243 Chico', 'ChIJiT24a25qjoARQ0U8cZDdZmw'),
        
        # Annie
        rider('Jacob', 'C9 Apartments', 'ChIJg5nvWgpBjoARREJcQDkWM6o'),
        rider('Eric', 'College Nine', 'ChIJg5nvWgpBjoARREJcQDkWM6o'),
        rider('Victoria', 'College 10', 'ChIJyVf7_gpBjoAR16yOfEaMy_s'),
        rider('Natalie', 'College 10', 'ChIJyVf7_gpBjoAR16yOfEaMy_s'),

        # Ashley
        rider('Amelia', '1010 Pacific Ave', 'ChIJv3vfkSdAjoARa88izbrekeQ'),
        rider('Aya', 'College Nine', 'ChIJg5nvWgpBjoARREJcQDkWM6o'),
        rider('Bdon', 'RCC', 'ChIJMXtLEZlBjoARkq5QnGwk-C8'),

        
        # Andy
        rider('SofaCho', '139 Alamo Ave', 'ChIJI65yLN9BjoARDF2Df2tIPLM'),
        rider('Clara', '139 Alamo Ave', 'ChIJI65yLN9BjoARDF2Df2tIPLM'),
        rider('Mindy', '139 Alamo Ave', 'ChIJI65yLN9BjoARDF2Df2tIPLM'),
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


if __name__ == '__main__':
    test()    
    