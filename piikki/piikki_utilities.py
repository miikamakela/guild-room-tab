from PIL import Image
from kivy.logger import Logger
from datetime import datetime, timedelta
import os
from drive import DriveClient
import threading
#import time

from popups import InformationPopup


#full_path = os.getcwd()
#full_path = "/sdcard/data"


class Item():
    
    def __init__(self, name, price, item_class, full_path):
        self.name = name
        self.price = price
        self.item_class = item_class #string with value Candy, Soft drink or Food
        self.normal_background = "{}{}{}{}".format(full_path, "/itempics/", name.lower(), ".png")
        self.item_pic_exists(full_path)

    #check does the item have a picture
    def item_pic_exists(self, full_path):
        try:
            Image.open(self.normal_background)
        except:
            self.normal_background = "{}{}".format(full_path, "/itempics/nopicpic.png")
        
class Settings():
    
    def __init__(self, full_path):
        self.settings_updated = None
        self.full_path = full_path
        self.last_backup = None
        self.time_between_backups = timedelta(days=3)
        self.read_settings("settings.txt")
        Logger.info("Settings: settings updated: {}".format(self.settings_updated))
        Logger.info("Settings: last backup: {}".format(self.last_backup))



    #not currently in use, but downloads the settings file drom drive
    def download_settings(self):

        google_client = DriveClient()
        #download to drive inside a different thread not to block the ui thread
        def download_settings_thread():            
            downloaded_filename = google_client.download_settings(full_path = self.full_path)
            
            if( downloaded_filename ):
                InformationPopup('Settings downloaded')

            else:
                InformationPopup('Downloading settings failed')
            Logger.info('Settings: downloading settings thread finished')
        
        thread1 = threading.Thread(group=None,target=download_settings_thread)
        thread1.start()         
        Logger.info('CustomerHandler: backup customers called')
        
        
     #TODO problems with multiple computers with different versions of settings.txt and different last backups
    '''reads settings.txt file and return the options as a list 
        (currently only one option so no list)'''       
    def read_settings(self, settings_name):
        last_backup_date = None
        last_settings_date = None
        #make new file if one does not exist
        try:            
            file = open(os.path.join(self.full_path, settings_name), "r")           
            #commenting on the settings if the first char is '#'
            
            for line in file:
                if line[0] == '#': continue
                line_wo_newline = line[:-1]
                a = line_wo_newline.split("=")
                if a[0]=='last_backup':
                    last_backup_date = a[1]
                    
                    if last_backup_date == "None":
                        Logger.info("Settings: no last backup based on settings")
                    else:
                        self.last_backup = datetime.strptime(last_backup_date, '%d-%m-%Y_%H:%M')
                if a[0]=='days_between_backups':
                    self.time_between_backups=timedelta(days=float(a[1]))
                if a[0]=='settings_updated':
                    last_settings_date = a[1]
                    if last_settings_date != "None":  
                        self.settings_updated = datetime.strptime(last_settings_date, '%d-%m-%Y_%H:%M')
            file.close()
            
        #if there is no file 
        except IOError:
            file = open(self.full_path +"/settings.txt", 'w')
            file.write('#this file contains settings\n')
            file.write('last_backup=None\n')
            file.write('days_between_backups=3\n')            
            file.close()
        except ValueError:
            Logger.exception("Settings: on read settings ValueError, some typo or missing last empty line")

            


    def select_more_recent_setting(self, new_settings):
        sett2 = Settings(self.full_path)
        sett2.read_settings(new_settings)
        #if new settings file is more recent update
        if sett2.settings_updated >  self.settings_updated:
            return sett2
        else:
            return self




     
    #if time from the last backup is longer than n days set in settings.txt
    def time_to_backup(self):
        
        if self.last_backup == None: return True
        if self.last_backup + self.time_between_backups < datetime.now():   
            Logger.info('Settings: time to backup {}'.format(True))
            return True
        Logger.info('Settings: time to backup {}'.format(False))
        return False 

    
    #updates the last updated time 
    def update_settings(self, update_time=None, update_settings=None):
        
        from tempfile import mkstemp
        from shutil import move
        from os import remove, close
        
        #Create temp file
        fh, abs_path = mkstemp()
        with open(abs_path,'w') as new_file:
            with open(self.full_path + "/settings.txt") as old_file:
                for line in old_file:
                    if update_time or update_settings:
                        if(line.split('=')[0] =='last_backup'):                        
                            new_file.write("{}={}\n".format('last_backup', update_time))
                        elif (line.split('=')[0] =='settings_updated'):                        
                            new_file.write("{}={}\n".format('settings_updated', update_settings))
                        else:
                            new_file.write(line)
                    else:
                        new_file.write(line)

        close(fh)
        
        #Remove original file
        remove(self.full_path +"/settings.txt" )
        #Move new file
        move(abs_path, self.full_path +"/settings.txt")
    
    
