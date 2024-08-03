from app import app, db, User, Customer, Sale, Interaction, SupportTicket
from werkzeug.security import generate_password_hash
from datetime import datetime

def populate_db():
    with app.app_context():
        # Create users
        admin = User(username='admin', password=generate_password_hash('admin123', method='pbkdf2:sha256'))
        user = User(username='user', password=generate_password_hash('user123', method='pbkdf2:sha256'))
        db.session.add(admin)
        db.session.add(user)
        db.session.commit()

        # Create customers
        customer1 = Customer(first_name='John', last_name='Doe', email='john@example.com', phone='123-456-7890', address='123 Elm St', date_of_birth=datetime(1990, 1, 1))
        customer2 = Customer(first_name='Jane', last_name='Smith', email='jane@example.com', phone='987-654-3210', address='456 Oak St', date_of_birth=datetime(1985, 5, 15))
        db.session.add(customer1)
        db.session.add(customer2)
        db.session.commit()

        # Create sales
        sale1 = Sale(customer_id=1, sale_date=datetime(2024, 1, 10), amount=200.00, status='Completed')
        sale2 = Sale(customer_id=2, sale_date=datetime(2024, 2, 20), amount=350.00, status='Pending')
        db.session.add(sale1)
        db.session.add(sale2)
        db.session.commit()

        # Create interactions
        interaction1 = Interaction(customer_id=1, interaction_date=datetime(2024, 1, 15), type='Call', notes='Discussed new features.')
        interaction2 = Interaction(customer_id=2, interaction_date=datetime(2024, 2, 25), type='Email', notes='Follow-up on payment status.')
        db.session.add(interaction1)
        db.session.add(interaction2)
        db.session.commit()

        # Create support tickets
        ticket1 = SupportTicket(customer_id=1, creation_date=datetime(2024, 1, 18), issue_description='Issue with product functionality', status='Resolved')
        ticket2 = SupportTicket(customer_id=2, creation_date=datetime(2024, 2, 28), issue_description='Delivery delay', status='Open')
        db.session.add(ticket1)
        db.session.add(ticket2)
        db.session.commit()

if __name__ == '__main__':
    populate_db()
