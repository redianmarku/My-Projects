from flask import render_template, url_for, flash, redirect, request, Blueprint, abort
from flask_login import login_user, current_user, logout_user, login_required
from app import db, bcrypt, app, mail
from app.models import Perdorues, Postim
from app.forms import FormRegjistrimi, FormHyrje, Postim_new, ProfileForm, RequestResetForm	, ResetPasswordForm
from app.utils import save_picture, save_post_picture
from flask_mail import Message



@app.route("/")
def index():
	current = current_user
	return render_template("index.html")

@app.route("/regjistrohu", methods=['GET','POST'])
def regjistrohu():
	form = FormRegjistrimi()
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf8')
		perdorues = Perdorues(emri_perdoruesit=form.emri_perdoruesit.data, email=form.email.data, password=hashed_password)
		db.session.add(perdorues)
		db.session.commit()
		login_user(perdorues)
		flash('Adresa u krijua! Miresevini ne Daily Code! Provoni te krijoni ndonje postim.', 'success')
		return redirect(url_for('postime'))
	return render_template('regjistrohu.html', title='Regjistrohu', form=form)


@app.route("/hyr",  methods=['GET','POST'])
def hyr():
	form = FormHyrje()
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	if form.validate_on_submit():
		user = Perdorues.query.filter_by(email=form.email.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user)
			current = current_user.emri_perdoruesit
			flash('Miresevini ' + current + ' !', 'success')
			return redirect(url_for('postime'))
		else:
			flash('Nuk munda te aksesoja adresen tende. Ju lumtem kontrolloni email ose fjalkalimin!', 'danger')
	return render_template('hyr.html', title='Hyr', form=form)


@app.route("/dil")
@login_required
def dil():
	logout_user()
	return redirect(url_for('hyr'))


@app.route("/rreth")
def rreth():
	return render_template('rreth.html')


@app.route("/profili", methods=['GET', 'POST'])
@login_required
def profili():
	form = ProfileForm()
	if form.validate_on_submit():
			if form.foto.data:
				profile_pic = save_picture(form.foto.data)
				current_user.image_file = profile_pic
			current_user.emri_perdoruesit = form.emri_perdoruesit.data
			current_user.email = form.email.data
			db.session.commit()
			flash('Profili juaj u perditsua', 'success')
			return redirect(url_for('profili'))
	elif request.method == 'GET':
		form.emri_perdoruesit.data = current_user.emri_perdoruesit
		form.email.data = current_user.email
	image_loc = url_for('static', filename='fotot/' + current_user.image_file)
	return render_template('profili.html', title='Profili',image_loc=image_loc, form=form)


@app.route("/postime")
@login_required
def postime():
	img_loc = url_for('static', filename='/fotot')
	page = request.args.get('page', 1, type=int)
	postime = Postim.query.order_by(Postim.data_postimit.desc()).paginate(page=page, per_page=5)
	return render_template('postime.html', title='Postimet',posts=postime )


@app.route("/krijo_postim", methods=['GET','POST'])
@login_required
def krijo_postim():
	form = Postim_new()
	if form.validate_on_submit():
		if form.imazhi.data:
			post_image = save_post_picture(form.imazhi.data) 
		else:
			post_image = 'default1.png'
		postim = Postim(titull = form.titulli.data, permbajtja = form.permbajtja.data, imazhi=post_image,  autori= current_user)
		db.session.add(postim)
		db.session.commit()
		flash('Postimi juaj u krijua!', 'success')
		return redirect(url_for('postime'))
	return render_template('postim_new.html', title='Posim i ri', form=form, legend='Postim i ri')



@app.route("/postim_detail/<int:post_id>")
@login_required
def postim_detail(post_id):
	postim = Postim.query.get_or_404(post_id)
	return render_template("postim_detail.html", title='Detaje', postim=postim)


@app.route("/postim_detail/<int:post_id>/perditso", methods=['GET','POST'])
@login_required
def perditso(post_id):
	post = Postim.query.get_or_404(post_id)
	if post.autori != current_user:
		abort(403)
	form = Postim_new()
	if request.method == 'GET':
		form.titulli.data = post.titull 
		form.permbajtja.data = post.permbajtja
		form.imazhi.data = post.imazhi
	elif form.validate_on_submit():
		post.titull = form.titulli.data
		post.permbajtja = form.permbajtja.data
		if form.imazhi.data:
			post_image = save_post_picture(form.imazhi.data)
			post.imazhi = post_image
		db.session.commit()
		flash('Postimi juaj u perditsua!', 'success')
		return redirect(url_for('postim_detail', post_id=post.id))
	return render_template('perditso.html', title='Perditso', form=form)


@app.route("/postim_detail/<int:post_id>/fshij", methods=['POST'])
@login_required
def fshij(post_id):
	post = Postim.query.get_or_404(post_id)
	if post.autori != current_user:
		abort(403)
	db.session.delete(post)
	db.session.commit()
	return redirect(url_for('postime'))		


@app.route("/perdorues/<string:emri_perdoruesit>")
@login_required
def postimet_e_perdoruesit(emri_perdoruesit):
	page = request.args.get('page', 1, type=int)
	perdorues = Perdorues.query.filter_by(emri_perdoruesit=emri_perdoruesit).first_or_404()
	postime = Postim.query.filter_by(autori=perdorues).order_by(Postim.data_postimit.desc()).paginate(page=page, per_page=5)
	return render_template('postimet_e_perdoruesit.html', title='Postimet',posts=postime, perdorues=perdorues )



def send_reset_email(user):
	token = user.get_reset_token()
	msg = Message('Ndrysho Fjalkalimin',
				  sender='RedianMarku@info.com',
				  recipients=[user.email])
	msg.body = f'''Per te ndryshuar fjalkalimin tuaj klikoni ne linkun poshte:
{url_for('reset_token', token=token, _external=True)}

Nese ju nuk e keni bere kete kerkese per te ndryshuar fjalkalimin, ju lutem shperfilleni kete email.


'''
	msg.html = render_template('undefined-llq1tunbu9h.html', token=token)
	mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
	if current_user.is_authenticated:
		return redirect(url_for('postime'))
	form = RequestResetForm()
	if form.validate_on_submit():
		user = Perdorues.query.filter_by(email=form.email.data).first()
		send_reset_email(user)
		flash('Nje email verifikimi u dergua. Ju lutem kontrolloni inboxin tuaj!', 'info')
		return redirect(url_for('hyr'))
	return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
	if current_user.is_authenticated:
		return redirect(url_for('postime'))
	user = Perdorues.verify_reset_token(token)
	if user is None:
		flash('Ky kod verifikimi ka skaduar ose nuk eshte i sakte!', 'warning')
		return redirect(url_for('reset_request'))
	form = ResetPasswordForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user.password = hashed_password
		db.session.commit()
		flash('Fjalkalimi juaj u ndryshua! ', 'success')
		return redirect(url_for('hyr'))
	return render_template('reset_token.html', title='Reset Password', form=form)



@app.errorhandler(404)
def error_404(error):
	return render_template('errors/404.html'), 404


@app.errorhandler(403)
def error_403(error):
	return render_template('errors/403.html'), 403


@app.errorhandler(500)
def error_500(error):
	return render_template('errors/500.html'), 500


@app.errorhandler(401)
def error_401(error):
	return render_template('errors/401.html'), 401