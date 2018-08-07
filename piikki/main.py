
#config has to be first import and set before anything else
from kivy.config import Config
   
#Config.read("~/.kivy/config.ini")
Config.set('kivy', 'keyboard_mode', 'systemanddock')


from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.uix.dropdown import DropDown
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.graphics import BorderImage
from kivy.logger import Logger

from kivy.properties import ObjectProperty, DictProperty, NumericProperty
from piikki_utilities import  ItemHandler, Settings
from customer import CustomerHandler, Customer
from popups import *
import os
import re

#Builder.load_file('piikki.kv')



button_color = (0.26, 0.43, 0.56,1)
button_font_color = (0, 0, 0, 1)
button_font_size = 26


'''MenuScreen is the landing screen of the app'''
class MenuScreen(Screen):
    
    def exit_app(self):
        App.get_running_app().stop()
 
'''LoginScreen is used for login'''  
class LoginScreen(Screen):
    
    def __init__(self, **kv):
        super(LoginScreen, self).__init__(**kv)
        self.main_app = kv['main_app']
        self.selected_account = None	    
        
        self.test_button = Button(text="press")
        
        filter_chars = "abcdefghijklmnopqrstuwxyzo"
        self.init_filter_buttons(filter_chars)
        
    

    #implements a method for kivy screen
    def on_pre_enter(self):
        self.ids.info_label.font_size=button_font_size-5
        if self.main_app.customer_handler.customers:    
            for cust in self.main_app.customer_handler.customers:
                self.make_account_button(cust)

    def on_leave(self):                
        self.ids.account_list.clear_widgets()   
        self.reset_fields()
        self.ids.filter_input_label.text = ""
        
    def make_account_button(self,customer):
    	button = AccountButton(customer, text = customer.account_name)
    	button.bind(on_release=self.select_account)
    	self.ids.account_list.add_widget(button)
        
    def select_account(self, button):   
        self.selected_account=button.account
        #self.ids.account_label.text = button.account.account_name
        #self.ids.tab_value_label.text = str(button.account.tab_value)
        #self.ids.customer_name_label.text = button.account.customer_name
        #self.ids.info_label.text = "Selected account:"
        #self.ids.info_label.font_size=button_font_size
        self.login()
    
    def reset_fields(self):        
        self.selected_account = None
        #self.ids.account_label.text = ""
        #self.ids.tab_value_label.text = ""
        #self.ids.customer_name_label.text = ""
        self.ids.info_label.text = "Please select your account from the list"
        
        
        
    def login(self):
        warning_label = self.ids.warning_label
        
        if self.selected_account == None:
            warning_label.text = "Please select an account"
        else:
            self.main_app.current_customer = self.selected_account
            self.manager.transition.direction = "left"
            self.manager.current = "osto"           
                
        
        def empty_warning():
            warning_label.text = ""        
        Clock.schedule_once(lambda dt: empty_warning(), 7)
        
            
        
        
    #filter visible account based on the text on filter_input_label
    def filter_account_buttons(self):
        filter_text = self.ids.filter_input_label.text
        self.ids.account_list.clear_widgets()   
    	for cust in self.main_app.customer_handler.customers:
    	    if filter_text in cust.account_name:
    		self.make_account_button(cust)
	
        
    
    #initializes filter buttons for names
    def init_filter_buttons(self, char_list):
    	for char in char_list:
    	    butt = Button(text=char, font_size=button_font_size,
    			    background_normal='', color= button_font_color,
                                background_color = button_color )
    	    butt.bind(on_release=self.on_filter_button_press)
    	    self.ids.filter_button_container.add_widget(butt)
	    
	    
	    
    def on_filter_button_press(self, button):
    	self.ids.filter_input_label.text += button.text
    	self.filter_account_buttons()
	
    def on_remove_filter_text(self):
    	self.ids.filter_input_label.text = self.ids.filter_input_label.text[0:-1] 
    	self.filter_account_buttons()
        

