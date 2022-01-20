from datetime import datetime
from gasmoney import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Reservation(db.Model):
    ride_id = db.Column(db.ForeignKey('ride.id'), primary_key=True)
    passenger_id = db.Column(db.ForeignKey('user.id'), primary_key=True)
    seats_reserved = db.Column(db.Integer, nullable=False, default=1)
    reservation_dt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"Reservation('{self.ride_id}', '{self.passenger_id}', '{self.seats_reserved}')"

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(254), unique=True, nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(1), nullable=False)
    password = db.Column(db.String(128), nullable=False)
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
    origin = db.Column(db.String(258), nullable=False)
    destination = db.Column(db.String(258), nullable=False)
    rendezvous = db.Column(db.String(258), nullable=False)
    departure_dt = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(1), nullable=False, default=0)
    seats_offered = db.Column(db.Integer, nullable=False, default=1)
    seats_available = column_property(
        seats_offered -
        select(func.coalesce(func.sum(Reservation.seats_reserved), 0)).
        where(Reservation.ride_id==id).
        scalar_subquery()
    )

    reservations = db.relationship(
        'Reservation',
        lazy=False,
        backref=db.backref('ride')
    )
    
    def __repr__(self):
        return f"Ride('{self.id}', '{self.origin}', '{self.destination}', '{self.rendezvous}', '{self.departure_dt}, {self.status})"
