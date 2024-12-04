from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit

app = Flask(__name__)

# Configuration for SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy and SocketIO
db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")  # Enable CORS for Socket.IO


# Models
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    comments = db.relationship('Comment', backref='post', lazy=True)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)

# Routes
@app.route('/')
def index():
    posts = Post.query.all()
    return render_template('index.html', posts=posts)

@app.route('/post', methods=['POST'])
def create_post():
    content = request.form['content']
    new_post = Post(content=content)
    db.session.add(new_post)
    db.session.commit()
    # Broadcast the new post to all clients
    socketio.emit('new_post', {'id': new_post.id, 'content': new_post.content}, to='broadcast')
    return redirect(url_for('index'))

@app.route('/comment/<int:post_id>', methods=['POST'])
def create_comment(post_id):
    content = request.form['content']
    new_comment = Comment(content=content, post_id=post_id)
    db.session.add(new_comment)
    db.session.commit()
    # Broadcast the new comment to all clients
    socketio.emit('new_comment', {'post_id': post_id, 'content': new_comment.content}, to='broadcast')
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Initialize the database
    with app.app_context():
        db.create_all()
    # Run the app with SocketIO
    socketio.run(app, debug=False )