class ItemHandler():

    item_list = []
    
    def __init__(self, path):
        self.full_path = path
        self.item_list = self.update_item_list()
        
    def get_items(self):
        return self.item_list
    
    def update_path(self, new_path):
        self.full_path = new_path

    def add_item(self,name, price, filename, item_class):
        
        file = open(self.full_path + "/items.txt", "a")    
        item_background = self.make_item_backgrounds(name, filename)
        
        file.write("{},{},{}\n".format(name.lower(), price,item_class))
        file.close()
        self.update_item_list()
        
        return Item(name.lower(),price, item_class, self.full_path)
        
        
    def update_item_list(self):
        items = []
        #make new file if one does not exist
        try:
            file = open(self.full_path + "/items.txt", "r")        
        
            file.readline() #reads the first description line
            
            for line in file:
                a = line.split(",")
                name = a[0]
                price = float(a[1])
                item_class = a[2][:-1]
                items.append(Item(name,price, item_class, self.full_path))
                items.sort(key=lambda x: x.name)
                
            file.close()
         
        #no items file exists   
        except IOError:
			file = open(self.full_path +"/items.txt", 'w')
			file.write("name,price,Item class")
			file.close()
            
        return items
        
    def update_item_price(self,item,new_price):
        Logger.info('Item_handler: on update_item_price with item {} and new price {}'.format(item.name,new_price))
        
        from tempfile import mkstemp
        from shutil import move
        from os import remove, close
        
        #Create temp file
        fh, abs_path = mkstemp()
        with open(abs_path,'w') as new_file:
            with open(self.full_path + "/items.txt") as old_file:
                for line in old_file:
                    if(line.split(',')[0] ==item.name):
                        new_file.write("{},{},{}\n".format(item.name.lower(), new_price,item.item_class))
                        Logger.info('ItemHandler: update price replace called')
                    else:
                        new_file.write(line)
        close(fh)
        
        #Remove original file
        remove(self.full_path +"/items.txt" )
        #Move new file
        move(abs_path, self.full_path +"/items.txt")
        self.update_item_list()
        
    def delete_item(self,item):
        Logger.info('Item_handler: about to delete {}'.format(item.name))
        
        from tempfile import mkstemp
        from shutil import move
        from os import remove, close
        
        #Create temp file
        fh, abs_path = mkstemp()
        with open(abs_path,'w') as new_file:
            with open(self.full_path + "/items.txt") as old_file:
                for line in old_file:
                    if(line.split(',')[0] ==item.name):
                        pass
                    else:
                        new_file.write(line)
        close(fh)
        #Remove original file
        remove(self.full_path +"/items.txt" )
        #Move new file
        move(abs_path, self.full_path +"/items.txt")    
    
    def make_item_backgrounds(self, name,filename):
        
        
        height, width = 300,300
        item_name = name.lower()
        
        pic = Image.open(filename)    
        #border = Image.open(self.full_path + "/kuvat/border1.png")    
        
        pic = pic.resize((height,width), Image.ANTIALIAS)
        #border = border.resize((300,300), Image.ANTIALIAS)    
       
        background = Image.new('RGBA', (height, width), (255, 255, 255))
        pic1_path = self.full_path + "/itempics/{}{}".format(item_name , ".png")
        #pic2_path = self.full_path + "/itempics/{}{}{}".format(item_name, "_pressed_" ,"pic.png")

        background.paste(pic, (0,0,height,width), pic)
       
        #creating normal background
        #pic.paste(border, (0,0), border)    
        background.save(pic1_path ,"PNG")
        
        #creating the pressed background
        #colour = Image.new("RGBA", (300,300), (50,50,225, 50))
        #pic2.paste(colour, (0,0,300,300), colour)
        #pic2.save(pic2_path,"PNG")

        Logger.info("ItemHandler: made item background for: {}".format(pic1_path ))        
        return pic1_path
    
        
    
    
