Data I can harvest from trulia.com

	51 states
	19982 locals area statistic information (average sqft, price, trends.)
	
	2,196,366+ property for sold
	3,000,000+ property for rent
	7,000,000+ property recently sold (with in 1 years)
	
	12 million + property

the detail I can get, not only and not ensured:
	sqft: 3320
	beds: 3.5
	baths: 2
	house_type: single house, town house, condo, ...
	floor_type: Tile - Ceramic, Vinyl
	exterior: Brick
	lot size: 5120
	heating fuel: natural gas
	rooms: 9
	built-in: 2012
	parking: 2

My capability:
	one computer:
		time:
			to get the full list:
				19982 * 3 seconds = 2 days
		
			to get all property detail:
				1 second per property
				12million = 138 days
				
	if I can have more bandwidth for internet, and applied multi-thread, I can make it faster.
	
Completed work. (It's Done)
	real-time query by: address + zipcode, address + city. Return property detail 
	Framework, library for this trulia crawler. 