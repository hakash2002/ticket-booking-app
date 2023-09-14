from flask import Flask, abort
from flask import render_template
from flask import request
from flask import redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import matplotlib.pyplot as plt
from flask_bcrypt import Bcrypt
from application.database import db
from flask_login import login_user, logout_user, current_user, login_required
from flask import current_app as app
from application.models import User , Venue, Admin, Show
from application.models import Userbooking,Rating

bcrypt = Bcrypt(app)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        usrname = request.form.get('userid')
        pwd = request.form.get('password')
        user = User.query.filter_by(id=usrname).first()
        print(User.query.all())
        if user is not None and bcrypt.check_password_hash(user.password, pwd):
            login_user(user)
            path = "/"+usrname
            print(current_user)
            return redirect(path)
        else:
            error = "Invalid credentials"
    return render_template('loginpage.html', error=error)


@app.route('/create', methods=['GET', 'POST'])
def create():
    error = None
    if request.method == 'GET':
        return render_template("newuser.html")
    if request.method == 'POST':
        usrid = request.form.get('userid')
        usr = User.query.filter_by(id=usrid).first()
        usrname = request.form.get('username')
        pwd = request.form.get('password')
        if usr:
            return render_template("newuser.html", error="UserID already exists")
        else:
            hashed_pwd = bcrypt.generate_password_hash(pwd)
            user = User(id=usrid, username=usrname, password=hashed_pwd)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            path = "/" + usrid
            return redirect(path)


@app.route('/<username>', methods=['GET', 'POST'])
@login_required
def userdash(username):
    if request.method == 'GET':
        user = User.query.filter_by(id=username).first()
        if user != None:
            venue = Venue.query.all()
            ub = Userbooking.query.all()
            dict = {}
            for i in ub:
                if i.show_no in dict.keys():
                    dict[i.show_no] += i.quantity
                else:
                    dict[i.show_no] = i.quantity

            for i in venue:
                for k in i.shows:
                    if k.show_no in dict.keys():
                        dict[k.show_no] = i.capacity - dict[k.show_no]
                    else:
                        pass

            L = []
            for i in dict.keys():
                if dict[i] == 0:
                    L.append(i)

            return render_template("userdash.html", venue=venue, user=user, L=L)
        else:
            abort(404)
    if request.method == 'POST':
        user = User.query.filter_by(id=username).first()
        L = []
        L1 = []
        dict = {}
        pref = request.form.get('pref')
        option = request.form.get('option')
        venue = Venue.query.all()
        ub = Userbooking.query.all()
        dict = {}
        for i in ub:
            if i.show_no in dict.keys():
                dict[i.show_no] += i.quantity
            else:
                dict[i.show_no] = i.quantity

        for i in venue:
            for k in i.shows:
                if k.show_no in dict.keys():
                    dict[k.show_no] = i.capacity - dict[k.show_no]
                else:
                    pass

        L2 = []
        for i in dict.keys():
            if dict[i] == 0:
                L2.append(i)

        if option == "cname":
            venue = Venue.query.filter_by(location=pref).all()
            if venue == []:
                return "No venues with such city name"
        elif option == "place":
            venue = Venue.query.filter_by(place=pref).all()
            if venue == []:
                return "No venues with such place name"
        elif option == "venue":
            venue = Venue.query.filter_by(name=pref).all()
            if venue == []:
                return "No venues with such name"
        elif option == "rating":
            try:
                msg = "Show based on Ratings"
                if float(pref) > 5:
                    return "Can't be more than 5"
                venue = Venue.query.all()
                dict1 = {}
                for v in venue:
                    for i in v.shows:
                        dict1[i.name] = i.admin_rate
                        for k in i.ratings:
                            if i.name in dict:
                                dict[i.name] = (dict[i.name] + k.rating)/2
                            else:
                                dict[i.name] = k.rating
                Lcopy = []
                L1copy = []
                for i in dict.keys():
                    if dict[i] > float(pref):
                        L.append(i)

                for i in dict1.keys():
                    if dict1[i] > float(pref):
                        Lcopy.append(i)
                show = Show.query.all()
                for i in show:
                    if i.name in dict.keys():
                        L1.append(i.venue_no)
                    if i.name in dict1.keys():
                        L1copy.append(i.venue_no)
                if dict != {}:
                    return render_template('ratepref.html', pref=pref, venue=venue, user=user, L=L, L1=L1, L2=L2, msg=msg)
                else:
                    return render_template('ratepref.html', pref=pref, venue=venue, user=user, L=Lcopy, L1=L1copy, L2=L2, msg=msg)
            except:
                return "Type proper rating between 1-5"

        elif option == "tags":
            L = []
            L1 = []
            msg = "Show based on Tags"
            venue = Venue.query.all()
            show = Show.query.all()
            for s in show:
                if pref.capitalize() in s.tags:
                    L.append(s.name)
                    L1.append(s.venue_no)
            if L == []:
                return "No shows with such tags"

            return render_template('ratepref.html', pref=pref, venue=venue, user=user, L=L, L1=L1, L2=L2, msg=msg)

        elif option == "show":
            if pref[0].isupper():
                pass
            else:
                pref = pref.capitalize()
            show = Show.query.filter_by(name=pref).all()
            if show == []:
                return "No Shows with such name"
            venue = Venue.query.all()
            return render_template('showpref.html', pref=pref, venue=venue, user=user, L2=L2)

        else:
            return "Please select any option"
        return render_template('userpreference.html', venue=venue, user=user, L2=L2)


