# Ridemaster

## Purpose
I'm part of a really awesome club called SOON Movement Global, but we often ran into the issue of having difficulty in organizing rides. Often after events, we would try to go grab food, or have to figure out how to take our members home. But figuring out who wanted to attend, who was willing to drive, and how to allocate the drivers efficiently would always be a logistical nightmare.

minkyo is a discord application purpose built to address this issue, and is intended to automate the process of:
1. figuring out who wants to go
2. figuring out who can drive, and how many people
3. figuring out who should go in which car

The application uses a simple Nearest Neighbor heuristic to allocate the rides, and so doesn't produce a globally optimal solution, but for our purposes, most often does produce a "good enough" approach.

## Usage
### If adding to your own guild:
Unfortunately, minkyo is not available to add across multiple guilds: as I am currently not willing to pay for Google Maps API crecits. However, fork this repository to run the bot locally.

Upon forking, create a .env file in the top level of the repository, where you will need the following:
GMAP_API <your api key here>
DISC_API <your discord api key here>


