import os

from dotenv import load_dotenv
from linebot import LineBotApi
from linebot.models import ButtonsTemplate, TemplateSendMessage, TextSendMessage, ImageSendMessage, QuickReply, QuickReplyButton, MessageAction, CarouselTemplate, CarouselColumn, DatetimePickerAction, PostbackAction
from linebot.exceptions import LineBotApiError

load_dotenv()
# DEFAULT_API_ENDPOINT = 'https://api.line.me'
# DEFAULT_API_DATA_ENDPOINT= 'https://api-data.line.me'
# channel_access_token = "n9eG76y/jysHQzzHn8QpB5iT79aRxX6ulLdx/ZrKvEnBXtKYOnjVsdlzcd9eavJHf4NQ98kk/Bh4nt/Rsx2KFvYFBH/f+oRABQiwX7tMjL/QI0ZQYKqOMC7vkavSpY3q9x+OPMRFXsRG1QGvelgeKwdB04t89/1O/w1cDnyilFU="
line_bot_api= LineBotApi(os.environ.get("LINE_CHANNEL_ACCESS_TOKEN"))
def webhook_parser(webhook):
    event = webhook["events"][0]
    reply_token = event["replyToken"]
    user_id = event["source"]["userId"]
    if "message" in event.keys():
        message = event["message"]["text"]

    elif "postback" in event.keys():
        if "data" in event["postback"]:
            message = event["postback"]["data"]

    return reply_token,user_id,message


class LineAPI:
    replyTkon = None
    messages = []

    @staticmethod
    def addMessage(reply_token, text):
        LineAPI.messages.append(text)
        LineAPI.replyTkon = reply_token

    @staticmethod
    def commitMessage():
        try:
            # print("Enter")
            line_bot_api.reply_message(LineAPI.replyTkon, LineAPI.messages)
            LineAPI.messages.clear()
        except LineBotApiError as e:
            print(e)
    
    @staticmethod
    def send_reply_message(reply_token, reply_msg, quickReply = None):
        reply = TextSendMessage(text=reply_msg, quick_reply = quickReply)
        try:
            LineAPI.addMessage(reply_token,reply)
        except LineBotApiError as e:
            print(e)
    


    @staticmethod
    def makeQuickReplyText(texts):
        replyButtons = []
        for item in texts:
            act = MessageAction(item,item)
            replyButtons.append(QuickReplyButton(action=act))
        reply = QuickReply(items = replyButtons)
        return reply
    

    @staticmethod
    def makeCarouselElement(pictureURI:str, text:str, label:str ,trigger: str="none"):
        act = None
        if trigger != "none" :
            act = PostbackAction(data = trigger, label =label)
            print(act)
        else:
            act = PostbackAction(data =label, label = label)
        return CarouselColumn(thumbnail_image_url = pictureURI, text = text , default_action=act,actions=[act])
    @staticmethod
    def sendCarousel(reply_token,elements:list):
        carousel = CarouselTemplate(elements)
        try:
            LineAPI.addMessage(reply_token,TemplateSendMessage(alt_text = "Tutor Images", template = carousel))
        except LineBotApiError as e:
            print(e)

    @staticmethod
    def sendButtons(reply_token, buttons:list =[], txt = ""):
        actions = []
        for button in buttons:
            if type(button) is str:
                actions.append(MessageAction(button,button))
            else:
                actions.append(button)
        template = ButtonsTemplate(txt,actions=actions)
        LineAPI.addMessage(reply_token,TemplateSendMessage("button menu",template))
    
    @staticmethod
    def sendImageWithURL(reply_token, url:str):
        message = ImageSendMessage(url,url)
        LineAPI.addMessage(reply_token, message)

    # def send_fsm_graph(self, reply_token):
    #     try:
    #         # for demo, hard coded image url, line api only support image over https
    #         LineAPI.addMessage(reply_token, ImageSendMessage(
    #             original_content_url=FSM_GRAPH_URL, preview_image_url=FSM_GRAPH_URL))
    #     except LineBotApiError as e:
    #         print(e)



   


"""
def send_image_url(id, img_url):
    pass

def send_button_message(id, text, buttons):
    pass
"""
