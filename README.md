# minkyo

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

GMAP_API {your api key here}

DISC_API {your discord api key here}

### Commands:
* /setup_rider {address} {_OPTIONAL_ user} : Use this command to set up the information of someone who needs a ride
  * address : String representation of the address of someone who needs a ride (i.e. not a driver)
  * user : Optional parameter, use this to set up someone else as someone who needs a ride
* /setup_driver {address} {capacity} {_OPTIONAL_ user} : Use this command to set up the information of someone who will be driving
  * address : String representation of the address of a driver
  * capacity : The number of passengers the driver can take (not including themselves)
  * user : Optional parameter, use this to set up someone else as someone who will be driving
* /makeride {_OPTIONAL_ ping} {_OPTIONAL_ dest} : Use this command to have **minkyo** send a message
  * ping : The role/member to mention
  * dest : The destination of where everyone will be going
  * Users will then have to react to the message corresponding to whether they will be driving or if they need a ride
* /genride : Use this command for **minkyo** to create a list of rides
* /hello : Replies with "hi wsp", used mainly as diagnostic tool
* /gen_mindy : I'm genuinely not sure why this command is still here, even after syncing command tree/etc, too lazy to figure out how to remove atp
