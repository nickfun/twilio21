
#
# Twilio Blackjac
#
# Nicholas Funnell 2015-03-19 nick@nick.gs
#

from flask import Flask, request, render_template
from random import randint
import pprint

server = Flask("blackjack")
pp = pprint.PrettyPrinter(indent=4)
db = {}
host = "http://deba25b.ngrok.com"

class SessionStruct(object):
    def __init__(self, count=None, wins=None, playerHand=None, dealerHand=None):
        self.count = count
        self.wins = wins
        self.playerHand = playerHand
        self.dealerHand = dealerHand

def getSession(number):
    if db.has_key(number):
        print "Session Exists! {}".format(number)
        return db[number]
    else:
        db[number] = SessionStruct()
        print "Session CREATED {}".format(number)
        return db[number]

def calculateHand(start=0):
    return start + randint(2,10)

@server.route("/")
def main():
    if request.values.get('From') == None:
        return "!!! Not from Twilio\n\n"
    session = getSession(request.values.get('From'))
    tplData = {}
    tplData['first_message'] = ""
    tplData['host'] = host
    if request.values.get('CallStatus') == "ringing":
        # the first call
        session.count = 0
        session.wins = 0
        session.playerHand = calculateHand()
        session.dealerHand = calculateHand()
        tplData['first_message'] = "Welcome to Twilio 21 the app by Nick your dealer is Jason"
    session.count = session.count + 1
    tplData['gather_message'] = 'this is the gather message I hope you enjoy it a lot. you are in session {}'.format(session.count)
    # save session
    db[request.values.get('From')] = session
    return render_template("twiml.xml", t=tplData)

@server.route("/sessions")
def showSessions():
    if len(db) == 0:
        return "No Session!\n"
    
    result = ""
    for key in db:
        result = result + "- {}\n".format(key)
    return result
    
# RUN SERVER
server.run(debug=True)
print "server is running :-)"