'''AccountScreen is used for creating a new accouont'''
class AccountScreen(Screen):
    
    def __init__(self, **kv):
        Screen.__init__(self, **kv)
        self.main_app = kv['main_app']  
        self.acc_name_input =self.main_app.add_input(self.ids.acc_name_container)
        self.given_name_input = self.main_app.add_input(self.ids.given_name_container)
        self.family_name_input = self.main_app.add_input(self.ids.family_name_container)
        #self.password1 = self.main_app.add_input(self.ids.password1_container, True)
        #self.password2 = self.main_app.add_input(self.ids.password2_container, True)
        self.acc_name_input.bind(on_text_validate=self.on_enter_press)
        self.given_name_input.bind(on_text_validate=self.on_enter_press)
        self.family_name_input.bind(on_text_validate=self.on_enter_press)

    #function for handling enter presses when writing
    def on_enter_press(self,instance):
	self.create_account()
       
    #function called when new account is created. Validates text inputs and creates customer through in customer_handler
    def create_account(self):
        acc_name = self.acc_name_input.text
        given_name = self.given_name_input.text
        family_name = self.family_name_input.text
        #password1 = self.password1.text
        #password2 = self.password2.text
        
        warning_label = self.ids.warning_label
                
        if acc_name == "" or given_name == "" or family_name == "":
            warning_label.text = "Please fill in all the information"
        else:
            '''making the names have format John Doe'''
            customer_name = given_name + " " + family_name
            if len(given_name) > 1 and len(family_name) > 1:
                customer_name = given_name[0].upper() + given_name[1:].lower() + " " + family_name[0].upper() + family_name[1:].lower()
                

            
            self.main_app.customer_handler.create_new_account(acc_name, customer_name, encode=True)
            warning_label.text = "Account created"

            if self.main_app.customer_handler.account_row(customer_name) > 1:
                warning_label.text = ("account with same name exists, make sure to have different nicks")
            
        
    
        def empty_warning():
            warning_label.text = ""        
        Clock.schedule_once(lambda dt: empty_warning(), 7)

    def clear_fields(self):
        self.acc_name_input.text = ""
        self.given_name_input.text = ""
        self.family_name_input.text = ""
                 
    
