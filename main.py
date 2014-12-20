from googlevoice import Voice
import os
import sys
import BeautifulSoup
import random
import re
from multiprocessing import Process
import time

def extractsms(htmlsms) :
    """
    extractsms  --  extract SMS messages from BeautifulSoup tree of Google Voice SMS HTML.

    Output is a list of dictionaries, one per message.
    """
    msgitems = []                                       # accum message items here
    #   Extract all conversations by searching for a DIV with an ID at top level.
    tree = BeautifulSoup.BeautifulSoup(htmlsms)         # parse HTML into tree
    conversations = tree.findAll("div",attrs={"id" : True},recursive=False)
    for conversation in conversations :
        #   For each conversation, extract each row, which is one SMS message.
        rows = conversation.findAll(attrs={"class" : "gc-message-sms-row"})
        for row in rows :                               # for all rows
            #   For each row, which is one message, extract all the fields.
            msgitem = {"id" : conversation["id"]}       # tag this message with conversation ID
            spans = row.findAll("span",attrs={"class" : True}, recursive=False)
            for span in spans :                         # for all spans in row
                cl = span["class"].replace('gc-message-sms-', '')
                msgitem[cl] = (" ".join(span.findAll(text=True))).strip()   # put text in dict
            msgitems.append(msgitem)                    # add msg dictionary to list
    return msgitems

def lastsms():
    print ("listening...")
    while 3:
        voice.sms()
        for msg in extractsms(voice.sms.html):
            if os.path.isfile("messages/" + msg["from"]) == False: #if it is a first-time number
                fo = open("messages/" + msg["from"], "a")
                voice.send_sms(msg["from"], "Welcome to Dexter Bot's text-based RPG game. Type !help for help")
                try:
                    fo.write("0\n" + msg["text"])
                except UnicodeEncodeError:
                    voice.send_sms(msg["from"], "only alpha-numeric characters please.")
                    print("non-alpha-numeric detected")
                except IndexError:
                    voice.send_sms(msg["from"], "no bot-crashing")
                    os.remove("messages/"+msg["from"])
                    print("IndexError handled from: "+msg["from"])



            else:
                #print str(msg)
                fo = open("messages/" + msg["from"], "r+")
                lines = fo.read().splitlines()
                ##print("\n\n"+str(lines)+"\n\n")
                fo.close()

                fo = open("messages/" + msg["from"], "w")
                
                try:
                    fo.write(str(lines[0]) + "\n" + str(msg["text"]));
                except UnicodeEncodeError:
                    voice.send_sms(msg["from"], "only alpha-numeric characters please.")
                    print("non-alpha-numeric detected")
                except IndexError:
                    voice.send_sms(msg["from"], "no bot-crashing")
                    os.remove("messages/"+msg["from"])
                    print("IndexError handled from: "+msg["from"])


                    

            fo.close()

            for message in voice.sms().messages:
                if str(message) == str(msg["id"]):
                    message.delete()






def main():
    while 2:
        file_list = os.listdir("messages")
        for filename in file_list:
            #check contents
            fo = open("messages/" + filename)
            #command = fo.read()
            lines = []
            if os.path.getsize("messages/"+filename) > 0:
                lines = fo.read().splitlines()
            
            if len(lines) > 1:
                try:
                    os.remove("messages/Me:")
                except:
                    pass
                progress = lines[0]
                response = lines[1]               
                print("situation id: "+progress+" from: "+filename+" said: "+response)

                prompt = ""

                if re.match("\!.*", response):
                    command = re.search("[^!][A-z0-9]*", response, flags=re.I).group(0)
                    
                    if command.lower() == "help":
                        prompt = "!new - starts a new game \n!credits - display credits \nhello dexter - greeting"

                    elif command.lower() == "credits":
                        prompt = "Programer(s): Jonathan Buchanan\nStory: Keadin Hull\nAPI: google voice"
                    
                    elif command.lower() == "botsnack":
                        prompt = ":D"
                    elif command.lower() == "new":
                        prompt = "game reset"
                        progress = 0
                    

                    else:
                        prompt = "command not found : " + command

                elif re.match("((dex.?.?.?).*((hello)|(hi)|(howdy)|(hey)|(greetings)).*)|(((hello)|(hey)|(hi)|(howdy)|(greetings)).*(dex.?.?.?)).*", response, flags=re.I):
                    prompt = random.choice(["Hello!","Hi","Salutations.", "Why, hello there!"])

                elif re.search("((what\'?s)|(what is)) ((your)|(youre)|(you're)|(ur)) (name)(.?)", response, flags=re.I):
                    prompt = "My name is Dexter V. Bot!"
                
                elif re.search("(.*)(hint)(.*)", response, flags=re.I):
                    prompt = random.choice(["*gasp* what?!", "I can't give hints!", "D:", "figure it out"])

                elif re.search("(shut) ?(up)(.*)(dex.?.?.?)(.*)", response, flags=re.I):
                    #nothing
                    prompt = ""

                elif re.search("(good)?(bye)(.*)(dex.?.?.?)(.*)", response, flags=re.I):
                    prompt = random.choice(["ttyl","cya","2daloo","bye"])

                else:

                    if int(progress) == 0:
                        prompt = "Hello, what is your favorite color? Blue, Yellow, or Green"
                        progress = 1
                    elif int(progress) == 1:
                        if response.lower() == "yellow":
                            prompt = "what shade of yellow? Dark or light?"
                            progress = 2
                        elif response.lower() == "blue":
                            prompt = "what shade of blue? Navy or Sky?"
                            progress = 3
                        elif response.lower() == "green":
                            prompt = "what shade of green? Dark Green or Neon Green?"
                            progress = 4
                        else:
                            prompt = random.choice(["I don't understand","The choices were blue, yellow, and green.","is that even a color?","I see. maybe you should try again","your mom is "+response])

                    elif int(progress) == 2 or int(progress) == 3 or int(progress) == 4:
                        prompt = "jk, I don't actually care"
                        progress = 5
                    
                    elif int(progress) == 5:
                        prompt = "you can type !new to reset game"

                    else:
                        prompt = "duuuude.  your save file is seriously messed up"

               
                try:
                    voice.send_sms(filename, prompt)
                    print("answered: "+prompt)
                except:
                    print("stupid google voice probably didn't send")


                fo.close()
                fo = open("messages/" + filename, "w")
                fo.write(str(progress))
            


print("logging in...")
voice = Voice()
try:
    voice.login("texterbot14","i<3texting")
except:
    print("unknown error")
    quit()
print("logged in successfully")

try:
    savesms = Process(target=lastsms)
    savesms.start()
except:
    savesms = Process(target=lastsms)
    savesms.start()
#savesms.join()

main()

"""
main = Process(target=main)
main.start()
main.join()
"""
