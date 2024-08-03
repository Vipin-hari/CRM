from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crm.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'supersecretkey'  # Change this to a more secure key in production

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect to login if not authenticated

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(15))
    address = db.Column(db.String(255))
    date_of_birth = db.Column(db.Date)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    sales = db.relationship('Sale', backref='customer', lazy=True)
    interactions = db.relationship('Interaction', backref='customer', lazy=True)
    support_tickets = db.relationship('SupportTicket', backref='customer', lazy=True)

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    sale_date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), nullable=False)

class Interaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    interaction_date = db.Column(db.Date, nullable=False)
    type = db.Column(db.String(20), nullable=False)
    notes = db.Column(db.Text)

class SupportTicket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    creation_date = db.Column(db.Date, nullable=False)
    issue_description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)  # Added is_admin field

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Login failed. Check your username and/or password', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')  # Updated method
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('User registered successfully!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/customers')
@login_required
def customers():
    search = request.args.get('search')
    if search:
        customers = Customer.query.filter(Customer.first_name.like(f'%{search}%') | Customer.last_name.like(f'%{search}%')).all()
    else:
        customers = Customer.query.all()
    return render_template('customers.html', customers=customers)

@app.route('/customer/<int:customer_id>')
@login_required
def customer_details(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    return render_template('customer_details.html', customer=customer)

@app.route('/customer/create', methods=['GET', 'POST'])
@login_required
def create_customer():
    if request.method == 'POST':
        # Get the date_of_birth from the form
        dob_str = request.form['date_of_birth']
        
        # Convert the string to a date object
        date_of_birth = datetime.strptime(dob_str, '%Y-%m-%d').date()
        
        # Create a new Customer object
        new_customer = Customer(
            first_name=request.form['first_name'],
            last_name=request.form['last_name'],
            email=request.form['email'],
            phone=request.form['phone'],
            address=request.form['address'],
            date_of_birth=date_of_birth  # Use the date object
        )
        
        # Add and commit to the database
        db.session.add(new_customer)
        db.session.commit()
        
        flash('Customer created successfully!', 'success')
        return redirect(url_for('customers'))
    
    return render_template('create_customer.html')

@app.route('/customer/edit/<int:customer_id>', methods=['GET', 'POST'])
@login_required
def edit_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    if request.method == 'POST':
        customer.first_name = request.form['first_name']
        customer.last_name = request.form['last_name']
        customer.email = request.form['email']
        customer.phone = request.form['phone']
        customer.address = request.form['address']
        customer.date_of_birth = datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d').date()
        db.session.commit()
        flash('Customer updated successfully!', 'success')
        return redirect(url_for('customer_details', customer_id=customer.id))
    return render_template('edit_customer.html', customer=customer)

@app.route('/customer/delete/<int:customer_id>', methods=['POST'])
@login_required
def delete_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    db.session.delete(customer)
    db.session.commit()
    flash('Customer deleted successfully!', 'success')
    return redirect(url_for('customers'))

@app.route('/sales')
@login_required
def sales():
    sales = Sale.query.all()
    return render_template('sales.html', sales=sales)

@app.route('/support-tickets')
@login_required
def support_tickets():
    tickets = SupportTicket.query.all()
    return render_template('support_tickets.html', tickets=tickets)

@app.route('/sales-report')
@login_required
def sales_report():
    sales = Sale.query.all()
    total_sales = sum(sale.amount for sale in sales)
    return render_template('sales_report.html', total_sales=total_sales, sales=sales)

@app.route('/sales/create', methods=['GET', 'POST'])
@login_required
def create_sale():
    if not current_user.is_admin:
        flash('You do not have permission to create sales.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        new_sale = Sale(
            customer_id=request.form['customer_id'],
            sale_date=datetime.strptime(request.form['sale_date'], '%Y-%m-%d').date(),
            amount=request.form['amount'],
            status=request.form['status']
        )
        db.session.add(new_sale)
        db.session.commit()
        flash('Sale created successfully!', 'success')
        return redirect(url_for('sales'))

    customers = Customer.query.all()
    return render_template('create_sale.html', customers=customers)

@app.route('/support-tickets/create', methods=['GET', 'POST'])
@login_required
def create_support_ticket():
    if request.method == 'POST':
        new_ticket = SupportTicket(
            customer_id=current_user.id,
            creation_date=datetime.strptime(request.form['creation_date'], '%Y-%m-%d').date(),
            issue_description=request.form['issue_description'],
            status=request.form['status']
        )
        db.session.add(new_ticket)
        db.session.commit()
        flash('Support ticket created successfully!', 'success')
        return redirect(url_for('support_tickets'))

    return render_template('create_support_ticket.html')

@app.route('/admin/customers')
@login_required
def admin_customers():
    if not current_user.is_admin:
        flash('You do not have permission to view this page.', 'danger')
        return redirect(url_for('index'))

    customers = Customer.query.all()
    return render_template('admin_customers.html', customers=customers)

if __name__ == '__main__':
    app.run(debug=True)
