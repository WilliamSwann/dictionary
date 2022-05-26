from flask import Flask, render_template, request, session, redirect
import sqlite3
from sqlite3 import Error
from flask_bcrypt import Bcrypt
import datetime

DB_NAME = "C:/Users/18268/Onedrive - Wellington College/smilescaf/smile.db"
# DB_NAME = "C:/Users/wmobi/Onedrive - Wellington College/smilescaf/smile.db"
# DB_NAME = "smile.db"
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = "89279812712hqwdhak"


def create_connection(db_file):
    try:
        connection = sqlite3.connect(db_file)
        return connection
    except Error as e:
        print(e)

    return None


def sidenav1(): #this function grabs all of the items from the product table and puts them into a list for the side nav
    con = create_connection(DB_NAME)
    query = """SELECT cata_id, catali FROM catalist ORDER BY catali"""
    cur = con.cursor()
    cur.execute(query)
    cata_list = cur.fetchall()
    con.commit()
    con.close()
    return cata_list




@app.route('/', methods=['GET', 'POST'])  #this function
def render_homepage():
    cata_list = sidenav1() #showing categorys

    return render_template('home.html', catagories=cata_list, logged_in=is_logged_in(), teacher=is_teacher())
    #rendering home.html and returning all of the variables needed in the html

@app.route('/contact')
def render_contact_page():
    cata_list = sidenav1() #showing categorys
    return render_template('contact.html', catagories=cata_list, logged_in=is_logged_in(), teacher=is_teacher())
    # rendering contact.html and returning all of the variables needed in the html

@app.route('/login', methods=["GET", "POST"])
def render_login_page():
    if is_logged_in(): #when logged in it will redirect you to home if you input login page
        redirect('/')
    cata_list = sidenav1() #showing categorys
    if request.method == "POST":    #if the website recives a post request it will run the login code.
        email = request.form['email'].strip().lower() #getting email and password and putting in correct form
        password = request.form['password'].strip()

        query = """SELECT id, fname, password, teacher FROM customer WHERE email = ?""" #sql query to grab data from customer databse
        con = create_connection(DB_NAME)
        cur = con.cursor()
        cur.execute(query, (email,))
        user_data = cur.fetchall() #putting data into list
        con.close()

        try:  #checking if data matches any in database
            userid = user_data[0][0]
            firstname = user_data[0][1]
            db_password = user_data[0][2]
            teacher = user_data[0][3]
        except IndexError:
            return redirect("/login?error=Email+andor+password+incorrect") #if it doesnt it redirects to login page and puts text in bar

        if not bcrypt.check_password_hash(db_password, password):
            return redirect(request.referrer + "?error=Email+andor+password+incorrect") #if passwords do not match redirects to login page and puts text in bar

        session['email'] = email  #sessioning useful information to use for logged in and teacher
        session['userid'] = userid
        session['firstname'] = firstname
        session['teacher'] = teacher
        print(session)
        return redirect("/")

    return render_template('login.html', logged_in=is_logged_in(), catagories=cata_list, teacher=is_teacher())
    # rendering login.html and returning all of the variables needed in the html

@app.route('/signup', methods=['GET', 'POST'])
def render_signup_page():
    if is_logged_in():  # when logged in it will redirect you to home if you input login page
        redirect('/')
    cata_list = sidenav1()  # showing categorys
    if request.method == 'POST':  # if the website recives a post request it will run the signup code.
        print(request.form)
        fname = request.form.get('fname').strip().title()  # getting signup information and putting in correct form
        lname = request.form.get('lname').strip().title()
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')
        password2 = request.form.get('password2')
        teacher = request.form.get('teacher')

        if password != password2:  # validating data and ading parameters, and if data does not comply it wll refresh page with error
            return redirect('/signup?error=Passwords+dont+match')

        if len(password) < 8:
            return redirect('/signup?error=Password+must+be+8+characters+or+more')

        hashed_password = bcrypt.generate_password_hash(password)
        con = create_connection(DB_NAME)
        query = "INSERT INTO customer(id, fname, lname, email, password, teacher) VALUES(NULL,?,?,?,?,?)"  # sql query to add data into the customer database

        cur = con.cursor()
        try:
            cur.execute(query, (fname, lname, email, hashed_password, teacher)) #adding the data to customer database
        except sqlite3.IntegrityError:
            return redirect('/signup?error=Email+already+in+use')  # posting error if email is already used

        con.commit()
        con.close()
        return redirect("/login")  # redirect to login page

    return render_template('signup.html', catagories=cata_list, logged_in=is_logged_in(), teacher=is_teacher())
    # rendering login.html and returning all of the variables needed in the html