'''BuyScreen displays the items in sale and handles buy transactions'''            
class BuyScreen(Screen):
    
    
    
    def __init__(self, **kv):        
        super(BuyScreen, self).__init__( **kv)
        self.main_app = kv['main_app']
        
        #item initialization
        self.selected_items = {}
        
        self.item_list = self.main_app.item_handler.get_items()
        self.show_all_items()
        self.init_filter_buttons("abcdefghijklmnopqrstuwxyz")
        
    def on_pre_enter(self):
        self.ids.account_label.text = self.main_app.current_customer.account_name
        self.ids.tab_value_label.text = str(self.main_app.current_customer.tab_value)
        self.ids.tab_value_label.color = self.tab_color()
        self.update_item_list()        
        self.show_all_items()
        self.selected_items = {}
        self.update_selected_items_table()

        
    def on_leave(self):
        self.selected_items = {}
        
        
    def update_item_list(self):
        self.item_list = self.main_app.item_handler.update_item_list()   
    
    '''Updates the customer account name and the tab value when entering the screen and when needed'''
    def update_screen(self):
        self.ids.account_label.text = self.main_app.current_customer.account_name
        self.ids.tab_value_label.text = str(self.main_app.current_customer.tab_value)
        self.ids.tab_value_label.color = self.tab_color()
        self.update_selected_items_table()
    
    '''Changes the current customer of the app to None, unselects the items, and swithces screens to login screen'''
    def to_login_and_logout(self):
        self.main_app.current_customer = None
        self.manager.transition.direction="right"                     
        self.manager.current = "login"

    #goes to the customer screen
    def go_to_customer_screen(self):
        self.manager.transition.direction = "left"
        self.manager.current = "customer"
       
        
    
    #shows all the items on the container 'buy_item_list' with classes and separators between classes    
    def show_all_items(self):
        self.ids.product_filter_label.text = ''
        if len(self.item_list) == 0: pass
        else:
            candy_list = filter(lambda x: x.item_class == "Candy", self.item_list)
            drink_list = filter(lambda x: x.item_class == "Soft drink", self.item_list)
            food_list = filter(lambda x: x.item_class == "Food", self.item_list)
            sorted_items = candy_list + drink_list + food_list
            container = self.ids.buy_item_list
            container.clear_widgets()
            for item in candy_list:
                item_layout = BuyItemLayout(item, container)
                container.add_widget(item_layout)
            container.add_widget(MySeparator())
            for item in drink_list:
                item_layout = BuyItemLayout(item, container)
                container.add_widget(item_layout)
            container.add_widget(MySeparator())
            for item in food_list:
                item_layout = BuyItemLayout(item, container)
                container.add_widget(item_layout)
            
            
    def show_candy(self):
        self.ids.product_filter_label.text = ''
        if self.item_list == None: pass
        else:
            candy_list = filter(lambda x: x.item_class == "Candy", self.item_list)
            container = self.ids.buy_item_list
            container.clear_widgets()
            for item in candy_list:
                item_layout = BuyItemLayout(item, container)
                container.add_widget(item_layout)
    
    def show_soft_drinks(self):
        self.ids.product_filter_label.text = ''
        if self.item_list == None: pass
        else:
            drink_list = filter(lambda x: x.item_class == "Soft drink", self.item_list)
            container = self.ids.buy_item_list
            container.clear_widgets()
            for item in drink_list:
                item_layout = BuyItemLayout(item, container)
                container.add_widget(item_layout)
    
    def show_food(self):
        self.ids.product_filter_label.text = ''
        if self.item_list == None: pass
        else:
            food_list = filter(lambda x: x.item_class == "Food", self.item_list)
            container = self.ids.buy_item_list
            container.clear_widgets()
            for item in food_list:
                item_layout = BuyItemLayout(item, container)
                container.add_widget(item_layout)
               
        
    def show_most_bought(self):
        #check if there are items or for some reasen a customer has not been selected (alwasy should be)
        if len(self.item_list) == 0 or self.main_app.current_customer == None: pass
        else:
            most_bought = self.main_app.customer_handler.most_bought(self.main_app.current_customer)
            if most_bought:
                most_bought_list = [x[0] for x in most_bought]
                most_bought_list = filter(lambda x: self.item_exists_update_price(x), most_bought_list)
                most_bought_list = most_bought_list[:3]
                container = self.ids.buy_item_list
                container.clear_widgets()
                for item in most_bought_list:
                    item_layout = BuyItemLayout(item, container)
                    container.add_widget(item_layout)              
                    
    
    #filter visible products based on the text on product_filter_label
    def filter_products(self):
	filter_text = self.ids.product_filter_label.text
	if self.item_list == None: pass
        else:
            container = self.ids.buy_item_list
            container.clear_widgets()
            for item in self.item_list:
		if filter_text in item.name:
		    item_layout = BuyItemLayout(item, container)
                    container.add_widget(item_layout)
	
    #updates the selected items screen
    def update_selected_items_table(self):
        container = self.ids.selected_item_container
        container.clear_widgets()
        for key in sorted(self.selected_items.keys(), key=lambda item: self.selected_items[item][1] , reverse=True):            
            container.add_widget(SelectedItemLayout(self.selected_items[key][0], self.selected_items[key][1], container))
            
                
    #initializes filter buttons for names
    def init_filter_buttons(self, char_list):
	for char in char_list:
	    butt = Button(text=char, font_size=button_font_size,
			    background_normal='',
                            background_color=button_color, color=button_font_color)
	    butt.bind(on_release=self.on_filter_button_press)
	    
	    self.ids.product_filter_button_container.add_widget(butt)	    
	    
    #determines what happens, when buttons with letters for filtering are pressed
    def on_filter_button_press(self, button):
	self.ids.product_filter_label.text += button.text
	self.filter_products()
	
    #determines what happens when backspace is used
    def on_remove_filter_text(self):
	self.ids.product_filter_label.text = self.ids.product_filter_label.text[0:-1] 
	self.filter_products()
	
    
    def select_item(self,item):
        if item.name in self.selected_items:
            self.selected_items[item.name] = (item, self.selected_items[item.name][1]+ 1)
        else:
            self.selected_items[item.name] = (item, 1)
        
        self.update_selected_items_table()       
        
            
    def unselect_item(self, item):
        #decrease the count of selected items
        if item.name in self.selected_items:            
            nmbr_selected = self.selected_items[item.name][1]
            if nmbr_selected < 2:
                del self.selected_items[item.name]                
            else:
                self.selected_items[item.name] = (item, self.selected_items[item.name][1] - 1)
            self.update_selected_items_table()
    
    
    def buy_item(self):
        if len(self.selected_items.keys()) == 0: pass
        else:
            amount = 0
            for key in self.selected_items:
                amount += self.selected_items[key][0].price * self.selected_items[key][1]
                #add all the bought items to database
                for ii in range(self.selected_items[key][1]):
                    self.main_app.customer_handler.save_buy(self.main_app.current_customer, self.selected_items[key][0])
            #save the buy to database
            self.main_app.customer_handler.pay_from_tab(self.main_app.current_customer, amount)
            self.selected_items = {}
            self.update_screen()

    def buy_and_exit(self):
        if len(self.selected_items.keys()) == 0: pass
        else:
            amount = 0
            for key in self.selected_items:
                amount += self.selected_items[key][0].price * self.selected_items[key][1]
                #add all the bought items to database
                for ii in range(self.selected_items[key][1]):
                    self.main_app.customer_handler.save_buy(self.main_app.current_customer, self.selected_items[key][0])                
            #save the buy to database
            self.main_app.customer_handler.pay_from_tab(self.main_app.current_customer, amount)
            self.selected_items = {}
            self.update_screen()
            self.to_login_and_logout()
            
    #in most bought this is used to check whether item exists and if it does, update price            
    def item_exists_update_price(self,item):
        for it in self.item_list:
            if it.name == item.name:
                item.price = it.price
                return True
        return False
            
    def tab_color(self):        
        tab = self.main_app.current_customer.tab_value 
        if tab >= 5.0:
            return (0,1,0,1)
        elif tab < 5.0 and tab >=0:  
            return (1,1,0,1)
        else:
            return (1,0,0,1)
        
        
