
from src.gameplay import Game, Player, Team, Round

alpha = Team( 'Alpha' )
alpha.add( 'Casey', None )
alpha.add( 'Jordan', None )

beta = Team( 'Beta' )
beta.add( 'Terry', None )
beta.add( 'Bill', None )
print("Starting Game")
game = Game( alpha, beta )
round = Round( game, 1, game.players )
round.run()