@app.route("/logout")
def logout():  # popping session key to log the user out of the website
    print(list(session.keys()))
    [session.pop(key) for key in list(session.keys())]
    print(list(session.keys()))
    return redirect('/?message=See+you+next+time!')


def is_logged_in():  # checking session for email to determine if a user is logged in
    if session.get("email") is None:
        print("not logged in")
        return False
    else:
        print("logged in")
        return True


def is_teacher():  # checking session for email to determine if the user is a teacher
    if session.get("teacher") == "on":
        print("is Teacher")
        return True
    else:
        print("not Teacher")
        return False


@app.route("/catagories/<cata_id>", methods=["GET", "POST"])  # displays the words in the category selected by the user
def render_catagories(cata_id):
    cata_list = sidenav1()  # showing categories

    con = create_connection(DB_NAME)
    query = """SELECT name_id, name, english, cata_id, category, definition, level, image FROM product WHERE cata_id=? ORDER BY name, english"""  # looking for the words and word information in the category selected by the user

    cur = con.cursor()
    cur.execute(query, (cata_id,))
    maori_list = cur.fetchall()  # putting the words into a list

    con = create_connection(DB_NAME)
    query = """SELECT cata_id, catali FROM catalist WHERE cata_id=?"""  # finding the category name and info
    cur = con.cursor()
    cur.execute(query, (cata_id,))
    cata_names_list = cur.fetchall()  # putting names into list
    con.close()

    return render_template("catagories.html", cata_names_list=cata_names_list, catagories=cata_list, maori=maori_list,
                           logged_in=is_logged_in(), teacher=is_teacher())
    # rendering home.html and returning all of the variables needed in the html

@app.route("/name/<name_id>", methods=["GET", "POST"]) # displays the word selected by the user
def render_maoriword(name_id):
    cata_list = sidenav1() # showing categories

    con = create_connection(DB_NAME)
    query = """SELECT name_id, name, english, cata_id, category, definition, level, image, date_time,edited_by FROM product WHERE name_id=? ORDER BY name""" # looking for the word information selected by the user
    cur = con.cursor()
    cur.execute(query, (name_id,))
    maori_list = cur.fetchall()

    query = """SELECT cata_id, catali FROM catalist WHERE cata_id=?""" # finding the category name and info
    cur = con.cursor()
    cur.execute(query, (maori_list[0][3],))
    cata_names_list = cur.fetchall() # putting names into list

    if is_logged_in() and is_teacher(): # if the user is a teacher(admin) they are allowed to update the information of the word.

        if request.method == "POST" and is_logged_in() and is_teacher():
            name = request.form.get('name').strip().title()
            english = request.form.get('english').strip().title()
            definition = request.form.get('definition').strip()
            level = request.form.get('level')
            cata_id = request.form.get('cata_id')
            edited_by = session.get('firstname')
            date_time = datetime.datetime.now()
            print(date_time)

            if len(name) > 30:
                return redirect('/addword?error=maori+word+must+be+less+than+30+characters')
            if len(english) > 30:
                return redirect('/addword?error=english+word+must+be+less+than+30+characters')
            if len(definition) > 300:
                return redirect('/addword?error=definition+must+be+less+than+300+characters')
            print("sussa")
            con = create_connection(DB_NAME)
            query = "UPDATE product SET name = ?, english = ? , definition = ?, level = ?, cata_id = ?, edited_by = ?, date_time = ? WHERE name_id = ?"

            cur = con.cursor()
            try:
                print("123dsfsd")
                cur.execute(query, (name, english, definition, level, cata_id, edited_by, date_time, name_id))
            except sqlite3.IntegrityError:
                return redirect('/?error=DIDNTWORK')

            con.commit()
            con.close()
            return redirect("/")

    return render_template("name.html", cata_names_list=cata_names_list, catagories=cata_list, maori=maori_list,
                           logged_in=is_logged_in(), teacher=is_teacher())
    # rendering name.html and returning all of the variables needed in the html

@app.route("/addcategory", methods=["GET", "POST"])
def render_addcategory():
    if is_logged_in() and is_teacher():
        cata_list = sidenav1()
        if request.method == "POST" and is_logged_in() and is_teacher():
            catali = request.form.get('catali').strip().title()

            con = create_connection(DB_NAME)
            query = "INSERT INTO catalist(cata_id, catali) VALUES(NULL,?)"
            cur = con.cursor()
            try:
                cur.execute(query, (catali,))
            except sqlite3.IntegrityError:
                return redirect('/?error=DIDNTWORK')

            con.commit()
            con.close()
            return redirect("/")
    else:
        return redirect("/")

    return render_template("addcategory.html", catagories=cata_list, logged_in=is_logged_in(), teacher=is_teacher())
    # rendering addcategory.html and returning all of the variables needed in the html

