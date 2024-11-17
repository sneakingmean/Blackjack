from settings import *
from cards import Card,Hand

class Player():
    def __init__(self,name,money):
        #info
        self.name=name #Player name
        self._money=money #Player money total

        #betting
        self.bet_placed = False #has player placed his bet for the round
        self.insurance = False #true if a player has decided on taking or not taking insurance
        self.insurance_amount = 0 #amount of insurance bet

        self.hands = {} #dictionary with all the hands the player is currently playing
        self.hand = 0 #hand that is currently being played by the player
        self.num_hands = 0 #number of hands the player has

    @property
    def money(self):
        return self._money
    
    @money.setter
    def money(self,value):
        self._money = max(value,0)

    def place_bet(self,bet=0,insurance=False):
        if insurance == True and bet>0:
            bet = int(self.hands[0].bet/2)
            bet = int((bet-bet%1)/5)*5 #round down bets to the nearest multiple of 5
        
        if bet>self.money: return False
        elif insurance == True:
            self.insurance_amount = bet
            self.money -= self.insurance_amount
            self.insurance=True
            return True
        else: 
            self.bet_placed = True
            self.current_bet = bet
            self.money -= self.current_bet
            self.hands[0] = Hand(self.current_bet)
            self.num_hands+=1 
            return True

    #Adds a card to a player's hand
    def add_card(self,card,hand=0):
        if hand in self.hands.keys():
            self.hands[hand].add_card(card)
        else:
            self.hands[hand] = Hand(self.current_bet)
            self.hands[hand].add_card(card)
            self.num_hands+=1    

    #Resets the players hand
    def reset(self):
        self.money = int(self.money)
        self.hands.clear()
        self.hand = 0 
        self.num_hands = 0 
        self.bet_placed = False
        self.insurance = False
        self.insurance_amount = 0

class Dealer(Hand):
    def __init__(self):
        super().__init__(bet=0)