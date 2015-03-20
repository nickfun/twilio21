#
# Twilio Blackjack
#
# Nicholas Funnell
# nick@nick.gs
# 2015-03-19 
#

from flask import Flask, request, render_template, Response
from random import randint
import pprint
import json

server = Flask("blackjack")
pp = pprint.PrettyPrinter(indent=4)
db = {}
host = "http://deba25b.ngrok.com"

def getSession(number):
    if db.has_key(number):
        print "Session Exists! {}".format(number)
        return db[number]
    else:
        db[number] = {
            "count": 0,
            "wins": 0,
            "playerHand": 0,
            "dealerHand": 0
        }
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
        session['count'] = 0
        session['wins'] = 0
        session['playerHand'] = calculateHand()
        session['dealerHand'] = calculateHand()
        tplData['first_message'] = "Welcome to Twilio 21 the app by Nick your dealer is Jason"
    session['count'] += 1
    tplData['gather_message'] = 'this is the gather message I hope you enjoy it a lot. you are in session {}'.format(session['count'])
    session['playerHand'] = calculateHand(session['playerHand'])
    session['dealerHand'] = calculateHand(session['dealerHand'])
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
server.run(debug=True)
