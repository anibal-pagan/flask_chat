import os
from buffer import Buffer, Message, ManageBuffer

from flask import Flask, session, render_template, request, redirect, url_for, jsonify
from flask_session import Session
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#Global variables (deleted once server shuts down, maybe do something else?)
all_chats = dict()
chat_names = []

@app.route("/")
def index():
    if 'username' in session:
        if 'chat' in session: 
            if session['chat'] in all_chats:
                return redirect(url_for('chat', chat_name=session['chat']))
            del session['chat']
        return redirect(url_for('chats'))
    return render_template("index.html")

@app.route("/login")
def login():
    if 'username' not in request.args:
        if 'username' in session:
            if 'chat' in session:
                del session['chat']
            return render_template("login.html", username=session['username'])
        else:
            return render_template("login.html")
    
    username = request.args['username']
    if username is None or username == "":
        error = "Please type a username."
        if 'username' in session:
            return render_template("login.html", error=error, username=session['username'])
        else:
            return render_template("login.html", error=error)
    else:
        session['username'] = username
        return redirect(url_for('chats'))

@app.route("/chats")
def chats():
    if 'page' in request.args:
        page = int(request.args['page'])
    else:
        page = 1
    
    if 'username' not in session:
        return redirect(url_for('login'))
    else:
        #Remove chat from session
        if 'chat' in session:
            del session['chat']
            
        if 'search' not in request.args and 'chat_name' not in request.args:
            return render_template("chats.html", username=session['username'], curr_page=page, chats=chat_names)

        if 'search' in request.args:
            if request.args['search'] is "" or request.args['search'] is None:
                return redirect(url_for('chats'))
            else:
                if request.args['search'] in all_chats:
                    return render_template("chats.html", username=session['username'], curr_page=page, chat_name=request.args['search'])
                else:
                    return render_template("chats.html", username=session['username'], curr_page=page, chat_name=None)
        
        if 'chat_name' in request.args:
            if request.args['chat_name'] is None:
                return redirect(url_for('chats'))
            else:
                if request.args['chat_name'] in all_chats:
                    return render_template("chats.html", username=session['username'], curr_page=page, chats=chat_names, error="Chat already exists!")
                else:
                    if request.args['chat_name'] is None or request.args['chat_name'] is "":
                        return render_template("chats.html", username=session['username'], curr_page=page, chats=chat_names, error="Please enter a name.")
                    name = request.args['chat_name']
                    all_chats[name] = []
                    session['chat'] = name
                    chat_names.append(name)
                    return redirect(url_for('chat', chat_name=name))

@app.route("/<string:chat_name>")
def chat(chat_name): 
    if 'username' not in session:
        return redirect(url_for('login'))
    if chat_name not in all_chats:
        return redirect(url_for('chats'))

    session['chat'] = chat_name
    #ToDo: Pass messages to session
    return render_template("chat.html", username=session['username'], chat_name=chat_name, messages=all_chats[chat_name])

@app.route("/messages", methods=["POST"])
def messages():

    chat_name = request.form.get("name")
    user = request.form.get("user")

    # Return list of messages.
    result = {
        chat_name: all_chats[chat_name],
        'current_user': user
    }
    return jsonify(result)

@socketio.on("send message")
def send(message):
    mes = message["message"]
    print(message["username"])
    message_content = Message(message["username"], mes).to_dict()
    ManageBuffer.add(all_chats[session['chat']], message_content)
    result = {
        'chats': all_chats,
        'current_user': message["username"]
    }
    emit("messages", result, broadcast=True)

@socketio.on("delete message")
def delete(index):
    all_chats[session['chat']].pop(int(index))
    emit("deleted", index, broadcast=True)