'''CustomerScreen allows customers to add value to the tab and see their balance history'''
class CustomerScreen(Screen):
    
    def __init__(self, **kv):
        super(CustomerScreen, self).__init__(**kv)
        self.main_app = kv['main_app'] 
        self.add_tab_input = FloatInput(write_tab=False, multiline=False)
        self.ids.add_tab_input_container.add_widget(self.add_tab_input)
                
    def add_to_tab(self):
        tab_input = self.add_tab_input
        try:
            if tab_input.text == "" or float(tab_input.text) >150.0:
                self.ids.warning_label.text = "Please enter a proper amount"
            else:
                self.main_app.customer_handler.pay_to_tab(self.main_app.current_customer, float(tab_input.text))
                self.update_screen()
                self.ids.warning_label.text = "Added {} succesfully to your tab".format(float(tab_input.text))
                tab_input.text= ""
        except ValueError:
            self.ids.warning_label.text = "Please enter a proper amount"
            
        
        def empty_warning():
            self.ids.warning_label.text = ""        
        Clock.schedule_once(lambda dt: empty_warning(), 7)

    def on_pre_enter(self):
        self.update_screen()
        
    def on_leave_screen(self):
        self.ids.account_label.text = ""
        self.ids.tab_value_label.text = ""
    
    def update_screen(self):
        if self.main_app.current_customer:
            self.ids.account_label.text = self.main_app.current_customer.account_name
            self.ids.tab_value_label.text = str(self.main_app.current_customer.tab_value)
            self.ids.tab_value_label.color = self.tab_color()

            
    def tab_color(self):        
        tab = self.main_app.current_customer.tab_value 
        if tab >= 5.0:
            return (0,1,0,1)
        elif tab < 5.0 and tab >=0:  
            return (1,1,0,1)
        else:
            return (1,0,0,1)  
        

            
'''Screen used for admin stuff, such as adding new items, viewing tabs and changing item prices
    Actually settings'''
class AdminScreen(Screen):
    
    
    def __init__(self,  **kv):
        Screen.__init__(self,  **kv)
        self.main_app = kv['main_app'] 


