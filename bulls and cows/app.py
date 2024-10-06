import os
import random
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session,url_for,jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_socketio import SocketIO, emit, join_room, leave_room
from helpers import apology, login_required, lookup, usd
from datetime import datetime

current_attimpt1=0
users=[]
old=0
user_number=None
now = datetime.now()
month = now.month
day = now.day
houre = now.hour
# Configure application
app = Flask(__name__)
socketio=SocketIO(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///final.db")

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@socketio.on('connect')
def handle_connect():
    print('client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('client disconnected')


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response



def generate_random_number():
    number=[1,2,3,4,5,6,7,8,9]
    number2=[1,2,3,4,5,6,7,8,9,0]
    x=random.randint(0, 8)
    digit1=number[x%9]
    print("digit1",digit1)

    for n in number2:
        if digit1 == n:
            number2.remove(n)
    print("number2",number2)
    y=random.randint(0, len(number2) - 1)
    digit2=number2[y%len(number2)]
    print("digit2",random.randint(0, len(number2) - 1)%len(number2))
    for n in number2:
        if digit2 == n:
            number2.remove(n)
    print("number2",number2)
    z=random.randint(0, len(number2) - 1)
    digit3 = number2[z%len(number2)]
    print("digit3",digit3)
    for n in number2:
        if digit3 == n:
            number2.remove(n)
    print("number2",number2)
    v=random.randint(0, len(number2) - 1)
    digit4 = number2[v%len(number2)]
    print("digit4",digit4)
    random_number=digit1*1000+digit2*100+digit3*10+digit4
    print("random_number",random_number)
    r_m = str(digit1)+str(digit2)+str(digit3)+str(digit4)
    r_m=int(r_m)

    return random_number

def generate_N_digit_random_number(digit_N,purvious_random_number=None):
    number=[1,2,3,4,5,6,7,8,9,0]
    random_number_L=[]
    for n in range(int(digit_N)):
        random_N=random.choice(number)
        number.remove(random_N)
        random_number_L.append(random_N)

    if random_number_L[0]==0:
        random_number_L=generate_N_digit_random_number(digit_N)
    random_number=""
    for n in range(int(digit_N)):
        random_number= random_number+str(random_number_L[n])
    print("random_number",random_number)

    if purvious_random_number:
        string=str(purvious_random_number)
        digit_plus=random.choice(number)
        print("digit_plus",digit_plus)
        digit_plus=str(digit_plus)
        index=random.randint(0, len(string) - 1) %len(string)
        new_string=string[:index]+digit_plus+string[index:]
        new_number=int(new_string)
        print("new_numberSSSSSSSSSSSSSSSSSSS",new_number)
        return new_number

    return random_number



def gusse_check(guess, random_number, user_id):
    print("Random number:", random_number)
    bulls = 0
    cows = 0
    winer = False
    global users


    # Search for the user in the existing users list
    user_exists = False
    for user in users:
        if user["user_id"] == user_id:
            # User found, update their guess and increment current_attempt
            if not user["current_attempt"]:
                user['current_attemp']:1
            user["current_attempt"] += 1
            user["guess"] = guess
            user["attempts"].append(guess)
            user_exists = True
            break

    # If the user does not exist, add a new entry
    if not user_exists:
        users.append({
            "user_id": user_id,
            "guess": guess,
            "current_attempt": 1,
            "help":1,
            "attempts": [guess]
        })


    digit4=int(random_number)%10
    number1=int(random_number)/10
    digit3=int(number1)%10
    number2=int(number1)/10
    digit2=int(number2)%10
    number3=int(number2)/10
    digit1=int(number3)
    plyer_gusse=[]
    string=str(guess)
    plyer_gusse_L=[]
    digits_L=[]
    for c in string:
        int1=int(c)
        plyer_gusse.append(int1)

    # Convert the guess and random number into lists of integers
    for c in guess:
        plyer_gusse_L.append(int(c))
    for c in str(random_number):
        digits_L.append(int(c))
    

    print("plyer_gusse_L", plyer_gusse_L)
    print("digits_L", digits_L)

    # First, find bulls (correct digit in the correct place)
    for i in range(len(digits_L)):
        if plyer_gusse_L[i] == digits_L[i]:
            bulls += 1
            # Mark the bull digits with placeholders
            digits_L[i] = 'a'
            plyer_gusse_L[i] = 'b'

    # Then, find cows (correct digit in the wrong place)
    for i in range(len(plyer_gusse_L)):
        if plyer_gusse_L[i] == 'b':  # Skip if it's already a bull
            continue
        for j in range(len(digits_L)):
            if digits_L[j] == 'a':  # Skip if it's already a bull
                continue
            if plyer_gusse_L[i] == digits_L[j]:
                cows += 1
                digits_L[j] = 'a'  # Mark the cow digit
                break
    for index, user in enumerate(users):
            if user["user_id"] == session["user_id"]:
                ind=index
                break
    # Check if all digits are bulls (win condition)
    if bulls == len(digits_L):
        winer = True
        users[ind]["help"]+=1
        print("winer444444444444",winer)
        print("help",users[ind]["help"])

    for user in users:
        if user["user_id"] == session["user_id"]:
            user["bulls"] = bulls
            user["cows"] = cows
            break

    print("current_attempt",users[ind]["current_attempt"])
    n=4
    c=[]
    if users[ind]["current_attempt"]>=10:
        c.append(users[ind]["current_attempt"])
        ff=str(users[ind]["current_attempt"])
        print("LLLLLLLLLLL",c)
        print("LLLLLLLLLLL",ff[0],ff[1])
        if ff[1]=='0':
                punch_number=generate_N_digit_random_number(n,random_number)
                while len(set(str(punch_number))) != len(str(punch_number)):
                    punch_number = generate_N_digit_random_number(n, random_number)
                    session["random_number"] = punch_number
                    print("New punch number without duplicates:", punch_number)
                session["random_number"]=punch_number
                print("punch_number",punch_number)



    return bulls,cows,users,winer,digits_L,plyer_gusse_L


def gusse_check_N_digits(guess, random_number, user_id):
    bulls = 0
    cows = 0
    winer1 = False
    global users

    # Search for the user in the existing users list
    user_exists = False
    for user in users:
        if user["user_id"] == user_id:
            # Initialize current_attempt_N if not already present
            user["current_attempt_N"] = user.get("current_attempt_N", 0) + 1
            user["guess"] = guess
            user["attempts"].append(guess)  # Add only the guess, not a dictionary
            user_exists = True
            break

    # If the user does not exist, add a new entry
    if not user_exists:
        users.append({
            "user_id": user_id,
            "guess": guess,
            "current_attempt_N": 1,  # Use current_attempt_N consistently
            "attempts": [guess],
            "bulls": 0,
            "cows": 0
        })

    # Convert the guess and random number into lists of integers
    plyer_gusse_L = [int(c) for c in guess]
    digits_L = [int(c) for c in str(random_number)]

    print("plyer_gusse_L", plyer_gusse_L)
    print("digits_L", digits_L)

    # First, find bulls (correct digit in the correct place)
    for i in range(len(digits_L)):
        if plyer_gusse_L[i] == digits_L[i]:
            bulls += 1

            digits_L[i] = 'a'
            plyer_gusse_L[i] = 'b'


    for i in range(len(plyer_gusse_L)):
        if plyer_gusse_L[i] == 'b':
            continue
        for j in range(len(digits_L)):
            if digits_L[j] == 'a':
                continue
            if plyer_gusse_L[i] == digits_L[j]:
                cows += 1
                digits_L[j] = 'a'  # Mark the cow digit
                break

    # Check if all digits are bulls (win condition)
    if bulls == len(digits_L):
        winer1 = True

    # Update the user's bulls and cows
    for user in users:
        if user["user_id"] == user_id:
            user["bulls"] = bulls
            user["cows"] = cows
            print("Updated user data:", users)
            break

    return bulls, cows, users, winer1




@app.route("/")
@login_required
def index():
    return redirect("/home")


@app.route("/home", methods=["GET", "POST"])
@login_required
def home():
    if request.method == "GET":
        return render_template("/home.html")

    if request.method == "POST":
        print(request.form)  # Debugging line

        # Check if 'local_game' button was pressed
        if 'local_game' in request.form:
            return redirect('/local_game', code=302)

        # Check if 'local_N_Digit_game' button was pressed
        if 'local_N_Digit_game' in request.form:
            
            return redirect("/local_N_Digit_game", code=302)
        if 'handle_game_selection' in request.form:
            return redirect("/handle_game_selection")

    return render_template("/home.html")


@app.route("/local_game",methods=["GET" ,"POST"])
#@login_required
def local_game():
    global users
    if request.method == "GET":
        return render_template("index.html")
    if request.method == "POST":

        print("HHHHHHHHHHHHHHH",session['user_id'])
        reveal=request.form.get("reveal")
        remove=request.form.get("remove")
        user_gusse=request.form.get("input")
        current_attempt=request.form.get("current_attempt")
        print("HHHHHHHHHHHHHHH",current_attempt)
        print("reveal:", reveal)

        if not session.get("random_number"):
             random_number=generate_random_number()
             print("random_number4444444",random_number)
             session["random_number"]=random_number
             session["attempts"] = []

        results=gusse_check(user_gusse,session["random_number"],session["user_id"])

        for index, user in enumerate(users):
                if user["user_id"] == session["user_id"]:
                    ind=index
                    break
        if users[ind]["help"]>0:
            if reveal == "reveal_digit":
                r_n=str(session["random_number"])
                show_digit = r_n[random.randint(0, len(user_gusse) - 1)]
                print("show_digit1111111111111111", show_digit)
                flash(f"Revealed digit:{show_digit}")
                users[ind]["help"]-=1


            if remove == "remove_wrong_number":
                number_list=[0,1,2,3,4,5,6,7,8,9]
                r_m=str(session["random_number"])
                for c in r_m:
                    number_list.remove(int(c))
                print("number_list:",number_list)
                removed_number=number_list[random.randint(0,9)%len(number_list)]
                flash(f"removed_number:{removed_number}")
                users[ind]["help"]-=1
        else:
                return apology("You don't have enough helps. Try to guess the number to increase help and try again.")

        required_length = 4 + (users[ind]["current_attempt"] // 10)
        if len(user_gusse) != required_length:
            return apology(f"The number length must equal to {required_length}", 403)

        print("session",session)
        bulls=results[0]
        cows=results[1]
        users_list=results[2]
        print("users_list",users_list)
        users=results[2]
        winer=results[3]
        print("bulls",bulls)
        print("cows",cows)
        print("winer",winer)
        print("users_list",users_list)
        if "attempts" not in session:
            session["attempts"] = []


         # Store the attempt
        session["attempts"].append({"guess": user_gusse, "bulls": bulls, "cows": cows})
        users[ind]["attempts"].append({"attempts":user_gusse})
        bulls = bulls if bulls else 0
        cows = cows if cows else 0



        if winer == True:
            global old
            random_number=generate_random_number()
            print("9999999999999999999",random_number)
            session["random_number"]=random_number
            session["attempts"] = []
            old=users[index]["current_attempt"]
            users[index]["current_attempt"] = 1
            print("users",users)
            return redirect("/win")

        return render_template("index.html", bulls=bulls, cows=cows,
                                attempts=session["attempts"],current_attempt=users_list[ind]["current_attempt"])

@app.route("/local_N_Digit_game",methods=["GET" ,"POST"])
@login_required
def local_N_Digit_game():
    global users
    if request.method == "GET":
        return render_template("local.html")
    if request.method == "POST":
        user_gusse=request.form.get("input")
        digit_N=request.form.get("digit")
        if digit_N:
                session["digit_N"]=digit_N
                random_number1=generate_N_digit_random_number(session["digit_N"])
                print("9999999999999999999",random_number1)
                session["random_number_N"]=random_number1
                session["attempts"] = []
                gusse_check_N_digits(user_gusse,session["random_number_N"],session["user_id"])
                users[0]["current_attempt_N"]=0
                print("users",users)
        if not session.get("random_number_N"):

            random_number1=generate_N_digit_random_number(session["digit_N"])
            session["random_number_N"]=random_number1
            #users[0]["current_attempt_N"] = 1
            session["attempts"] = []


        #current_attempt=request.form.get("current_attempt")
        print("session",session)
        if int(session["digit_N"]) > 6:
            return apology("the maximum lenght is 6 ", 403)
        if len(user_gusse) != int(session["digit_N"]):
            return apology("the number length must equal to digit ", 403)
        if not user_gusse.isdigit():
            return apology("the number must be integer", 403)

        results=gusse_check_N_digits(user_gusse,session["random_number_N"],session["user_id"])
        print("results",results)
        bulls=results[0]
        cows=results[1]
        users_list=results[2]
        users=results[2]
        winer=results[3]
        print("bulls",bulls)
        print("cows",cows)
        print("users_list",users_list)
        print("winer11111",winer)
        print("users000000000000000",users)
        if "attempts" not in session:
            session["attempts"] = []

         # Store the attempt
        session["attempts"].append({"guess": user_gusse, "bulls": bulls, "cows": cows})
        #session["digit_N"]=digit_N
        users[0]["attempts"].append({"attempts":user_gusse})
        bulls = bulls if bulls else 0
        cows = cows if cows else 0

        if winer == True:
            return redirect("/win_N")

        for index, user in enumerate(users):
                if user["user_id"] == session["user_id"]:
                    ind=index
                    break

        return render_template("local.html", bulls=bulls, cows=cows, attempts=session["attempts"],
                               current_attempt=users[ind]["current_attempt_N"])


@app.route('/handle_game_selection', methods=['POST','GET'])
@login_required
def handle_game_selection():
    if request.method=='POST':
        game_id = request.form.get('game_id')
        print("game_id",game_id)
        user_number=request.form.get("user_number")
        # Check if the game exists
        game = db.execute("SELECT * FROM games WHERE game_id = ?", (game_id,))

        if game:
            # If the game exists, redirect to join the game
            print("game")
            session["player2_number"]=user_number
            return redirect(url_for('join_game', game_id=game_id))
        else:
            # If the game doesn't exist, create a new game
            print("exist")
            session["player1_number"]=user_number
            return redirect(url_for('create_game', game_id=game_id))
    else:
        return render_template('create_join_game.html')

@app.route("/create_game/<int:game_id>")
@login_required
def create_game(game_id):
   
    user_id = session["user_id"]
    user_number=session["player1_number"]
    if not user_number.isdigit():
        return apology("the number must be integer", 403)
    if len(user_number) != 4:
        return apology("the number length must equal to 4 ", 403)
    session["player1_id"] = user_id
    
    # Insert the custom game_id into the games table
    db.execute("INSERT INTO games (game_id, player1_id, random_number1,current_turn) VALUES (?,?,?,?)",
               game_id,user_id, user_number,user_id)

    return redirect(url_for('game_room', game_id=game_id))



@app.route("/join_game/<int:game_id>")
@login_required
def join_game(game_id):
    
    user_id=session["user_id"]
    session["player2_id"]=user_id
    user_number=session["player2_number"]
    if not user_number.isdigit():
        return apology("the number must be integer", 403)
    if len(user_number) != 4:
        return apology("the number length must equal to 4 ", 403)
        
    game = db.execute("SELECT * FROM games WHERE game_id = ? AND player2_id IS NULL ",(game_id))
    if not game:
        return apology("game is full or dos't exist") 
        
    else:
        db.execute("UPDATE games SET player2_id =? ,random_number2=? WHERE game_id =? ",user_id,user_number,game_id)
        #join_room(game_id)
        print(f"User {user_id} has joined room {game_id}")
        # Broadcast to the room that a new user has joined
        #emit('message', {'msg': f"{user_id} has joined the game."}, room=game_id)
        return redirect(url_for('game_room',game_id=game_id)) 
@socketio.on('join')
def handle_join(data):
    room = data['room']  # The room name sent from the client
    user_id = session['user_id']  # Get user ID from session (or adjust this to how you're storing it)

    # Have the user join the room
    join_room(room)
    
    # Optionally: Broadcast a message to all other users in the room that this user has joined
    emit('message', {'msg': f"{user_id} has joined the game."}, room=room)

# Handle a player leaving a game room
@socketio.on('leave')
def on_leave(data):
    room = data['room']
    user_id = session['user_id']
    username = db.execute("SELECT username FROM users WHERE id = ?", (user_id,))[0]["username"]

    leave_room(room)
    
    print(f"User {user_id} has left room {room}")
    
    # Broadcast to the room that the user has left
    emit('message', {'msg': f"{user_id} has left the game."}, room=room)
        
@app.route("/game_room/<int:game_id>",methods=["POST","GET"])
@login_required
def game_room(game_id):
    global current_attimpt1
    print(f"Received game_id: {game_id}")
    if request.method=="GET":
        return render_template("mltiplyer.html",game_id=game_id)
    
    player1_data= db.execute("SELECT player1_id FROM games WHERE game_id =?",(game_id))
    player2_data= db.execute("SELECT player2_id FROM games WHERE game_id = ?",(game_id))
    player1_i=player1_data[0]
    player2_i=player2_data[0]
    player1_id=player1_i["player1_id"]
    player2_id=player2_i["player2_id"]
      
    game_data=db.execute("SELECT * FROM games WHERE game_id = ?",(game_id))
    print("session['user_id']", session["user_id"])
    print("player1_id:", player1_id)
    print("player2_id:", player2_id)
    if not game_data:
        return apology("the game is not exsist")
           
    elif session["user_id"] !=player1_id and session["user_id"]!=player2_id :
        print("session['user_id']",session["user_id"])
        print(session)
        return apology("You are not part of this game")
    
    if request.method=="POST":
        user_id=session["user_id"]
        if game_data[0]["is_active"]==False:
            return apology("the game was end")
        if user_id != game_data[0]["current_turn"]:
            print("game_data[0]['current_turn']]",game_data[0]["current_turn"])
            print("user_id",user_id)
            return apology("this is not your turn")  
             
        #
        #db.execute("INSERT random_number1 VALUE? INTO games WHERE game_id = ? ",session["player1_number"],game_id)
        #db.execute("INSERT random_number2 VALUE? INTO games WHERE game_id = ? ",session["player2_number"],game_id)
        player1_data=db.execute("SELECT random_number1 FROM games WHERE game_id = ?",(game_id))
        player2_data=db.execute("SELECT random_number2 FROM games WHERE game_id = ?",(game_id))
        player1_number=player1_data[0]["random_number1"]
        player2_number=player2_data[0]["random_number2"]
        print("player1_number",player1_number)
        print("player2_number",player2_number)
        gusse=request.form.get("input")
        if not gusse.isdigit():
             return apology("the number must be integer", 403)
        if len(gusse) != 4:
            return apology("the number length must equal to 4 ", 403)
        
        print(f"gusse : {gusse}")
        if user_id == game_data[0]["player1_id"]:
           results= gusse_check(gusse,player2_number,user_id)
        elif user_id== game_data[0]["player2_id"]:
           results= gusse_check(gusse,player1_number,user_id) 
        bulls=results[0]
        cows=results[1]
        winer=results[3]
        print(cows,bulls,winer)
        db.execute("INSERT INTO game_attimpts (gusse, game_id, player_id, bulls, cows) VALUES (?, ?, ?, ?, ?)", gusse, game_id, user_id, bulls, cows)
        current=db.execute("SELECT count (gusse) FROM game_attimpts  WHERE player_id = ? AND game_id = ? ",user_id,game_id)
        current_attimpt=current[0]['count (gusse)']
        current_attimpt1=current_attimpt
        print("3333333333",current_attimpt)
                                             
        #switch turn
        #db.execute("UPDATE games SET current_turn = ? WHERE game_id = ? ",session["user_id"],game_id)  
        current_turn=db.execute("SELECT current_turn FROM games WHERE game_id = ?",(game_id,))
        print(current_turn)   
        if current_turn[0]["current_turn"]==player1_id:
            next_turn=player2_id
            print("player2_id11111111111",player2_id)
            db.execute("UPDATE games SET current_turn = ? WHERE game_id = ? ",next_turn,game_id)
        elif current_turn[0]["current_turn"]==player2_id:
            next_turn=player1_id
            print("player1_id22222222222",player1_id)
            db.execute("UPDATE games SET current_turn = ? WHERE game_id = ? ",next_turn,game_id)
        
        if winer ==True :
            db.execute("UPDATE games SET is_active = ? WHERE game_id =?",'FALSE',game_id)
            db.execute("UPDATE games SET winner = ? WHERE game_id =?",user_id,game_id)
             # Emit win message to both players
            room = f"game_{game_id}"
            socketio.emit('game_result', {
                'result': 'win',
                'winner': user_id,
                'loser': next_turn,  # Replace with actual losing user's ID
            }, room=room)
            return redirect(url_for("win_mlti"))
        
        user_n=db.execute("SELECT username FROM users WHERE id = ? ", next_turn)
        user_name=user_n[0]["username"]
        print("user_name",user_name) 
        attimpts_data1=db.execute("SELECT * FROM game_attimpts WHERE game_id = ? AND player_id =? ", game_id,player1_id)
        attimpts_data2=db.execute("SELECT * FROM game_attimpts WHERE game_id =? AND player_id =?",game_id,player2_id)
        # Notify the other player about the move and the result via socket.io
        room = f"game_{game_id}"
        socketio.emit('move', {
        'attimpts_data1': attimpts_data1,
        'attimpts_data2': attimpts_data2,
        'current_attimpt': current_attimpt,
        'name':user_name,
        'bulls': bulls,
        'cows': cows,
        'next_turn': next_turn
        }, room=room)
        
        reveal=request.form.get("reveal")
        remove=request.form.get("remove")
        
        
        if game_data[0]["player1_help"]>0 or game_data[0]['player2_help']>0:
            print('heeeeelllllllp')
            if reveal == "reveal_digit":
                print('revallllllllll')
                if session['user_id']==player1_id:
                    r_n=str(game_data[0]['random_number2'])
                    show_digit = r_n[random.randint(0, len(gusse) - 1)]
                    print("show_digit1111111111111111", show_digit)
                    flash(f"Revealed digit:{show_digit}")
                    new_help=game_data[0]['player1_help']-1
                    db.execute("UPDATE games SET player1_help = ? WHERE game_id = ? AND player1_id =?",new_help,game_id,player1_id)
                elif session['user_id']==player2_id:
                    print("game_data",game_data)
                    r_n=str(game_data[0]["random_number1"])
                    show_digit = r_n[random.randint(0, len(gusse) - 1)]
                    print("show_digit1111111111111111", show_digit)
                    flash(f"Revealed digit:{show_digit}")
                    new_help=game_data[0]['player2_help']-1
                    db.execute('UPDATE games SET player2_help = ? WHERE game_id = ? AND player2_id =?',new_help,game_id,player2_id)
                    
                    

            if remove == "remove_wrong_number":
                if session['user_id']==player1_id:
                    number_list=[0,1,2,3,4,5,6,7,8,9]
                    r_m=str(game_data[0]['random_number2'])
                    for c in r_m:
                        number_list.remove(int(c))
                    print("number_list:",number_list)
                    removed_number=number_list[random.randint(0,9)%len(number_list)]
                    flash(f"Removed number:{removed_number}")
                    new_help=game_data[0]['player1_help']
                    db.execute('UPDATE games SET player1_help = ? WHERE game_id = ? AND player1_id =?',new_help,game_id,player2_id)
                elif session['user_id']==player2_id:
                    number_list=[0,1,2,3,4,5,6,7,8,9]
                    r_m=str(game_data[0]['random_number1'])
                    for c in r_m:
                        number_list.remove(int(c))
                    print("number_list:",number_list)
                    removed_number=number_list[random.randint(0,9)%len(number_list)]
                    flash(f"Removed number:{removed_number}")
                    new_help=game_data[0]['player2_help']
                    db.execute('UPDATE games SET player2_help = ? WHERE game_id = ? AND player2_id =?',new_help,game_id,player2_id)
        else:
                return apology("You don't have enough helps. Try to guess the number to increase help and try again.")

    return render_template("mltiplyer.html", game_id=game_id,user_id=user_id,current_attimpt=current_attimpt,bulls=bulls,cows=cows,
                           attimpts_data1=attimpts_data1,attimpts_data2=attimpts_data2,name=user_name)




@socketio.on('move')
def on_move(data):
            room = data['room']
            results=gusse_check(data[gusse],random_num,user_id)
            emit('move',results,room=room)
            result={
            'player' : data['player'],
            'guess' : data[gusse],
            'bulls':results[0],
            'cows':results[1],
            'help': results[1],
            'name' : user_name   
             }
            #bulls,cows,users,winer,digits_L,plyer_gusse_L

            return render_template("mltiplyer.html")


@app.route("/win",methods=["GET" ,"POST"])
@login_required
def win():
    global users
    global old
    for index, user in enumerate(users):
                if user["user_id"] == session["user_id"]:
                    ind=index
                    break

    attempts=old
    print("attempts00000000000000",attempts)
    return render_template("win.html",X=attempts)


@app.route("/win_N",methods=["GET" ,"POST"])
@login_required
def win_N():
    global users    

    attempts=users[0]["current_attempt_N"]
    print("attempts00000000000000",attempts)
    return render_template("win_N.html",X=attempts)


@app.route("/win_mlti")
@login_required
def win_mlti():
    global current_attimpt1

    attempts=current_attimpt1
    print("attempts00000000000000",attempts)
    return render_template("win_mlti.html",X=attempts)

@app.route("/statistics",methods=["POST","GET"])
@login_required
def statistics():
    """Show history of game"""
    user_id=session["user_id"]
    if request.method=='POST':
        game_id=request.form.get('game_id')
        
        game=db.execute("SELECT * FROM games WHERE game_id = ?", game_id)
        print('games',game)
        winner=game[0]['winner']
        print('winner',winner)
        winner_n=db.execute('SELECT username FROM users WHERE id = ?',winner)
        winner_name=winner_n[0]['username']
        player1_id=game[0]['player1_id']
        player2_id=game[0]['player2_id']
        h1=db.execute("SELECT * FROM games WHERE (player1_id = ? OR player2_id = ?) AND game_id=?", user_id,user_id,game_id)
        print('player2_id',h1)
        user_name1=db.execute('SELECT username FROM users WHERE id = ? OR id = ?',player1_id,player2_id)
        print('user_name',user_name1)
        user_name=user_name1[0]['username']
        user_name2=user_name1[1]['username']
        history=db.execute('SELECT * FROM game_attimpts WHERE  game_id=? AND player_id = ? ',game_id,player1_id)
        history1=db.execute('SELECT * FROM game_attimpts WHERE  game_id=? AND player_id = ? ',game_id,player2_id)
        print('history',history)
        return render_template("statistics.html",user_name1=user_name,user_name2=user_name2,symbols=history,symbols1=history1,winner_name=winner_name)

    elif request.method=='GET':
            return render_template("statistics.html")
        

















@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        print("99999999999AAAAAAAAAAA",session["user_id"])

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

    """Log user out"""
@app.route("/logout")
def logout():
    global users
    user_id = session["user_id"]
    for user in users:
        if user["user_id"] == user_id:
            user["current_attempt"] = 0
            user["current_attempt_N"] = 0
            break
    session.clear()
    return redirect("/")




@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    user_name=request.form.get("username")
    password=request.form.get("password")
    password_confirm=request.form.get("confirmation")
    print(user_name,password,password_confirm)
    if request.method=="GET":
        return render_template("register.html")
    if request.method=="POST":
        if  user_name and password and password_confirm:
            username=db.execute("SELECT username FROM users WHERE username= ?", user_name)
            if len(username)==1:
               return apology("the username is already taken")
            if password != password_confirm:
               return apology("the password_comfirm doesn't match with password")
            password_hash=generate_password_hash(password)
            db.execute("INSERT INTO users (username,hash) VALUES (?,?) ",user_name,password_hash)
            rows = db.execute("SELECT id FROM users WHERE username = ?", user_name)
            session["user_id"] = rows[0]["id"]
            return render_template("login.html")
        else:
            return apology("you must enter username pasword and pasword confirme ")



@app.route("/password_change", methods=["GET", "POST"])
def passowrd_change():
    if request.method=="GET":
        return render_template("passowrd_change.html")
    if request.method=="POST":
        user_name=request.form.get("username")
        old_passowrd=request.form.get("old_passowrd")
        new_passowrd=request.form.get("new_passowrd")
        password_confirm=request.form.get("password_confirm")


        if  user_name and old_passowrd and password_confirm:
            username=db.execute("SELECT username FROM users WHERE username= ?", user_name)
            print("username",username)
            if not username:
               return apology("the username or passowrd is incorrect")
            if username[0]["username"]==user_name:
               #password_hash=generate_password_hash(old_passowrd)
               passowrd_database=db.execute("SELECT hash FROM users WHERE username = ?", user_name)
               print("passowrd_database",passowrd_database[0]["hash"])
               if check_password_hash(passowrd_database[0]["hash"],old_passowrd):
                    if new_passowrd != password_confirm:
                        return apology("the password_comfirm doesn't match with password")
                    new_hash=generate_password_hash(new_passowrd)
                    db.execute("UPDATE users SET hash = ? WHERE username = ?",new_hash,username[0]["username"])
               else:
                   return apology("the password or user name is incorrect")

            rows = db.execute("SELECT id FROM users WHERE username = ?", user_name)
            session["user_id"] = rows[0]["id"]
            return redirect("/")
        
if __name__ == '__main__':
    socketio.run(app, debug=True)