@app.route('/<username>/updateprofile', methods=['GET', 'POST'])
@login_required
def updateuser(username):
    if request.method == 'GET':
        user = User.query.filter_by(id=username).first()
        return render_template("updateuser.html", user=user)
    if request.method == 'POST':
        user = User.query.filter_by(id=username).first()
        pwd = request.form.get('pass')
        hashed_pwd = bcrypt.generate_password_hash(pwd)
        user.password = hashed_pwd
        db.session.commit()
        path = "/"+user.id
        return redirect(path)


@app.route('/<username>/<int:venue_no>/<int:show_no>/ticketbooking', methods=['GET', 'POST'])
@login_required
def booking(username, venue_no, show_no):

    if request.method == 'GET':
        user = User.query.filter_by(id=username).all()
        venu = Venue.query.filter_by(venue_no=venue_no).all()
        show = Show.query.filter_by(show_no=show_no).all()
        if user != [] and venu != [] and show != []:
            ub = Userbooking.query.filter_by(show_no=show_no).all()
            venu = Venue.query.filter_by(venue_no=venue_no).first()
            count = 0
            for i in ub:
                count += i.quantity

            count = venu.capacity - count
            return render_template("ticketbooking.html", username=username, show_no=show_no, venue_no=venue_no, count=count)
        else:
            abort(404)
    if request.method == 'POST':
        quantity = request.form.get('numtickets')
        path = "/" + username + "/" + \
            str(venue_no) + "/" + str(show_no) + \
            "/" + str(quantity) + "/confirmbooking"
        return redirect(path)


@app.route('/<username>/<venue_no>/<show_no>/<numtickets>/confirmbooking', methods=['GET', 'POST'])
@login_required
def conbook(username, venue_no, show_no, numtickets):
    if request.method == 'GET':
        user = User.query.filter_by(id=username).first()
        show = Show.query.filter_by(show_no=show_no).first()
        venue = Venue.query.filter_by(venue_no=venue_no).first()
        if user != None and venue != None and show != None:
            total = int(numtickets) * show.price
            count = 0
            k = 0
            for i in show.ratings:
                k += i.rating
                count += 1
            if count == 0:
                avg = show.admin_rate
            else:
                avg = round(k/(count), 2)
            return render_template("bookingconfirm.html", vname=venue.name, sname=show.name, quantity=numtickets, price=show.price, total=total, avg=avg)
        else:
            abort(404)
    if request.method == 'POST':
        if 'confirm' in request.form:
            user = User.query.filter_by(id=username).first()
            ub = Userbooking(
                show_no=show_no, user_no=user.user_no, quantity=numtickets)
            db.session.add(ub)
            db.session.commit()

        elif 'cancel' in request.form:
            pass
        path = "/" + username
        return redirect(path)