'''AccManageScreen is used by admin to monitor and change accounts balances and 
to remove accounts'''        
class AccManageScreen(Screen):
    
    def __init__(self, **kv):
        super(AccManageScreen, self).__init__(**kv)
        self.main_app = kv['main_app']        
        
    def on_pre_enter(self):
        for cust in self.main_app.customer_handler.customers:
            layout = CustomerLayout(cust, self.ids.customer_container)
            self.ids.customer_container.add_widget(layout)
            
    def on_leave(self):
        self.ids.customer_container.clear_widgets()
        
    def confirm_replace_cust_db(self):
        p = ConfirmationPopup(self.main_app.customer_handler.replace_customer_db,
                              "Are you sure you wish to replace the current customers?")
        p.open()
        
    def confirm_backup_customers(self):
        p = ConfirmationPopup(self.main_app.customer_handler.backup_customers,
                              "Do you wish to backup your customer db? (by uploading to drive)")
        p.open()
        

'''FileManageScreen is used by admin to add, delete and update items'''
class ItemManageScreen(Screen):
    
    def __init__(self, **kv):
        super(ItemManageScreen, self).__init__( **kv)
        self.main_app = kv['main_app']
        
        for item in self.main_app.item_handler.item_list:
            layout = ManageItemLayout(item, self.ids.item_manage_container)
            self.ids.item_manage_container.add_widget(layout)
            
        self.ids.item_manage_container.add_widget(AddItemLayout(self.ids.item_manage_container))
        
    def add_one_item(self, item):
        last_widget = self.ids.item_manage_container.children[0] #might not work always
        Logger.info('ItemManageScreen: OBS last widget to be removed {}'.format(last_widget))
        self.ids.item_manage_container.remove_widget(last_widget)        
        self.ids.item_manage_container.add_widget(ManageItemLayout(item,self.ids.item_manage_container))
        self.ids.item_manage_container.add_widget(AddItemLayout(self.ids.item_manage_container))

    def add_item(self):        
        p = AddItemPopup(self)    
        p.open()   
        
        
'''FileScreen is used to select item paths from the device'''        
class FileScreen(Screen):
    pass  

class TestScreen(Screen):
    
    def __init__(self, **kv):
        super(TestScreen, self).__init__(**kv)
        self.app = App.get_running_app()
        
        
class CustomerLayout(BoxLayout):
    customer = ObjectProperty(None)
    
    def __init__(self, customer, container, **kv):
        self.customer = customer
        self.container = container
        super(CustomerLayout, self).__init__(**kv)

        #for child in self.children[int(len(self.children)/2):int(len(self.children))]:
        #    self.remove_widget(child)
            
    def update_tab_value(self):
        p = UpdateCustomerTabPopup(self, self.customer)
        p.open()
    
    def confirm_delete_customer(self):
        title = 'Do you wish to remove account for {} ?'.format(self.customer.customer_name)
        p = ConfirmationPopup(self.delete_customer, title)
        p.open()
        
    def delete_customer(self):
        App.get_running_app().man.customer_handler.delete_customer(self.customer)
        self.container.remove_widget(self) 
        
class ManageItemLayout(BoxLayout):
    
    item = ObjectProperty(None)
    container = ObjectProperty(None)
    
    def __init__(self, item, container, **kv):
        self.item = item
        self.container = container
        BoxLayout.__init__(self, **kv)
        
        #for some reason all objects in kivy file are added twice, remove duplicates
        #for child in self.children[4:9]:
        #    self.remove_widget(child)
            
    def confirm_delete_item(self):
        title = 'Do you wish to delete {}?'.format(self.item.name)
        p = ConfirmationPopup(self.delete_item, title)
        p.open()
        
    def delete_item(self):
        App.get_running_app().man.item_handler.delete_item(self.item)
        self.container.remove_widget(self)
    
    def update_item_price(self):        
        p = UpdateItemPopup(self,self.item)    
        p.open()
        
            
class AddItemLayout(BoxLayout):
    
    container = ObjectProperty(None)
    
    def __init__(self,container, **kv):
        self.container = container
        super(AddItemLayout, self).__init__(**kv)
        
        #stupid bug again
        #for child in self.children[int(len(self.children)/2):int(len(self.children))]:
        #    self.remove_widget(child)   
            
