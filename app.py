from flask import Flask, render_template, request, redirect, url_for,session
from flask_mysqldb import MySQL
import MySQLdb.cursors  
import base64 
from datetime import timedelta
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)

app.secret_key = "Detroja_D_E_E_P"

app.config["MYSQL_HOST"] = 'localhost'
app.config["MYSQL_USER"] = 'root'
app.config["MYSQL_PASSWORD"] = '12345'
app.config['MYSQL_PORT'] = 3306
app.config["MYSQL_DB"] = 'deep'

db = MySQL(app) 

@app.route('/')
def index():
    return render_template('login.html')

@app.route("/store",methods = ['GET','POST'])   
def store():
       if request.method == 'POST':
        Username = request.form["Username"]
        Email = request.form["Email"]
        Phone = request.form["Phone"]
        Address = request.form["Address"]
        City = request.form['City']
        State = request.form['State']
        Image = request.files["Image"]
        Password = request.form['Password']
        Task_Name = request.form['Task_Name']
        Status = request.form.getlist("Status")
        a = ','.join(Status)
        Start_Date = request.form['Start_Date']
        End_Date = request.form['End_Date']
        hashed_Password = bcrypt.generate_password_hash (Password).decode("utf-8")
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("INSERT INTO task1 (Username,Email,Phone,Address,City,State,Image,Password,Task_Name,Status,Start_Date,End_Date) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(Username,Email,Phone,Address,City,State,Image.read(),hashed_Password,Task_Name,[a],Start_Date,End_Date,))
        db.connection.commit()

        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("select * from task1 where Username = %s",(Username,))
        uplode = cursor.fetchone()
       
        encode_Image = base64.b64encode(uplode['Image']).decode('utf-8')
        uplode['encode_Image'] = encode_Image

        return redirect(url_for("login"))
       
@app.route("/form")
def form():
    cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM task1")
    store = cursor.fetchall()
    cursor.close()
    return render_template('form.html',store = store)       
       
@app.route("/login",methods = ['GET','POST'])
def login():    
    if request.method == 'POST' and 'Username' in request.form and 'Password'  in request.form:
        Username = request.form['Username']
        Password = request.form['Password']
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("select * from task1 WHERE Username = %s",(Username,))
        upload = cursor.fetchone()
        
        if upload and bcrypt.check_password_hash(upload['Password'],Password):
            encoded_Image = base64.b64encode(upload['Image']).decode('utf-8')
            upload['encoded_Image']  = encoded_Image
            
            session['loggedin'] = True
            session['id'] = upload['id']
            session['Username'] = upload['Username']
            return redirect(url_for('display',upload=upload['Username']))
        else:
            msg = "User id or Password is incorrect!"
            return render_template('login.html',msg = msg)
    
    return render_template('login.html') 

@app.route("/display",methods = ['GET'])
def display():    
    if 'loggedin' in session:
        Username = session['Username']
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("select * from task1 WHERE Username = %s", (Username,))
        upload = cursor.fetchone()
        encoded_Image = base64.b64encode(upload["Image"]).decode('utf-8')
        upload['Image']  = encoded_Image

        if upload :
            return render_template('display.html',upload=upload)
        else :
            return render_template('login.html')
    else :
        return redirect(url_for('login'))
    
@app.route("/edit/<int:id>",methods = ['GET','POST'])
def edit(id):
    cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("select * from task1 where id = %s",(id,))
    id = cursor.fetchone()
    encoded_Image = base64.b64encode(id["Image"]).decode('utf-8')
    id['Image']  = encoded_Image
    return render_template('edit.html',id = id)

@app.route('/update/<id>', methods=['GET', 'POST'])
def update(id):
    if request.method == 'POST':
        Username = request.form["Username"]
        Email = request.form["Email"]
        Phone = request.form["Phone"]
        Address = request.form["Address"]
        City = request.form['City']
        State = request.form['State']
        Task_Name = request.form['Task_Name']
        Status = request.form.getlist('Status')
        a = ','.join(Status)
        Image = request.files["Image"]
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("UPDATE task1 SET Username = %s,Email = %s,Phone = %s,Address = %s,City = %s,State = %s,Task_Name = %s,Status = %s,Image = %s WHERE id = %s",(Username,Email,Phone,Address,City,State,Task_Name,[a],Image.read(),id,))
        db.connection.commit()
        cursor.close()
        return redirect(url_for('display'))

    cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT id task1 WHERE id = %s", (id,))
    upload = cursor.fetchone()
    cursor.close()
    return render_template('form.html', upload=upload)  

@app.route('/logout')
def logout():
    session.pop('loggedin',None)
    session.pop('id',None)
    session.pop('Username',None) 
    return redirect(url_for('login'))

@app.route("/data")
def data():
    cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM task1")
    store = cursor.fetchall()
    cursor.close()
    return render_template('admin.html',store = store)

@app.route('/delete1/<id>')
def delete1(id):
    cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("DELETE FROM task1 WHERE id = %s", (id,))
    db.connection.commit()
    cursor.close()
    return redirect(url_for('data'))  
    
@app.route('/delete/<id>')
def delete(id):
    cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("DELETE FROM task1 WHERE id = %s", (id,))
    db.connection.commit()
    cursor.close()
    return redirect(url_for('login'))  

@app.route('/updatepass/<int:id>',methods = ['POST','GET'])
def updatepass(id):
    msg = ''
    if request.method == 'POST' and 'oldPassword' in request.form and 'newPassword' in request.form:
        oPassword = request.form['oldPassword']
        nPassword = request.form['newPassword']
        Username = session['Username']
        cur = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('select * from task1 where Username=%s',(Username,))
        account = cur.fetchone()
        is_true = bcrypt.check_password_hash(account['Password'], oPassword)
        if is_true:
            if account:
                cur = db.connection.cursor(MySQLdb.cursors.DictCursor)
                hashed_password = bcrypt.generate_password_hash (nPassword).decode('utf-8')
                cur.execute('UPDATE task1 set Password = %s where id = %s', (hashed_password,id,))
                db.connection.commit()
                
                return redirect(url_for('display'))
        else:
            msg = "Old Password is Doesn't match"
            
    cur = db.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('select * from task1 where id=%s',(id,))
    account = cur.fetchone()

    encoded_image = base64.b64encode(account['Image']).decode('utf-8')
    account['encoded_image'] = encoded_image

    return render_template('updatepass.html', account=account, msg = msg)

if __name__ == '__main__':
    app.run(debug=True)       