@app.route('/<username>/profile', methods=['GET'])
@login_required
def userpro(username):
    if request.method == 'GET':
        user = User.query.filter_by(id=username).first()
        if user:
            duplicates = (
                Userbooking.query
                .group_by(Userbooking.user_no, Userbooking.show_no)
                .having(func.count() > 1)
                .with_entities(
                    Userbooking.user_no,
                    Userbooking.show_no,
                    func.sum(Userbooking.quantity).label('total_quantity')
                )
                .all()
            )
            for user_no, show_no, total_quantity in duplicates:
                bookings = (
                    Userbooking.query
                    .filter_by(user_no=user_no, show_no=show_no)
                    .all()
                )
                for booking in bookings[1:]:
                    db.session.delete(booking)
                bookings[0].quantity = total_quantity
                db.session.commit()

            user = User.query.filter_by(id=username).first()
            ub = Userbooking.query.filter_by(user_no=user.user_no).all()
            venue = Venue.query.all()
            show = Show.query.all()
            return render_template('userprofile.html', ub=ub, venue=venue, show=show, user=user)
        else:
            abort(404)


@app.route('/<username>/rate/<show_no>', methods=['GET', 'POST'])
@login_required
def rate(username, show_no):
    user = User.query.filter_by(id=username).first()
    show = Show.query.filter_by(show_no=show_no).first()
    if request.method == 'GET':
        if user and show:
            rate = Rating.query.filter_by(
                user_no=user.user_no, show_no=show_no).all()
            if rate:
                msg = "Already rated"
            else:
                msg = None
            return render_template('rate.html', sname=show.name, msg=msg, user=user)
        else:
            abort(404)
    if request.method == 'POST':
        rating = request.form.get('rating')
        rating = Rating(user_no=user.user_no, show_no=show_no, rating=rating)
        db.session.add(rating)
        db.session.commit()
        path = "/" + username + "/profile"
        return redirect(path)


@app.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect('/login')

# --------------------------------------------------------------------------------------


@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        usrname = request.form.get('userid')
        pwd = request.form.get('password')
        user = Admin.query.filter_by(id=usrname).first()
        if user is not None and bcrypt.check_password_hash(user.password, pwd):
            path = "admin/"+usrname
            login_user(user)
            error = None
            return redirect(path)
        error = "Invalid Credentials"
    return render_template("adminlogin.html", error=error)


@app.route('/admin/<username>', methods=['GET', 'POST'])
@login_required
def admin_dash(username):
    if request.method == "GET":
        admin = Admin.query.filter_by(id=username).first()
        if admin:
            venue = Venue.query.filter_by(admin_no=admin.admin_no).all()
            return render_template("admindash.html", username=username, venue=venue, admin=admin)
        else:
            abort(404)


