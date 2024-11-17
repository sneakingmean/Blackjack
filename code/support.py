from settings import *

def audio_importer(*path):
    audio_dict = {}
    for folder_path, _, file_names in walk(join(*path)):
        for file_name in file_names:
            full_path = join(folder_path,file_name)
            file = pygame.mixer.Sound(full_path)
            file.set_volume(.2)
            audio_dict[file_name.split('.')[0]]=file
    return audio_dict

def card_importer(*path,color):
    dict = {}
    ranks = ['A','2','3','4','5','6','7','8','9','10','J','Q','K']

    #card backs
    card_back_path = join(*path,'card_backs_vertical_1.png')
    back_surf = pygame.image.load(card_back_path).convert_alpha()
    back_cutout_width = back_surf.get_width()/2
    back_cutout_height = back_surf.get_height()
    if color == 'red': back_cutout_rect = pygame.FRect(0,0,back_cutout_width,back_cutout_height)   
    elif color == 'blue': back_cutout_rect = pygame.FRect(back_cutout_width,0,back_cutout_width,back_cutout_height)
    back_cutout_surf = back_surf.subsurface(back_cutout_rect).convert_alpha()
    back_cutout_surf.set_colorkey('#408080')

    #card fronts
    for folder_path, _, file_names in walk(join(*path)):
        for file_name in file_names:
            if file_name.split('_')[1] == 'fronts':
                full_path = join(folder_path,file_name)
                suit = file_name.split('_')[2].split('.')[0].title()
                surf = pygame.image.load(full_path).convert_alpha()
                cutout_width = surf.get_width()/5
                cutout_height = surf.get_height()/3
                for row in range(3):
                    for col in range(5):
                        if 5*row+col<13:
                            name = f'{ranks[row*5+col]} of {suit}'
                            cutout_rect = pygame.FRect(cutout_width*col,cutout_height*row,cutout_width,cutout_height)
                            cutout_surf = surf.subsurface(cutout_rect).convert_alpha()
                            cutout_surf.set_colorkey('#008080')
                            dict[name] = cutout_surf,back_cutout_surf                                  
    return dict

def chip_importer(*path):
    dict = {}
    values = [1,5,25,10,100,1000,10,500,2.5,10]
    full_path = join(*path)
    surf = pygame.image.load(full_path).convert_alpha()
    cutout_width = surf.get_width()/5
    cutout_height = surf.get_height()/2
    #first row
    for row in range(2):
        for col in range(5):
            if 5*row+col<13:
                name = values[row*5+col]
                cutout_rect = pygame.FRect(cutout_width*col,cutout_height*row,cutout_width,cutout_height)
                cutout_surf = surf.subsurface(cutout_rect).convert_alpha()
                cutout_surf.set_colorkey('#008080')
                if name not in dict.keys():
                    dict[name] = cutout_surf  
    sorted_dict = {key:dict[key] for key in sorted(dict)}                             
    return sorted_dict