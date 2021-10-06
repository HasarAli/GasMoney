from flaskr import db
from datetime import datetime

class Reservation(db.Model):
    ride_id = db.Column(db.ForeignKey('ride.id'), primary_key=True)
    passenger_id = db.Column(db.ForeignKey('user.id'), primary_key=True)
    seats_reserved = db.Column(db.Integer, nullable=False, default=1)
    reservation_dt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"Reservation('{self.ride_id}', '{self.passenger_id}', '{self.seats_reserved}')"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(20), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.String(1), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    register_dt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    offered_rides = db.relationship('Ride', backref=db.backref('driver', lazy=True) , lazy=True)
    rides = db.relationship(
        'Reservation', 
        lazy=True,
        backref=db.backref('passenger', lazy=False)
    )

    def __repr__(self):
        return f"User('{self.first_name}', '{self.email}', '{self.image_file}')"

class Ride(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    origin = db.Column(db.String, nullable=False)
    destination = db.Column(db.String, nullable=False)
    rendezvous = db.Column(db.String, nullable=False)
    departure_dt = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String, nullable=False)
    seats_available = db.Column(db.Integer, nullable=False, default=1)

    passengers = db.relationship(
        'Reservation',
        lazy=True,
        backref=db.backref('ride', lazy=False)
    )
    
    def __repr__(self):
        return f"Ride('{self.id}', {self.origin}', '{self.destination}', '{self.rendezvous}', '{self.departure_dt}, {self.status})"
