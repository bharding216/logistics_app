from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from sqlalchemy import event

app = Flask (__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class appts_db(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    carrier = db.Column(db.String(100))
    volume = db.Column(db.Integer)
    material = db.Column(db.String(10))
    pickup_date = db.Column(db.String(10))
    pickup_time = db.Column(db.String(5))
    PO_number = db.Column(db.String(30))

    #backref behaves like a column in the log_db model. This way, 
    #you can access the appt that the log was assigned to using the
    #"appt" attribute. 
    log_id = db.relationship("log_db", backref="appt", lazy=True)

class carriers_db(db.Model):
    carrier_id = db.Column(db.Integer, primary_key=True)
    carrier_name = db.Column(db.String(100))
    phone_number = db.Column(db.String(15))

@event.listens_for(appts_db, "after_insert")
def insert_log(mapper, connection, target):
    po = log_db.__table__
    connection.execute (po.insert().values(appt_id=target.id, action='Created'))

#@event.listens_for(appts_db, "before_update")
#def update_log_old(mapper, connection, target):
#    po = log_db.__table__
#    connection.execute (po.insert().values(appt_id=target.id, action='Updated - Old'))

@event.listens_for(appts_db, "after_update")
def update_log_new(mapper, connection, target):
    po = log_db.__table__
    connection.execute (po.insert().values(appt_id=target.id, action='Updated - New'))

@event.listens_for(appts_db, "before_delete")
def delete_log(mapper, connection, target):
    po = log_db.__table__
    connection.execute (po.insert().values(appt_id=target.id, action='Deleted'))

class log_db(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appt_id = db.Column(db.Integer, db.ForeignKey('appts_db.id'))
    modified_on = db.Column(db.DateTime, default=datetime.now)
    action = db.Column(db.String(7))

    def __repr__(self):
        return '<Appt %r>' % self.id

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        carrier_name = request.form['carrier']
        requested_volume = request.form['volume']
        material_name = request.form['material']
        pickup_date_input = request.form['pickup_date']
        pickup_time_input = request.form['pickup_time']
        PO_number = request.form['PO_number']
        
        new_appt = appts_db(carrier=carrier_name, volume=requested_volume,
            material=material_name, pickup_date=pickup_date_input, 
            pickup_time=pickup_time_input, PO_number=PO_number)
        
        db.session.add(new_appt)
        db.session.commit()
        return redirect('/')
    
    else:
        search_material = request.args.getlist('material_filter')
        if not request.args.get('start_date_filter'):
            #this if-block will execute if the string is empty  
            search_date_start = '2022-01-01'
        else:
            search_date_start = request.args.get('start_date_filter')
        if not request.args.get('end_date_filter'):
            search_date_end = '2100-01-01'
        else:
            search_date_end = request.args.get('end_date_filter')
        if not request.args.get('start_time_filter'):
            search_time_start = '00:00'
        else:
            search_time_start = request.args.get('start_time_filter')
        if not request.args.get('end_time_filter'):
            search_time_end = '23:59'
        else:
            search_time_end = request.args.get('end_time_filter')
        
        #if the user wants to see the appointments for all carriers
        if request.args.get('carrier') == 'all':
            #then don't filter the results by carrier name
            appts = appts_db.query.filter(appts_db.material.in_(search_material)) \
                .filter(appts_db.pickup_date.between(search_date_start, search_date_end)) \
                .filter(appts_db.pickup_time.between(search_time_start, search_time_end)) \
                .order_by(appts_db.pickup_date).all()
        #if you want to filter by a specific carrier
        else:
            search_carrier = request.args.get('carrier')
            appts = appts_db.query.filter(appts_db.material.in_(search_material)) \
                .filter(appts_db.pickup_date.between(search_date_start, search_date_end)) \
                .filter(appts_db.pickup_time.between(search_time_start, search_time_end)) \
                .filter(appts_db.carrier == search_carrier) \
                .order_by(appts_db.pickup_date).all()

        #to generate the carriers within the dropdown list
        carriers = carriers_db.query.order_by(carriers_db.carrier_name).all()

        return render_template('index.html', appts=appts, carriers=carriers)

@app.route('/history', methods=['GET'])
def history():
    if not request.args.get('log'):
        query_limit = "10"
    else:
        query_limit = request.args.get('log')

    log = log_db.query.order_by(log_db.id.desc()).limit(query_limit).all()
    return render_template('history.html', log=log)

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        carrier_name = request.form['carrier']
        requested_volume = request.form['volume']
        material_name = request.form['material']
        pickup_date_input = request.form['pickup_date']
        pickup_time_input = request.form['pickup_time']
        PO_number = request.form['PO_number']
        
        new_appt = appts_db(carrier=carrier_name, volume=requested_volume,
            material=material_name, pickup_date=pickup_date_input, 
            pickup_time=pickup_time_input, PO_number=PO_number)

        db.session.add(new_appt)
        db.session.commit()
        return redirect('/')

    else:
        #this query variable is passed to the 'create.html' page where
        #it is rendered. 
        carriers = carriers_db.query.order_by(carriers_db.carrier_name).all()
        return render_template('create.html', carriers=carriers)

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    appt = appts_db.query.get_or_404(id)

    if request.method == 'POST':
        appt.carrier = request.form['carrier']
        appt.volume = request.form['volume_update']
        appt.material = request.form['material_update']
        appt.pickup_date = request.form['pickup_date']
        appt.pickup_time = request.form['pickup_time']
        appt.PO_number = request.form['PO_number_update']

        db.session.commit()
        return redirect('/')
    
    else:
        carriers = carriers_db.query.order_by(carriers_db.carrier_name).all()
        return render_template('update.html', appt=appt, carriers=carriers)

@app.route('/delete/<int:id>')
def delete(id):
    appt_to_delete = appts_db.query.get_or_404(id)
    db.session.delete(appt_to_delete)
    db.session.commit()
    return redirect('/')

#the view function describes the steps taken when you are
#on that specific page. The view function can also pass 
#variables to an html page and return the rendered page. 
@app.route('/new_carrier', methods=['GET', 'POST'])
def new_carrier():
    if request.method == 'POST':
        carrier = request.form['carrier_name']
        phone = request.form['carrier_phone']
        
        new_carrier = carriers_db(carrier_name=carrier, phone_number=phone)
        
        db.session.add(new_carrier)
        db.session.commit()
        return redirect('/create')

    else:
        return render_template('new_carrier.html')

if __name__ == '__main__':
    app.run(host='localhost', port=2000, debug=True)