@app.route('/admin/<username>/summary', methods=['GET', 'POST'])
@login_required
def summary(username):
    if request.method == 'GET':
        admin = Admin.query.filter_by(id=username).first()
        if admin:
            return render_template('summary.html', admin=admin)
        else:
            abort(404)
    if request.method == "POST":
        admin = Admin.query.filter_by(id=username).first()
        data = {}
        error = None
        error1 = True
        show = request.form.get('shows')
        shows = Show.query.filter_by(name=show).all()
        data = {}
        venue = Venue.query.all()
        ub = Userbooking.query.all()
        # Count the number of ratings for each value in the dictionary
        for i in shows:
            for k in i.ratings:
                if k.rating in data.keys():
                    data[k.rating] += 1
                else:
                    data[k.rating] = 1
        if data != {}:
            plt.bar(range(len(data)), list(data.values()), align='center')
            plt.xticks(range(len(data)), list(data.keys()))
            plt.ylabel('Number of Ratings')
            plt.xlabel('Rating')
            plt.yticks(list(range(max(data.values())+1)))
            plt.savefig('static/showrate.jpg')
        else:
            error = True

        tickets_sold = {}

        venues = Venue.query.filter(Venue.shows.any(name=show)).all()

        for venue in venues:
            bookings = Userbooking.query.join(Show).filter(
                Show.name == show, Show.venue_no == venue.venue_no).all()
            total_tickets_sold = sum(
                [booking.quantity for booking in bookings])
            tickets_sold[venue.name] = total_tickets_sold

        venues = list(tickets_sold.keys())
        num_tickets = list(tickets_sold.values())
        for i in num_tickets:
            if i > 0:
                error1 = False
                break
        if error1 == False:
            plt.bar(range(len(venues)), num_tickets, align='center')
            plt.xticks(range(len(venues)), venues)
            yticks = range(0, max(tickets_sold.values())+10, 10)
            plt.yticks(yticks)
            plt.xlabel('Venue')
            plt.ylabel('Number of Tickets Sold')
            plt.title('Tickets Sold per Venue')
            plt.savefig('static/venueticks.jpg')

        return render_template('summarypost.html', admin=admin, show=show, error=error, error1=error1)


@app.route('/admin/<username>/createvenue', methods=['GET', 'POST'])
@login_required
def createvenue(username):
    admin = Admin.query.filter_by(id=username).first()
    if request.method == "GET":
        if admin:
            return render_template("venuecreate.html", venue=[1], admin=admin, heading="Create Venue")
        else:
            abort(404)
    if request.method == "POST":
        venue_name = request.form.get('vname')
        vplace = request.form.get('vplace')
        vlocation = request.form.get('vlocation')
        vcapacity = request.form.get('vcapacity')
        venue = Venue(name=venue_name, location=vlocation,
                      place=vplace, capacity=vcapacity, admin_no=admin.admin_no)
        db.session.add(venue)
        db.session.commit()
        path = "/admin"+"/"+username
        return redirect(path)


@app.route('/admin/<username>/<venue_no>/updatevenue', methods=['GET', 'POST'])
@login_required
def updateven(username, venue_no):
    if request.method == 'GET':
        admin = Admin.query.filter_by(id=username).first()
        venue = Venue.query.filter_by(venue_no=venue_no).all()
        if venue and admin:
            return render_template('venuecreate.html', venue=venue, heading="Update Venue", admin=username)
        else:
            abort(404)
    if request.method == 'POST':
        venue = Venue.query.filter_by(venue_no=venue_no).first()
        venue.venue_name = request.form.get('vname')
        venue.place = request.form.get('vplace')
        venue.location = request.form.get('vlocation')
        venue.capacity = request.form.get('vcapacity')
        db.session.commit()
        path = "/admin"+"/"+username
        return redirect(path)


@app.route('/admin/<username>/<venue_no>/deletevenue', methods=['GET'])
@login_required
def deleteven(username, venue_no):
    if request.method == 'GET':
        venue = Venue.query.filter_by(venue_no=venue_no).first()
        admin = Admin.query.filter_by(id=username).first()
        if venue and admin:
            for i in venue.shows:
                ub = Userbooking.query.filter_by(show_no = i.show_no).first()
                if ub != None:
                    return "This venue has show bookings"
            for i in venue.shows:
                num = int(i.show_no)
                rating = Rating.query.filter_by(show_no = num).all()
                for k in rating:
                    db.session.delete(k)
                db.session.delete(i)
                db.session.commit()
                max_id = int(db.session.query(func.max(Show.show_no)).scalar())
                for i in range(num,max_id):
                    ub = Userbooking.query.filter_by(show_no=i+1).all()
                    show = Show.query.filter_by(show_no=i+1).first()
                    if ub != []:
                        for j in ub:
                            j.show_no = i
                    show.show_no = i
                    db.session.commit()
            num1 = int(venue_no)
            max_id1 = int(db.session.query(func.max(Venue.venue_no)).scalar())
            db.session.delete(venue)
            db.session.commit()
            for i in range(num1,max_id1):
                venue = Venue.query.filter_by(venue_no=i+1).first()
                for j in venue.shows:
                    j.venue_no = i
                venue.venue_no = i
                db.session.commit()
             

            path = "/admin/"+admin.id
            return redirect(path)
        else:
            abort(404)


