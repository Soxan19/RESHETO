from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from .models import Note
from website import db
import json
views = Blueprint('views',__name__)

@views.route('/',methods=["GET","POST"])
@login_required 
def home():
    if request.method == "POST":
        note = request.form.get('note')

        if len(note)<1:
            flash('Note is too short', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note has been added',category="success")

    return render_template("home.html", user=current_user)

@views.route('/delete-note',methods=['POST'])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:                        #отсутсвует проверка if note.user_id == current_user.id: (так что кто угодно может удалять заметки)
        db.session.delete(note)
        db.session.commit()
    return jsonify({})

@views.route('home/note/<int:note_id>') #мало того что нет @login_required так еще и if note.user_id == current_user.id: нет!!!
def view_note(note_id):                 #(кто угодно может получить доступ к ЛЮБОЙ заметке) ПРИМЕР: переходим по http://127.0.0.1:5000/home/note/1
    note = db.session.get(Note, note_id)#и получаем что находится в этой заметке 
    if note is None:
        return jsonify({'error': 'not found'}), 404
    return jsonify({'id': note.id, 'data': note.data, 'owner': note.user_id})
