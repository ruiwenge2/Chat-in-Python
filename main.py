import os
from flask import Flask, render_template, request, redirect, session
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask("app", static_url_path="")
app.config["SECRET_KEY"] = os.getenv("secret")

socketio = SocketIO(app)
rooms = {"main":[]}
users = {}

@app.route("/")
def index():
  return render_template("index.html", loggedin=("username" in session), session=session)

@app.route("/setusername", methods=["POST"])
def setusername():
  if "username" in request.form:
    session["username"] = request.form["username"]
  return redirect("/")

@socketio.on("joined")
def joined(username):
  users[request.sid] = [username, "main"]
  rooms["main"].append(username)
  join_room("main")
  print(username + " joined")
  emit("users_update", rooms["main"], room="main")

@socketio.on("message")
def chat_message(user, room, message):
  emit("message", {"user":user, "message":message}, room=room)
  print("sent message")

@socketio.on("changeroom")
def changeroom(room):
  info = users[request.sid]
  firstroom = info[1]
  name = info[0]
  rooms[firstroom].remove(name)
  leave_room(firstroom)
  emit("users_update", rooms[firstroom], room=firstroom)
  join_room(room)
  if room == "main":
    words = "You are in the main room"
  else:
    words = "You are in the room " + room
  if room not in rooms:
    rooms[room] = []
  rooms[room].append(name)
  users[request.sid][1] = room
  emit("room", words)
  print(f"{name} changed room from {firstroom} to {room}")
  emit("users_update", rooms[room], room=room)

@socketio.on("connect")
def connect():
  pass

@socketio.on("disconnect")
def disconnect():
  sid = request.sid
  name = users[sid][0]
  room = users[sid][1]
  del users[sid]
  rooms[room].remove(name)
  print(name + " left")
  emit("users_update", rooms[room], room=room)

socketio.run(app, host="0.0.0.0", port=8080)