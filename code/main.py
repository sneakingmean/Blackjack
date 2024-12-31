from settings import *
from support import *
from player import *
from cards import *
from ui import UI
from random import randint,choice,shuffle
from custom_timer import Timer
from math import ceil,floor

class Game:
    def __init__(self,fullscreen=False):
        if fullscreen: self.display_surface = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
        else: self.display_surface = pygame.display.set_mode((DEFAULT_WINDOW_WIDTH,DEFAULT_WINDOW_HEIGHT))
        pygame.display.set_caption('Blackjack')
        self.fullscreen = fullscreen #boolean for detecting whether DEFAULT_WINDOW is fullscreen or not
        self.dimensions = self.display_surface.get_size() #current dimensions of the DEFAULT_WINDOW
        self.fullscreen_dimensions = self.display_surface.get_size() if fullscreen else (0,0) #record size of fullscreen. Will update once DEFAULT_WINDOW is made fullscreen
        self.running = True #controls whether application is open
        self.game_state = 'start' #controls the state of the game(start,init,play)
        self.player_index = 0 #index of player who's turn it is
        self.num_bets_placed = 0 #indicates number of players who have bet this round
        self.num_insurance = 0 #indicates number of players who have decided to take or decline insurance
        self.running_count = 0 #running count
        
        #Set the table min and max bets
        self.table_min,self.table_max = 15,500 #will be changed in intializer screen

        #imports
        self.import_assets() 

        #groups
        self.card_sprites = pygame.sprite.Group() #cards in play for a round
        self.dealer_card_sprites = pygame.sprite.Group() #dealer cards for a round

        #players
        self.players = [] #list of current players
        self.dealer = Dealer()

        #initialization
        self.names = ['Badlands','Donald','Dana','Radahn','Leo','Kamala','Joe','Thiccems','Jesus',
                      'God','The Devil','The Judge','Smough','Gwyn','Larry Lawton','Big Ben',
                      'Gael','Andre','Solaire','V','Geralt','LoadMaster','Nameless',
                      'Raskolnikov','Seldon','Degen','Dealer','Shark','The Diddler',
                      'Cheater','Missy','Murphy','Tucker','Ace','Hershey','Milo','Roxy','Gambler']
        self.player_1_state, self.player_2_state, self.player_3_state = False,False,False #true if a player is playing
        self.name_1, self.name_2, self.name_3 = 'Player 1','Player 2','Player 3' #names of the players. No way to change them rn
        self.money_1, self.money_2, self.money_3 = 0,0,0 #starting money of each player
        self.player_1, self.player_2, self.player_3 = Player(self.name_1,self.money_1),Player(self.name_2,self.money_2),Player(self.name_3,self.money_3) #player objects
        self.table = 0 #index of table chose (0-4)
        self.do_sounds = True #play sound effects
        self.do_count = False #display the outline for the count rect
        self.show_count = True #display the count in the count rect
        self.do_total = True #display the current hand total
        self.num_decks = 6 #number of decks in the shoe
        self.count_rect = pygame.FRect(0,0,200,50) #rect for displaying the count
        #will add each player if they are added in init. Money will be changed based on the table chosen (starting money=table max)

        #helps print the cards in the correct spot
        self.card_width = self.card_surfs['A of Spades'][0].get_width() #width of a card. used for positioning
        self.card_height = self.card_surfs['A of Spades'][0].get_height() #height of a card
        self.offset = pygame.Vector2(self.card_width/2,-self.card_height/2) #offset of the current card played from the last one

        #round stages
        self.stage = 'bet' #controls what state the game is in ('bet','player turn' etc)
        self.current_card = None #card that has been pulled and is on a timer for when it is displayed
        self.current_result = None #last win,loss, or push that is being displayed in draw_result
        self.dealer_blackjack = False #true if dealer has blackjack
        self.insurance = False #true if dealer is currenly offering insurance

        #timers
        deal_delay = 600
        stage_delay = 1200
        self.player_deal_timer = Timer(deal_delay,func=self.add_card) #timer activated when a card is dealt to the player
        self.dealer_deal_timer = Timer(deal_delay,func=self.add_dealer_card) #timer activated when a card is dealt to the dealer
        self.stage_change_timer = Timer(stage_delay) #timer used when self.stage changes and a few other times when a generic timer is needed
        self.flip_timer = Timer(deal_delay,func=self.flip_card) #activated when a card is being flipped
        self.result_timer = Timer(stage_delay,func=self.change_player_index) #activated when a player loss/push/win is shown on screen
        self.bust_sound_timer = Timer(deal_delay,func=self.audio['bust'].play) #timer for playing the bust audio
        self.shuffle_timer = Timer(stage_delay) #timer for when the shoe is shuffled

        self.timers = [self.player_deal_timer,self.dealer_deal_timer,self.stage_change_timer,self.flip_timer,self.result_timer,self.bust_sound_timer,self.shuffle_timer]

        self.audio['here_comes_the_money'].play(-1)

    def import_assets(self):
        self.card_surfs = card_importer('images','top_down','cards',color='blue') #dict with keys = card name (Ace of Spades), values being a front and back surf
        self.chip_surfs = chip_importer('images','top_down','chips.png') #dict with keys = chip values, values being surfs

        #table graphics
        self.table_surfs = table_importer('images','top_down','tables') #dict with keys = name of table, values = surf
        self.table_rect = self.table_surfs[0].get_frect(center = (self.dimensions[0]*.5,self.dimensions[1]*.361)) #same for each table
        self.table_rect_full = None

        #start screen
        #default
        self.start_screen_surf = pygame.image.load(join('images','top_down','start_screen.png')) 
        self.start_screen_rect = self.start_screen_surf.get_frect(topleft = (0,0))
        self.start_screen_surf_full = None
        
        self.audio = audio_importer('audio') #dict of audio files
        #volumes are automatically set to .2
        self.audio['deal'].set_volume(.3)
        self.audio['ambience'].set_volume(.1)
        self.audio['stand'].set_volume(.15)
        self.audio['shuffle'].set_volume(.4)

    def draw_start_screen(self):
        #background
        self.display_surface.fill('black')
        if self.fullscreen: 
            if self.start_screen_surf_full == None:
                self.start_screen_surf_full = pygame.transform.smoothscale(self.start_screen_surf,self.fullscreen_dimensions)
                self.start_screen_rect_full = self.start_screen_surf_full.get_frect(topleft=(0,0))
            self.display_surface.blit(self.start_screen_surf_full,self.start_screen_rect_full)

        else:
            self.display_surface.blit(self.start_screen_surf,self.start_screen_rect)
            fullscreen_font = pygame.font.Font(FONT_FILE,20)
            fullscreen_surf = fullscreen_font.render('Press F for Fullscreen',True,COLORS['white'])
            fullscreen_rect = fullscreen_surf.get_frect(center=(self.dimensions[0]*.5,self.dimensions[1]*.05))
            self.display_surface.blit(fullscreen_surf,fullscreen_rect)

        #start button
        self.start_button_rect = pygame.FRect(self.dimensions[0]*.6953,self.dimensions[1]*.8472,200,100)
        pygame.draw.rect(self.display_surface,COLORS['white'],self.start_button_rect,0,4)
        pygame.draw.rect(self.display_surface,COLORS['gray'],self.start_button_rect,4,4)
        start_button_font = pygame.font.Font(FONT_FILE,20)
        start_button_words_surf = start_button_font.render('Click to Start',True,COLORS['black'])
        start_button_words_rect = start_button_words_surf.get_frect(center=self.start_button_rect.center)
        self.display_surface.blit(start_button_words_surf,start_button_words_rect)

    #check if the start button has been pressed from the start screen
    def check_start(self):
        mouse_pos = pygame.mouse.get_pos()
        if pygame.mouse.get_pressed()[0] and self.start_button_rect.collidepoint(mouse_pos):
            self.game_state = 'init'

    #screen for initializing the game
    def draw_initializer(self):
         #background
        self.display_surface.fill(COLORS['table_1'])

        section_font = pygame.font.Font(FONT_FILE,70)
        rect = pygame.FRect(self.dimensions[0]*.1289,0,150,180)
        players_section_surf = section_font.render('Players',True,COLORS['white'])
        players_section_rect = players_section_surf.get_frect(center=rect.center)
        self.display_surface.blit(players_section_surf,players_section_rect)

        #Add Players
        caption_font = pygame.font.Font(FONT_FILE,20)
        self.player_1_rect = pygame.FRect(self.dimensions[0]*.102,self.dimensions[1]*.208,220,100)
        self.player_2_rect = pygame.FRect(self.dimensions[0]*.414,self.dimensions[1]*.208,220,100)
        self.player_3_rect = pygame.FRect(self.dimensions[0]*.727,self.dimensions[1]*.208,220,100)        

        #player rects will be white if not clicked, green when clicked
        #player 1
        if self.player_1_state == False:
            pygame.draw.rect(self.display_surface,COLORS['white'],self.player_1_rect,0,4)
            player_1_name_surf = caption_font.render('+',True,COLORS['black'])
        else:
            pygame.draw.rect(self.display_surface,COLORS['green'],self.player_1_rect,0,4)
            player_1_name_surf = caption_font.render(self.player_1.name,True,COLORS['black'])
        pygame.draw.rect(self.display_surface,COLORS['gray'],self.player_1_rect,4,4)
        player_1_name_rect = player_1_name_surf.get_frect(center=self.player_1_rect.center)
        self.display_surface.blit(player_1_name_surf,player_1_name_rect)

        #player 2
        if self.player_2_state == False:
            pygame.draw.rect(self.display_surface,COLORS['white'],self.player_2_rect,0,4)
            player_2_name_surf = caption_font.render('+',True,COLORS['black'])
        else:
            pygame.draw.rect(self.display_surface,COLORS['green'],self.player_2_rect,0,4)
            player_2_name_surf = caption_font.render(self.player_2.name,True,COLORS['black'])
        pygame.draw.rect(self.display_surface,COLORS['gray'],self.player_2_rect,4,4)
        player_2_name_rect = player_2_name_surf.get_frect(center=self.player_2_rect.center)
        self.display_surface.blit(player_2_name_surf,player_2_name_rect)

        #player 3
        if self.player_3_state == False:
            pygame.draw.rect(self.display_surface,COLORS['white'],self.player_3_rect,0,4)
            player_3_name_surf = caption_font.render('+',True,COLORS['black'])
        else:
            pygame.draw.rect(self.display_surface,COLORS['green'],self.player_3_rect,0,4)
            player_3_name_surf = caption_font.render(self.player_3.name,True,COLORS['black'])
        pygame.draw.rect(self.display_surface,COLORS['gray'],self.player_3_rect,4,4)
        player_3_name_rect = player_3_name_surf.get_frect(center=self.player_3_rect.center)
        self.display_surface.blit(player_3_name_surf,player_3_name_rect)

        #table
        #the selected table will be highlighted green
        rect = pygame.FRect(self.dimensions[0]*.1289,self.dimensions[1]*.347,150,180)
        tables_section_surf = section_font.render('Table',True,COLORS['white'])
        tables_section_rect = tables_section_surf.get_frect(center=rect.center)
        self.display_surface.blit(tables_section_surf,tables_section_rect)

        self.table_1_rect = pygame.FRect(self.dimensions[0]*.0313,self.dimensions[1]*.569,220,100)
        self.table_2_rect = pygame.FRect(self.dimensions[0]*.223,self.dimensions[1]*.569,220,100)
        self.table_3_rect = pygame.FRect(self.dimensions[0]*.414,self.dimensions[1]*.569,220,100) 
        self.table_4_rect = pygame.FRect(self.dimensions[0]*.605,self.dimensions[1]*.569,220,100) 
        self.table_5_rect = pygame.FRect(self.dimensions[0]*.797,self.dimensions[1]*.569,220,100) 

        #table 1
        if self.table==0:
            pygame.draw.rect(self.display_surface,COLORS['green'],self.table_1_rect,0,4)
        else:
            pygame.draw.rect(self.display_surface,COLORS['white'],self.table_1_rect,0,4)
        pygame.draw.rect(self.display_surface,COLORS['gray'],self.table_1_rect,4,4)
        table_1_name_surf = caption_font.render('$15 - $500',True,COLORS['black'])
        table_1_name_rect = table_1_name_surf.get_frect(center=self.table_1_rect.center)
        self.display_surface.blit(table_1_name_surf,table_1_name_rect)

        #table 2
        if self.table==1:
            pygame.draw.rect(self.display_surface,COLORS['green'],self.table_2_rect,0,4)
        else:
            pygame.draw.rect(self.display_surface,COLORS['white'],self.table_2_rect,0,4)
        pygame.draw.rect(self.display_surface,COLORS['gray'],self.table_2_rect,4,4)
        table_2_name_surf = caption_font.render('$25 - $1000',True,COLORS['black'])
        table_2_name_rect = table_2_name_surf.get_frect(center=self.table_2_rect.center)
        self.display_surface.blit(table_2_name_surf,table_2_name_rect)

        #table 3
        if self.table==2:
            pygame.draw.rect(self.display_surface,COLORS['green'],self.table_3_rect,0,4)
        else:
            pygame.draw.rect(self.display_surface,COLORS['white'],self.table_3_rect,0,4)
        pygame.draw.rect(self.display_surface,COLORS['gray'],self.table_3_rect,4,4)
        table_3_name_surf = caption_font.render('$50 - $5000',True,COLORS['black'])
        table_3_name_rect = table_3_name_surf.get_frect(center=self.table_3_rect.center)
        self.display_surface.blit(table_3_name_surf,table_3_name_rect)

        #table 4
        if self.table==3:
            pygame.draw.rect(self.display_surface,COLORS['green'],self.table_4_rect,0,4)
        else:
            pygame.draw.rect(self.display_surface,COLORS['white'],self.table_4_rect,0,4)
        pygame.draw.rect(self.display_surface,COLORS['gray'],self.table_4_rect,4,4)
        table_4_name_surf = caption_font.render('$100 - $10000',True,COLORS['black'])
        table_4_name_rect = table_4_name_surf.get_frect(center=self.table_4_rect.center)
        self.display_surface.blit(table_4_name_surf,table_4_name_rect)

        #table 5
        if self.table==4:
            pygame.draw.rect(self.display_surface,COLORS['green'],self.table_5_rect,0,4)
        else:
            pygame.draw.rect(self.display_surface,COLORS['white'],self.table_5_rect,0,4)
        pygame.draw.rect(self.display_surface,COLORS['gray'],self.table_5_rect,4,4)
        table_5_name_surf = caption_font.render('$500 - $50000',True,COLORS['black'])
        table_5_name_rect = table_5_name_surf.get_frect(center=self.table_5_rect.center)
        self.display_surface.blit(table_5_name_surf,table_5_name_rect)

        #audio
        self.audio_rect = pygame.FRect(self.dimensions[0]*.07,self.dimensions[1]*.833,150,100)
        if self.do_sounds==True:
            pygame.draw.rect(self.display_surface,COLORS['green'],self.audio_rect,0,4)
        else:
            pygame.draw.rect(self.display_surface,COLORS['white'],self.audio_rect,0,4)
        pygame.draw.rect(self.display_surface,COLORS['gray'],self.audio_rect,4,4)
        audio_surf = caption_font.render('Sound Effects',True,COLORS['black'])
        audio_rect =  audio_surf.get_frect(center=self.audio_rect.center)
        self.display_surface.blit( audio_surf, audio_rect)

        #count
        self.init_count_rect = pygame.FRect(self.dimensions[0]*.207,self.dimensions[1]*.833,150,100)
        if self.do_count==True:
            pygame.draw.rect(self.display_surface,COLORS['green'],self.init_count_rect,0,4)
        else:
            pygame.draw.rect(self.display_surface,COLORS['white'],self.init_count_rect,0,4)
        pygame.draw.rect(self.display_surface,COLORS['gray'],self.init_count_rect,4,4)
        init_count_surf = caption_font.render('Count',True,COLORS['black'])
        init_count_rect =  init_count_surf.get_frect(center=self.init_count_rect.center)
        self.display_surface.blit( init_count_surf, init_count_rect)

        #totals
        self.total_rect = pygame.FRect(self.dimensions[0]*.344,self.dimensions[1]*.833,150,100)
        if self.do_total==True:
            pygame.draw.rect(self.display_surface,COLORS['green'],self.total_rect,0,4)
        else:
            pygame.draw.rect(self.display_surface,COLORS['white'],self.total_rect,0,4)
        pygame.draw.rect(self.display_surface,COLORS['gray'],self.total_rect,4,4)
        total_surf = caption_font.render('Show Total',True,COLORS['black'])
        total_rect =  total_surf.get_frect(center=self.total_rect.center)
        self.display_surface.blit( total_surf, total_rect)

        #shoe
        self.shoe_rect = pygame.FRect(self.dimensions[0]*.48,self.dimensions[1]*.833,150,100)
        pygame.draw.rect(self.display_surface,COLORS['white'],self.shoe_rect,0,4)
        pygame.draw.rect(self.display_surface,COLORS['gray'],self.shoe_rect,4,4)
        num_decks_surf = caption_font.render(f'{self.num_decks}',True,COLORS['black'])
        num_decks_rect =  num_decks_surf.get_frect(midtop=self.shoe_rect.center)
        self.display_surface.blit( num_decks_surf, num_decks_rect)
        num_decks_label_surf = caption_font.render('Decks in Shoe',True,COLORS['black'])
        num_decks_label_rect =  num_decks_label_surf.get_frect(midbottom=self.shoe_rect.center)
        self.display_surface.blit( num_decks_label_surf, num_decks_label_rect)

        #start button
        self.start_button_rect = pygame.FRect(self.dimensions[0]*.695,self.dimensions[1]*.833,200,100)
        pygame.draw.rect(self.display_surface,COLORS['gold'],self.start_button_rect,0,4)
        pygame.draw.rect(self.display_surface,COLORS['gray'],self.start_button_rect,4,4)
        start_button_words_surf = caption_font.render('Click to Start',True,COLORS['black'])
        start_button_words_rect = start_button_words_surf.get_frect(center=self.start_button_rect.center)
        self.display_surface.blit(start_button_words_surf,start_button_words_rect)

    #checks when player is done setting up the game and is ready to start playing
    def check_initializer(self):
        mouse_pos = pygame.mouse.get_pos()
        if pygame.mouse.get_just_pressed()[0] and self.player_1_rect.collidepoint(mouse_pos): #player 1
            self.player_1.name = choice(self.names)
            self.player_1_state = not self.player_1_state
        elif pygame.mouse.get_just_pressed()[0] and self.player_2_rect.collidepoint(mouse_pos): #player 2
            self.player_2.name = choice(self.names)
            self.player_2_state = not self.player_2_state
        elif pygame.mouse.get_just_pressed()[0] and self.player_3_rect.collidepoint(mouse_pos): #player 3
            self.player_3.name = choice(self.names)
            self.player_3_state = not self.player_3_state

        elif pygame.mouse.get_just_pressed()[0] and self.table_1_rect.collidepoint(mouse_pos): #table 1
            self.table,self.table_min,self.table_max = 0,15,500
        elif pygame.mouse.get_just_pressed()[0] and self.table_2_rect.collidepoint(mouse_pos): #table 2
            self.table,self.table_min,self.table_max = 1,25,1000
        elif pygame.mouse.get_just_pressed()[0] and self.table_3_rect.collidepoint(mouse_pos): #table 3
            self.table,self.table_min,self.table_max = 2,50,5000
        elif pygame.mouse.get_just_pressed()[0] and self.table_4_rect.collidepoint(mouse_pos): #table 4
            self.table,self.table_min,self.table_max = 3,100,10000
        elif pygame.mouse.get_just_pressed()[0] and self.table_5_rect.collidepoint(mouse_pos): #table 5
            self.table,self.table_min,self.table_max = 4,500,50000

        elif pygame.mouse.get_just_pressed()[0] and self.audio_rect.collidepoint(mouse_pos): #sound effects
            self.do_sounds = not self.do_sounds
        elif pygame.mouse.get_just_pressed()[0] and self.init_count_rect.collidepoint(mouse_pos): #show count
            self.do_count = not self.do_count
        elif pygame.mouse.get_just_pressed()[0] and self.total_rect.collidepoint(mouse_pos): #show totals
            self.do_total = not self.do_total
        elif pygame.mouse.get_just_pressed()[0] and self.shoe_rect.collidepoint(mouse_pos): #decks in shoe
            self.num_decks = max((self.num_decks+2)%10,2)

        elif pygame.mouse.get_just_pressed()[0] and self.start_button_rect.collidepoint(mouse_pos):
            self.players.clear()
            if self.player_1_state: 
                self.player_1.money = self.table_max
                self.players.append(self.player_1)
            if self.player_2_state: 
                self.player_2.money = self.table_max
                self.players.append(self.player_2)
            if self.player_3_state:
                self.player_3.money = self.table_max 
                self.players.append(self.player_3)

            self.num_hands_left = len(self.players) #number of hands left during each round. If player busts, has blackjack, or surrenders -1, split +1
            if self.num_hands_left>0:
                self.game_state = 'play'
                self.get_card_positions()
                self.ui = UI(self.display_surface,self.chip_surfs,self.players,self.player_index,self.table_min,self.table_max,self.count_rect)
                self.shoe = Shoe(self.card_surfs,self.num_decks)
                self.audio['here_comes_the_money'].stop()
                self.audio['ambience'].play(-1) if self.do_sounds else False 

    #draws the correct table graphic based on the table min
    def draw_table(self):
        match self.table_min:
            case 15:
                table_surf = self.table_surfs[0]
                color = COLORS['table_1']         
            case 25:
                table_surf = self.table_surfs[1]
                color = COLORS['table_2']     
            case 50:
                table_surf = self.table_surfs[2]
                color = COLORS['table_3']     
            case 100:
                table_surf = self.table_surfs[3]
                color = COLORS['table_4']     
            case 500:
                table_surf = self.table_surfs[4]
                color = COLORS['table_5']     

        self.table_rect.center = (self.dimensions[0]*.5,self.dimensions[1]*.361)
        self.display_surface.fill(color)       
        self.display_surface.blit(table_surf,self.table_rect)

    #draws the current bet on each hand
    def draw_current_bets(self):
        font = pygame.font.Font(FONT_FILE,20)
        
        for i,player in enumerate(self.players):
            color = COLORS['white'] if self.player_index==i and not self.player_deal_timer else COLORS['gray'] #highlight the bet of the current hand being played
            for j,hand in enumerate(player.hands.values()):
                #show player's bet
                bet_pos = self.placements[i]+self.current_hand_offset(player.num_hands-1,j)+pygame.Vector2(0,5)
                bet_shown = hand.bet if not hand.bust else hand.last_bet
                bet_surf = font.render(f'${bet_shown}',True,color)
                bet_rect = bet_surf.get_frect(midtop = bet_pos)
                self.display_surface.blit(bet_surf,bet_rect)

                #show a player's total
                if self.do_total and hand.total>0 and not self.player_deal_timer: 
                    rect = pygame.FRect((hand.cards[-1].rect.move(-15,-23).midtop),(30,23))
                    pygame.draw.rect(self.display_surface,COLORS['white'],rect,border_radius=3)
                    pygame.draw.rect(self.display_surface,COLORS['gray'],rect,3,3)
                    total_surf = font.render(f'{hand.total}',True,COLORS['black'])
                    total_rect = total_surf.get_frect(center = rect.center)
                    self.display_surface.blit(total_surf,total_rect)
        
        #draw dealer total
        dealer_rect = pygame.FRect((self.dimensions[0]*.488,0),(30,23))
        if self.do_total and self.dealer.total>0 and (not self.dealer_deal_timer and not self.flip_timer):
            pygame.draw.rect(self.display_surface,COLORS['white'],dealer_rect,border_radius=3)
            pygame.draw.rect(self.display_surface,COLORS['gray'],dealer_rect,3,3)
            if self.dealer.cards[0].face_up: shown_total = self.dealer.total #don't add face down hole card to total
            else:
                if len(self.dealer.cards)==2: 
                    if self.dealer.cards[1].get_value()==1: shown_total=11
                    else: shown_total=self.dealer.cards[1].get_value()
                else: shown_total=0
            dealer_total_surf = font.render(f'{shown_total}',True,COLORS['black'])
            dealer_total_rect = dealer_total_surf.get_frect(center = dealer_rect.center)
            self.display_surface.blit(dealer_total_surf,dealer_total_rect)

    #draws each players name and total money
    def draw_players(self):
        font = pygame.font.Font(FONT_FILE,20)

        for i,player in enumerate(self.players):
            #highlight current player
            color = COLORS['white'] if self.player_index==i and not self.player_deal_timer else COLORS['gray']
            player_surf = font.render(f'{player.name}',True,color)
            player_rect = player_surf.get_frect(midtop = self.placements[i]+pygame.Vector2(0,30))
            self.display_surface.blit(player_surf,player_rect)

            #money
            money_surf = font.render(f'${player.money}',True,color)
            money_rect = money_surf.get_frect(midtop = self.placements[i]+pygame.Vector2(0,60))
            self.display_surface.blit(money_surf,money_rect)

    #displays the result (win,push,loss) for each hand and how much was won or lost
    def draw_result(self):
        rect = pygame.FRect(self.dimensions[0]*.383,self.dimensions[1]*.431,self.dimensions[0]*.234,self.dimensions[1]*.139)
        pygame.draw.rect(self.display_surface,COLORS['white'],rect,0,4)
        pygame.draw.rect(self.display_surface,COLORS['gray'],rect,4,4)
        font = pygame.font.Font(FONT_FILE,40)

        #Player name
        name_pos = (self.dimensions[0]*.5,self.dimensions[1]*.465)
        name_surf = font.render(f'{self.players[self.player_index].name}',True,'black')
        name_rect = name_surf.get_frect(center = name_pos)
        self.display_surface.blit(name_surf,name_rect)

        #result
        money_pos = (self.dimensions[0]*.5,self.dimensions[1]*.535)
        if self.current_result>0: money_surf = font.render(f'Win ${self.current_result}',True,'green') #win
        elif self.current_result==0: money_surf = font.render(f'Push',True,COLORS['gray']) #push
        else: money_surf = font.render(f'Lose ${-self.current_result}',True,COLORS['red']) #lose
            
        money_rect = money_surf.get_frect(center = money_pos)
        self.display_surface.blit(money_surf,money_rect)
        
    #displays the running and true counts
    def draw_count(self):
        font = pygame.font.Font(FONT_FILE,20)
        #display counts
        if self.show_count: #true if the count rect is fully open, not minimized
            self.count_rect = self.count_rect = pygame.FRect(0,0,200,50)
            pygame.draw.rect(self.display_surface,COLORS['white'],self.count_rect,0,4)
            pygame.draw.rect(self.display_surface,COLORS['gray'],self.count_rect,4,4)
            running_count_surf = font.render(f'Running Count: {self.running_count}',True,'black')
            running_count_rect = running_count_surf.get_frect(topleft = self.count_rect.move(10,0).topleft)
            self.display_surface.blit(running_count_surf,running_count_rect)
            true_count_surf = font.render(f'True Count: {max(floor(self.running_count/ceil(self.shoe.get_num_cards_left()/52)),0)}',True,'black')
            true_count_rect = true_count_surf.get_frect(bottomleft = self.count_rect.move(10,0).bottomleft)
            self.display_surface.blit(true_count_surf,true_count_rect)
            arrow_surf = font.render('<',True,'black')
            arrow_rect = arrow_surf.get_frect(center = self.count_rect.move(-9,0).midright)
            self.display_surface.blit(arrow_surf,arrow_rect)
        else:
            self.count_rect = self.count_rect = pygame.FRect(0,0,20,50)
            pygame.draw.rect(self.display_surface,COLORS['white'],self.count_rect,0,4)
            pygame.draw.rect(self.display_surface,COLORS['gray'],self.count_rect,4,4)
            arrow_surf = font.render('>',True,'black')
            arrow_rect = arrow_surf.get_frect(center = self.count_rect.center)
            self.display_surface.blit(arrow_surf,arrow_rect)

    #checks if the player minimized the count rect. Only applicable when count has been enabled
    def check_draw_count(self):
        if pygame.mouse.get_just_pressed()[0] and self.count_rect.collidepoint(pygame.mouse.get_pos()):
            self.show_count = not self.show_count

    #gets the starting position on the screen for each player. Changes based on how many players there are
    def get_card_positions(self):
        #positioning of cards
        self.dealer_pos = pygame.Vector2(self.dimensions[0]*.5-self.card_width,self.dimensions[1]*.208)
        start_pos = pygame.Vector2(self.dimensions[0]*.5,self.dimensions[1]*.861) #position of the middle player

        self.placements = {} #hold vectors of player positions based on index
        x = self.dimensions[0]*.286 #x offset from player position 2 (directly below dealer)
        y = -self.dimensions[1]*.069 #y offset from player position 2

        if len(self.players)%2==0: #%2 comes from the fact that an even number of players will have 2 bottom players (largest y value) while an odd number will only have 1
            start_pos -= pygame.Vector2(x/2,0)
            for i in range(len(self.players)):
                if i == len(self.players)/2 or i == len(self.players)/2-1: #middle players
                    y=0
                    self.placements[i] = start_pos + (int(len(self.players)/2)-i)*pygame.Vector2(x,y)
                elif len(self.players)/2-i < 0: #left player
                    y=self.dimensions[1]*.069
                    self.placements[i] = start_pos + (int(len(self.players)/2)-i)*pygame.Vector2(x,y)
                else: #right player
                    y*=(int(len(self.players)/2)-i-1)/(int(len(self.players)/2)-i)
                    self.placements[i] = start_pos + (int(len(self.players)/2)-i)*pygame.Vector2(x,y)
        else:
            for i in range(len(self.players)):
                if int(len(self.players)/2)-i < 0: y = self.dimensions[1]*.069
                self.placements[i] = start_pos + (int(len(self.players)/2)-i)*pygame.Vector2(x,y)

    #adds offset for when a player has split and has multiple hands
    def current_hand_offset(self,num_hands,hand):
        return pygame.Vector2((-1*num_hands + 2*hand)*self.card_width,0) #ratio of first coefficient to second should be 1:2 to keep cards centered
                            #adjust placement  #adds offset for each additional hand
    
    #takes insurance bets from players if applicable. Same logic as bet()
    def offer_insurance(self):
        if self.num_insurance != len(self.players):
            if not self.players[self.player_index].insurance and self.players[self.player_index].hands[0].bet>0:
                self.ui.state = 'insurance'
                if self.ui.bet_try==False and self.do_sounds: self.audio['invalid_move'].play()
                self.ui.bet_try = None
            else:
                self.num_insurance += 1
                self.player_index = (self.player_index+1)%len(self.players)

        elif self.stage=='insurance': 
            self.num_insurance = 0
            self.insurance = False
            self.stage = 'checking_blackjacks' #move onto the deal when all bets are placed

    #checks if dealer has blackjack
    def check_dealer_blackjack(self,val):
        if self.dealer.cards[0].get_value()==val: 
            self.dealer_blackjack = True

    #checks if each player has blackjack
    def check_player_blackjacks(self):
        if not self.result_timer and not self.flip_timer:
            if self.player_index>=len(self.players):
                if self.dealer_blackjack: self.reset() #end the hand if the dealer has blackjack and all the player's blackjacks have been checked
                else:
                    self.stage = 'player_turn'
                    self.player_index=0
            else:
                current_hand = self.players[self.player_index].hands[0]
                if current_hand.total==21: #player has blackjack
                    self.num_hands_left-=1
                    if not self.dealer_blackjack: #dealer doesn't have blackjack
                        #win
                        self.current_result = current_hand.bet*1.5 - self.players[self.player_index].insurance_amount
                        self.players[self.player_index].money += 5/2*current_hand.bet
                    elif self.dealer_blackjack: #dealer also has blackjack
                        #push
                        self.current_result = 2*self.players[self.player_index].insurance_amount
                        self.players[self.player_index].money += current_hand.bet + 3*self.players[self.player_index].insurance_amount
                    current_hand.reset()
                    self.result_timer.activate()
                elif self.dealer_blackjack and current_hand.bet>0: #loss to dealer blackjack
                    self.current_result = -current_hand.bet + 2*self.players[self.player_index].insurance_amount
                    self.players[self.player_index].money += 3*self.players[self.player_index].insurance_amount
                    current_hand.reset()
                    self.result_timer.activate()
                elif self.players[self.player_index].insurance_amount>0: #no dealer blackjack and player has less than 21
                    self.current_result = -self.players[self.player_index].insurance_amount
                    self.players[self.player_index].insurance_amount = 0
                    self.result_timer.activate()
                else:
                    self.player_index+=1

    #takes player bets for the round             
    def bet(self):
        if not self.shuffle_timer and not self.result_timer:
            if self.num_bets_placed != len(self.players):
                if not self.players[self.player_index].bet_placed:
                    self.ui.state = 'bet'
                    if self.ui.bet_try==False and self.do_sounds: self.audio['invalid_move'].play()
                    self.ui.bet_try = None
                else:
                    if self.do_sounds: self.audio['bet'].play()
                    self.num_bets_placed += 1
                    self.player_index = (self.player_index+1)%len(self.players)

            elif self.stage=='bet': self.stage = 'deal' #move onto the deal when all bets are place
        else: 
            if self.shoe.get_num_cards_left()<self.shoe.cut_card: #shuffle the shoe
                self.shoe.reset(self.card_surfs,self.num_decks)
                self.audio['shuffle'].play()
                self.running_count = 0
            rect = pygame.FRect(self.dimensions[0]*.383,self.dimensions[1]*.43,300,100)
            pygame.draw.rect(self.display_surface,COLORS['white'],rect,0,4)
            pygame.draw.rect(self.display_surface,COLORS['gray'],rect,4,4)
            font = pygame.font.Font(FONT_FILE,40)
            surf = font.render('Shuffling Shoe',True,'black')
            rect = surf.get_frect(center = rect.center)
            self.display_surface.blit(surf,rect)

    #deals out 2 cards to each player and the dealer    
    def deal(self):
        if not self.player_deal_timer and not self.dealer_deal_timer:
            if self.player_index < len(self.players):
                if self.players[self.player_index].hands[self.players[self.player_index].hand].bet>0:
                    current_hand = self.players[self.player_index].hands[self.players[self.player_index].hand]
                    if not current_hand.get_len()==2:
                        self.current_card = self.shoe.deal_card()
                        pos = self.placements[self.player_index]+current_hand.get_len()*self.offset
                        self.current_card.assign_rect(pos)
                        current_hand.add_card(self.current_card)
                        self.player_deal_timer.activate()
                self.player_index += 1
            else:
                self.current_card = self.shoe.deal_card()
                pos = self.dealer_pos+len(self.dealer.cards)*pygame.Vector2(self.card_width,0)
                self.current_card.assign_rect(pos)
                self.dealer.add_card(self.current_card)
                self.dealer_deal_timer.activate()
                if len(self.dealer.cards) == 1: self.current_card.flip() 
                elif len(self.dealer.cards) == 2:
                    if self.dealer.cards[1].get_value() == 1: #check for dealer upcard being an ace to offer insurance
                        self.insurance = True
                        self.check_dealer_blackjack(10)
                    elif self.dealer.cards[1].get_value() == 10: #check for dealer upcard being a 10 to check a blackjack
                        self.check_dealer_blackjack(1)
                    self.stage = 'checking_blackjacks' #check if any player has blackjack
                self.player_index=0

    #player's turn where he decides what action to take after being dealt his initial cards
    def player_turn(self):
        if not (self.stage_change_timer or self.result_timer) and not self.player_index >= len(self.players): #make sure it's not dealer's turn
            if self.players[self.player_index].hands[self.players[self.player_index].hand].bet>0: #make sure the player has bet this hand
                current_hand = self.players[self.player_index].hands[self.players[self.player_index].hand]
                if current_hand.get_len()==1 and not self.player_deal_timer: #for after a split, automatically deal another card
                    self.current_card = self.shoe.deal_card()
                    pos = self.placements[self.player_index]+current_hand.get_len()*self.offset+self.current_hand_offset(self.players[self.player_index].num_hands-1,self.players[self.player_index].hand)
                    self.current_card.assign_rect(pos)
                    current_hand.add_card(self.current_card)
                    self.player_deal_timer.activate(True)
                    if current_hand.cards[0].get_value()==1:
                        if self.players[self.player_index].hand == self.players[self.player_index].num_hands-1: self.player_index += 1 
                        else: self.players[self.player_index].hand+=1
                else:
                    if not current_hand.bust and current_hand.total!=21: #check player is bust and doesn't have a 21
                        self.ui.state = 'player_turn'
                        player_action = self.ui.player_action
                        match player_action:
                            case None: pass
                            case 'hit':
                                self.current_card = self.shoe.deal_card()
                                pos = self.placements[self.player_index]+current_hand.get_len()*self.offset+self.current_hand_offset(self.players[self.player_index].num_hands-1,self.players[self.player_index].hand)
                                self.current_card.assign_rect(pos)
                                current_hand.add_card(self.current_card)
                                self.player_deal_timer.activate()
                            case 'stand':
                                if self.do_sounds: self.audio['stand'].play()
                                if self.players[self.player_index].hand == self.players[self.player_index].num_hands-1: self.player_index += 1 
                                else: self.players[self.player_index].hand+=1
                            case 'up_double': #face up
                                if self.players[self.player_index].money > 0 and current_hand.get_len()==2:
                                    #alter bet
                                    double_amount = 0
                                    if self.players[self.player_index].money < current_hand.bet: double_amount = self.players[self.player_index]._money
                                    else: double_amount = current_hand.bet
                                    current_hand.bet += double_amount
                                    self.players[self.player_index].money-=double_amount

                                    self.current_card = self.shoe.deal_card()
                                    self.current_card.rotate()
                                    pos = self.placements[self.player_index]+current_hand.get_len()*self.offset+self.current_hand_offset(self.players[self.player_index].num_hands-1,self.players[self.player_index].hand)
                                    self.current_card.assign_rect(pos)
                                    current_hand.add_card(self.current_card)
                                    self.player_deal_timer.activate()
                                    
                                    if self.players[self.player_index].hand == self.players[self.player_index].num_hands-1: self.player_index += 1 
                                    else: self.players[self.player_index].hand+=1
                                elif self.do_sounds: self.audio['invalid_move'].play()
                            case 'down_double': #face down
                                if self.players[self.player_index].money > 0 and current_hand.get_len()==2:
                                    #alter bet
                                    double_amount = 0
                                    if self.players[self.player_index].money < current_hand.bet: double_amount = self.players[self.player_index]._money
                                    else: double_amount = current_hand.bet
                                    current_hand.bet += double_amount
                                    self.players[self.player_index].money-=double_amount

                                    self.current_card = self.shoe.deal_card()
                                    self.current_card.flip()
                                    self.current_card.rotate()
                                    pos = self.placements[self.player_index]+current_hand.get_len()*self.offset+self.current_hand_offset(self.players[self.player_index].num_hands-1,self.players[self.player_index].hand)
                                    self.current_card.assign_rect(pos)
                                    current_hand.add_card(self.current_card)
                                    self.player_deal_timer.activate()
                                    
                                    if self.players[self.player_index].hand == self.players[self.player_index].num_hands-1: self.player_index += 1 
                                    else: self.players[self.player_index].hand+=1
                                elif self.do_sounds: self.audio['invalid_move'].play()
                            case 'split':                 #check that player has enough money to split                    #check the player has only 2 cards                   #check that the cards have the same value                 #only allow 3 splits
                                if self.players[self.player_index].money >= self.players[self.player_index].current_bet  and current_hand.get_len()==2 and current_hand.cards[0].get_value() == current_hand.cards[1].get_value() and self.players[self.player_index].num_hands<4:
                                    card = current_hand.remove_card()
                                    self.players[self.player_index].add_card(card,self.players[self.player_index].num_hands)
                                    self.players[self.player_index].money -= current_hand.bet
                                    self.num_hands_left+=1

                                    #adjust placement of the hands and add money
                                    for i,hand in enumerate(self.players[self.player_index].hands.values()):
                                        for j,card in enumerate(hand.cards):    
                                            card.rect.midbottom = self.placements[self.player_index]+j*self.offset+self.current_hand_offset(self.players[self.player_index].num_hands-1,i)
                                        hand.bet = current_hand.bet

                                elif self.do_sounds: self.audio['invalid_move'].play()
                            case 'surrender': #can't surrender after split
                                if not self.players[self.player_index].num_hands>1 and current_hand.get_len()==2:
                                    self.players[self.player_index].money += current_hand.bet/2
                                    self.current_result = -current_hand.bet/2
                                    self.result_timer.activate() #display result immediately
                                    current_hand.bet = 0
                                    current_hand.reset() #avoid the result graphic showing up at the end
                                    self.num_hands_left-=1
                                    if self.do_sounds: self.audio['surrender'].play()
                                elif self.do_sounds: self.audio['invalid_move'].play()
                        if current_hand.bust:
                            current_hand.bet = 0
                            self.num_hands_left-=1
                            if self.do_sounds: self.bust_sound_timer.activate()
                    else:
                        if self.players[self.player_index].hand == self.players[self.player_index].num_hands-1: self.player_index += 1
                        else: self.players[self.player_index].hand+=1
            else:
                if self.players[self.player_index].hand == self.players[self.player_index].num_hands-1: self.player_index += 1
                else: self.players[self.player_index].hand+=1
        else:
            if self.player_index >= len(self.players):
                self.player_index-=1 #start at the left most player when paying out bets
                self.stage = 'dealer_turn'
                for player in self.players: player.hand = 0 #reset hand so that on evaluate we can compare hands to the dealer in the right order
                self.stage_change_timer.activate()
    
    #deals the dealer remaining cards until he reaches 17 or busts. Only flips his hole card if all the other players have bust,blackjack,surrender
    def dealer_turn(self):
        if not self.stage_change_timer:
            if not self.flip_timer and len(self.dealer.cards) == 2 and not self.dealer.cards[0].face_up:
                self.flip_timer.activate()

            if not self.flip_timer and not self.dealer_deal_timer:
                if self.num_hands_left>0:
                    if self.dealer.total>=17: #stand on s17
                        self.stage = 'evaluate'
                        self.stage_change_timer.activate()
                    else:
                        self.current_card = self.shoe.deal_card()
                        pos = self.dealer_pos+len(self.dealer.cards)*pygame.Vector2(self.card_width,0)
                        self.current_card.assign_rect(pos)
                        self.dealer.add_card(self.current_card)
                        self.dealer_deal_timer.activate()
                else:
                    self.stage = 'evaluate'
                    self.stage_change_timer.activate()

    #keeps track of what stage of the round the game is at and calls functions to run at each stage
    def get_stage(self):
        if not self.result_timer: #for when blackjacks are checked and results put up
            match self.stage:
                case 'bet':
                    self.bet()
                case 'deal':
                    self.deal()
                case 'insurance':
                    self.offer_insurance()
                case 'dealer_blackjack':
                    if not self.flip_timer:
                        if not self.dealer.cards[0].face_up:
                            self.flip_timer.activate()
                        self.check_player_blackjacks()
                case 'checking_blackjacks':
                    if not self.dealer_deal_timer:
                        if self.insurance: self.stage = 'insurance'
                        elif self.dealer_blackjack: self.stage = 'dealer_blackjack'
                        else: self.check_player_blackjacks()                    
                case 'player_turn': #for when players get to act after intitial deal
                    self.player_turn()
                case 'dealer_turn': #for when the dealer has to act after the initial deal
                    self.dealer_turn()
                case 'evaluate':self.evaluate()

    #evaluates the result of a round by comparing dealer and player hands
    def evaluate(self):
        if self.stage == 'evaluate':
            if not self.result_timer and not self.stage_change_timer:
                if self.player_index<0: self.reset()
                else:
                    current_hand = self.players[self.player_index].hands[self.players[self.player_index].hand]
                    if current_hand.get_len()>0:
                        if not current_hand.cards[-1].face_up: #flip any doubles that are face down
                            not current_hand.cards[-1].flip()
                            current_hand.counter()
                            if current_hand.cards[-1].get_value()==1 or current_hand.cards[-1].get_value()==10: self.running_count-=1
                            elif current_hand.cards[-1].get_value()<=6: self.running_count+=1
                            if current_hand.bust: self.bust_sound_timer.activate()
                            self.stage_change_timer.activate()
                        if not self.stage_change_timer:
                            if (self.dealer.total < current_hand.total or self.dealer.bust) and not current_hand.bust: #win
                                self.current_result = current_hand.bet
                                self.players[self.player_index].money += 2*current_hand.bet
                            elif self.dealer.total == current_hand.total and not current_hand.bust: #push
                                self.current_result = 0
                                self.players[self.player_index].money += current_hand.bet
                            else: #loss
                                self.current_result = min(-current_hand.bet,-current_hand.last_bet)
                            current_hand.bet = 0
                            self.result_timer.activate()
                    else:
                        self.change_player_index()

    #resets all hands and bets for the next round
    def reset(self):
        #reset stage variables
        self.stage = 'bet'
        self.num_bets_placed = 0
        self.player_index = 0
        self.dealer_blackjack = False

        #activate shuffle timer
        if self.shoe.get_num_cards_left()<self.shoe.cut_card:
            self.shuffle_timer.activate()
        
        #clear sprite groups
        for sprite in self.card_sprites:
            sprite.kill()
        for sprite in self.dealer_card_sprites:
            sprite.kill()

        #reset the players and dealers
        temp_list = []
        for player in self.players:
            if player.money >= self.table_min:
                temp_list.append(player)
                player.reset()
        self.players = temp_list
        self.ui.players = self.players
        self.get_card_positions()

        self.num_hands_left = len(self.players)

        self.dealer.reset()

        #reset game if no players are left
        if self.num_hands_left == 0: self.restart()

    #restarts the game from the start screen
    def restart(self):
        self.audio['ambience'].stop()
        if self.fullscreen: self.__init__(True)
        else: self.__init__()

