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
            if os.path.isfile("messages/" + msg["from"]) == False:
                fo = open("messages/" + msg["from"], "a")
                fo.write("0\n" + msg["text"])

            else:
                #print str(msg)
                fo = open("messages/" + msg["from"], "r+")
                lines = fo.read().splitlines()
                ##print("\n\n"+str(lines)+"\n\n")
                fo.close()

                fo = open("messages/" + msg["from"], "w")

                fo.write(str(lines[0]) + "\n" + str(msg["text"]));

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
            lines = fo.read().splitlines()
            
            if len(lines) > 1:
                os.remove("messages/Me:")
                progress = lines[0]
                print("situation id: "+progress)
                response = lines[1]
                print("their response: "+response)
                prompt = ""

                if int(progress) == 0:
                    prompt = "Hello, what is your favorite color? Blue, Yellow, or Green]"
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
                        prompt = "I don't understand.  Try again"
                elif int(progress) == 2 or int(progress) == 3 or int(progress) == 4:
                    prompt = "jk, I don't actually care"
                    progress = 0
                else:
                    prompt = "duuuude.  your save file is seriously messed up"
                print(prompt)
                try:
                    voice.send_sms(filename, prompt)
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

savesms = Process(target=lastsms)
savesms.start()
#savesms.join()

main()

"""
main = Process(target=main)
main.start()
main.join()
"""
