# -*- coding: utf-8 -*-
"""
Created on Sun Aug 28 19:48:00 2016

@author: miika
"""
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.logger import Logger
from kivy.app import App
import os



button_color = (0.26, 0.43, 0.56,1)
button_font_color = (0, 0, 0, 1)
button_font_size = 26

class ConfirmationPopup(Popup):
    
    def __init__(self, func_on_confirmation,title="", **kv):
        super(ConfirmationPopup, self).__init__(**kv)
        self.title = title
        self.size_hint = (None,None)
        self.size = (400,150)
        self.func_on_confirmation = func_on_confirmation
        b = BoxLayout(orientation='horizontal',
                      spacing = 10, padding = 10)
        b.add_widget(Button(text='Cancel',
                            background_normal='', background_color = button_color,
                            color= button_font_color, font_size = button_font_size,
                            on_release=self.dismiss))      
        b.add_widget(Button(text='Confirm', 
                            background_normal='', background_color = button_color,
                            color= button_font_color, font_size = button_font_size,
                            on_release=self.confirm))
          
        self.content = b
        
    def confirm(self, callback):
        self.func_on_confirmation()
        self.dismiss()

class InformationPopup(Popup):
    
    def __init__(self, title):        
        p = Popup(title=title,size_hint=(None,None),size=(300,150))
        button = Button(text="okay", 
                        background_normal='', background_color = button_color,
                        color= button_font_color, font_size = button_font_size,
                        on_release=p.dismiss)
        p.content = button
        p.open()          
            
            
'''Popup created in python side'''
class UpdateCustomerTabPopup(Popup):
    
    def __init__(self,layout, customer, **kv):
        super(UpdateCustomerTabPopup, self).__init__(**kv)
        self.customer_layout = layout
        self.customer =customer
        self.title = 'Set new tab value for {}'.format(customer.customer_name) 
        self.size_hint = (None,None)
        self.size = (300,300)
        b = BoxLayout(orientation='vertical',
                      spacing = 10, padding = 10)
        b.add_widget(Label(text="Current tab value: {}".format(customer.tab_value)))
        self.balance_input = TextInput()
        b.add_widget(self.balance_input)
        self.info_label = Label(size_hint=[1,.1])
        b.add_widget(self.info_label)
        b2 = BoxLayout(orientation='horizontal',spacing=10, padding=10)        
        b2.add_widget(Button(text='Cancel',
                            background_normal='', background_color = button_color,
                            color= button_font_color, font_size = button_font_size,
                            on_release=self.dismiss)) 
        b2.add_widget(Button(text='Confirm', 
                            background_normal='', background_color = button_color,
                            color= button_font_color, font_size = button_font_size,
                            on_release=self.update_tab_value))               
        b.add_widget(b2)
        self.content = b
        
    def update_tab_value(self, callback):
        if self.balance_input.text.isnumeric():
            App.get_running_app().man.customer_handler.update_tab_value(self.customer, float(self.balance_input.text))
            self.customer_layout.ids.balance_label.text = str(float(self.balance_input.text))
            self.dismiss()       
        else:
            self.info_label.text = "Not valid number"
        

'''Popup created in python side'''
class UpdateItemPopup(Popup):
    
    def __init__(self,manage_layout,item, **kv):
        super(UpdateItemPopup, self).__init__(**kv)
        self.manage_layout= manage_layout
        self.item =item
        self.title = 'Update item price'
        self.size_hint = (None,None)
        self.size = (300,400)
        b = BoxLayout(orientation='vertical',
                      spacing = 10, padding = 10)
        b.add_widget(Label(text='Give a new price'))
        self.price_input = TextInput(text='With a dot e.g. 0.0')
        b.add_widget(self.price_input)
        b.add_widget(Button(text='Confirm', 
                            background_normal='', background_color = button_color,
                            color= button_font_color, font_size = button_font_size,
                            on_release=self.confirm))
        b.add_widget(Button(text='Cancel',
                            background_normal='', background_color = button_color,
                            color= button_font_color, font_size = button_font_size,
                            on_release=self.dismiss))       
        self.content = b
        
    def confirm(self, callback):
        new_price=0
        try: 
            new_price = float(self.price_input.text)
            App.get_running_app().man.item_handler.update_item_price(self.item,new_price)
            self.manage_layout.ids.price_label.text = str(new_price)            
        except ValueError: pass
        self.dismiss()
        

