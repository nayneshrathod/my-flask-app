import os
import yaml
from flask import Flask, render_template, redirect, request, session, flash
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
Bootstrap(app)
CKEditor(app)

db = yaml.load(open('db.yaml'))
# app.config['MYSQL_']
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['SECRET_KEY'] = os.urandom(24)
mysql = MySQL(app)

app.config['SECRET_KEY'] = 'secret'


@app.route('/')
def index():
    cur = mysql.connection.cursor()
    resultValue = cur.execute("select * from blog")
    if resultValue > 0:
        blogs = cur.fetchall()
        cur.close()
        return render_template('index.html', blogs=blogs)
    cur.close()
    return render_template('index.html', blogs=None)


@app.route('/about/')
def about():
    return render_template('about.html')


@app.route('/contact/')
def contact():
    return render_template('contact.html')


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        userDetails = request.form
        if userDetails['password'] != userDetails['password_confirmation']:
            flash('Password do not match ! Try Again', 'danger')
            return render_template('register.html')
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO user(first_name,last_name,email,username,password) values(%s,%s,%s,%s,%s)",
                    (userDetails['first_name'], userDetails['last_name'], userDetails['email'], userDetails['username'],
                     generate_password_hash(userDetails['password'])))
        mysql.connection.commit()
        cur.close()
        flash('Registration Successfully', 'success')
        return redirect('/login')
    return render_template('register.html')


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userDetails = request.form
        username = userDetails['username']
        cur = mysql.connection.cursor()
        resultValue = cur.execute("select *  from user  where username =  %s ", ([username]))
        if resultValue > 0:
            user = cur.fetchone()
            if check_password_hash(user['password'], userDetails['password']):
                session['login'] = True
                session['firstname'] = user['first_name']
                session['lastname'] = user['last_name']
                flash('Welcome ' + session['firstname'] + ' You have been successfully Login ', 'success')
            else:
                cur.close()
                flash('Password do not match ! Try Again', 'danger')
                return render_template('login.html')
        else:
            cur.close()
            flash('User Does not Found', 'danger')
            return render_template('login.html')
        cur.close()
        return redirect('/')
    return render_template('login.html')


@app.route('/logout/')
def logout():
    session.clear()
    flash('You Have been Log out', 'info')
    return redirect('/login')


@app.route('/write-blog/', methods=['GET', 'POST'])
def write_blog():
    if request.method == 'POST':
        blogPost = request.form
        title = blogPost['title']
        body = blogPost['body']
        author = session['firstname'] + ' ' + session['lastname']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO blog(title,body,author) values(%s,%s,%s)", (title, body, author))
        mysql.connection.commit()
        cur.close()
        flash('Successfully Added Blog', 'success')
        return redirect('/')
    return render_template('write-blog.html')


@app.route('/my-blog/')
def my_blog():
    author = session['firstname'] + ' ' + session['lastname']
    cur = mysql.connection.cursor()
    resultValue = cur.execute("select * from blog WHERE author = %s", [author])
    if resultValue > 0:
        my_blogs = cur.fetchall()
        cur.close()
        return render_template('my-blogs.html', my_blogs=my_blogs)
    else:
        cur.close()
        return render_template('my-blogs.html', my_blogs=None)


@app.route('/edit-blogs/<int:id>/', methods=['GET', 'POST'])
def edit_blogs(id):
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        title = request.form['title']
        body = request.form['body']
        cur.execute("update blog SET   title=%s,body=%s where blog_id =%s", (title, body, id))
        mysql.connection.commit()
        cur.close()
        flash('Blog Is Update', 'success')
        return redirect('/blogs/{}'.format(id))
    cur = mysql.connection.cursor()
    resultValue = cur.execute("select * from blog where blog_id = {}".format(id))
    if resultValue > 0:
        blog = cur.fetchone()
        blog_form = {}
        blog_form['title'] = blog['title']
        blog_form['body'] = blog['body']
        # cur.close()
        return render_template('edit-blogs.html', blog_form=blog_form)


@app.route('/blogs/<int:id>/')
def blog(id):
    cur = mysql.connection.cursor()
    resultValue = cur.execute("select * from blog where blog_id = {}".format(id))
    if resultValue > 0:
        blog = cur.fetchone()
        cur.close()
        return render_template('blog.html', blog=blog)
    return "Blog Not Found"


@app.route('/delete-blogs/<int:id>/', methods=['POST'])
def delete_blog(id):
    cur = mysql.connection.cursor()
    cur.execute("delete  from blog where blog_id = {}".format(id))
    mysql.connection.commit()
    cur.close()
    flash('Your Blog Has been Deleted ', 'success')
    return redirect('/my-blogs')


if __name__ == '__main__':
    app.run(debug=True, port=5200)
