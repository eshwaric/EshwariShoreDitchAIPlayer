###########
### AI Controller with HTTP abstracted away
###
### DB is a wrapper for whatever storage is backing the AI
### Use this for storage across games
###
### game contains a "storage" object which is a dict which will be
### persisted after returning
###
###########

from game import RESOURCES, GENERATOR_COST, GENERATOR_IMPROVEMENT_COST, PR_COST, MAX_RESOURCE_GENERATORS, MAX_IMPROVED_RESOURCE_GENERATORS
import operator
THRESHOLD = 10

def start_game(db, game):
	# A new game is starting
	print "Starting a game"

def start_turn(db, game, actions):
	# Start of a turn
	# We have to end the turn with game.end_turn() when we're done
	# alhough we only get 15 seconds to act before our turn is ended by force
	
	# actions is a dict of things which have happened since my last turn,
	# where the keys are player ids, and the values are lists of actions taken,
	# each action is a dict which has an 'action' key (which can be 'purchase-pr', 'trade', etc.)

	#Current Requirement
	requirements={} 

	#To eliminate trade where nothing was offered
	def empty_offers(trade):
		if len(trade['offer'].keys())!=0:
			return True
		else:
			return False
	#To filter trades which have resources i need
	def offers_I_need(trade):
		
		for res in trade['offer'].keys():
			#if game.resources.get(res,0)<trade['offer'].get(res,0):
			if res in requirements and requirements.get(res,0)<trade['offer'].get(res,0):
				return True
		return False
	#To eliminate trades with requests i cant fulfill
	def requests_I_can_fulfill(trade):
		myResToCheck = set(game.resources.keys()).intersection(set(trade['request'].keys()))
		for res in myResToCheck:
			if game.resources.get(res,0)>trade['request'].get(res,0):
				#I have some resource in this trade that I can fulfill - Keep the trade
				return True
		#Coming here means I cannot offer any of the requested res - chuck the trade
		return False
			
	def trade_for(requirements):
		# This just figures out how much I can give away without harming the minimum requirements
		# then offers everything extra I have for everything I need.
		# It's very dumb, you should replace it
		request = {}
		offer = {}

		
		#Understand the trade of opponent rejected
		oppTrades = actions.values()
		oppTradesFlattened = []
		rejectedOppTrades = []
		#Concatenate all oppponents action lists
		for iterator in oppTrades:
			oppTradesFlattened.extend(iterator) 
		#create list of rejected trades
		for trade in oppTradesFlattened:
			if trade['action']=='trade-rejected':
				rejectedOppTrades.append({u'request': trade['request'], u'offer': trade['offer']});
		
		#Remove trades that had empty offers
		if len(rejectedOppTrades)>0:
			tmp = []
			tmp  = filter(empty_offers,rejectedOppTrades)
			rejectedOppTrades = tmp
		
		#Filter trades which have resources I need
		if len(rejectedOppTrades)>0:
			tmp = []
			tmp = filter(offers_I_need,rejectedOppTrades)
			rejectedOppTrades = tmp

		#Remove things i dont need in the offer of those trades
		if len(rejectedOppTrades)>0:
			for trade in rejectedOppTrades:
				for res in trade['offer'].keys():
					#if game.resources[res]>trade['offer'][res]:
					if res in requirements and requirements[res]>trade['offer'][res]:
						del trade['offer'][res]
		#Remove trades that have empty offers
		if len(rejectedOppTrades)>0:
			tmp = []
			tmp  = filter(empty_offers,rejectedOppTrades)
			rejectedOppTrades = tmp

		#find which trade will give me maximum resources
		if (len(rejectedOppTrades)>0):
			for trade in rejectedOppTrades:
				trade['benefit'] = sum(trade['offer'].values())
			rejectedOppTrades = sorted(rejectedOppTrades,key=operator.itemgetter('benefit'))

		#At this point i have trades where maximum of the resources required by me is in last place
		#Find if there is a offer in the trades whose request value can be satisfied with my resources
		#if found make myReq->tradeOffer and myOffer->sum(tradeReqVal+1)
		i = len(rejectedOppTrades)-1
		newoffer={}
		affordableVal= 0
		for res in game.resources.keys():
			if game.resources[res]>1:
				affordableVal=affordableVal+game.resources[res]-1
		#Need to simplyfy this logic is written		
		while(i>=0):
			request = rejectedOppTrades[i]['offer']
			valOfReq = sum(request.values())
			if(affordableVal>valOfReq):
				#can afford this req
				print 'affordable req:',request,'resources:',game.resources
				valOfOffer  = 0
				myCopy = game.resources;
				#print 'myCopy',myCopy
				while(valOfOffer<=valOfReq):
					for res in game.resources.keys():
						if myCopy[res]>1:
							if res in newoffer:
								newoffer[res]=newoffer[res]+1
								
							else:
								newoffer[res]=1
							myCopy[res]-=1
							valOfOffer+=1
							#print 'mycopy:',myCopy,'newoffer:',newoffer
						if valOfOffer>valOfReq:
							break;
				break;
			else:
				#move further up the list
				i = i-1

			
		#print 'offer is:',offer,'new offer:',newoffer
		oldOffer=offer
		if len(newoffer.keys())!=0:
			offer=newoffer
			print 'sent new offer:'
		

		result = game.trade(offer, request)
		#print 'offer:',offer,'req:',request,'result:',result
		
		##Trading with bank only if other players have not accepted by reducing the req
		#But trade only if you have a lot of resources
		
		if (sum(game.resources.values())>THRESHOLD):
			bankReq=request
			bankOffer=offer

			if result==False:
				#find how many resources can i ask from the bank
				askBank=sum(offer.values())/4
				if(askBank>0):
					if (sum(bankReq.values())>askBank):
						#Modify the request for the bank
						resReq = bankReq.keys()
						asking=0
						for res in resReq:
							#asking+=bankReq[res]
							if(asking+bankReq[res]>askBank):
								#bankReq[res]=bankReq[res]-(asking-askBank)
								bankReq[res]=(askBank-asking)
								asking +=bankReq[res]
							else:
								asking+=bankReq[res]
							print 'bank req is',bankReq
						#Modify the offering for the bank
						toDeductVal = sum(offer.values())%4
						deducted = toDeductVal
						resOffer = bankOffer.keys()
						for res in resOffer:
							offering = bankOffer[res]
							if offering >= deducted:
								bankOffer[res]=bankOffer[res]-deducted
							
							else:
								bankOffer[res]=0
						
							deducted = deducted - offering
							if deducted<=0:
								break;
						
				else:
					bankReq={}
					bankOffer={}
				
				result = game.trade(bankOffer, bankReq)
				#print 'bankoffer:',bankOffer,'bankreq:',bankReq,'result',result
		return result

	### First try to trade for resources I need
	
	if sum(game.generators.values()) < MAX_RESOURCE_GENERATORS:
		# Can build generators - try to trade for them
		requirements = GENERATOR_COST
		if trade_for(GENERATOR_COST):
			taking_turn = True

	if sum(game.improved_generators.values()) < MAX_IMPROVED_RESOURCE_GENERATORS:
		# Can improve one of our existing ones
		requirements = GENERATOR_IMPROVEMENT_COST
		if trade_for(GENERATOR_IMPROVEMENT_COST):
			taking_turn = True
	requirements = PR_COST
	trade_for(PR_COST)

	# Then spend the resources

	while game.can_purchase_generator() and game.turn:
		generator_type = game.purchase_generator()
		print "Purchased %s" % generator_type

	while game.can_upgrade_generator() and game.turn:
		generator_type = game.upgrade_generator()
		print "Upgraded %s" % generator_type

	while game.can_purchase_pr() and game.turn:
		game.purchase_pr()
		print "Purchased PR"

	if game.turn:
		game.end_turn()

def time_up(db, game):
	# We have ran out of time for this turn, it has been forced to end
	print 'Too late'
	pass

def end_game(db, game, error=None):
	if error:
		print "Something went wrong! %s" % error
	else:
		print "Game over"

def incoming_trade(db, game, player, offering, requesting):
	# As long as I'm gaining at least one resource more than I'm giving away, I'll accept
	#Accept trade only if i need something and the trade is good engh
	'''if sum(offering.values()) > sum(requesting.values()):
		return True'''
	#Find I find any resource less than wat i have- check for value and then trade
	for res in offering.keys():
		if game.resources.has_key(res) and game.resources[res]<offering[res]:
			if sum(offering.values()) > sum(requesting.values()):
				return True
	return False
