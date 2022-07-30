import linebot
from linebot.models.send_messages import QuickReply
from transitions import Machine
from datetime import datetime, timedelta
# from app import Order_Item
from utils import LineAPI
import random


FSM_GRAPH_URL = 'https://toc.c.gtco.team/graphs/fsm.png'
class FSMchatbot(object):
    fsmDefinition = {
        "states":  [
            'main',
            'fsm',
            'menu',
            'drink',
            'main_dishes',
            'set_order',
            
            'register_client',
            'get_phone',
            'confirm',
            'check_out',
            'query_orders',
            'not_user', 
            'order_show',
            'all_orders',
            'test'
        ],

        "transitions":[
            {
                'trigger': 'menu_query',
                'source':'main',
                'dest':'menu'
            },
            {
                'trigger': 'test_query',
                'source':'*',
                'dest':'test'
            },
            {
                'trigger': 'drink_query',
                'source':'menu',
                'dest': 'drink'  
            },
            {
                'trigger': 'main_query',
                'source':'menu',
                'dest': 'main_dishes'  
            },
            {
                'trigger': 're_sample',
                'source':'drink',
                'dest': 'drink'  
            },
            {
                'trigger': 'check',
                'source':'drink',
                'dest': 'menu'  
            },
            {
                'trigger': 'check',
                'source':'main_dishes',
                'dest': 'menu'  
            },
            {
                'trigger': 're_sample',
                'source':'main_dishes',
                'dest': 'main_dishes'  
            },
            {
                'trigger': 'registered',
                'source':'main',
                'dest': 'query_order'  
            },
            {
                'trigger': 'not_registered',
                'source':'main',
                'dest': 'not_user'  
            },
            {
                'trigger': 'set_query',
                'source':'order_show',
                'dest': 'set_order'  
            },
            {
                'trigger': 'back_to_menu',
                'source':'order_show',
                'dest': 'menu'  
            },
            {
                'trigger': 'main',
                'source':'*',
                'dest': 'main'  
            },
            {
                'trigger': 'order_show_query',
                'source':'menu',
                'dest': 'order_show'  
            },
            {
                'trigger': 'login',
                'source':'set_order',
                'dest': 'register_client'  
            },
            {
                'trigger': 'go_back',
                'source':'register_client',
                'dest': 'set_order'  
            },
            {
                'trigger': 'failed',
                'source':'register_client',
                'dest': 'register_client'  
            },
            {
                'trigger': 'name',
                'source':'set_order',
                'dest': 'get_phone'  
            },
            {
                'trigger': 'not_phone',
                'source':'set_order',
                'dest': 'get_phone'  
            },
            {
                'trigger': 'success',
                'source':'register_client',
                'dest': 'confirm'  
            },
            {
                'trigger': 'phone',
                'source':'get_phone',
                'dest': 'confirm'  
            },
            {
                'trigger':'No',
                'source':'confirm',
                'dest':'set_order'
            },
            {
                'trigger': 'yes',
                'source':'confirm',
                'dest': 'check_out'  
            },
            {
                'trigger': 'all_orders_query',
                'source':'main',
                'dest': 'all_orders'  
            },
            {
                'trigger':'fsm_query',
                'source':'*',
                'dest':'fsm'
            },
            
        ],
        "initial": 'main',
    }

    def __init__(self):
        self.machine = Machine(model=self, **FSMchatbot.fsmDefinition)
        self.dataQuery = datetime.utcnow()
        self.userName = ""
        self.phoneNumber = ""
        self.lineId = ""
        self.curr_main = []
        self.curr_drink = []
        self.current_order = None
        self.total_price = 0
        self.repeatedDish = False
        self.repeatedDrink = False

    main_menu_text = (
        "Welcome to the chatbot for TOC\n"+
        "(Please Select any of the following options\n"+
        "-Main\n" +
        "-Menu\n" 
    )

    def on_enter_main(self, reply_token):
        quick_reply = LineAPI.makeQuickReplyText([
            'Menu'
        ])
        LineAPI.send_reply_message(reply_token,reply_msg = FSMchatbot.main_menu_text,quickReply=quick_reply)
        LineAPI.commitMessage()

    menu_text = (
        "Our Current Schedule for the restaurant is: \n " +
        "Monday from 07:00 to    20:00\n "+
        "Thusday from 07:00 to   20:00\n "+
        "Wesnesday from 07:00 to 20:00\n "+
        "Thursday from 07:00 to  20:00\n "+
        "Friday from 07:00 to  21:00\n "+
        "Saturday from 11:00 to  20:00\n"+
        "Sunday------------Close-------\n"
    )

    def on_enter_fsm(self,reply_token):
        quick_reply = LineAPI.makeQuickReplyText([
            'Main'
        ])
        LineAPI.sendImageWithURL(reply_token,FSM_GRAPH_URL)
        # LineAPI.send_fsm_graph(reply_token)
        LineAPI.commitMessage()


    def on_enter_menu(self,reply_token):
        quick_reply = LineAPI.makeQuickReplyText([
            'Main Dishes',
            'Drinks',
            'Order Show'
        ])
        LineAPI.send_reply_message(
            reply_token, reply_msg = FSMchatbot.menu_text, quickReply=quick_reply 
        )
        LineAPI.commitMessage()

    def on_enter_main_dishes(self, reply_token):
        from app import MainDish 
        
        LineAPI.send_reply_message(
            reply_token, reply_msg="There are some of our Main Dishes:")
        
        #Send 5 Carousel of 5 random Main Dishes:
        main_dishes = MainDish.query.all()
        main_dishes = random.sample(main_dishes, 5)
        elements  = []
        
        for main in main_dishes:
            elements.append(LineAPI.makeCarouselElement(
                main.picture,
                f"                            {main.name}",
                main.price,
                f"SET_MAIN {main.id} {main.price}"        
            ))

        print(elements)
        LineAPI.sendCarousel(reply_token, elements) 
        quick_reply = LineAPI.makeQuickReplyText([
            'More Food',
            'Check',
            'Main'
            
        ])
        if self.repeatedDish == True:
            LineAPI.send_reply_message(reply_token,reply_msg="Sorry right now only can order \n " +
                                        "one main dish per order\n"+
                                        "If you want to change order you have to go back to main")
        LineAPI.send_reply_message(
            reply_token, reply_msg="Are you Hungry?", quickReply=quick_reply)
        LineAPI.commitMessage()
    def on_enter_test(self,reply_token):        
    
        LineAPI.send_reply_message(
            reply_token, reply_msg="New State")
        LineAPI.commitMessage()


    def on_enter_drink(self, reply_token):
        from app import Drink 

        LineAPI.send_reply_message(
            reply_token, reply_msg="There are some of our Main Dishes:")
        LineAPI.commitMessage()
        
        #Send 5 Carousel of 5 random Main Dishes:
        drinks= Drink.query.all()
        drinks= random.sample(drinks, 5)
        elements = [LineAPI.makeCarouselElement(
            main.picture, 
            main.name, 
            main.price,
            f"SET_DRINK {main.id} {main.price}"   
        )
        for main in drinks]
        LineAPI.sendCarousel(reply_token, elements) 
        quick_reply = LineAPI.makeQuickReplyText([
            'More Drinks',
            'Check',
            'Main'
        ])
        if self.repeatedDrink == True:
            LineAPI.send_reply_message(reply_token,reply_msg="Sorry right now only can order \n " +
                                        "one main drink per order\n"+
                                        "If you want to change order you have to go back to main")
        LineAPI.send_reply_message(
            reply_token, reply_msg="Are you Hungry?", quickReply=quick_reply)
        LineAPI.commitMessage()

    def on_enter_order_show(self,reply_token):

        if self.curr_drink or self.curr_main: 
            LineAPI.send_reply_message(reply_token,
                                        f"Hi {self.userName}\n" + 
                                        f"Your Order is { 'not ordered' if not  self.curr_main else self.curr_main.name}\n"+
                                        f"with {'not ordered' if not self.curr_drink else self.curr_drink.name}\n"+
                                        f"And a price of {self.total_price} NTD\n",
                                        LineAPI.makeQuickReplyText([
                                            'Go back to menu',
                                            'Set order',
                                            'Main'
                                            ]))                                        
            LineAPI.commitMessage()
        else:
            LineAPI.send_reply_message(reply_token,
                                        "Sorry you havent order anything\n",
                                        LineAPI.makeQuickReplyText([
                                            'Go back to menu'
                                        ])
                                        )
            LineAPI.commitMessage()


    def on_enter_set_order(self, reply_token):
        LineAPI.send_reply_message(reply_token,
                                    "Before confirm your order we just need\n"+
                                    "some information from you\n")
        LineAPI.sendButtons(reply_token,["Log In"], 'Set at order before?')
        LineAPI.send_reply_message(
            reply_token,"How do we should call you? (Please write your name)"
        )
        LineAPI.commitMessage()

    def on_enter_get_phone(self,reply_token,invalid:bool = False):
        if invalid:
            LineAPI.send_reply_message(
                reply_token, "Please insert a valid Phone Number"
            )
        else:
            LineAPI.send_reply_message(
                reply_token,"Write your phone number to contact you"
            )
        LineAPI.commitMessage()
    
    def on_enter_register_client(self,reply_token, repeated:bool = False):
        if repeated:
            LineAPI.send_reply_message(
                reply_token,"Wrong Input or Not register Before")
        LineAPI.send_reply_message(reply_token,"Please Write your phone Number", 
                                     LineAPI.makeQuickReplyText(['go back']))
        LineAPI.commitMessage()
        pass
    
    def on_enter_confirm(self,reply_token) :
        LineAPI.send_reply_message(reply_token,"The following is the contaact\n" +
                                    "information you have entered\n"+
                                    f"Name: {self.userName}\n"+
                                    f"Phone Number: {self.phoneNumber}"
        )
        quick_reply = LineAPI.makeQuickReplyText(["Yes","No"])
        LineAPI.send_reply_message(reply_token,"Is this Correct?",quick_reply)
        LineAPI.commitMessage()

    def on_enter_check_out(self,reply_token):

        from app import User,db
        user = User.query.filter(User.line_id == self.lineId).first()
        if not user:
            print("Create New User")
            user = User(line_id = self.lineId, name  = self.userName,
                        phone=self.phoneNumber)


        # print (user.name,user.phone, order.user_id)

        db.session.add(user)
        db.session.commit()

    #Send Response to the Client
        LineAPI.send_reply_message(reply_token,
                                f"---------------ORDER----------------\n"+
                                f"Your order has been created at time {datetime.utcnow().strftime('%B %d %Y - %H:%M:%S')}\n"+
                                f"User: {self.userName}\n"+
                                f"Phone:{self.phoneNumber}\n"+
                                f"Your Order is { 'not ordered' if not  self.curr_main else self.curr_main.name}\n"+
                                f"with {'not ordered' if not self.curr_drink else self.curr_drink.name}\n"+
                                f"The price to pay is {self.total_price} NTD\n"+
                                "Have a nice day",
                                LineAPI.makeQuickReplyText(['Main'
                                ]))
        LineAPI.commitMessage()





    # def on_enter_main(self,reply_token):


    
    # def __init__(self, **machine_configs):
    #     self.machine = GraphMachine(model=self, **machine_configs)

    # def is_going_to_state1(self, event):
    #     text = event.message.text
    #     return text.lower() == "go to state1"

    # def is_going_to_state2(self, event):
    #     text = event.message.text
    #     return text.lower() == "go to state2"

    # def on_enter_state1(self, event):
    #     print("I'm entering state1")

    #     reply_token = event.reply_token
    #     send_text_message(reply_token, "Trigger state1")
    #     self.go_back()

    # def on_exit_state1(self):
    #     print("Leaving state1")

    # def on_enter_state2(self, event):
    #     print("I'm entering state2")

    #     reply_token = event.reply_token
    #     send_text_message(reply_token, "Trigger state2")
    #     self.go_back()

    # def on_exit_state2(self):
    #     print("Leaving state2")

if __name__ == '__main__':
    mach = FSMchatbot()