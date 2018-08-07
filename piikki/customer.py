import sqlite3
import os
from piikki_utilities import Item
from kivy.logger import Logger
from kivy.app import App
from drive import DriveClient
from popups import InformationPopup
import threading
from datetime import datetime

#full_path =  os.getcwd() #on a computer
#db_path = "{}/{}".format(os.getcwd(), "piikki.db")
#full_path = "/sdcard/data/piikki.db"        #on android, create the data folder on your home folder which is /sdcard


#'''Resets all tab values to 0, USE WITH CAUTION'''        
#def clear_tab_values():
#    
#    con = sqlite3.connect(db_path)
#            
#    c = con.cursor()        
#    c.execute("UPDATE customers SET tab_value=0.0")
#    
#    con.commit()        
#    con.close()

class CustomerHandler():
    
    full_path = os.getcwd()
    db_path = "{}/{}".format(os.getcwd(), "piikki.db")
    customers = []
    
    def __init__(self,path):
        self.full_path = path
        self.db_path =os.path.join(path, "piikki.db")
        self.enable_databases()
        self.load_customers()

    '''Returns a list[Customer] of all customers or None if there are no customers'''
    def load_customers(self):       
        
        customers = []
        con = sqlite3.connect(self.db_path)   
        con.text_factory = unicode
        c = con.cursor()      
        
        c.execute("SELECT * FROM customers")
        data=c.fetchall()
        con.close()
        if data is None: pass
        else: 
            for customer in data:
                print(customer)
                customers.append(Customer(int(customer[0]), customer[1], customer[2], customer[3], tab_value=float(customer[4]) ))
        
        self.customers = customers


    '''Creates piikki database if it doesn't exist and adds customer and buy_action tables'''
    def enable_databases(self):      
        con = sqlite3.connect(self.db_path)
        con.text_factory = unicode
                
        c = con.cursor()        
        c.execute('''CREATE TABLE IF NOT EXISTS customers (account_id int, account_name str, identification_id str,
         customer_name str, tab_value real)''')
        con.commit() 
        c.close()       
        con.close()
                
        con = sqlite3.connect(self.db_path)
        c = con.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS buy_actions (account_id int, item_name str, item_class str, buy_value real, time_stamp str)''')
        
        con.commit()        
        con.close()
            
    def drop_customers(self):
        con = sqlite3.connect(self.db_path)
        con.text_factory = unicode
                
        c = con.cursor()        
        c.execute('''DROP TABLE customers''')
        con.commit() 
        c.close()       
        con.close()
                
            
    
    '''all the data is stored in database piikki.db'''
    def create_new_account(self, acc_name, customer_name, encode=False):

        new_id = self.get_available_id()
        customer = Customer(new_id, acc_name, '', customer_name, encode=encode) 

        con = sqlite3.connect(self.db_path)
        con.text_factory = unicode
        
        c = con.cursor()        
        values = (customer.account_id, customer.account_name, customer.identification_id, customer.customer_name, customer.tab_value)
        c.execute("INSERT INTO customers VALUES (?,?,?,?,?)", values)
                
        con.commit()        
        con.close() 

        self.customers.append(customer)  

    def create_existing_account(self, customer):      

        con = sqlite3.connect(self.db_path)
        con.text_factory = unicode
        
        c = con.cursor()        
        values = (customer.account_id, customer.account_name, customer.identification_id, customer.customer_name, customer.tab_value)
        c.execute("INSERT INTO customers VALUES (?,?,?,?,?)", values)
                
        con.commit()        
        con.close() 

        self.customers.append(customer)  



    #returns id that is not in use (int)
    def get_available_id(self):

        poss_id = 1

        con = sqlite3.connect(self.db_path)
        con.text_factory = unicode
        
        c = con.cursor()         
        c.execute("SELECT  account_id FROM customers")
        data = c.fetchall()   

        con.close() 

        old_max_id = 0

        for i in data:
            the_id = i[0]
            Logger.info("Get_available_id: {}".format(the_id))
            Logger.info("Get_available_id: {}".format( int(the_id)))
            if the_id > old_max_id:
                old_max_id = the_id


        poss_id = old_max_id + 1
        Logger.info("CustomerHandler: next available id: {}".format(poss_id))
        return poss_id
           
        
    '''Saves the buy information into buy_actions TABLE with values account_name, item_name, item_class, buy_value '''    
    def save_buy(self,customer, item):
        con = sqlite3.connect(self.db_path)
        con.text_factory = unicode
        
        c = con.cursor()        
        values = (customer.account_id, item.name, item.item_class, item.price, datetime.now().strftime('%d-%m-%Y_%H:%M'))
        c.execute("INSERT INTO buy_actions VALUES (?,?,?,?,?)", values)
                
        con.commit()        
        con.close() 
    
    '''Gets the items that the customer has bought, prob dict with item ids as keys'''
    def load_buy_history(self):
        pass   
    
        
    
    '''returns the items in the order of most bought first together with the bought amount'''
    def most_bought(self, customer):
        con = sqlite3.connect(self.db_path)
        con.text_factory = unicode
        
        c = con.cursor()
        c.execute("SELECT  item_name, buy_value, item_class, COUNT(item_name) FROM buy_actions WHERE account_id=? GROUP BY account_id,item_name", (customer.account_id,))
        data = c.fetchall()        
        con.close()
        
        items = [(Item(i[0], i[1], i[2], self.full_path), i[3]) for i in data ]
        items.sort(key=lambda x: x[1])
        items.reverse()
        #items is list of tuples (Item, number of bought)
        return items
        
        
    '''Updates the customers tab_value in the database'''
    def update_tab_value(self,customer, new_balance):
        
        customer.set_tab_value(new_balance)
        con = sqlite3.connect(self.db_path)
        con.text_factory = unicode
        
        c = con.cursor()               
        c.execute("UPDATE customers SET tab_value=? WHERE account_id=?", (customer.tab_value, customer.account_id))
                
        con.commit()        
        con.close()        
        
    def delete_customer(self, customer):
        Logger.info('CustomerHandler: delete customer called for {}'.format(customer.customer_name))
    
        con = sqlite3.connect(self.db_path)
        con.text_factory = unicode
        
        c = con.cursor()               
        c.execute("DELETE FROM customers WHERE account_id=?", (customer.account_id,))
        self.customers = list((x for x in self.customers if customer.account_name != x.account_name))
        
        
        con.commit()        
        con.close()

        #TODO remove entries made by this customer from the bought (this works, but left it there)
        #c = con.cursor()
        #c.execute("DELETE FROM buy_actions WHERE account_id=?", (customer.account_id,))
        #con.commit()
        #con.close()
        
        
    def save_csv(self):
        from time import strftime
        time_now_string = strftime("%d-%m-%Y_%H:%M")
        abs_name = os.path.join( self.full_path, 'logs', 'customers_csv_{}.txt'.format(time_now_string))
        filename =  'customers_csv_{}.txt'.format(time_now_string)
        
        f = open(abs_name, 'w')        
        for c in self.customers:
            Logger.info("save_csv: '{},{},{},{},{}\n".format(c.account_id, c.account_name , c.identification_id, c.customer_name,str(c.tab_value) ))
            f.write('{},{},{},{},{}\n'.format(c.account_id, c.account_name , c.identification_id, c.customer_name,str(c.tab_value)))
            
        Logger.info('called save csv, filename: {}'.format(filename))
        return filename, time_now_string



            
    def load_csv(self, file_name='customers.txt'):       
           
        abs_name = os.path.join(self.full_path, 'logs', file_name)   
        customers = []       

        import pprint
        try: 
            f = open(abs_name, 'r') 
                 
            line_number = 1
            for line in f:
                if ( line_number == 1):
                    u = line.decode("utf-8-sig")
                    line = u.encode("utf-8")   
                Logger.info("Load_csv: {}".format(line))
                values = ""; acc_name = ""; full_name = ""; value = 0;
                try:
                    values = line.split(',')
                    customer_id = int(values[0])
                    acc_name = values[1]
                    identity = values[2]
                    full_name = values[3]
                    value = float(values[4])

                    customers.append(Customer(customer_id, acc_name, identity, full_name,value ))
                except IndexError:
                    Logger.exception("On load_csv: IndexError on line {}".format(str(line_number) ) )
                except ValueError:
                    Logger.exception("On load_csv: ValueError on line {}".format(str(line_number) ) )

                line_number = line_number + 1
                
            f.close()    
        except IOError: Logger.exception('tried to load a nonexisting csv {}'.format(file_name))
        return customers
    
    #also updates the settings        
    def backup_customers(self):
        csv_name, time_str = self.save_csv()
        
        google_client = DriveClient()
        #upload to drive inside a different thread not to block the ui thread
        def upload_to_drive():            
            google_client.upload_file(filename = csv_name, file_path= os.path.join( self.full_path, 'logs') )            
            os.remove(os.path.join(self.full_path, 'logs', csv_name))            
            InformationPopup('File uploaded')
            Logger.info('CustomerHandler: upload thread finished')
            App.get_running_app().settings.update_settings(update_time=time_str)
        
        thread1 = threading.Thread(group=None,target=upload_to_drive)
        thread1.start()         
        Logger.info('CustomerHandler: backup customers called')
        
    def replace_customer_db(self):
        #download in a separate thread        
        def download_from_drive():
            google_client = DriveClient()
            csv_filename = google_client.download_latest_csv(full_path = self.full_path)
            new_customers = self.load_csv(csv_filename)
            #drop customer table and replace the customers with the downloaded customers
            if new_customers:
                self.customers = []
                self.drop_customers()
                self.enable_databases()
                for c in new_customers:
                    self.create_existing_account(c)
            
            App.get_running_app().man.get_screen("acc_manage").on_pre_enter()
            InformationPopup('File downloaded')
            Logger.info('CustomerHandler: download thread finished')
            
        thread1 = threading.Thread(group=None,target=download_from_drive)
        thread1.start()
        Logger.info('CustomerHandler: replace customers called')
        
        
    '''Returns row number where the account is in the database or None if it doesn't exist''' 
    def account_row(self,name):
            
            con = sqlite3.connect(self.db_path)        
            c = con.cursor()        
            
            c.execute("SELECT rowid FROM customers WHERE customer_name = ?", (name,))
            data=c.fetchall()
            con.close()
            if data is None: return None
            else: return len(data)        
       
        
    
    '''customer pays money to the tab'''
    def pay_to_tab(self,customer, amount):
        customer.pay_to_tab(amount)
        self.update_tab_value(customer, customer.tab_value)
    
    
    '''customer buys something using the tab'''
    def pay_from_tab(self,customer, amount):
        customer.pay_from_tab(amount)
        self.update_tab_value(customer, customer.tab_value)
    
    
    

        
    
'''class Customer portrays users of the tab'''
class Customer():
    
    def __init__(self, account_id, account_name, identity, full_name, tab_value = 0.0, encode=False):  
        self.account_id = account_id
        self.customer_name = full_name
        self.account_name = account_name
        self.identification_id = identity
        #only encode on the first creation of a certain customer
        if encode:
            self.customer_name = self.customer_name.encode('utf-8')
            self.account_name = self.account_name.encode('utf-8')
        self.tab_value = tab_value
        
    '''customer pays money to the tab'''
    def pay_to_tab(self, amount):
        self.tab_value = self.tab_value + amount    
    
    '''customer buys something using the tab'''
    def pay_from_tab(self, amount):
        self.tab_value = self.tab_value - amount
        
    '''Set customer tab_value to given'''
    def set_tab_value(self,amount):
        self.tab_value = amount

    def print_customer(self):
        print("Customer {} '{}'".format(self.customer_name, self.account_name))
        print("Account id: {}, identification id: {} and tab: {}".format(self.account_id, self.identification_id, self.tab_value))

    
    