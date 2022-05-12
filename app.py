from flask import Flask, render_template, request, session, redirect
import sqlite3
from sqlite3 import Error

DB_NAME = "C:/Users/18268/Onedrive - Wellington College/smilescaf/smile.db"
#DB_NAME = "C:/Users/wmobi/Onedrive - Wellington College/smilescaf/smile.db"
#DB_NAME = "smile.db"
app = Flask(__name__)
app.secret_key = "89279812712hqwdhak"


def create_connection(db_file):
    try:
        connection = sqlite3.connect(db_file)
        return connection
    except Error as e:
        print(e)

    return None

def sidenav1():
    con = create_connection(DB_NAME)
    query = """SELECT cata_id, catali FROM catalist ORDER BY catali"""
    cur = con.cursor()
    cur.execute(query)
    cata_list = cur.fetchall()
    con.commit()
    con.close()
    return cata_list

@app.route('/')
def render_homepage():
    cata_list = sidenav1()


    return render_template('home.html', catagories=cata_list, logged_in=is_logged_in())

@app.route('/menu')
def render_menu_page():

    con = create_connection(DB_NAME)
    query = "SELECT name, english, category, definition, level, image FROM product"
    cur = con.cursor()
    cur.execute(query)
    product_list = cur.fetchall()
    con.close()

    cata_list = sidenav1()



    return render_template('menu.html', products=product_list, catagories=cata_list)


@app.route('/contact')
def render_contact_page():

    cata_list = sidenav1()
    return render_template('contact.html',  catagories=cata_list, logged_in=is_logged_in())




@app.route('/login', methods=["GET", "POST"])
def render_login_page():
    cata_list = sidenav1()
    if request.method == "POST":
        email = request.form['email'].strip().lower()
        password = request.form['password'].strip()

        query = """SELECT id, fname, password FROM customer WHERE email = ?"""
        con = create_connection(DB_NAME)
        cur = con.cursor()
        cur.execute(query, (email,))
        user_data = cur.fetchall()
        con.close()

        try:
            userid = user_data[0][0]
            firstname = user_data[0][1]
            db_password = user_data[0][2]
        except IndexError:
            return redirect("/login?error=Email+andor+password+incorrect")

        if db_password != password:
            return redirect("/login?error=Email+andor+password+incorrect")

        session['email'] = email
        session['userid'] = userid
        session['firstname'] = firstname
        print(session)
        return redirect("/")

    return render_template('login.html', logged_in=is_logged_in(), catagories=cata_list)




@app.route('/signup', methods=['GET', 'POST'])
def render_signup_page():
    cata_list = sidenav1()
    if request.method == 'POST':
        print(request.form)
        fname = request.form.get('fname').strip().title()
        lname = request.form.get('lname').strip().title()
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')
        password2 = request.form.get('password2')

        if password != password2:
            return redirect('/signup?error=Passwords+dont+match')

        if len(password)<8:
            return redirect('/signup?error=Password+must+be+8+characters+or+more')


        con = create_connection(DB_NAME)
        query = "INSERT INTO customer(id, fname, lname, email, password) VALUES(NULL,?,?,?,?)"

        cur = con.cursor()
        try:
            cur.execute(query, (fname, lname, email, password))
        except sqlite3.IntegrityError:
            return redirect('/signup?error=Email+already+in+use')

        con.commit()
        con.close()
        return redirect("/login")

    return render_template('signup.html', catagories=cata_list, logged_in=is_logged_in())

@app.route("/logout")
def logout():
    print(list(session.keys()))
    [session.pop(key) for key in list(session.keys())]
    print(list(session.keys()))
    return redirect('/?message=See+you+next+time!')


def is_logged_in():
    if session.get("email") is None:
        print("not logged in")
        return False
    else:
        print("logged in")
        return True

@app.route("/catagories/<cata_id>", methods=["GET", "POST"])
def render_catagories(cata_id):
    cata_list = sidenav1()

    con = create_connection(DB_NAME)
    query = """SELECT name_id, name, english, cata_id, category, definition, level, image FROM product WHERE cata_id=? ORDER BY name, english"""
    cur = con.cursor()
    cur.execute(query, (cata_id,))
    maori_list = cur.fetchall()

    con = create_connection(DB_NAME)
    query = """SELECT cata_id, catali FROM catalist WHERE cata_id=?"""
    cur = con.cursor()
    cur.execute(query, (cata_id,))
    cata_names_list = cur.fetchall()
    con.close()

    return render_template("catagories.html", cata_names_list=cata_names_list, catagories=cata_list, maori=maori_list, logged_in=is_logged_in())

@app.route("/name/<name_id>")
def render_maoriword(name_id):
    cata_list = sidenav1()

    con = create_connection(DB_NAME)
    query = """SELECT name_id, name, english, cata_id, category, definition, level, image FROM product WHERE name_id=? ORDER BY name"""
    cur = con.cursor()
    cur.execute(query, (name_id,))
    maori_list = cur.fetchall()
    
    query = """SELECT cata_id, catali FROM catalist WHERE cata_id=?"""
    cur = con.cursor()
    cur.execute(query, (maori_list[0][3],))
    cata_names_list = cur.fetchall()
    
    return render_template("name.html", cata_names_list=cata_names_list, catagories=cata_list, maori=maori_list, logged_in=is_logged_in())


app.run(host='0.0.0.0', debug=True)
