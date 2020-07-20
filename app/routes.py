from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, \
    ResetPasswordRequestForm, ResetPasswordForm, MessageForm, InviteForm, \
    AnnouncementForm
from app.models import User, Company, Message, Notification, Timezone
from datetime import datetime, timedelta, time

import os
from flask import send_from_directory
from app.email import send_password_reset_email, send_confirm_email, \
    send_invite_email, send_all_email, send_lunch_invite_email

@app.route('/lunch')
@login_required
def lunch():
    if current_user.get_task_in_progress('lunch'):
        flash('An lunch task is currently in progress', category='warning')
    else:
        current_user.launch_task('lunch',
            'Searching for your Lunch buddies...', 100)
        db.session.commit()
    return redirect(url_for('user', username=current_user.username))

@app.route('/notifications')
@login_required
def notifications():
    since = request.args.get('since', 0.0, type=float)
    notifications = current_user.notifications.filter(
        Notification.timestamp > since).order_by(Notification.timestamp.asc())
    return jsonify([{
        'name': n.name,
        'data': n.get_data(),
        'timestamp': n.timestamp
    } for n in notifications])

@app.route('/messages')
@login_required
def messages():
    current_user.last_message_read_time = datetime.utcnow()
    current_user.add_notification('unread_message_count', 0)
    db.session.commit()
    page = request.args.get('page', 1, type=int)
    messages = current_user.messages_received.order_by(
        Message.timestamp.desc()).paginate(
            page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('messages', page=messages.next_num) \
        if messages.has_next else None
    prev_url = url_for('messages', page=messages.prev_num) \
        if messages.has_prev else None
    return render_template('messages.html', messages=messages.items,
        next_url=next_url, prev_url=prev_url, refresh=app.config['PAGE_REFRESH'])

@app.route('/send_message/<recipient>', methods=['GET', 'POST'])
@login_required
def send_message(recipient):
    user = User.query.filter_by(username=recipient).first_or_404()
    form = MessageForm()
    if form.validate_on_submit():
        msg = Message(author=current_user, recipient=user,
                      body=form.message.data)
        db.session.add(msg)
        user.add_notification('unread_message_count', user.new_messages())
        db.session.commit()
        flash('Your message has been sent.', category='success')
        return redirect(url_for('user', username=recipient))
    return render_template('send_message.html', title='Send Message',
        form=form, recipient=recipient, refresh=app.config['PAGE_REFRESH'])

@app.route('/user/<username>/popup')
@login_required
def user_popup(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user_popup.html', user=user)

@app.route('/confirm_email/<token>')
def confirm_email(token):
    user = User.verify_confirm_email_token(token)
    if user:
        designation = user.email.split("@")[1].split(".")[-2].upper()
        co = Company.query.filter_by(name=designation).first()
        if not co:
            co = Company(name=designation)
            db.session.add(co)
            db.session.commit() # we need to commit before using co.id
        user.company_id = co.id
        user.confirmed = True
        db.session.add(user)
        db.session.commit()
        flash('Valid token. You may login now.', category='success')
        return redirect(url_for('login'))
    flash('Unable to confirm your email! Please double check your link!',
            category='danger')
    return redirect(url_for('login'))

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        # once we set the password, lets confirm also the/for old users
        designation = user.email.split("@")[1].split(".")[-2].upper()
        co = Company.query.filter_by(name=designation).first()
        if not co:
            co = Company(name=designation)
            db.session.add(co)
            db.session.commit() # we need to commit before using co.id
        user.company_id = co.id
        user.confirmed = True
        db.session.add(user)
        db.session.commit()
        flash('Your password has been reset.', category='success')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for instructions on how to reset your password!',
                category='warning')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)

@app.route('/tools/cleanup')
def tools_cleanup_non_active_users_msgs():
    now = datetime.utcnow()
    weeks_ago = now - timedelta(weeks=app.config['IDLEUSER_LIFETIME_WEEKS'])
    oldusers = User.query.filter(User.last_seen < weeks_ago).all()
    for user in oldusers:
        notices = user.notifications
        for notice in notices: db.session.delete(notice)
        tasks = user.tasks
        for task in tasks: db.session.delete(task)
        db.session.delete(user)
    msgs = Message.query.filter(Message.timestamp < weeks_ago).all()
    for msg in msgs: db.session.delete(msg)
    db.session.commit()
    # TODO: do some (internal) logging
    return redirect(url_for('login'))

@app.route('/tools/load/users')
def tools_load_users_to_redis():
    coList = Company.query.all()
    for co in coList:
        for hour in range(1,24):
            tmin = time(hour=hour)
            tmax = time(hour=hour, minute=59)
            coUserList = User.query.filter(User.company_id == co.id,
                User.lunch_time >= tmin, User.lunch_time <= tmax,
                User.confirmed == True, User.invite_me == True).all()
            for user in coUserList:
                hash = co.name + '=H%02d' % hour
                if user.site: hash += '=' + user.site
                if user.canteen: hash += '=' + user.canteen
                app.redis.sadd("NewSuperHash", hash)
                app.redis.sadd(hash, user.id)
    return redirect(url_for('login'))

