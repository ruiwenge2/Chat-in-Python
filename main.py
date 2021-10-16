import os
from flask import Flask, render_template, request, redirect, session
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask("app")
app.config["SECRET_KEY"] = os.getenv("secret")

socketio = SocketIO(app)

@app.route("/")
def index():
  return render_template("index.html", loggedin=("username" in session), session=session)

@app.route("/setusername", methods=["POST"])
def setusername():
  if "username" in request.form:
    session["username"] = request.form["username"]
  return redirect("/")

@socketio.on("joined")
def joined():
  join_room("main")

@socketio.on("message")
def chat_message(user, room, message):
  emit("message", {"user":user, "message":message}, room=room)

@socketio.on("changeroom")
def changeroom(room):
  join_room(room)
  if room == "main":
    words = "You are in the main room"
  else:
    words = "You are in the room " + room
  emit("room", words)

socketio.run(app, host="0.0.0.0", port=8080)