'''Popup created in python side'''
class AddItemPopup(Popup):
    
    def __init__(self, manage_screen, **kv):
        super(AddItemPopup, self).__init__(**kv)
        self.parent_screen = manage_screen
        self.title = 'Add a new item'
        self.size_hint = (None,None)
        self.size = (400,400)
        self.auto_dismiss = False
        self.selected_type = None
        b = BoxLayout(orientation='vertical',
                      spacing = 10, padding = 10)
        self.name_input = TextInput(text='Name of the item')
        self.price_input = TextInput(text='Price e.g. 0.0')
        b1 = BoxLayout(spacing = 10)
        self.soft_drink_button = Button(text = 'Soft drink',
                            background_normal='', background_color = button_color,
                            color= button_font_color, font_size = button_font_size,
                            on_release=self.select_type)
        self.candy_button = Button(text = 'Candy',
                            background_normal='', background_color = button_color,
                            color= button_font_color, font_size = button_font_size,
                            on_release=self.select_type)
        self.food_button = Button(text = 'Food',
                            background_normal='', background_color = button_color,
                            color= button_font_color, font_size = button_font_size,
                            on_release=self.select_type)
        self.warning_label = Label()
        l1 = Label(text='file name \'kuva.png\', in home/user/Pictures/')
        self.path_input = TextInput(text='~/Pictures/*')
        b1.add_widget(self.soft_drink_button)
        b1.add_widget(self.candy_button)
        b1.add_widget(self.food_button)
        b.add_widget(self.name_input)
        b.add_widget(self.price_input)
        b.add_widget(Label(text='Select item type'))
        b.add_widget(b1)
        b.add_widget(l1)
        b.add_widget(self.path_input)
        b2 = BoxLayout(spacing = 10)
        b2.add_widget(Button(text='Cancel',
                            background_normal='', background_color = button_color,
                            color= button_font_color, font_size = button_font_size,
                            on_release=self.dismiss))
        b2.add_widget(Button(text='Add item', 
                            background_normal='', background_color = button_color,
                            color= button_font_color, font_size = button_font_size,
                            on_release=self.confirm))
        b.add_widget(self.warning_label)
        b.add_widget(b2)
        
        
        self.content = b
        
    def confirm(self, callback):
        price=0
        name = self.name_input.text
        pictures = os.path.join(os.path.expanduser("~"), "Pictures")
        file_name = os.path.join(pictures, self.path_input.text)
        Logger.info('AddItemPopup: file path for picture {}'.format(file_name))
        item_class = self.selected_type
        
        try: 
            price = float(self.price_input.text)        
            if name == "" or price == "" or file_name == "" or item_class == None:
                self.warning_label.text = "Please fill all the needed information"
            elif not os.path.isfile(file_name):
                self.warning_label.text = "picture does not exist"
            else:
                #where the update happens
                sm = App.get_running_app().man
                it = sm.item_handler.add_item(name, price,
                                             file_name, item_class)
                self.parent_screen.add_one_item(it)
                self.dismiss()
        except ValueError: self.warning_label.text = "Invalid input, use the dot"
        
        def empty_warning():
            self.warning_label.text = "" 
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: empty_warning(), 5)
        
    #just manually unselect all and select the pressed button
    def select_type(self, *args):        
        self.soft_drink_button.background_normal='kuvat/nappi_tausta.png'
        self.candy_button.background_normal = 'kuvat/nappi_tausta.png'
        self.food_button.background_normal = 'kuvat/nappi_tausta.png'
        args[0].background_normal = 'kuvat/nappi_tausta_pressed.png'
        self.selected_type = args[0].text
