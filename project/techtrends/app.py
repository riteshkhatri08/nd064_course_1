import sqlite3
from datetime import datetime
import logging, sys

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash, json
from werkzeug.exceptions import abort


# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    app.db_connections = app.db_connections + 1
    return connection


# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                              (post_id, )).fetchone()
    connection.close()
    return post


# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'
app.db_connections = 0


# Define the main route of the web application
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)


# Define how each individual article is rendered
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        app.logger.info("Article doesn't exist - Returning 404!")
        return render_template('404.html'), 404
    else:
        app.logger.info("Article - \"" + post['title'] +
                        "\" retrieved !")
        
        # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        return render_template('post.html', post=post)


# Define the About Us page
@app.route('/about')
def about():
    
    app.logger.info("Returing \"About Us \" page")
    return render_template('about.html')


# Define the post creation functionality
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute(
                'INSERT INTO posts (title, content) VALUES (?, ?)',
                (title, content))
            connection.commit()
            connection.close()
            app.logger.info("New Article \"" + title +
                            "\" created")
            return redirect(url_for('index'))

    return render_template('create.html')


# Health Endpoint
@app.route('/healthz')
def health():
    data = {"result": "OK - healthy"}
    response = app.response_class(response=json.dumps(data),
                                  status=200,
                                  mimetype='application/json')
    return response


# Metrics Endpoint
@app.route('/metrics')
def metrics():

    conn = get_db_connection()
    post_count = conn.execute('SELECT count(*) from posts').fetchone()
    data = {"db_connections": app.db_connections, "posts": post_count[0]}
    response = app.response_class(response=json.dumps(data),
                                  status=200,
                                  mimetype="application/json")

    return response


# start the application on port 3111
if __name__ == "__main__":
    #Set up logging
    stdout_handler = logging.StreamHandler(sys.stdout)
    stderr_handler = logging.StreamHandler(sys.stderr)
    stdout_handler.setLevel(logging.DEBUG)
    stderr_handler.setLevel(logging.ERROR)
    handlers = [stdout_handler, stderr_handler]
    logging.basicConfig(format='%(levelname)s:%(name)s: %(asctime)s %(message)s', encoding='utf-8',level=logging.DEBUG, datefmt='%d/%m/%Y, %H:%M:%S,',handlers=handlers)
    
    app.run(host='0.0.0.0', port='3111')
   