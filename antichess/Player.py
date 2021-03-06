import Board
import Rules
import Move
import Pieces
		
import random
import sys
import time

class Player:
	colour = None
	rules = None
	name = None
	def __init__(self, col, rules=Rules.Suicide()):
		self.colour = col
		self.rules = rules



class HumanPlayer(Player):
	name = "Human"
	def getMove(self, board, maxTime):
                promptText = "Enter move: "
		moves, iscaptures = self.rules.getAllValidMoves(board, self.colour)
                # Is there a single forced capture?
                if len(moves)==1 and iscaptures[0]:
                    forcedCapture = True
                    promptText = "Enter move [ENTER for " + str(moves[0]) + "]: "
                else:
                    forcedCapture = False

		metacommand = True
		while metacommand:
			m = raw_input(promptText)
                        # Single forced capture
                        if m=="" and forcedCapture==True:
                            return moves[0]
			# Re-display board
			if m=="b":
				board.display()
				continue
			# Retract (undo) last move
			if m=="u" or m=="r":
				return Rules.Move.RETRACT
			# Show list of valid moves
			if m=="v":
				for i,move in enumerate(moves):
					if iscaptures[i]:
						print move.__str__() + " [CAPTURE]"
					else:
						print move
				continue
			if m=="q":
				return Rules.Move.RESIGN
			metacommand = False

		# If we've got this far, input should be a move

                try:
                        return Move.Move.fromNotation(m, self.colour)
                except Exception as e:
                        print "Couldn't parse input."
                        return Move.NONE

class PassingPlayer(Player):
	name = "Passing"
	def getMove(self, board, maxTime):
		return Move.PASS

class RandomPlayer(Player):
	name = "Random"
	def __init__(self, col, rules=Rules.Suicide()):
		Player.__init__(self, col, rules)
		random.seed()

	def getMove(self, board, maxTime):
		validMoves, isCapture = self.rules.getAllValidMoves(board, self.colour)
		if len(validMoves)==0:
			return Move.PASS
		#[fr, to] = validMoves[ random.randint(0, len(validMoves)-1) ]
		#return [8*fr[0] + fr[1], 8*to[0] + to[1]]
		return validMoves[ random.randint(0, len(validMoves)-1) ]
		
class AIPlayer(Player):
	name = "AI"
	maxDepth = 0
	INFINITY = 999999
	def __init__(self, col, maxDepth=1, verbose=False, rules=Rules.Suicide()):
		Player.__init__(self, col, rules)
		self.maxDepth = maxDepth
                self.verbose = verbose
		random.seed()
        
        def getMove(self, board, maxTime):
                startTime = time.time()
                # Be conservative with time
                # TODO enforce this exactly
                maxTime = maxTime * 0.95
		validMoves, isCapture = self.rules.getAllValidMoves(board, self.colour)
		random.shuffle(validMoves)
		#NOTE: isCapture is now out of order
		if len(validMoves)==0:
			return Move.PASS
		if len(validMoves)==1:
			return validMoves[0]

		overallBestScore, overallBestMove = -self.INFINITY, validMoves[0]

                for depth in range(0,self.maxDepth):
                    if self.verbose: 
                        print "At depth ", depth
                    else:
                        sys.stdout.write(".")
                    bestScore, bestMove = self.getMoveToDepth(board, maxTime, startTime, validMoves, depth)
                    # Less than or equals means deeper moves at same score will supersede
                    if bestScore>=overallBestScore:
                        overallBestMove = bestMove
                        overallBestScore = bestScore
                        if self.verbose: print "Changing best move to ", overallBestMove
                    if time.time()-startTime > maxTime:
                        break
                # TODO give more weight to deeper evaluations
                # TODO overwrite shallow scores with deeper scores - otherwise might make a move which looks good at shallow depth but not at deeper depth

		return overallBestMove

	def getMoveToDepth(self, board, maxTime, startTime, validMoves, depth):
		bestScore, bestMove = -self.INFINITY, validMoves[0]
		counter=0

		for move in validMoves:
                        if self.verbose:
                                print move.__str__()+" ",
			        done = counter/float(len(validMoves)) * 100
			        sys.stdout.write( "%d%% " % done )
			        sys.stdout.flush()
			counter += 1
			#fr = move[0]
			#to = move[1]
			#board.makeMove(  [8*fr[0]+fr[1], 8*to[0]+to[1]]  )
			board.makeMove( move )
			#score = -self.minimax(board, self.maxDepth, 1-self.colour) #works
			score = -self.alphabeta(board, depth, -self.INFINITY, self.INFINITY, 1-self.colour, startTime, maxTime)
			board.retractMove()
                        # Check time - if overtime, ignore this move
                        elapsedTime = time.time() - startTime
                        if elapsedTime>maxTime:
                            if self.verbose: print "Ran out of time."
                            break
                        if self.verbose: print "score=%d" % score
			sys.stdout.flush()
			if score > bestScore:
				bestScore, bestMove = score, move
			if bestScore==self.INFINITY:
				break
                if self.verbose: print "Best score is",bestScore,"for move",bestMove

		#fr = bestMove[0]
		#to = bestMove[1]
		#return [ 8*fr[0] + fr[1], 8*to[0]+to[1] ]
		return bestScore, bestMove

	def heuristic(self, board, colour, validMoves, isCapture):
		n_me = board.getNumPieces(colour)
		n_him = board.getNumPieces(1-colour)

                # Win from material
		if n_me==0:
			return +self.INFINITY
		if n_him==0:
			return -self.INFINITY
                # Win from no moves
                if len(validMoves)==0:
                    return +self.INFINITY

		# Prefer fewer pieces
                material_score = n_him - n_me

                # Prefer either no captures or lots of capture choices
                # TODO just prefer more available moves in general?
                num_captures = sum(isCapture)
                if num_captures==0:
                    freedom_score = 3
                elif num_captures==1:
                    freedom_score = -3
                else:
                    freedom_score = 0

		return material_score + freedom_score

	def minimax(self, board, depth, colour):
		validMoves, isCapture = self.rules.getAllValidMoves(board, colour)
		if len(validMoves)==0 or depth <= 0:
			return self.heuristic(board, colour)
		a = -self.INFINITY
		for move in validMoves:
			#fr = move[0]
			#to = move[1]
			#board.makeMove(  [8*fr[0]+fr[1], 8*to[0]+to[1]]  )
			board.makeMove( move )
			a = max(a, -self.minimax(board, depth-1, 1-colour))
			board.retractMove()

	def alphabeta(self, board, depth, a, b, colour, startTime, maxTime):
		validMoves, isCapture = self.rules.getAllValidMoves(board, colour)
		# if there are fewer than N captures, keep looking...
		#if 0 < sum(isCapture) < 4:
		#	#print "---Deepening search [", board.getLastMove(), "]",
		#	#sys.stdout.flush()
		#	depth += 1
		if len(validMoves)==0 or depth <= 0:
			return self.heuristic(board, colour, validMoves, isCapture)
		for move in validMoves:
			#print " "*(self.maxDepth - depth), move
#			fr = move[0]
#			to = move[1]
#			board.makeMove(  [8*fr[0]+fr[1], 8*to[0]+to[1]]  )
			board.makeMove( move )
			a = max(a, -self.alphabeta(board, depth-1, -b, -a, 1-colour, startTime, maxTime))
			board.retractMove()
			if b <= a:
				break	
                        # Check time
                        elapsedTime = time.time() - startTime
                        if elapsedTime>maxTime:
                            return 0 # Will be ignored

		return a

	
		
		
		 
