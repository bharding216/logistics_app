from flask import Blueprint, render_template, request, flash, redirect
from flask_login import login_required, current_user
from .models import carriers_db, users, appts_db, log_db, carriers_db
from . import db

views = Blueprint("views", __name__)

# When you want to have blueprint-specific 
# templates and static files:

#views = Blueprint(
# "views", __name__, 
# template_folder='templates',
# static_folder='static'
# )

#--------------------------------------------------------------------
#--------------------------------------------------------------------


@views.route('/', methods=['GET', 'POST'])
@login_required
def index():
    # If the user creates a new appointment:
    if request.method == 'POST':

        carrier_name = request.form['carrier']
        requested_volume = request.form['volume']
        material_name = request.form['material']
        pickup_date_input = request.form['pickup_date']
        pickup_time_input = request.form['pickup_time']
        PO_number = request.form['PO_number']
        
        new_appt = appts_db(
            carrier=carrier_name, 
            volume=requested_volume,
            material=material_name, 
            pickup_date=pickup_date_input, 
            pickup_time=pickup_time_input, 
            PO_number=PO_number
        )
        
        create_new_log = log_db(
            action="Created",
            carrier=carrier_name, 
            volume=requested_volume,
            material=material_name, 
            pickup_date=pickup_date_input, 
            pickup_time=pickup_time_input, 
            PO_number=PO_number
        )

        db.session.add_all([new_appt, create_new_log])
        db.session.commit()
        return redirect('/')
    
    # If the user is NOT creating a new appointment and is just
    # requesting data from the server ("GET"):
    else:
        search_material = request.args.getlist('material_filter')
        if not request.args.get('start_date_filter'):
            # If no start-date was selected, then:
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
        
        # If the user wants to see the appointments for all carriers
        if request.args.get('carrier') == 'all':
            #then don't filter the results by carrier name
            appts = appts_db.query.filter(appts_db.material.in_(search_material)). \
                filter(appts_db.pickup_date.between(search_date_start, search_date_end)). \
                filter(appts_db.pickup_time.between(search_time_start, search_time_end)). \
                order_by(appts_db.pickup_date).all()
        # If you want to filter by a specific carrier
        else:
            search_carrier = request.args.get('carrier')
            appts = appts_db.query.filter(appts_db.material.in_(search_material)) \
                .filter(appts_db.pickup_date.between(search_date_start, search_date_end)) \
                .filter(appts_db.pickup_time.between(search_time_start, search_time_end)) \
                .filter(appts_db.carrier == search_carrier) \
                .order_by(appts_db.pickup_date).all()

        #to generate the carriers within the dropdown list
        carriers = carriers_db.query.order_by(carriers_db.carrier_name).all()

        return render_template('index.html', 
            appts=appts, 
            carriers=carriers, 
            user=current_user)


#--------------------------------------------------------------------
#--------------------------------------------------------------------


@views.route('/history', methods=['GET'])
@login_required
def history():
    if not request.args.get('log'):
        query_limit = "10"
    else:
        query_limit = request.args.get('log')

    log = log_db.query.order_by(log_db.id.desc()).limit(query_limit).all()
    return render_template('history.html', log=log, query_limit=query_limit, user=current_user)


#--------------------------------------------------------------------
#--------------------------------------------------------------------


@views.route('/create', methods=['GET', 'POST'])
@login_required
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
        return redirect('/', user=current_user)

    else:
        #this query variable is passed to the 'create.html' page where
        #it is rendered. 
        carriers = carriers_db.query.order_by(carriers_db.carrier_name).all()
        return render_template('create.html', carriers=carriers, user=current_user)


#--------------------------------------------------------------------
#--------------------------------------------------------------------


@views.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    appt = appts_db.query.get_or_404(id)

    if request.method == 'POST':

        update_new_log_old = log_db(
            action="Updated - Old",
            carrier=appt.carrier,
            volume=appt.volume,
            material=appt.material,
            pickup_date=appt.pickup_date,
            pickup_time=appt.pickup_time, 
            PO_number=appt.PO_number
        )

        appt.carrier = request.form['carrier']
        appt.volume = request.form['volume_update']
        appt.material = request.form['material_update']
        appt.pickup_date = request.form['pickup_date']
        appt.pickup_time = request.form['pickup_time']
        appt.PO_number = request.form['PO_number_update']

        update_new_log_new = log_db(
            action="Updated - New",
            carrier=request.form['carrier'],
            volume=request.form['volume_update'],
            material=request.form['material_update'],
            pickup_date=request.form['pickup_date'],
            pickup_time=request.form['pickup_time'], 
            PO_number=request.form['PO_number_update']
        )

        db.session.add_all([update_new_log_old, update_new_log_new])
        db.session.commit()
        return redirect('/')
    
    else:
        carriers = carriers_db.query.order_by(carriers_db.carrier_name).all()
        return render_template('update.html', appt=appt, carriers=carriers, user=current_user)


#--------------------------------------------------------------------
#--------------------------------------------------------------------


@views.route('/delete/<int:id>', methods=['GET', 'DELETE', 'POST'])
@login_required
def delete(id):
    appt_to_delete = appts_db.query.get_or_404(id)

    delete_new_log = log_db(
        action="Deleted",
        carrier=appt_to_delete.carrier,
        volume=appt_to_delete.volume,
        material=appt_to_delete.material,
        pickup_date=appt_to_delete.pickup_date,
        pickup_time=appt_to_delete.pickup_time, 
        PO_number=appt_to_delete.PO_number
    )

    db.session.add(delete_new_log)
    db.session.delete(appt_to_delete)
    db.session.commit()
    return redirect('/')

# FROM THE USERS PRACTICE APP:

#@views.route("delete-appt/<int:id>")
#@login_required
#def delete_appt(id):
#   appt_to_delete = appts_db.query.filter_by(id=id).first()

#   if not appt_to_delete:
#       flash("appt does not exist.", category="error")
#   elif current_user.id != appt_to_delete.id:
#       flash("you do not have permission to delete this appt.", category="error")
#   else:
#       db.session.delete(appt_to_delete)
#       db.session.commit()
#       flash("appt deleted", category="success")
#   return redirect(url_for('views.home'))



#--------------------------------------------------------------------
#--------------------------------------------------------------------


@views.route('/new_carrier', methods=['GET', 'POST'])
@login_required
def new_carrier():
    if request.method == 'POST':
        carrier = request.form['carrier_name']
        phone = request.form['carrier_phone']
        
        new_carrier = carriers_db(carrier_name=carrier, phone_number=phone)
        
        db.session.add(new_carrier)
        db.session.commit()
        return redirect('/create')

    else:
        return render_template('new_carrier.html', user=current_user)


#--------------------------------------------------------------------
#--------------------------------------------------------------------