@app.route('/admin/<username>/<venue_no>/createshow', methods=['GET', 'POST'])
@login_required
def createshow(username, venue_no):
    admin = Admin.query.filter_by(id=username).first()
    venue = Venue.query.filter_by(venue_no=venue_no).first()
    if request.method == "GET":
        if admin and venue:
            return render_template("showcreate.html", show=[1], admin=admin, heading="Create Show")
        else:
            abort(404)
    if request.method == "POST":
        show_name = request.form.get('name')
        tags = request.form.get('tags')
        start_time = request.form.get('stime')
        end_time = request.form.get('etime')
        price = request.form.get('price')
        admin_rate = request.form.get('ratings')
        show = Show(name=show_name, tags=tags, start_time=start_time,
                    end_time=end_time, price=price, admin_no=admin.admin_no, venue_no=venue.venue_no, admin_rate=admin_rate)
        db.session.add(show)
        db.session.commit()
        path = "/admin"+"/"+username
        return redirect(path)


@app.route('/admin/<username>/<show_no>/updateshow', methods=['GET', 'POST'])
@login_required
def updatshow(username, show_no):
    if request.method == 'GET':
        admin = Admin.query.filter_by(id=username).first()
        show = Show.query.filter_by(show_no=show_no).all()
        if admin and show != []:
            return render_template('showcreate.html', show=show, heading="Update Show", admin=admin)
        else:
            abort(404)
    if request.method == 'POST':
        show = Show.query.filter_by(show_no=show_no).first()
        show.name = request.form.get('name')
        show.tags = request.form.get('tags')
        show.start_time = request.form.get('stime')
        show.end_time = request.form.get('etime')
        show.price = request.form.get('price')
        show.admin_rate = request.form.get('ratings')
        db.session.commit()
        path = "/admin"+"/"+username
        return redirect(path)


@app.route('/admin/<username>/<show_no>/deleteshow', methods=['GET'])
@login_required
def deletesho(username, show_no):
    if request.method == 'GET':
        admin = Admin.query.filter_by(id=username).first()
        show = Show.query.filter_by(show_no=show_no).first()
        ub = Userbooking.query.filter_by(show_no = show_no).first()
        if show and admin:
            if ub is None:
                rating = Rating.query.filter_by(show_no=show_no).all()
                for k in rating:
                    db.session.delete(k)
                db.session.delete(show)
                db.session.commit()
                num = int(show_no)
                max_id = int(db.session.query(func.max(Show.show_no)).scalar())
                for i in range(num,max_id):
                    ub = Userbooking.query.filter_by(show_no=i+1).all()
                    show = Show.query.filter_by(show_no=i+1).first()
                    rt = Rating.query.filter_by(show_no=i+1).all()
                    if ub != []:
                        for j in ub:
                            j.show_no = i
                    if rt != []:
                        for l in rt:
                            l.show_no = i
                    show.show_no = i
                    db.session.commit()
            else:
                return "Cant delete user Has Booked this Show"
                
            path = "/admin"+"/"+admin.id
            return redirect(path)
        else:
            abort(404)


@app.route('/admin/logout', methods=['GET'])
@login_required
def admin_logout():
    logout_user()
    return redirect('/admin')
