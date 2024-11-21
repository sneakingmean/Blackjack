from settings import *
from random import shuffle
from support import audio_importer

class Card(pygame.sprite.Sprite):
    def __init__(self,front_surf,back_surf,suit,rank):
        super().__init__()
        self.front_surf = front_surf
        self.back_surf = back_surf
        self.image = front_surf
        self.suit = suit
        self.rank = rank
        self.value = self.get_value()
        self.face_up = True #which side of card is currently showing
        self.rotated = False #true if card is rotated

    #Returns the value of the card. Value of ace is returned as 1
    def get_value(self):
        if self.rank in ['K','Q','J']:
            return 10
        elif self.rank!='A':
            return eval(self.rank)
        else:
            return 1
        
    #set the position of the card when it is dealt
    def assign_rect(self,pos):
        self.rect = self.image.get_frect(midbottom=pos)

    #flips a card. Maintains the rotation
    def flip(self):
        if self.face_up:
            self.image = self.back_surf
            self.face_up = False
        else:
            self.face_up = True
            if self.rotated:
                self.rotate()
            else:
                self.image = self.front_surf

    #rotates a card. Will alwyays show the front of a card
    def rotate(self):
        if self.face_up: self.image = pygame.transform.rotozoom(self.front_surf,90,1)
        else: self.image = pygame.transform.rotozoom(self.back_surf,90,1)
        self.rotated = True

class Hand():
    def __init__(self,bet):
        self.bet=bet #amount bet on this hand

        #card totals
        self.cards=[] #List of player cards
        self.total=0 #Current value of the player's hand
        self.index=0 #What card the counter is currently on
        self.num_aces=0 #number of soft aces
        self.bust = False #is player currently bust
        self.last_bet = 0 #set value after player busts to be used when the loss is displayed

    #add a card to the hand and count it if face up
    def add_card(self,card):
        self.cards.append(card)
        self.counter()

    #remove a card from the hand. Used for splits
    def remove_card(self):
        card = self.cards.pop()
        
        #reset counter and total
        self.index=0
        self.total=0
        self.num_aces=0
        self.counter()

        return card

    #counts the total of the hand and is called as each card is added
    def counter(self):
        if self.cards[self.index].face_up: #only count if face up
            value = self.cards[self.index].get_value()
            if value==1: #get the value of an ace
                if self.total+11>21:
                    self.total+=value
                else: 
                    self.total+=11
                    self.num_aces+=1
            else:
                if self.total + value > 21:
                    if self.num_aces > 0: #make a soft ace hard
                        self.total -=10
                        self.num_aces-=1
                self.total+=value

            self.index+=1

            if self.total>21:
                self.bust=True
                self.last_bet=self.bet

    #get the number of cards in the hand
    def get_len(self):
        return len(self.cards)        
    
    #reset the hand
    def reset(self):
        self.bet=0
        self.cards.clear()
        self.total=0 #Current value of the player's hand
        self.index=0 #What card the counter is currently on
        self.num_aces=0 #number of soft aces
        self.bust = False #is player currently bust
        self.last_bet = 0 #set value after player busts to be used when the loss is displayed

class Shoe():
    #Initializes a shoe with a num_decks number of decks
    def __init__(self,surfs,num_decks):
        self.shoe = []
        self.cut_card = max(num_decks*13,40) #position of cut card from the bottom
        self.surfs = surfs
        for i in range(num_decks):
            for card in surfs.keys():
                name = card.split()
                rank = name[0]
                suit = name[2]
                self.shoe.append(Card(surfs[card][0],surfs[card][1],suit,rank))

        shuffle(self.shoe)

    #Deals a single card
    def deal_card(self):
        return self.shoe.pop(0)

    #Gets the number of cards left in the shoe
    def get_num_cards_left(self):
        return len(self.shoe)
    
    #call the initilize function
    def reset(self,surfs,num_decks):
        self.__init__(surfs,num_decks)