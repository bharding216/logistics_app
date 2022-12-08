from flask import Blueprint, render_template, request, redirect, flash, session
from flask_login import login_required, current_user
from sqlalchemy import func, or_, and_
from .models import carriers_db, appts_db, log_db, carriers_db
from . import db, mail
from flask_mail import Message
import datetime

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


@views.route('/')
@login_required
def index():

    search_material = request.args.getlist('material_filter')
    
    if request.args.get('start_date_filter') is None:
        start_date = datetime.datetime.now().strftime("%Y-%m-%d")
    else:
        start_date = request.args.get('start_date_filter')

    if request.args.get('end_date_filter') is None:
        end_date = datetime.datetime.now().strftime("%Y-%m-%d")
    else:
        end_date = request.args.get('end_date_filter')

    if request.args.get('start_time_filter') is None:
        start_time = '00:00'
    else:
        start_time = request.args.get('start_time_filter')

    if request.args.get('end_time_filter') is None:
        end_time = '23:59'
    else:
        end_time = request.args.get('end_time_filter')

    # Subquery to match the status requested. 
    status_selection = request.args.get('status')
    if status_selection == 'All':
        status_query = db.session.query(appts_db.id).subquery()
    else:
        status_query = db.session.query(appts_db.id) \
            .filter(appts_db.status == status_selection).subquery()
        
    # Subquery to match the carrier requested.
    carrier_selection = request.args.get('carrier')
    if carrier_selection == 'All':
        carrier_query = db.session.query(appts_db.id).subquery()
    else:
        carrier_query = db.session.query(appts_db.id) \
            .filter(appts_db.carrier == carrier_selection).subquery()

    appts = db.session.query(appts_db) \
        .filter(appts_db.id.in_(status_query)) \
        .filter(appts_db.id.in_(carrier_query)) \
        .filter(appts_db.material.in_(search_material)) \
        .filter(appts_db.pickup_date.between(start_date, end_date)) \
        .filter(appts_db.pickup_time.between(start_time, end_time)) \
        .order_by(appts_db.pickup_date, appts_db.pickup_time).all()     

  
    # To generate the carriers within the dropdown list
    carriers = carriers_db.query.order_by(carriers_db.carrier_name).all()

    ############################################################################
    # Sum the queried volumes by product.
    # And count the number of trucks.
    hcl_volumeList = []
    hcl_load_counter = 0
    for appt in appts:
        if appt.material == '36% HCl' or \
        appt.material == '32% HCl' or \
        appt.material == '15% HCl':
            hcl_volumeList.append(appt.volume)
            hcl_load_counter = hcl_load_counter + 1
    hcl_gallons = (sum(hcl_volumeList))/1000
    hcl_load_total_count = hcl_load_counter

    caustic_volumeList = []
    caustic_load_counter = 0
    for appt in appts:
        if appt.material == '50% Caustic' or \
        appt.material == '32% Caustic' or \
        appt.material == '30% Caustic' or \
        appt.material == '25% Caustic' or \
        appt.material == '20% Caustic':
            caustic_volumeList.append(appt.volume)
            caustic_load_counter = caustic_load_counter + 1
    caustic_gallons = (sum(caustic_volumeList))/1000
    caustic_load_total_count = caustic_load_counter

    bleach_volumeList = []
    bleach_load_counter = 0
    for appt in appts:
        if appt.material == '12.5% Bleach' or \
        appt.material == '10% Bleach' or \
        appt.material == '14%+ Bleach':
            bleach_volumeList.append(appt.volume)
            bleach_load_counter = bleach_load_counter + 1
    bleach_gallons = (sum(bleach_volumeList))/1000
    bleach_load_total_count = bleach_load_counter

    ############################################################################


    return render_template(
        'index.html', 
        appts=appts, 
        carriers=carriers, 
        carrier_selection=carrier_selection,
        status_selection=status_selection,
        user=current_user,
        hcl_gallons=hcl_gallons,
        hcl_load_total_count=hcl_load_total_count,
        caustic_gallons=caustic_gallons,
        caustic_load_total_count=caustic_load_total_count,
        bleach_gallons=bleach_gallons,
        bleach_load_total_count=bleach_load_total_count,
        start_date=start_date,
        end_date=end_date,
        search_material=search_material,
        start_time=start_time,
        end_time=end_time
    )


#--------------------------------------------------------------------
#--------------------------------------------------------------------


