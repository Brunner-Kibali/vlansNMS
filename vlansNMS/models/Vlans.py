from vlansNMS import db


class Vlan(db.Model):
    __tablename__ = 'vlans'

    id = db.Column(db.Integer, nullable=False, unique=True, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    state = db.Column(db.String)