#Functions triggered by timers
    #adds a card to the player_card_sprites
    def add_card(self):
        self.card_sprites.add(self.current_card)
        if self.current_card.face_up:
            if self.current_card.get_value()==1 or self.current_card.get_value()==10:
                self.running_count -=1
            elif self.current_card.get_value()<7:
                self.running_count+=1
        if self.do_sounds: self.audio['deal'].play()

    #adds a card to the dealer_card_sprites
    def add_dealer_card(self):
        self.dealer_card_sprites.add(self.current_card)
        if self.current_card.face_up:
            if self.current_card.get_value()==1 or self.current_card.get_value()==10:
                self.running_count -=1
            elif self.current_card.get_value()<7:
                self.running_count+=1
        if self.do_sounds: self.audio['deal'].play()

    #flips the dealers hole card
    def flip_card(self):
        self.dealer.cards[0].flip()
        if self.dealer.cards[0].get_value()==1 or self.dealer.cards[0].get_value()==10:
            self.running_count -=1
        elif self.dealer.cards[0].get_value()<7:
            self.running_count+=1
        if self.do_sounds: self.audio['deal'].play()

    #changes player index or changes a player's hand index if he has more hands left to play
    def change_player_index(self):
        if self.stage == 'evaluate':dir=-1
        else: dir=1

        if self.players[self.player_index].hand == self.players[self.player_index].num_hands-1: self.player_index += dir
        elif self.players[self.player_index].hand < self.players[self.player_index].num_hands-1: self.players[self.player_index].hand+=1

    #runs the game  
    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_f and (self.game_state == 'start' or self.game_state == 'init' or (self.game_state == 'play' and self.stage=='bet')): #The second condition makes it so that fullscreen can't be toggled when cards are being dealt
                        self.fullscreen = not self.fullscreen
                        if self.fullscreen: self.display_surface = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
                        else: self.display_surface = pygame.display.set_mode((DEFAULT_WINDOW_WIDTH,DEFAULT_WINDOW_HEIGHT))
                        self.dimensions = self.display_surface.get_size()    
                        if self.fullscreen_dimensions == (0,0) and self.fullscreen: self.fullscreen_dimensions = self.dimensions      
                        self.get_card_positions() #reset player positions       
                    elif event.key == pygame.K_ESCAPE and self.game_state=='start':
                        self.running = False                  

            #playing screen
            if self.game_state == 'play':
                self.draw_table()
                self.get_stage() #calls appropriate functions based on self.stage

                #draw
                if self.do_count: self.draw_count()
                self.check_draw_count()
                self.draw_players()
                self.draw_current_bets()
                self.card_sprites.draw(self.display_surface)
                self.dealer_card_sprites.draw(self.display_surface)
                if self.result_timer and self.player_index>=0:
                    self.draw_result()

                self.ui.update(self.player_index,self.dimensions)
                for timer in self.timers:
                    timer.update()
                if self.ui.return_home: self.restart()

            #initializer screen
            elif self.game_state == 'init': 
                self.draw_initializer()
                self.check_initializer()

            #start screen
            else: 
                self.draw_start_screen()
                self.check_start()
            pygame.display.update()
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()