@app.route('/tools/find/lunch')
def tools_find_users_for_lunch():
    for hash in app.redis.smembers("NewSuperHash"):
        while True:
            pair = app.redis.spop(hash, 2)
            # no point to send a lunch invite if there are no pairs
            if len(pair) == 1: app.redis.sadd(hash, pair.pop())
            if not pair: break
            send_lunch_invite_email(pair)
    return redirect(url_for('login'))

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                    'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        current_user.topics = form.topics.data
        current_user.lunch_time = form.lunch_time.data
        current_user.invite_me = form.invite_me.data
        current_user.site = form.site.data.title()
        current_user.canteen = form.canteen.data.title()
        db.session.commit()
        flash('Your changes have been saved.', category='success')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
        form.topics.data = current_user.topics
        form.lunch_time.data = current_user.lunch_time
        form.invite_me.data = current_user.invite_me
        if current_user.site: form.site.data = current_user.site.title()
        if current_user.canteen: form.canteen.data = current_user.canteen.title()
    return render_template('edit_profile.html', title='Edit Profile',
        form=form, refresh=app.config['PAGE_REFRESH'])

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user,
        refresh=app.config['PAGE_REFRESH'])

@app.route('/register/<parent>', methods=['GET', 'POST'])
def register(parent):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data.lower())
        user.set_password(form.password.data)
        user.lunch_time = form.lunch_time.data
        user.site = form.site.data.title()
        user.canteen = form.canteen.data.title()
        user.confirmed = False
        master = User.query.filter_by(username=parent).first()
        if master: user.followed.append(master) # yes, just an ugly hack
        db.session.add(user)
        db.session.commit()
        send_confirm_email(user)
        flash('Please check your email and confirm that you own it!',
                category='warning')
        return redirect(url_for('login'))
    elif request.method == 'GET':
        form.invite_me.data = True
        form.lunch_time.data = time(hour=11, minute=45)
    return render_template('register.html', title='Register', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', category='danger')
            return redirect(url_for('login'))
        if not user.confirmed:
            send_confirm_email(user)
            flash('Please check your email and confirm that you own it!',
                    category='warning')
            return redirect(url_for('login'))
        tz = Timezone.query.filter_by(name=form.timezone.data).first()
        if not tz:
            tz = Timezone(name=form.timezone.data)
            db.session.add(tz)
            db.session.commit() # we need to commit before using tz.id
        user.tz_id = tz.id
        db.session.add(user)
        db.session.commit()
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form, tzcode=True)

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = InviteForm()
    if form.validate_on_submit():
        # reused from Company detection, git grep designation to find it
        designation = current_user.email.split("@")[1].split(".")[-2].upper()
        to_email = form.email.data.lower()
        if designation in to_email.upper() or current_user.is_super:
            to_name = form.firstname.data.capitalize()
            message = " ".join(form.message.data.split()) # flat 1 liner
            send_invite_email(current_user, to_name, to_email, message)
            flash('Email invitation sent to '+ to_name, category='success')
        else:
            flash('Sorry, you may send email invites Only Inside Your Company!',
                    category='warning')
    return render_template('index.html',
        title=Company.query.get(current_user.company_id).name, form=form,
        refresh=app.config['PAGE_REFRESH'])

@app.route('/explore')
@login_required
def explore():
    your_company = Company.query.get(current_user.company_id).name
    your_site = current_user.site
    if current_user.is_admin: your_site = "All"
    if current_user.is_super:
        your_company = "ALL"
        your_site = "All"
    filter = { 'company_id': current_user.company_id, 'site': current_user.site }
    if current_user.is_admin: filter = { 'company_id': current_user.company_id }
    if current_user.is_super: filter = {}
    page = request.args.get('page', 1, type=int)
    users = User.query.filter_by(**filter).paginate(page,
        app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('explore', page=users.next_num) \
        if users.has_next else None
    prev_url = url_for('explore', page=users.prev_num) \
        if users.has_prev else None
    return render_template('explore.html',
        your_company=your_company, your_site=your_site, users=users.items,
            next_url=next_url, prev_url=prev_url,
            refresh=app.config['PAGE_REFRESH'])

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if not current_user.is_admin and not current_user.is_super:
        return redirect(url_for('index'))
    form = AnnouncementForm()
    if form.validate_on_submit():
        message = " ".join(form.message.data.split()) # flat 1 liner
        send_all_email(current_user, form.subject.data, message)
        flash('Email announcement sent to your colleagues.', category='success')
    return render_template('admin.html', form=form,
        refresh=app.config['PAGE_REFRESH'])

@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username), category='danger')
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!', category='warning')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are now following {}!'.format(username), category='success')
    return redirect(url_for('user', username=username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username), category='danger')
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!', category='warning')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following anymore {}.'.format(username),
            category='success')
    return redirect(url_for('user', username=username))