''' the layout for items presented in buyscreen, each should have know its own item'''            
class BuyItemLayout(BoxLayout):    
    
    
    def __init__(self,item, container, **kv):
        self.item = item
        self.container = container
        super(BuyItemLayout,self).__init__(**kv)    
        
    def increase_item(self):
        App.get_running_app().man.get_screen('osto').select_item(self.item)
        
    def decrease_item(self):
        App.get_running_app().man.get_screen('osto').unselect_item(self.item)



''' the layout for items presented in buyscreen, each should have know its own item'''            
class SelectedItemLayout(BoxLayout):    
    
    
    def __init__(self,item, amount_of_selected, container, **kv):
        self.item = item
        self.amount_of_selected = amount_of_selected
        self.container = container
        super(SelectedItemLayout,self).__init__(**kv)
   
            
class MyInputListener(Widget):
    
    def __init__(self, parent_screen, **kv):
	super(MyInputListener,self).__init__(**kv)
	#self.orientation = "vertical"
	#self.data_label = Label(text="saaas")
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self, 'text')
        if self._keyboard.widget:
	    print(self._keyboard.widget)
        #self._keyboard.bind(on_key_down=self._on_keyboard_down)
        #self.add_widget(self.data_label)
        
    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None
        
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
	pass
        #self.data_label.text = self.data_label.text
        
        
'''ItemButton is used in the BuyScreen to portray the items'''
class ItemButton(Button):
    
    def __init__(self, item, **kv):
        super(ItemButton, self).__init__(**kv)
        self.item = item
        
class MySeparator(Label):
    
    pass
    
        



'''AccountButton is used in the loginScreen account selection'''
class AccountButton(Button):
    
    def __init__(self,account, **kv):
        Button.__init__(self, **kv)
        self.account = account
        
class CustomDropDown(DropDown):
    pass


class FloatInput(TextInput):

    pat = re.compile('[^0-9]')
    def insert_text(self, substring, from_undo=False):
        pat = self.pat
        if '.' in self.text:
            s = re.sub(pat, '', substring)
        else:
            s = '.'.join([re.sub(pat, '', s) for s in substring.split('.', 1)])
        return super(FloatInput, self).insert_text(s, from_undo=from_undo)

        
        
'''PiikkiManager is the parent class of every screen and 
    contains data that should be available to all the screens'''  
class PiikkiManager(ScreenManager):  

    def __init__(self, **kv):
        ScreenManager.__init__(self, **kv)
        self.app = kv['piikki_app']
        
        from kivy.utils import platform
        if platform == 'android':
            path = self.app.user_data_dir             
        else:
            path = os.path.dirname(os.path.realpath(__file__))        
        
        self.current_customer = None
        self.customer_handler = CustomerHandler(path)
        self.item_handler = ItemHandler(path)
        

        self.add_widget(MenuScreen(name="menu", main_app = self))
        self.add_widget(TestScreen(name="test", main_app=self))
        self.add_widget(LoginScreen(name="login", main_app = self))
        self.add_widget(AccountScreen(name="account", main_app = self))
        self.add_widget(CustomerScreen(name="customer", main_app = self))
        self.add_widget(BuyScreen(name="osto", main_app = self))
        self.add_widget(AdminScreen(name="admin", main_app = self))
        self.add_widget(AccManageScreen(name='acc_manage', main_app = self))
        self.add_widget(ItemManageScreen(name='item_manage', main_app = self))
        self.add_widget(FileScreen(name="select", main_app = self))
        
    
    #add a text input to a given container, used by multiple screens
    def add_input(self, container, passw=False):
        text_input = TextInput(password=passw)
	text_input.write_tab = False
	text_input.multiline = False
        container.add_widget(text_input)
        return text_input
  
       
        

'''Finally the main app class used by kivy'''        
class PiikkiApp(App):  
    

    def check_back_up(self):
        if self.settings.time_to_backup():
            self.man.customer_handler.backup_customers()
 
    
    def build(self):
        self.man = PiikkiManager(piikki_app = self)
        self.settings = Settings(os.path.dirname(os.path.realpath(__file__)))
        self.check_back_up()
        Clock.schedule_interval(lambda dt: self.check_back_up(), 40000)
        
        return self.man

if __name__ == '__main__':
    PiikkiApp().run()

