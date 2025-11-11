import json
from flask import Flask,render_template,request,redirect,flash,url_for
from datetime import datetime

def loadClubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showSummary',methods=['POST'])
def showSummary():
    club = [club for club in clubs if club['email'] == request.form['email']][0]
    return render_template('welcome.html',club=club,competitions=competitions)


@app.route('/book/<competition>/<club>')
def book(competition,club):
    foundClub = [c for c in clubs if c['name'] == club][0]
    foundCompetition = [c for c in competitions if c['name'] == competition][0]
    if foundClub and foundCompetition:
        return render_template('booking.html',club=foundClub,competition=foundCompetition)
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions)
    
    
@app.template_filter("is_past")
def is_past_filter(value, fmt="%Y-%m-%d %H:%M:%S"):
    if isinstance(value, datetime):
        date_value = value
    else:
        try:
            date_value = datetime.strptime(value, fmt)
        except Exception:
            return False
    return date_value < datetime.now()


@app.route('/purchasePlaces',methods=['POST'])
def purchasePlaces():
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
    placesRequired = int(request.form['places'])
    comp_date = datetime.strptime(competition["date"], "%Y-%m-%d %H:%M:%S")
    if comp_date < datetime.now():
        error = "Il est n'est pas possible de réserver des places dans une compétition déjà terminée."
        return render_template("booking.html", club=club, competition=competition, error=error), 400
    
    MAX_PLACES = 12
    already_booked = club.get(competition['name'], 0)
    total_places = placesRequired + already_booked
    
    if placesRequired > MAX_PLACES or total_places > MAX_PLACES:
        error = f"You can't book more than {MAX_PLACES} seats per competition."
        return render_template("booking.html", club=club, competition=competition, error=error), 400
    
    competition['numberOfPlaces'] = int(competition['numberOfPlaces'])-placesRequired
    flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))