@app.route("/addword", methods=["GET", "POST"])
def render_addword():
    if is_logged_in() and is_teacher():
        cata_list = sidenav1()
        if request.method == "POST" and is_logged_in() and is_teacher():
            name = request.form.get('name').strip().title()
            english = request.form.get('english').strip().title()
            definition = request.form.get('definition').strip()
            level = request.form.get('level')
            cata_id = request.form.get('cata_id')
            image = "noimage.png"
            edited_by = session.get('firstname')
            date_time = datetime.datetime.now()
            print(date_time)

            if len(name) > 30:
                return redirect('/addword?error=maori+word+must+be+less+than+30+characters')
            if len(english) > 30:
                return redirect('/addword?error=english+word+must+be+less+than+30+characters')
            if len(definition) > 300:
                return redirect('/addword?error=definition+must+be+less+than+300+characters')

            con = create_connection(DB_NAME)
            query = "INSERT INTO product(name_id, name, english, definition, level, cata_id, image, edited_by, date_time) VALUES(NULL,?,?,?,?,?,?,?,?)"
            cur = con.cursor()
            try:

                cur.execute(query, (name, english, definition, level, cata_id, image, edited_by, date_time))
            except sqlite3.IntegrityError:
                return redirect('/?error=DIDNTWORK')

            con.commit()
            con.close()
            return redirect("/")
    else:
        return redirect("/")

    return render_template("addword.html", catagories=cata_list, logged_in=is_logged_in(), teacher=is_teacher())
    # rendering addword.html and returning all of the variables needed in the html

@app.route("/deletecategory/<cata_id>", methods=["GET", "POST"])
def render_deletecategory(cata_id):
    cata_list = sidenav1()
    con = create_connection(DB_NAME)
    query = """SELECT cata_id, catali FROM catalist WHERE cata_id=?"""
    cur = con.cursor()
    cur.execute(query, (cata_id,))
    cata_names_list = cur.fetchall()

    if is_logged_in() and is_teacher():

        if request.method == "POST" and is_logged_in() and is_teacher():
            if request.form['submit'] == 'DELETE CATAGORY (!!CANNOT BE UNDONE!!)':
                con = create_connection(DB_NAME)
                query = "DELETE FROM catalist WHERE cata_id=?"
                cur = con.cursor()
                try:
                    cur.execute(query, (cata_id,))
                except sqlite3.IntegrityError:
                    return redirect('/?error=DIDNTWORK')

                query = "DELETE FROM product WHERE cata_id=?"
                cur = con.cursor()
                try:
                    cur.execute(query, (cata_id,))
                except sqlite3.IntegrityError:
                    return redirect('/?error=DIDNTWORK')

                con.commit()
                con.close()
                print("bab")
                return redirect("/")
    else:
        return redirect("/")

    return render_template("deletecategory.html", catagories=cata_list, logged_in=is_logged_in(), teacher=is_teacher(),
                           cata_names_list=cata_names_list)
    # rendering deletecategory.html and returning all of the variables needed in the html

@app.route("/deleteword/<name_id>", methods=["GET", "POST"])
def render_deleteword(name_id):
    if is_logged_in() and is_teacher():
        cata_list = sidenav1()
        print("sik")
        con = create_connection(DB_NAME)
        query = "SELECT name_id, name, english, category, definition, level, image FROM product WHERE name_id=?"
        cur = con.cursor()
        cur.execute(query,(name_id,))
        maori_list = cur.fetchall()

        if request.method == "POST" and is_logged_in() and is_teacher():
            if request.form['submit'] == 'DELETE NAME (!!CANNOT BE UNDONE!!)':

                query = "DELETE FROM product WHERE name_id=?"
                cur = con.cursor()
                try:
                    cur.execute(query, (name_id,))
                except sqlite3.IntegrityError:
                    return redirect('/?error=DIDNTWORK69')

                con.commit()
                con.close()
                return redirect("/")
    else:
        return redirect('/')

    return render_template("deleteword.html", maori=maori_list, catagories=cata_list, logged_in=is_logged_in(), teacher=is_teacher())
    # rendering delete.html and returning all of the variables needed in the html

app.run(host='0.0.0.0', debug=True)
