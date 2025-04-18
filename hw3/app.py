from flask import Flask, render_template, url_for, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Initialize Flask App
app = Flask(__name__)

# Configure Database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///thereviews.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize SQLAlchemy with Declarative Base
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Define the Review model using `Mapped` and `mapped_column`
class Review(db.Model):
    __tablename__ = "thereviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(60), nullable=False)
    text: Mapped[str] = mapped_column(String, nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)

    def __init__(self, title: str, text: str, rating: int):
        self.title = title
        self.text = text
        self.rating = rating

# DATABASE UTILITY CLASS
class Database:
    def __init__(self):
        pass

    def get(self, review_id: int = None):
        """Retrieve all reviews or a specific review by ID."""
        if review_id:
            return db.session.get(Review, review_id)
        return db.session.query(Review).all()

    def create(self, title: str, text: str, rating: int):
        """Create a new review."""
        new_review = Review(title=title, text=text, rating=rating)
        db.session.add(new_review)
        db.session.commit()

    def update(self, review_id: int, title: str, text: str, rating: int):
        """Update an existing review."""
        review = self.get(review_id)
        if review:
            review.title = title
            review.text = text
            review.rating = rating
            db.session.commit()

    def delete(self, review_id: int):
        """Delete a review."""
        review = self.get(review_id)
        if review:
            db.session.delete(review)
            db.session.commit()

db_manager = Database()  # Create a database manager instance

# Initialize database with sample data
@app.before_request
def setup():
    with app.app_context():
        db.create_all()
        if not db_manager.get():  # If database is empty, add a sample entry
            db_manager.create("Mr. Pumpkin Man", "This is a pretty bad movie", 2)
            db_manager.create("Onions: The Musical", "Sondheim really cooked on this one", 5)
            db_manager.create("Piranesi", "Animation is so back", 4)
            db_manager.create("Secretariat 4", "We really need to stop beating this dead horse", 1)
            print("Database initialized with sample data!")

# Reset the database
@app.route('/reset-db', methods=['GET', 'POST'])
def reset_db():
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("Database reset: success!")
    # ok so i did change this from the starter code. it just renders with a template so you don't have to manually type the url to go back
    return render_template('message.html', message='Database has been reset!')


# ROUTES
"""You will add all of your routes below, there is a sample one which you can use for testing"""

@app.route('/')
def home():
    """Shows a table of all reviews"""
    reviews = db_manager.get()
    url_for('static', filename='style.css')
    return render_template('home.html', reviews = reviews)

@app.route('/<id>')
def review_page(id = Integer):
    """Shows a single review"""
    review = db_manager.get(id)
    url_for('static', filename='style.css')
    return render_template('review.html', review = review)

@app.post('/delete/<id>')
def delete(id = Integer):
    """Deletes the review at a given index"""
    db_manager.delete(id)
    return home()

@app.route('/edit/<id>')
def edit(id = Integer):
    """Form to edit a given review"""
    content = db_manager.get(id)
    url_for('static', filename='style.css')
    return render_template('form.html', review = content)

@app.route('/edit')
def add():
    """Form to add a new review"""
    url_for('static', filename='style.css')
    return render_template('form.html', review = False)

@app.post('/update/<id>')
def update(id = Integer):
    """Updates a review from form data"""
    # form parsing
    title = request.form['title']
    text = request.form['text']
    rating = request.form['star-range']
    db_manager.update(id, title, text, rating)
    
    return render_template('message.html', message='Updated review for ' + title + '!')

@app.post('/update/')
def create():
    """Creates a new review from form data"""
    # form parsing
    title = request.form['title']
    text = request.form['text']
    rating = request.form['star-range']
    db_manager.create(title, text, rating)
    
    return render_template('message.html', message='Created review for ' + title + '!')

  
# RUN THE FLASK APP
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure DB is created before running the app
    app.run(debug=True)
