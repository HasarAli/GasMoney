from datetime import datetime, timezone
from itsdangerous import BadData, BadSignature, TimedJSONWebSignatureSerializer as Serializer

from sqlalchemy.orm import column_property
from sqlalchemy.sql import select, func
from gasmoney import db, login_manager, app
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def get_utc():
    return datetime.now(timezone.utc)

class Reservation(db.Model):
    ride_id = db.Column(db.ForeignKey('ride.id'), primary_key=True)
    passenger_id = db.Column(db.ForeignKey('user.id'), primary_key=True)
    seats_reserved = db.Column(db.Integer, nullable=False, default=1)
    reservation_dt = db.Column(db.DateTime, nullable=False, default=get_utc)
    
    def __repr__(self) -> str:
        return f"Reservation('{self.ride_id}', '{self.passenger_id}', '{self.seats_reserved}')"

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(254), unique=True, nullable=False)
    username = db.Column(db.String(32), unique=True, nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(1), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    image_link = db.Column(db.String(254), nullable=False, default='default.jpg')
    register_dt = db.Column(db.DateTime, nullable=False, default=get_utc)
    is_email_verified = db.Column(db.Boolean, nullable=False, default=False)
    is_phone_verified = db.Column(db.Boolean, nullable=False, default=False)
    
    offered_rides = db.relationship('Ride', backref=db.backref('driver'))
    reservations = db.relationship('Reservation', backref=db.backref('passenger'))

    def get_token(self, desc, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id, **desc}).decode('utf-8')

    @staticmethod
    def verify_token(token, desc):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            dict = s.loads(token)
            user_id = dict['user_id']
            if not desc.items() <= dict.items():
                raise Exception('token did not contain given dictionary')
        except BadSignature as e:
            app.logger.info('token failed to load', exc_info=True)
            if e.payload is not None:
                try:
                    s.load_payload(e.payload)
                except BadData:
                    app.logger.info('token contains unsafe data', exc_info=True)
            raise
        except:
            app.logger.exception('token is invalid')
            raise
        
        return User.query.filter_by(id=user_id).first()

    def __repr__(self):
        return f"User('{self.first_name}', '{self.email}', '{self.image_link}')"

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
