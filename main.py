from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import cgi

#upfront flask stuff to make it work
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://crafty:gDFS36@67cb67#7@localhost:3306/crafty'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

#secret key for databasing
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

#TODO: Create, Read, Delete is working. Still need to Update Materials value, name, quantity. Maybe add in an edit button for the whole
#thing / individual update for number of materials
#create classes for storing data. We need Users/Materials/Schematics...maybe games too

#TODO: Need to get username working in order to be able to test further integration. Materials relationship is set up, just need a page for username, sign in etc... -- This is done
#TODO: Link Materials List to Username and display only materials for the user the is logged in -- DONE

#TODO: Make a list of Schematics that materials can build in to

#TODO: Database for Schematics, Games, Drop down list...


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    materials = db.relationship('Materials', backref = 'owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

class Materials(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.String(120))
    total = db.Column(db.Integer)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self,name,description,total,owner):
        self.name = name
        self.description = description
        self.total = total
        self.owner = owner


#MAIN PAGE/READ
@app.route('/', methods = ['POST','GET'])
def index():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        user_name = User.query.filter_by(username = session['username']).first()
        user_id = user_name.id
        materials = Materials.query.filter_by(owner_id = user_id).all()
        return render_template("home.html", title = "Main Page", materials = materials)
    
    
        
   #CREATE   things to do: make validation to ensure that a duplicate entry does not exist 
@app.route('/addmaterial', methods = ['POST'])
def add():
    mat_name = request.form["name"]
    mat_desc = request.form["description"]
    mat_total = request.form["total"]
    owner = User.query.filter_by(username=session['username']).first()
    new_material = Materials(mat_name,mat_desc,mat_total,owner)
    db.session.add(new_material)
    db.session.commit()

    return redirect('/')

#DELETE
@app.route('/delete',methods = ['POST'])
def delete():
    id = request.form["columnid"]
    delete_id = Materials.query.filter_by(id = id).first()
    db.session.delete(delete_id)
    db.session.commit()

    return redirect('/')

#UPDATE
@app.route('/update_value_minus',methods = ['POST'])
def update_value_minus():
    id = request.form["columnid"]
    modify_value = Materials.query.filter_by(id = id).first()
    if modify_value.total > 0:
        modify_value.total = modify_value.total - 1
        db.session.commit()

    return redirect('/')
@app.route('/update_value_plus',methods = ['POST'])
def update_value_plus():
    id = request.form["columnid"]
    modify_value = Materials.query.filter_by(id = id).first()
    if modify_value.total < 999:
        modify_value.total = modify_value.total + 1
        db.session.commit()

    return redirect('/')

@app.route("/login", methods=['GET', 'POST'])
def login():
    error_username = ''
    error_password = ''

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:
            session['username'] = username
            session['logged_in'] = True
            return redirect('/')
        if not user:
            error_username = 'User name does not exist'
            return render_template('login.html', error_username=error_username)
        else: 
            error_password = 'Password incorrect'
            return render_template('login.html', error_password=error_password)
    return render_template('login.html')

@app.route('/logout', methods=['GET','POST'])
def logout():
    del session['username']
    session['logged_in'] = False
    return redirect('/')

@app.route("/signup", methods=['GET', 'POST'])
def signup():

    error_username = ''
    error_password = ''
    error_verify_password = ''
    

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify_password = request.form['verify_password']

        if username == '':
            error_username = 'Please enter a User name'
            return render_template('signup.html', error_username = error_username)

        if password == '':
            error_password = 'Please enter a Password'
            return render_template('signup.html', error_password = error_password)

        if verify_password == '':
            error_verify_password = 'Please retype the password'
            return render_template('signup.html', error_verify_password = error_verify_password)

        if len(username) <= 3:
            error_username = 'User name must be longer than 3 characters'
            return render_template('signup.html',error_username=error_username) 

        if len(password) <= 3:
            error_password = 'Password must be longer than 3 characters'
            return render_template('signup.html', error_password=error_password)       
        
        if password != verify_password:
            error_verify_password = 'Please match password'
            return render_template('signup.html', error_verify_password=error_verify_password)
        
        username_in_db = User.query.filter_by(username=username).count()
        if username_in_db > 0:
            error_username = 'User name is already taken'
            return render_template('signup.html', error_username=error_username)


        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        session['user'] = user.username
        return redirect("/")
    else:
        return render_template('signup.html')






if __name__ == '__main__':
    app.run()