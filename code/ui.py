from settings import *
from custom_timer import Timer

# invalid_move = pygame.mixer.Sound(join('audio','invalid_move.ogg'))
# invalid_move.set_volume(.1)

class UI:
    def __init__(self,display_surface,chip_surfs,players,player_index,table_min,table_max,count_rect):
        self.state = 'off' #determines which ui is shown (off,bet,playing)
        self.display_surface = display_surface
        self.players = players #list of all the players
        self.player_index = player_index

        #bet ui
        self.chip_surfs = chip_surfs
        self.bet = 0 #bet amount that is displayed on the ui
        self.chip_values = [5,25,50,100,500,1000,5000] #ordered list used for getting the value of a chip from the surface that was clicked on
        self.table_min = table_min
        self.table_max = table_max
        self.bet_try = None #if an invalid bet is attempted, will turn false, then reset after 1 frame. Will turn true if valid bet is placed

        #player turn ui
        self.help_open = False #true if help menu has been clicked and is open
        self.rules_open = False #true if rules menu is open
        self.return_home = False #True if game has been ended and returned to the start screen
        self.first_mouse = None #record the first mouse click of a player during their move
        self.player_action = None #action the player chose which will be returned to main
        self.count_rect = count_rect #rect displaying the count

        #insurance
        self.insurance_try = None ##if an invalid insurance bet is attempted, will turn false, then reset after 1 frame. Will turn true if valid insurance bet is placed

        #timer
        self.double_click_timer = Timer(300)

    def input(self):
        self.player_action = None
        mouse_pos = pygame.mouse.get_pos()
        if self.state == 'bet':
            if pygame.mouse.get_just_pressed()[0]:
                for i,chip in enumerate(self.chips.values()):
                    if chip[1].collidepoint(mouse_pos):
                        self.bet = min(self.bet+self.chip_values[i],self.table_max,self.players[self.player_index].money)
                if self.reset_rect_hitbox.collidepoint(mouse_pos):
                    self.bet = 0
                elif self.min_bet_rect_hitbox.collidepoint(mouse_pos):
                    self.bet = self.table_min
                elif self.max_bet_rect_hitbox.collidepoint(mouse_pos):
                    self.bet = min(self.table_max,self.players[self.player_index].money)

            if pygame.key.get_just_pressed()[pygame.K_SPACE] or pygame.mouse.get_just_pressed()[2]:
                if self.try_bet(self.bet):
                    self.bet_try=True
                    self.bet = 0
                    self.state='off'
                else: 
                    self.bet_try = False
        elif self.state == 'player_turn':
            if not self.help_open and not self.rules_open:
                mouse = pygame.mouse.get_just_pressed()
                keys = pygame.key.get_pressed()
                keys_just_pressed = pygame.key.get_just_pressed()
                #if not over the help box
                if not self.help_rect.collidepoint(mouse_pos) and not self.rules_rect.collidepoint(mouse_pos) and not self.home_rect.collidepoint(mouse_pos):
                    if not self.count_rect.collidepoint(mouse_pos):
                        #mouse controls
                        #l click
                        if mouse[0] and not (mouse[1] or mouse[2]):
                            if self.double_click_timer:
                                if self.first_mouse[0]:
                                    self.player_action = 'up_double'
                                    self.first_mouse=None
                                    self.double_click_timer.deactivate()
                                elif self.first_mouse[2]:
                                    self.player_action = 'split'
                                    self.first_mouse=None
                                    self.double_click_timer.deactivate()
                            else:
                                self.first_mouse = mouse
                                self.double_click_timer.activate()

                        #r click
                        if mouse[2] and not (mouse[0] or mouse[1]):
                            if self.double_click_timer and self.first_mouse[0]:
                                self.player_action = 'split'
                                self.first_mouse=None
                                self.double_click_timer.deactivate()
                            elif self.double_click_timer and self.first_mouse[2]:
                                self.player_action = 'down_double'
                                self.first_mouse=None
                                self.double_click_timer.deactivate()
                            else:
                                self.first_mouse = mouse
                                self.double_click_timer.activate()

                        #split
                        if mouse[0] and mouse[2]:
                            self.player_action = 'split'

                        #surrender
                        if mouse[1] and not (mouse[0] or mouse[2]):
                            self.player_action = 'surrender'

                        if self.first_mouse!=None and not self.double_click_timer:
                            if self.first_mouse[0]:
                                self.player_action = 'hit'
                            elif self.first_mouse[2]:
                                self.player_action = 'stand'
                            self.first_mouse=None
                elif self.help_rect.collidepoint(mouse_pos):
                    #open help menu
                    if mouse[0]:
                        self.help_open=True
                elif self.rules_rect.collidepoint(mouse_pos):
                    #open rules menu
                    if mouse[0]:
                        self.rules_open=True
                else:
                    #return to start screen
                    if mouse[0]:
                        self.return_home = True

                #keyboard controls
                #hit
                if not any(mouse) and keys_just_pressed[pygame.K_SPACE]:
                    print('hit')
                    self.player_action = 'hit'
                #stand
                if not any(mouse) and keys_just_pressed[pygame.K_s]:
                    self.player_action = 'stand'
                #face up double
                if not any(mouse) and keys_just_pressed[pygame.K_d]:
                    self.player_action = 'up_double'
                #face down double
                if not any(mouse) and (keys[pygame.K_LSHIFT] and keys_just_pressed[pygame.K_d]):
                    self.player_action = 'down_double'
                #split
                if not any(mouse) and ((keys[pygame.K_LEFT] and keys_just_pressed[pygame.K_RIGHT]) or (keys_just_pressed[pygame.K_LEFT] and keys[pygame.K_RIGHT])):
                    self.player_action = 'split'
                #surrender
                if not any(mouse) and (keys[pygame.K_LSHIFT] and keys_just_pressed[pygame.K_s]):
                    self.player_action = 'surrender'
                #help
                if not any(mouse) and keys_just_pressed[pygame.K_h]:
                    self.help_open = True
                #rules
                if not any(mouse) and keys_just_pressed[pygame.K_r]:
                    self.rules_open = True
                
            elif self.help_open:
                #close help menu
                if self.close_help_rect.collidepoint(mouse_pos) and pygame.mouse.get_just_pressed()[0] or pygame.key.get_just_pressed()[pygame.K_h]:
                    self.help_open=False

            else:
                if self.close_rules_rect.collidepoint(mouse_pos) and pygame.mouse.get_just_pressed()[0] or pygame.key.get_just_pressed()[pygame.K_r]:
                    self.rules_open=False
        elif self.state=='insurance':
            if pygame.mouse.get_just_pressed()[0]:
                if self.yes_rect_hitbox.collidepoint(mouse_pos):
                    if self.try_bet(bet=1,insurance=True):
                        self.insurance_try=True
                        self.state='off'
                    else:
                        self.insurance_try=False
                elif self.no_rect_hitbox.collidepoint(mouse_pos):
                    if self.try_bet(bet=0,insurance=True):
                        self.state='off'
        
    def bet_ui(self):
        player = self.players[self.player_index]

        #draw ui for placing bet
        rect = pygame.FRect(WINDOW_WIDTH/2-300,WINDOW_HEIGHT/2-200,600,400)
        pygame.draw.rect(self.display_surface,COLORS['white'],rect,0,50)
        pygame.draw.rect(self.display_surface,COLORS['gray'],rect,4,50)
        font = pygame.font.Font(FONT_FILE,40)
        small_font = pygame.font.Font(FONT_FILE,30)

        #Table min and max
        min_pos = (WINDOW_WIDTH/2-230,WINDOW_HEIGHT/2-160)
        min_surf_1 = small_font.render('Min',True,COLORS['black'])
        min_surf_2 = small_font.render(f'${self.table_min}',True,COLORS['table_1'])
        min_rect_1 = min_surf_1.get_frect(center = min_pos)
        min_rect_2 = min_surf_2.get_frect(center = min_pos+pygame.Vector2(0,40))
        self.display_surface.blit(min_surf_1,min_rect_1)
        self.display_surface.blit(min_surf_2,min_rect_2)

        max_pos = (WINDOW_WIDTH/2+230,WINDOW_HEIGHT/2-160)
        max_surf_1 = small_font.render('Max',True,COLORS['black'])
        max_surf_2 = small_font.render(f'${self.table_max}',True,COLORS['table_1'])
        max_rect_1 = max_surf_1.get_frect(center = max_pos)
        max_rect_2 = max_surf_2.get_frect(center = max_pos+pygame.Vector2(0,40))
        self.display_surface.blit(max_surf_1,max_rect_1)
        self.display_surface.blit(max_surf_2,max_rect_2)

        #Player name
        name_pos = (WINDOW_WIDTH/2,WINDOW_HEIGHT/2-150)
        name_surf = font.render(f'Player: {player.name}',True,'black')
        name_rect = name_surf.get_frect(center = name_pos)
        self.display_surface.blit(name_surf,name_rect)

        #bankroll
        money_pos = (WINDOW_WIDTH/2,WINDOW_HEIGHT/2-110)
        money_surf = font.render(f'${player.money}',True,COLORS['table_1'])
        money_rect = money_surf.get_frect(center = money_pos)
        self.display_surface.blit(money_surf,money_rect)

        #Draw all chips
        spacing = rect.width/(len(self.chip_values))
        chip_font = pygame.font.Font(FONT_FILE,15)
        chip_pos = [(12+rect.left+spacing*i,WINDOW_HEIGHT/2-10) for i in range(len(self.chip_values))]
        self.chips = {} #self used so that input can recognize clicks on chips
        for i,val in enumerate(self.chip_values):
            self.chips[val] = self.chip_surfs[val],self.chip_surfs[val].get_frect(bottomleft=chip_pos[i])
            chip_val_surf = chip_font.render(f'{val}',True,'black')
            chip_val_rect = chip_val_surf.get_frect(center = self.chips[val][1].center)
            self.display_surface.blit(self.chips[val][0],self.chips[val][1])
            self.display_surface.blit(chip_val_surf,chip_val_rect)
            
        #bet caption
        bet_pos = (WINDOW_WIDTH/2,WINDOW_HEIGHT/2+25)
        bet_surf = font.render('Click Chips to Change Bet',True,'black')
        bet_rect = bet_surf.get_frect(center = bet_pos)
        self.display_surface.blit(bet_surf,bet_rect)
        bet_caption_pos = (WINDOW_WIDTH/2,WINDOW_HEIGHT/2+60)
        bet_caption_surf = small_font.render('Press Space or R-Click to Enter Bet',True,'black')
        bet_caption_rect = bet_caption_surf.get_frect(center = bet_caption_pos)
        self.display_surface.blit(bet_caption_surf,bet_caption_rect)

        #bet amount
        bet_amount_pos = (WINDOW_WIDTH/2,WINDOW_HEIGHT/2+100)
        bet_amount_surf = font.render(f'{self.bet}',True,'black')
        bet_amount_rect = bet_amount_surf.get_frect(center = bet_amount_pos)
        self.display_surface.blit(bet_amount_surf,bet_amount_rect)

        #Table min and max quick select buttons
        min_bet_pos = (WINDOW_WIDTH/2-230,rect.bottom-40)
        min_bet_surf = small_font.render('Min',True,COLORS['black'])
        min_bet_rect = min_bet_surf.get_frect(center = min_bet_pos)
        self.min_bet_rect_hitbox = min_bet_rect.scale_by(1.2)
        self.display_surface.blit(min_bet_surf,min_bet_rect)
        pygame.draw.rect(self.display_surface,COLORS['green'],self.min_bet_rect_hitbox,4,4)

        #Table min and max quick select buttons
        max_bet_pos = (WINDOW_WIDTH/2+230,rect.bottom-40)
        max_bet_surf = small_font.render('Max',True,COLORS['black'])
        max_bet_rect = max_bet_surf.get_frect(center = max_bet_pos)
        self.max_bet_rect_hitbox = max_bet_rect.scale_by(1.2)
        self.display_surface.blit(max_bet_surf,max_bet_rect)
        pygame.draw.rect(self.display_surface,COLORS['green'],self.max_bet_rect_hitbox,4,4)

        #reset
        reset_pos = (WINDOW_WIDTH/2,rect.bottom-40)
        reset_surf = font.render('Reset',True,'black')
        reset_rect = reset_surf.get_frect(center = reset_pos)
        self.reset_rect_hitbox = reset_rect.scale_by(1.1)
        self.display_surface.blit(reset_surf,reset_rect)
        pygame.draw.rect(self.display_surface,COLORS['black'],self.reset_rect_hitbox,4,4)

    def try_bet(self,bet=0,insurance=False):
        if insurance:
            return self.players[self.player_index].place_bet(bet,insurance=True)
        else:
            if bet%5 != 0 or bet<self.table_min or bet>self.table_max:
                return False
            else:
                return self.players[self.player_index].place_bet(bet)

    def insurance_ui(self):
        player = self.players[self.player_index]

        #draw ui for placing bet
        rect = pygame.FRect(WINDOW_WIDTH/2-150,WINDOW_HEIGHT/2-75,300,150)
        pygame.draw.rect(self.display_surface,COLORS['white'],rect,0,4)
        pygame.draw.rect(self.display_surface,COLORS['gray'],rect,4,4)
        font = pygame.font.Font(FONT_FILE,30)

        #Player name
        name_pos = (WINDOW_WIDTH/2,WINDOW_HEIGHT/2-50)
        name_surf = font.render(f'{self.players[self.player_index].name}',True,'black')
        name_rect = name_surf.get_frect(center = name_pos)
        self.display_surface.blit(name_surf,name_rect)

        #insurance
        insurance_pos = (WINDOW_WIDTH/2,WINDOW_HEIGHT/2)
        insurance_surf = font.render('Insurance?',True,'black')
        insurance_rect = insurance_surf.get_frect(center = insurance_pos)
        self.display_surface.blit(insurance_surf,insurance_rect)

        #yes
        yes_pos = (WINDOW_WIDTH/2-50,WINDOW_HEIGHT/2+45)
        yes_surf = font.render('Yes',True,'black')
        yes_rect = yes_surf.get_frect(center = yes_pos)
        self.yes_rect_hitbox = yes_rect.scale_by(1.1)
        self.yes_rect_hitbox.width*=1.5
        self.yes_rect_hitbox.center = yes_pos
        yes_rect.center = yes_pos
        self.display_surface.blit(yes_surf,yes_rect)

        #no
        no_pos = (WINDOW_WIDTH/2+50,WINDOW_HEIGHT/2+45)
        no_surf = font.render('No',True,'black')
        no_rect = no_surf.get_frect(center = no_pos)
        self.no_rect_hitbox = no_rect.scale_by(1.1)
        self.no_rect_hitbox.width*=1.5
        self.no_rect_hitbox.center = no_pos
        no_rect.center = no_pos
        self.display_surface.blit(no_surf,no_rect)

        pygame.draw.rect(self.display_surface,COLORS['green'],self.yes_rect_hitbox,4,4)
        pygame.draw.rect(self.display_surface,COLORS['red'],self.no_rect_hitbox,4,4)

    def player_turn_ui(self):
        if not self.help_open and not self.rules_open:
            font = pygame.font.Font(FONT_FILE,20)

            #small window that will open if pressed for more details on hitting
            self.help_rect = pygame.FRect(WINDOW_WIDTH-100,0,100,100)
            pygame.draw.rect(self.display_surface,COLORS['white'],self.help_rect,0,4)
            pygame.draw.rect(self.display_surface,COLORS['gray'],self.help_rect,4,4)
            help_surf = font.render('Help',True,'black')
            help_rect = help_surf.get_frect(center = self.help_rect.center)
            self.display_surface.blit(help_surf,help_rect)

            #small window that will open if pressed for more details on the rules. Positioned below help
            self.rules_rect = pygame.FRect(WINDOW_WIDTH-100,100,100,100)
            pygame.draw.rect(self.display_surface,COLORS['white'],self.rules_rect,0,4)
            pygame.draw.rect(self.display_surface,COLORS['gray'],self.rules_rect,4,4)
            rules_surf = font.render('Rules',True,'black')
            rules_rect = rules_surf.get_frect(center = self.rules_rect.center)
            self.display_surface.blit(rules_surf,rules_rect)

            self.home_rect = pygame.FRect(WINDOW_WIDTH-100,200,100,100)
            pygame.draw.rect(self.display_surface,COLORS['white'],self.home_rect,0,4)
            pygame.draw.rect(self.display_surface,COLORS['gray'],self.home_rect,4,4)
            home_surf = font.render('  Start\nScreen',True,'black')
            home_rect = home_surf.get_frect(center = self.home_rect.center)
            self.display_surface.blit(home_surf,home_rect)

        elif self.help_open:
            #controls screen
            rect = pygame.FRect(WINDOW_WIDTH/2-300,WINDOW_HEIGHT/2-200,600,400)
            pygame.draw.rect(self.display_surface,COLORS['white'],rect,0,4)
            pygame.draw.rect(self.display_surface,COLORS['gray'],rect,4,4)
            font = pygame.font.Font(FONT_FILE,20)

            action_surf = font.render('Action\n______\nHit\n\nStand\n\nFace Up Double\n\nFace Down Double\n\nSplit\n\nSurrender',True,'black')
            action_rect = action_surf.get_frect(midleft = rect.move(10,0).midleft)
            self.display_surface.blit(action_surf,action_rect)

            mouse_action_surf = font.render('Mouse\n_____\nL-Click\n\nR-Click\n\n2x L-Click\n\n2x R-Click\n\nL-Click + R-Click\n\nMouseWheel-CLick',True,'black')
            mouse_action_rect = mouse_action_surf.get_frect(center = rect.center)
            self.display_surface.blit(mouse_action_surf,mouse_action_rect)

            keyboard_action_surf = font.render('Keyboard\n________\nSpace\n\nS\n\nD\n\nL-Shift + D\n\nL-Arrow + R-Arrow\n\nL-Shift + S',True,'black')
            keyboard_action_rect = keyboard_action_surf.get_frect(midright = rect.move(-10,0).midright)
            self.display_surface.blit(keyboard_action_surf,keyboard_action_rect)

            close_help_surf = font.render('X',True,'black')
            self.close_help_rect = close_help_surf.get_frect(topright = rect.move(-5,5).topright)
            self.display_surface.blit(close_help_surf,self.close_help_rect)

        elif self.rules_open:
            #rules screen
            rect = pygame.FRect(WINDOW_WIDTH/2-300,WINDOW_HEIGHT/2-200,600,400)
            pygame.draw.rect(self.display_surface,COLORS['white'],rect,0,4)
            pygame.draw.rect(self.display_surface,COLORS['gray'],rect,4,4)
            font = pygame.font.Font(FONT_FILE,20)

            rules_surf = font.render(
"""Splitting
-Can Split up to 3 Times (4 Hands)
-Can Only Split Aces Once\n
Doubling
-Can Double for Less\n
Surrender
-Late Surrender is Available
-Surrender is not Allowed After Splitting or Drawing Cards\n
Betting
-Player Must be Able to Cover Minimum Bet to Play
""",True,'black')
            rules_rect = rules_surf.get_frect(midleft = rect.move(10,0).midleft)
            self.display_surface.blit(rules_surf,rules_rect)

            close_rules_surf = font.render('X',True,'black')
            self.close_rules_rect = close_rules_surf.get_frect(topright = rect.move(-5,5).topright)
            self.display_surface.blit(close_rules_surf,self.close_rules_rect)

    def update(self,player_index):
        self.player_index = player_index
        if self.state == 'bet':
            self.bet_ui()
            self.input()
        elif self.state == 'player_turn':
            self.player_turn_ui()
            self.input()
        elif self.state == 'insurance':
            self.insurance_ui()
            self.input()
        self.double_click_timer.update()