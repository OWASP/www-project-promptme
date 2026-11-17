from Market import db, bcrypt, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    email_address = db.Column(db.String(length=50), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    budget = db.Column(db.Integer, nullable=False, default=0)
    items = db.relationship('Item', backref='owned_user', lazy=True)
    
    def __repr__(self):
        return f'User {self.username}'
    
    @property
    def prettier_budget(self):
        if len(str(self.budget)) >= 4:
            return f'{str(self.budget)[:-3]},{str(self.budget)[-3:]} $'
        return f'{self.budget} $'
    
    @property
    def password(self):
        raise AttributeError('Password is write-only.')
    
    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')
    
    def password_check(self, password_attempt):
        return bcrypt.check_password_hash(self.password_hash, password_attempt)
    
    def can_purchase(self, item_obj):
        return self.budget >= item_obj.price
    
    def can_sell(self, item_obj):
        return item_obj in self.items
    
    def delete_user(user_id):
        user = User.query.filter_by(id=user_id).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            return True
        return False

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(length=30), nullable=False, unique=True)
    barcode = db.Column(db.String(length=12), nullable=False, unique=True)
    price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(length=1024), nullable=False)
    owner = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __repr__(self):
        return f'Item {self.name}'
    
    @property
    def prettier_price(self):
        if len(str(self.price)) >= 4:
            return f'{str(self.price)[:-3]},{str(self.price)[-3:]} $'
        else:
            return f'{self.price} $'
        
    def buy(self, user):
        self.owner = user.id
        user.budget -= self.price
        db.session.commit()
    
    def sell(self, user):
        self.owner = None
        user.budget += self.price
        db.session.commit()
    
    def delete_item(item_id):
        item = Item.query.filter_by(id=item_id).first()
        if item:
            db.session.delete(item)
            db.session.commit()
            return True
        return False
    
    def update_item(self, name, price, barcode, description):
        self.name = name
        self.price = price
        self.barcode = barcode
        self.description = description
        db.session.commit()
