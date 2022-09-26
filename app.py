from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date


app = Flask (__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)



class appts_db(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    carrier = db.Column(db.String(100))
    material = db.Column(db.String(10))
    pickup_date = db.Column(db.String(10))
    pickup_time = db.Column(db.String(5))

class carriers_db(db.Model):
    carrier_id = db.Column(db.Integer, primary_key=True)
    carrier_name = db.Column(db.String(100))
    phone_number = db.Column(db.String(15))




    def __repr__(self):
        return '<Appt %r>' % self.id




@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        carrier_name = request.form['carrier']
        material_name = request.form['material']
        pickup_date_input = request.form['pickup_date']
        pickup_time_input = request.form['pickup_time']
        
        new_appt = appts_db(carrier=carrier_name, material=material_name, 
            pickup_date=pickup_date_input, pickup_time=pickup_time_input)
        
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

        appts = appts_db.query.filter(appts_db.material.in_(search_material)) \
            .filter(appts_db.pickup_date.between(search_date_start, search_date_end)) \
            .order_by(appts_db.pickup_date).all()


        return render_template('index.html', appts=appts)




@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        carrier_name = request.form['carrier']
        material_name = request.form['material']
        pickup_date_input = request.form['pickup_date']
        pickup_time_input = request.form['pickup_time']
        
        new_appt = appts_db(carrier=carrier_name, material=material_name, 
            pickup_date=pickup_date_input, pickup_time=pickup_time_input)
        
        db.session.add(new_appt)
        db.session.commit()
        return redirect('/')

    else:
        return render_template('create.html')



@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    appt = appts_db.query.get_or_404(id)

    if request.method == 'POST':
        appt.carrier = request.form['carrier']
        appt.material = request.form['material_update']
        appt.pickup_date = request.form['pickup_date']
        appt.pickup_time = request.form['pickup_time']

        db.session.commit()
        return redirect('/')
    
    else:
        return render_template('update.html', appt=appt)





@app.route('/delete/<int:id>')
def delete(id):
    appt_to_delete = appts_db.query.get_or_404(id)
    db.session.delete(appt_to_delete)
    db.session.commit()
    return redirect('/')




if __name__ == '__main__':
    app.run(host='localhost', port=2000, debug=True)