@views.route('/history', methods=['GET'])
@login_required
def history():
    if request.args.get('number_of_records') is None:
        query_limit = "10"
    else:
        query_limit = request.args.get('number_of_records')

    if request.args.get('action') is None:
        action_choice = 'Created'
    else:
        action_choice = request.args.get('action')

    log_list = db.session.query(log_db) \
        .filter(log_db.action == action_choice) \
        .order_by(log_db.id.desc()) \
        .limit(query_limit).all()

    return render_template(
        'history.html', 
        query_limit=query_limit, 
        user=current_user,
        action_choice=action_choice,
        log_list=log_list
    )


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
        status = 'Scheduled'
        notes = request.form['notes']


        if 'HCl' in material_name:
            category = 'HCl'
        if 'Caustic' in material_name:
            category = 'Caustic'
        if 'Bleach' in material_name:
            category = 'Bleach'


        # Try to find an appointment in that time slot.
        duplicate_appt = appts_db.query.filter(and_(
            appts_db.material.contains(category),
            appts_db.pickup_date == pickup_date_input,
            appts_db.pickup_time == pickup_time_input
            )).first()
        
        if duplicate_appt is None:

            new_appt = appts_db(
                carrier=carrier_name, 
                volume=requested_volume,
                material=material_name, 
                pickup_date=pickup_date_input, 
                pickup_time=pickup_time_input, 
                PO_number=PO_number,
                status=status,
                notes=notes
            )

            create_new_log = log_db(
                action="Created",
                carrier=carrier_name, 
                volume=requested_volume,
                material=material_name, 
                pickup_date=pickup_date_input, 
                pickup_time=pickup_time_input, 
                PO_number=PO_number,
                modified_by=current_user.username
            )


            db.session.add_all([new_appt, create_new_log])
            db.session.commit()
            flash('Your appointment was successfully created!', category='success')
            return redirect('/')
        
        
        else:
            flash('This time slot is already taken. Please check the schedule and try again.', category='error')
            carriers = carriers_db.query.order_by(carriers_db.carrier_name).all()
            return render_template('create.html', carriers=carriers, user=current_user)
    
        

    else:
        carriers = carriers_db.query.order_by(carriers_db.carrier_name).all()
        # 'carriers' is passed to the 'create.html' page where it is rendered. 
        return render_template('create.html', carriers=carriers, user=current_user)


#--------------------------------------------------------------------
#--------------------------------------------------------------------


@views.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    appt = appts_db.query.get_or_404(id)

    if request.method == 'POST' :

        # If the user is just marking the appt as "Completed",
        # then just update the appt list and NOT the History log.
        # This is done to limit the number of nuisance entries 
        # made to the history log. 
        if request.form['status'] == "Completed":

            appt.carrier = request.form['carrier']
            appt.volume = request.form['volume_update']
            appt.material = request.form['material_update']
            appt.pickup_date = request.form['pickup_date']
            appt.pickup_time = request.form['pickup_time']
            appt.PO_number = request.form['PO_number_update']
            appt.status = request.form['status']
            appt.notes = request.form['notes']

            db.session.commit()
            flash('Appointment was successfully marked as "completed".', category='success')
            return redirect('/')
    
        # Else, if user is doing a normal update, then update
        # the appt list AND add the change to the History log:
        else:
            # Record the ORIGINAL appt data before the update:
            update_new_log_old = log_db(
                action="Updated - Old",
                carrier=appt.carrier,
                volume=appt.volume,
                material=appt.material,
                pickup_date=appt.pickup_date,
                pickup_time=appt.pickup_time, 
                PO_number=appt.PO_number,
                notes=appt.notes,
                modified_by=current_user.username
            )

            # To get the category of the product for the new appointment
            if 'HCl' in request.form['material_update']:
                category = 'HCl'
            if 'Caustic' in request.form['material_update']:
                category = 'Caustic'
            if 'Bleach' in request.form['material_update']:
                category = 'Bleach'

            duplicate_appt = appts_db.query.filter(and_(
                appts_db.material.contains(category),
                appts_db.pickup_date == request.form['pickup_date'],
                appts_db.pickup_time == request.form['pickup_time']
                )).first()
            
            if duplicate_appt is None or appt.id == duplicate_appt.id:

                # Collect NEW appt data and modify 'appt':
                appt.carrier = request.form['carrier']
                appt.volume = request.form['volume_update']
                appt.material = request.form['material_update']
                appt.pickup_date = request.form['pickup_date']
                appt.pickup_time = request.form['pickup_time']
                appt.PO_number = request.form['PO_number_update']
                appt.status = request.form['status']
                appt.notes = request.form['notes']

                update_new_log_new = log_db(
                    action="Updated - New",
                    carrier=request.form['carrier'],
                    volume=request.form['volume_update'],
                    material=request.form['material_update'],
                    pickup_date=request.form['pickup_date'],
                    pickup_time=request.form['pickup_time'], 
                    PO_number=request.form['PO_number_update'],
                    notes=request.form['notes'],
                    modified_by=current_user.username
                )

                db.session.add_all([update_new_log_old, update_new_log_new])
                db.session.commit()
                flash('Your appointment was successfully updated!', category='success')
                return redirect('/')
            
            else:
                flash('This time slot is already taken. Please check the schedule and try again.', category='error')
                # To generate the dropdown list options:
                carriers = carriers_db.query.order_by(carriers_db.carrier_name).all()
                status_list = appts_db.query.with_entities(appts_db.status).distinct().all()

                return render_template('update.html', appt=appt, carriers=carriers, 
                    user=current_user, status_list=status_list)
        
            

    # Else, the user is just looking at the Update page:
    else:
        # To generate the dropdown list options:
        carriers = carriers_db.query.order_by(carriers_db.carrier_name).all()
        status_list = appts_db.query.with_entities(appts_db.status).distinct().all()

        return render_template('update.html', appt=appt, carriers=carriers, 
            user=current_user, status_list=status_list)


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
        PO_number=appt_to_delete.PO_number,
        modified_by=current_user.username
    )

    db.session.add(delete_new_log)
    db.session.delete(appt_to_delete)
    db.session.commit()
    return redirect('/')



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



    




#--------------------------------------------------------------------
#--------------------------------------------------------------------

