#
# Twilio Blackjack
#
# Nicholas Funnell
# nick@nick.gs
# 2015-03-19 
#

from flask import Flask, request, render_template, Response
from random import randint
import json
import os

HIT  = "1"
STAY = "3"
QUIT = "6"
PORT = int(os.getenv("PORT", "5050"))
HOST = os.getenv("HOST", "localhost")

server = Flask("blackjack")
db = {}
messages = {
    "welcome": "Welcome to the Twilio 21 App by Nick. ",
    "begin_game": "It's time for a new game! The dealer has {dealer} and you have {player}. ",
    "instructions": "{} to hit, {} to stay, {} to quit. ".format(HIT, STAY, QUIT),
    "status": "Dealer has {dealer} and you have {player}, what do you want to do? "
}

def getSession(number):
    if db.has_key(number):
        print "Session Exists! {}".format(number)
        return db[number]
    else:
        db[number] = {
            "count": 0,
            "wins": 0,
            "playerHand": 0,
            "dealerHand": 0,
            "callSid": None
        }
        print "Session CREATED {}".format(number)
        return db[number]

def calculateHand(start=0):
    return start + randint(2,10)

@server.route("/")
def index():
    return render_template("index.html")
    
@server.route("/app")
def main():
    if request.values.get('From') == None:
        print "--- Not From Twilio!"
        return "!!! Not from Twilio\n\n"
    session = getSession(request.values.get('From'))
    choice = request.values.get("Digits")
    tplData = {}
    tplData['host'] = HOST + ":" + str(PORT)
    tplData['key_hit'] = HIT
    tplData['key_stay'] = STAY
    tplData['key_quit'] = QUIT

    if request.values.has_key('CallSid'):
        session['callSid'] = request.values.get('CallSid')

    if request.values.get('CallStatus') == "ringing":
        # the first call
        print "First Call!"
        session['count'] = 0
        session['wins'] = 0
        session['playerHand'] = calculateHand()+calculateHand()
        session['dealerHand'] = calculateHand()
        tplData['message'] = messages['welcome']
        tplData['message'] += messages['begin_game'].format(dealer=session['dealerHand'], player=session['playerHand']) + messages['instructions']
    else:
        # decide based on user choice
        if choice == HIT:
            print "PLAYER CHOOSE HIT"
            session['playerHand'] = calculateHand(session['playerHand'])
            if session['playerHand'] > 21:
                tplData['message'] = "You bused! You have {} and that is too much! Sorry. ".format(session['playerHand'])
                # restart the game
                session['playerHand'] = calculateHand()+calculateHand()
                session['dealerHand'] = calculateHand()
                tplData['message'] += messages['begin_game'].format(dealer=session['dealerHand'], player=session['playerHand'])
                session['count'] += 1
            else:
                tplData['message'] = messages['status'].format(dealer=session['dealerHand'], player=session['playerHand'])
        elif choice == STAY:
            print "PLAYER CHOOSE STAY"
            while session['dealerHand'] <= 18 or session['dealerHand'] <= session['playerHand']:
                nextHand = calculateHand(session['dealerHand'])
                print "DEALER HITS: {} => {} ".format(session['dealerHand'], nextHand)
                session['dealerHand'] = nextHand
            if session['dealerHand'] > 21 or session['playerHand'] > session['dealerHand']:
                # player wins!
                session['count'] += 1
                session['wins'] += 1
                tplData['message'] = "The dealer busted with {}, you are the winner! ".format(session['dealerHand'])                
            else:
                # dealer wins
                tplData['message'] = "The dealer wins the game with {} ".format(session['dealerHand'])
                session['count'] += 1
            # restart the game
            session['playerHand'] = calculateHand()+calculateHand()
            session['dealerHand'] = calculateHand()
            tplData['message'] += messages['begin_game'].format(dealer=session['dealerHand'], player=session['playerHand'])
        elif choice == QUIT:
            print "PLAYER CHOOSE QUIT"
            # Save Session
            db[request.values.get('From')] = session
            tplData = {}
            wins = session['wins']
            loss = session['count'] - wins
            if wins > loss:
                tplData['message'] = "You are a pretty good player! "
            else:
                tplData['message'] = "Stay away from Las Vegas. "
            return render_template("quit.xml", s=session, t=tplData)
        else:
            print "UNKNOWN PLAYER CHOICE"
            tplData['message'] = 'Unknown Choice! ' + messages['status'].format(dealer=session['dealerHand'], player=session['playerHand']) + messages['instructions']

    # save session
    db[request.values.get('From')] = session
    return render_template("twiml.xml", t=tplData, s=session)

@server.route("/sessions")
def showSessions():
    if len(db) == 0:
        return "No Session!\n"
    
    result = ""
    for key in db:
        result = result + "- {}\n".format(key)
    return result

@server.route("/json")
def showAllSession():
    resp = Response(json.dumps(db, indent=4))
    resp.headers['Content-Type'] = 'application/json'
    return resp
    
# RUN SERVER
print "HOST is {} PORT is {}".format(HOST,PORT)
server.run(debug=True, port=PORT, host="0.0.0.0")
