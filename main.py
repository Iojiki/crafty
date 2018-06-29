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


 #Database
class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    materials = db.relationship('Materials', backref = 'owner')
    recipes = db.relationship('Recipes', backref = 'owner')

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


class Recipes(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.String(120))
    craftable = db.Column(db.Boolean(True))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self,name,description,craftable,owner):
        self.name = name
        self.description = description
        self.craftable = craftable
        self.owner = owner

class Ingredients(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    mat_id = db.Column(db.Integer)
    mat_name = db.Column(db.String(120))
    rec_qty = db.Column(db.Integer)
    rec_id = db.Column(db.Integer, db.ForeignKey('recipes.id'))
    

    def __init__(self,mat_id,mat_name,rec_qty,rec_id):
        self.mat_id = mat_id
        self.mat_name = mat_name
        self.rec_qty = rec_qty
        self.rec_id = rec_id


#PAGES -----------------------------------------
@app.route('/', methods = ['POST','GET'])
def index():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        checkIfCraft()
        user_name = User.query.filter_by(username = session['username']).first()
        user_id = user_name.id
        materials = Materials.query.filter_by(owner_id = user_id).all()
        recipes = Recipes.query.filter_by(owner_id = user_id).all()
        ingredients = Ingredients.query.all()         

    return render_template("home.html", title = "Main Page", materials = materials, recipes = recipes, ingredients = ingredients)


@app.route('/Pages/Recipe', methods = ['POST', 'GET'])
def recipepage():
    if request.method == 'POST':
        total_mat_needed = request.form["total_mat_needed"]
        user_name = User.query.filter_by(username = session['username']).first()
        user_id = user_name.id
        materials = Materials.query.filter_by(owner_id = user_id).all()
        recipes = Recipes.query.filter_by(owner_id = user_id).all()
        return render_template("recipe.html", title = "Create Recipe", materials = materials, recipes = recipes, total_mat_needed = total_mat_needed)

    else:
        return render_template("recipe_value.html", title = "Select Number of Components")
        
@app.route('/Pages/Inventory', methods = ['POST', 'GET'])
def inventorypage():
    if not session.get('logged_in'):
        return redirect('/')
    else:
        user_name = User.query.filter_by(username = session['username']).first()
        user_id = user_name.id
        materials = Materials.query.filter_by(owner_id = user_id).all()
        return render_template("inventory.html", title = "User Inventory", materials = materials)

@app.route('/Pages/Craft', methods = ['POST', 'GET'])
def craftpage():
    if not session.get('logged_in'):
        return redirect('/')
    else:
        checkIfCraft()
        user_name = User.query.filter_by(username = session['username']).first()
        user_id = user_name.id
        recipes = Recipes.query.filter_by(owner_id = user_id).all()
        ingredients = Ingredients.query.all()   
        return render_template("craft.html", title = "Craft", recipes = recipes, ingredients = ingredients)
        
   #CREATE  ----------------------
@app.route('/addmaterial', methods = ['POST'])
def add():
    mat_name = request.form["name"]
    mat_desc = request.form["description"]
    mat_total = request.form["total"]
    owner = User.query.filter_by(username=session['username']).first()
    new_material = Materials(mat_name,mat_desc,mat_total,owner)
    db.session.add(new_material)
    db.session.commit()

    return redirect('/Pages/Inventory')

@app.route('/addrecipe', methods = ['POST'])
def add_recipe():
    rec_name = request.form["name"]
    rec_desc = request.form["description"]
    craftable = False

    owner = User.query.filter_by(username=session['username']).first()
    new_recipe = Recipes(rec_name,rec_desc,craftable,owner)
    db.session.add(new_recipe)
    db.session.commit()
    

    recipe = Recipes.query.filter_by(name= rec_name).first()
    recipe_id = recipe.id

    iteration_Value = request.form["total_mat_needed"]
    rec_mat_init = ''
    rec_mat_val_init = ''
    
    for i in range(1, int(iteration_Value) + 1):

        rec_mat_init = request.form["material" + str(i)]
        rec_mat_val_init = request.form["total" + str(i)]
  
        rec_mat_name_q = Materials.query.filter_by(id = int(rec_mat_init)).first()
        rec_mat_name = rec_mat_name_q.name

        rec_mat = Ingredients(rec_mat_init,rec_mat_name,rec_mat_val_init,recipe_id)
        db.session.add(rec_mat)
        db.session.commit()
            
    return redirect('/Pages/Craft')


#DELETE --------------------------------
@app.route('/delete',methods = ['POST'])
def delete():
    id = request.form["columnid"]
    delete_id = Materials.query.filter_by(id = id).first()
    db.session.delete(delete_id)
    db.session.commit()

    return redirect('/')

@app.route('/deleterecipe',methods = ['POST'])
def deleterecipe():
    id = request.form["columnid"]
    delete_id = Recipes.query.filter_by(id = id).first()
    deleteComponentId = Ingredients.query.filter_by(rec_id = id).all()
    db.session.delete(delete_id)
    for component in deleteComponentId:
        db.session.delete(component)
    db.session.commit()

    return redirect('/Pages/Craft')

#UPDATE ---------------------------
@app.route('/update_value_minus',methods = ['POST'])
def update_value_minus():
    id = request.form["columnid"]
    modify_value = Materials.query.filter_by(id = id).first()
    if modify_value.total > 0:
        modify_value.total = modify_value.total - 1
        db.session.commit()

    return redirect('/Pages/Inventory')
@app.route('/update_value_plus',methods = ['POST'])
def update_value_plus():
    id = request.form["columnid"]
    modify_value = Materials.query.filter_by(id = id).first()
    if modify_value.total < 999:
        modify_value.total = modify_value.total + 1
        db.session.commit()

    return redirect('/Pages/Inventory')

@app.route('/craft',methods = ['POST'])
def craft():
    id = request.form["craft"]
    ingredientsInRecipe = Ingredients.query.filter_by(rec_id = id).all()
    for component in ingredientsInRecipe:
        comp_id = component.mat_id
        matAssoc = Materials.query.filter_by(id = comp_id).first()
        matAssoc.total = matAssoc.total - component.rec_qty
        db.session.commit()
        
    
    return redirect('/Pages/Craft')

#LOGIN --------------------

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

#Non Route Functions -------------------------------

def checkIfCraft():
    user_name = User.query.filter_by(username = session['username']).first()
    user_id = user_name.id
    materials = Materials.query.filter_by(owner_id = user_id).all()
    recipes = Recipes.query.filter_by(owner_id = user_id).all()
    ingredients = Ingredients.query.all()
        
    #Checking if recipe is craftable
    for recipe in recipes:
        craftValue = True
        for component in ingredients:
            if component.rec_id == recipe.id:
                filterValue = Materials.query.filter_by(id = component.mat_id).first()
                if filterValue.total >= component.rec_qty and craftValue != False:
                    craftValue = True 
                    recipe.craftable = craftValue  
                else:
                    craftValue = False
                    recipe.craftable = craftValue          
    db.session.commit()  






if __name__ == '__main__':
    app.run()