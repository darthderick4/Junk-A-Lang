from datetime import datetime
from distutils.log import error

from flask import *
import pyrebase

from redmail import EmailSender




app = Flask(__name__)

config = {
  "apiKey": "AIzaSyAeZZoEQA0q3fqPNEHunP8-ZIIllkPh-AE",
  "authDomain": "junkshopapp-1e67d.firebaseapp.com",
  "databaseURL": "https://junkshopapp-1e67d-default-rtdb.firebaseio.com/",
  "projectId": "junkshopapp-1e67d",
  "storageBucket": "junkshopapp-1e67d.appspot.com",
  "messagingSenderId": "627034955102",
  "appId": "1:627034955102:web:f0cfea41245a6b1bdcc3cf",
  "measurementId": "G-HR4TD068ZW"
};

firebase = pyrebase.initialize_app(config)
user_admin = firebase.auth()
db = firebase.database()
storage =firebase.storage() 
names = db.child('Users').get()
# db_price= db.child('Price').child('-NBW2FEtIpOVbZNOoO4i').get()
db_price= db.child('Price').get()
db_post = db.child('Post').get()
db_report = db.child('Report').get()
db_pending = db.child('Pending_Post').get()

# data = {"Aluminum Cans":25}
# db.child('Price').child('Items').update(data)

# price_test = db.child('Price').child('Test').get()
# for price in price_test:
#   print(price.key())


# for category in db_price.each():
#   for item in category.val():
#     print(item)

# db.child('Price').push({"Aluminum Cans":25})
# data = {'item':'1'}
# for item in db_approved.each():
#   item_key = item.key()
#   db.child('Approved_Post').child(item_key).set(data)

# Post
# categories
# email
# first name
# last name

# session
app.secret_key = 'secret'
@app.route('/test')
def test():
  return render_template('test.html')

# login and logout
@app.route('/', methods = ['GET', 'POST'])
def index():
  if('user' in session):
    return redirect('dashboard')
  if request.method == 'POST':
    email = request.form.get('email')
    password = request.form.get('password')
    try:
      user_admin.sign_in_with_email_and_password(email, password)
      session['user']=email
      return redirect('/dashboard')
    except:
      flash("Invalid credentials")
      return render_template('index.html')
  return render_template('index.html')


@app.route('/reset_pass')
def reset_pass():
  pass

@app.route('/logout')
def logout():
	session.pop('user')
	return redirect('/')

# home
@app.route('/homepage', methods = ['GET', 'POST'])
def display():
  if 'user' not in session:
    return redirect('/')
  count_post = len(db_post.each())
  names = db.child('Users').get()
  
  print(f"Post Count: {count_post}\n")
  post = []
  for name in names.each():
    if "Post" in name.val():
      post.append(list(name.val()['Post'])[0])
  return render_template('homepage.html', names=names.each(), post=len(db_post.each()))


@app.route('/dashboard')
def dashboard():
  # user login check
  if 'user' not in session:
    return redirect('/')

  # counter declaration
  t_user = 0
  t_report_comment = 0
  # t_buyer = 0
  # t_seller = 0
  t_sold = 0

  # database importation
  db_post = db.child('Post').get()
  names = db.child('Users').get()
  db_report = db.child('Report').child('Reported Post').get()
  db_report_user = db.child('Report').child('Reported User').get()
  db_pending = db.child('Pending_Post').get()


  # post-pending-report count
  try:
    t_report = len(db_report.each())
  except:
    t_report = 0
  try:
    t_pending = len(db_pending.each())
  except:
    t_pending = 0
  try:
    t_post = len(db_post.each())
  except:
    t_post = 0
  try:
    t_report_comment = len(db_report_user.each())
  except:
    t_report_comment = 0

  # loop counter
  for name in names.each():
    t_user +=1
    if 'Sold_Post' in name.val():
      t_sold += 1
  
    # if name.val()['categories'] == 'Junk Buyers':
    #   t_buyer += 1
    # else:
    #   t_seller += 1
  return render_template("dashboard.html",user=session['user'],t_report=t_report,t_sold=t_sold,t_pending=t_pending,t_post=t_post,t_user=t_user,t_report_comment=t_report_comment)

# pending
@app.route('/pending', methods=['GET','POST'])
def pending_post():
  db_pending = db.child("Pending_Post").get()
  try:
    pending = db_pending.each()
    for post in pending:
      date = post.val()['date']
      date = datetime.strptime(date, '%d/%m/%y')
      db.child('Pending').child(post.key()).update({'date':date})
      print(date.strftime("%d %B %Y"))
    pending = pending.reverse()
  except:
    pending = "No Item"
# approve
  if request.method == 'POST':
    if request.form.get('approve') == 'approve':
      p_key = str(request.form.get('p_key'))
      for item in db_pending.each():
        if p_key == item.key():
          categories = item.val()['categories']
          date = item.val()['date']
          description = item.val()['description']
          email = item.val()['email']
          first_name = item.val()['firstname']
          item_id = item.val()['id']
          imageUrl = item.val()['imageUrl']
          item_categories = item.val()['itemCategories']
          last_name = item.val()['lastname']
          location = item.val()['location']
          profile = item.val()['profile']
          report = item.val()['report']
          status =item.val()['status']
          data = {'categories' : categories,'date':date,'description': description,'email':email,
          'firstname':first_name,'id':item_id,'imageUrl':imageUrl,
          'itemCategories':item_categories,'lastname':last_name,'location':location,
          'profile':profile,'report':report,'status':status}
          # print(data)
          db.child('Post').child(item.key()).set(data)
          db.child('Post').child(item.key()).update({'status':'Approved'})
          db.child('Pending_Post').child(item.key()).remove()

          # email
          # post_desc = pending.val()['description']
          # image = pending.val()['imageUrl']
          email = EmailSender(host='smtp.gmail.com',port=587,username='darthderick4@gmail.com',password='jqesvcnxjnqbekbu')
          email.send(
          subject="Post Reviewed",
          sender="noreply@gmail.com",
          receivers=[item.val()['email']],
          html="""
          <html>
          <head></head>
          <body>
          <h4>Your post has been approved by the Junk-A-Lang Admin</h4>
          <p>Post Name: {{post_desc}}</p>
          <img width="200" height="200" src="{{image}}">
          </body>
          </html>
          """,
          body_params={
          'post_desc': item.val()['description'],
          'image': item.val()['imageUrl'],
            }
            )
        # end email

          flash('Post Approved')
          
          return redirect(url_for('pending_post'))

  # if request.method == 'POST':
  #   if request.form.get('approve') == 'approve':
  #     u_mail = str(request.form.get('u_mail'))
  #     u_post_desc = str(request.form.get('u_post_desc'))
  #     u_post_date = str(request.form.get('u_post_date'))
  #     for post in pending_db.each():
  #       if u_mail == post.val()['email'] and u_post_desc == post.val()['description'] and u_post_date == post.val()['date']:
  #         try:
  #           db.child('Post').child(post.key()).update({"status": "Approved"})
  #           flash('Post Approved Successfully')
  #         except:
  #           flash('Error Approving Post')
  #         return redirect(url_for('pending_post'))

  return render_template("pending.html",user=session['user'],db_pending=db_pending)

# pending comment
@app.route('/pending_comment/<key>',methods=['GET','POST'])
def pending_comment(key):
  pending_db = db.child('Pending_Post').get()
  if request.method == 'POST':
    comment = request.form.get('comment')
    if request.form.get('submit') == 'submit':
      for pending in pending_db.each():
        if key == pending.key():
          # email
          post_desc = pending.val()['description']
          image = pending.val()['imageUrl']
          email = EmailSender(host='smtp.gmail.com',port=587,username='darthderick4@gmail.com',password='jqesvcnxjnqbekbu')
          email.send(
          subject="Post Reviewed",
          sender="noreply@gmail.com",
          receivers=[pending.val()['email']],
          html="""
          <html>
          <head></head>
          <body>
          <h4>The pending post that you have requested have been reviewed by the Junk-A-Lang admin, please edit your post based on the admin comments</h4>
          <p>Comment: {{comment}}</p>
          <p>Post Name: {{post_desc}}</p>
          <img width="200" height="200" src="{{image}}">
          </body>
          </html>
          """,
          body_params={
          'post_desc': post_desc,
          'image': image,
          'comment':comment
            }
            )
        # end email
      flash('Comment successfully sent')
  return redirect(url_for('pending_post'))

# post

@app.route('/posted', methods=['GET', 'POST'])
def posted():
  if 'user' not in session:
    return redirect('/')
  # view
  db_post = db.child('Post').get()
  posted = db_post.each()
  posted = posted.reverse()
  if request.method == 'POST':
    if request.form.get('submit')=='view':
      u_mail = str(request.form.get('u_mail'))
      u_first = str(request.form.get('u_first'))
      u_last = str(request.form.get('u_last'))
      u_desc = str(request.form.get('u_post_desc'))
      u_date = str(request.form.get('u_post_date'))
      for p in db_post.each():
        if u_first == p.val()['firstname'] and u_desc == p.val()['description']:
          print(p.val()['profile'])
          image=p.val()['imageUrl']
          profile=p.val()['profile']
          return render_template('post_details.html',email=u_mail,f_name=u_first,l_name=u_last,desc=u_desc,date=u_date,image=image,user_profile=profile)
  return render_template('posted.html',user=session,posted=db_post.each())

# report
@app.route('/reported_post')
def report_posted():
  db_report = db.child('Report').child('Reported Post').get()
  reported = db_report.each()
  reported = reported.reverse()
  # if request.method == 'POST':
  #   if request.form.get('submit')=='view':
  #     report_post=str(request.form.get('report_post'))
  #     report_comment= str(request.form.get('report_comment'))
  #     reported_by= str(request.form.get('reported_by'))
  #     report_date= str(request.form.get('report_date'))
  #     location = str(request.form.get('location'))
  #     for item in db_report.each():
  #       if report_post == item.val()['description'] and report_comment == item.val()['report'] and reported_by == item.val()['reported_by'] and report_date == item.val()['reported_date']:
  #         f_name = item.val()['firstname']
  #         l_name = item.val()['lastname']
  #         reported_name =f"{f_name} {l_name}"
  #         post_image = item.val()['imageUrl']
  #         return render_template('report_detail.html', report_post=report_post,report_comment=report_comment,reported_by=reported_by,report_date=report_date,reported_name=reported_name,post_image=post_image,location=location)
  return render_template('report_post.html',user=session['user'],db_report=db_report.each())

@app.route('/report_detail/<key>')
def report_detail(key):
  db_report = db.child('Report').child('Reported Post').get()
  reported = db_report.each()
  for post in reported:
    if key == post.key():
      key = post.key()
      post_image = post.val()['imageUrl']
      report_post = post.val()['description']
      reported_name = f"{post.val()['firstname']} {post.val()['lastname']}"
      # location = post.val()['location']
      report_comment = post.val()['report']
      report_date = post.val()['reported_date']
      reported_by = post.val()['reported_by']
      return render_template('report_detail.html',
      post_image=post_image,report_post=report_post,
      reported_name=reported_name,
      report_comment=report_comment,report_date=report_date,
      reported_by=reported_by,user=session['user'],key=key)

# user
@app.route('/user', methods=['POST','GET'])
def user():
  names = db.child('Users').get()
  if request.method == 'POST':
    if request.form.get('view'):
      return redirect(url_for('/user_details'))
  return render_template('user.html',user=session['user'],names=names.each())

# user report
@app.route('/user_report',methods=['POST','GET'])
def user_report():
  user_report_db = db.child('Report').child('Reported User').get()
  # user_db = db.child('Users').get()
  # for user_report in user_report_db.each():
  #   for user in user_db.each():
  #     if user.val()['email'] in user_report.vaL():
  #       try:
  #         times_reported = user.val()['times_report']
  #         db.child('User').child(user.key()).set({'times_reported':int(times_reported)+1})
  #       except:
  #         db.child('User').child(user.key()).set('times_reported':1)
  return render_template('user_report.html',user=session['user'],user_report=user_report_db.each())

# warning and remove comment
@app.route('/send_warning/<key>',methods=['POST','GET'])
def send_warning(key):
  user_report_db = db.child('Report').child('Reported User').get()
  post_db = db.child('Post').get()
  user_db = db.child('Users').get()

  for user_report in user_report_db.each():
    if user_report.key() == key:
      # print(user_report.key())
      # print(user_report.val())
      for user in user_db.each():
        if user.val()['email'] == user_report.val()['email']:
          # print(user.val()['email'])
          try:
            times_reported = int(user.val()['times_report'])+1
            db.child('Users').child(user.key()).set({'times_reported':times_reported})
          except:
            db.child('Users').child(user.key()).update({'times_reported':1})

  for violator in user_report_db.each():
    if key == violator.key():
      for item in post_db.each():
        if 'Comments' in item.val():
          db.child('Post').child(item.key()).child('Comments').child(key).remove()
          db.child('Report').child('Reported User').child(key).remove()
          # print('found')
          # if key in item.val():
          #   print('found')
          # print(comment.val())

          # if key in item.val()['Comments']:
          #   print('found1')
            # db.child('Post').child(item.key()).child('Comments').child(key).remove()
            
      # email
      comment = violator.val()['comment']
      email = EmailSender(host='smtp.gmail.com',port=587,username='darthderick4@gmail.com',password='jqesvcnxjnqbekbu')
      email.send(
      subject="Comment Deleted",
      sender="noreply@gmail.com",
      receivers=[violator.val()['email']],
      html="""
        <html>
        <head></head>
        <body>
        <h4>The comment that you have posted has been reported</h4>
        <p>Your comment: {{comment}}</p>
        <p>The comment that you have posted has reviewed by the Junk-A-Lang Admin and now has been removed. With such behaviour will not be tolerated
        be sure to keep the comment section friendly and respectful as possible. <b>Unwanted behaviour will lead to a deletion of account</b>.</p>
        </body>
        </html>
        """,
        body_params={
        'comment': comment
            }
            )
      # end email
      flash('Comment has been deleted')
  return redirect(url_for('user_report'))

# user detail
@app.route('/user_detail/<key>',methods=['POST','GET'])
def user_detail(key):
  user_report_db = db.child('Report').child('Reported User').get() 
  users = db.child('Users').get()
  for reported_user in user_report_db.each() :
    if key == reported_user.key():
      comment = reported_user.val()['comment']
      email = reported_user.val()['email']
      reported_name = f"{reported_user.val()['firstname']} {reported_user.val()['lastname']}"
      profile_pic = reported_user.val()['profile']
      report = reported_user.val()['report']
      reported_by = reported_user.val()['reported_by']
      report_date = reported_user.val()['reported_date']

      for user in users.each():
        if user.val()['email'] == reported_user.val()['email']:
          try:
            reported_times = reported_user.val()['times_reported']
          except:
            db.child('Users').child(user.key()).update({'times_reported':0})
            reported_times = 0
      # try:
      #   reported_times = reported_user.val()['times_reported']
      # except:
      #   for user in users.each():
      #     if user.val()['email'] == email:
      #       db.child('Users').child(user.key()).update({'times_reported':0})
      #       reported_times = reported_user.val()['times_reported']
  return render_template('user_detail.html',
  key=key,comment=comment,profile_pic=profile_pic,reported_name=reported_name,
  report=report,report_date=report_date,reported_by=reported_by,reported_times=reported_times,email=email)

# delete user report
@app.route('/user_report_del/<key>',methods=['POST','GET'])
def user_report_del(key):
  user_report_db = db.child('Report').child('Reported User').get() 
  post_db = db.child('Post').get()

  for reported_user in user_report_db.each():
    if key == reported_user.key():
      # print(reported_user.val()['comment'])
      db.child('Report').child('Reported User').child(key).remove()
      flash('Comment Deleted')
      # for item in post_db.each():
      #   if 'Comments' in item.val():
      #     if key in item.val()['Comments']:
            # print(item.val()['Comments'][key]['usermsg'])
            # db.child('Post').child(item.key()).child('Comments').child(key).remove()
            

  return redirect(url_for('user_report'))


@app.route('/user_details', methods=['GET', 'POST'])
def user_details():
  if request.method == "POST":
    fname=request.form.get('fname')
    lname=request.form.get('lname')
    user_mail=request.form.get('user_mail')
    user_category=request.form.get('user_category')
    for user in names.each():
      if fname == user.val()['firstname'] and lname == user.val()['lastname'] and user_mail == user.val()['email'] and user_category == user.val()['categories']:
        profile_picture = user.val()['profile']
  return render_template('user_details.html',fname=fname,lname=lname,user_mail=user_mail,user_category=user_category,prof_picture=profile_picture)
  

# price
@app.route('/price', methods=['POST','GET'])
def price():
  db_category = db.child('Price').child('Items').get()
  item_list = []
  # for item,value in db_category.each():
  #   for i in list(item.val().keys()):
  #     item_list.append(i)
    # item_list.append(x)
  # db_price = db.child('Price').child('-NBW2FEtIpOVbZNOoO4i').get()
  # if request.method == 'POST':
  #   if 'submit' in request.form:
  #     p_bottle = str(request.form.get('p_bottle'))
  #     c_bottle = str(request.form.get('c_bottle'))
  #     g_bottle = str(request.form.get('g_bottle'))
  #     white_paper = str(request.form.get('white_paper'))
  #     carton = str(request.form.get('carton'))
  #     m_box = str(request.form.get('m_box'))
  #     magazine = str(request.form.get('magazine'))
  #     cans = str(request.form.get('cans'))
  #     plastic = str(request.form.get('plastic'))
  #     newspaper = str(request.form.get('newspaper'))
  #     metal = str(request.form.get('metal'))
  #     cd = str(request.form.get('cd'))
  #     copper = str(request.form.get('copper'))
  #     e_waste= str(request.form.get('e_waste'))
  #     mobo = str(request.form.get('mobo'))
  #     diskette = str(request.form.get('diskette'))
  #     ink_cartridge = str(request.form.get('ink_cartridge'))
  #     price={"plastic_bottle":p_bottle,'clean_bottle':c_bottle,
  #     'glass_bottle':g_bottle,'white_paper':white_paper,
  #     'carton':carton,'cartolina':m_box,'magazine':magazine,
  #     'cans':cans,'plastic':plastic,'newspaper':newspaper,
  #     'metal':metal,'cd':cd,'copper':copper,'mobo':mobo,'e_waste':e_waste
  #     ,'diskette':diskette,'ink_cartridge':ink_cartridge}
  #     try:
  #       db.child('Price').child('-NBW2FEtIpOVbZNOoO4i').update(price)
  #       flash('Price Updated')
  #     except:
  #       flash('Error updating price')


      # email
      # for user in names.each():
      #   if user.val()['categories'] == 'Junk Buyers':
      #     email = EmailSender(host='smtp.gmail.com',port=587,username='darthderick4@gmail.com',password='jqesvcnxjnqbekbu')
      #     email.send(
      #     subject="Price list update",
      #     sender="noreply@gmail.com",
      #     receivers=[user.val()['email']],
      #     html="""
      #     <html>
      #     <head></head>
      #     <body>
      #     <h4>The Price list have been updated.</h4>
      #     <p>The price list has now been updated you can check the latest price on the Junk-A-Lang mobile app.</p>
      #     </body>
      #     </html>
      #     """)
          # end email

  #     return redirect(url_for('price'))
  # return render_template('price.html',user=session['user'],db_price=db_price.each())
      # return redirect(url_for('price'))

      # item_list = item_list
  return render_template('price.html',user=session['user'],db_category=db_category.each(),item_list=item_list)

# price update
@app.route('/price_update', methods=['GET','POST'])
def price_update():
  db_category = db.child('Price').child('Items').get()
  if request.method == 'POST':
    price = request.form.get('update')
    item_cat = request.form.get('item_cat')
    if request.form.get('submit') == 'submit':
      for category in db_category.each():
        if item_cat == category.key():
    #       for item in category.val():
            db.child('Price').child('Items').update({item_cat:price})
            flash('Price has been updated')
  return redirect(url_for('price'))

@app.route('/category_del', methods=['GET','POST'])
def category_del():
  if request.method == 'POST':
    if request.form.get('submit') == 'submit':
      item = request.form.get('item-value-cat')
      db.child('Price').child('Items').child(item).remove()
      flash('Category has been deleted')
  # db.child('Price').child(key).remove()

  return redirect(url_for('price'))

@app.route('/add_category', methods=['GET','POST'])
def add_category():
  if request.method == 'POST':
    if request.form.get('submit') == 'submit':
      category_add = request.form.get('category-add')
      price_add = request.form.get('price-add')
      data = {category_add:price_add}
      print(data)
      db.child('Price').child('Items').update(data)
      flash('Category added')
    return redirect(url_for('price'))


# delete section
# pending
@app.route('/pending_del/<key>', methods=['GET','POST'])
def pending_del(key):
  pending_db = db.child('Pending_Post').get()
  users = db.child('Users').get()
  # post table
  for pending in pending_db.each():
    if key == pending.key():
      # email
      post_desc = pending.val()['description']
      image = pending.val()['imageUrl']
      email = EmailSender(host='smtp.gmail.com',port=587,username='darthderick4@gmail.com',password='jqesvcnxjnqbekbu')
      email.send(
      subject="Post Deleted",
      sender="noreply@gmail.com",
      receivers=[pending.val()['email']],
      html="""
        <html>
        <head></head>
        <body>
        <h4>The pending post that you have requested have been rejected by the Junk-A-Lang admin</h4>
        <p>Post Name: {{post_desc}}</p>
        <img width="200" height="200" src="{{image}}">
        </body>
        </html>
        """,
        body_params={
        'post_desc': post_desc,
        'image': image
            }
            )
        # end email

    if pending.val()['status'] != "Approved":
      if pending.key() == key:
        db.child('Pending_Post').child(pending.key()).remove()
        flash('Pending Post Deleted Successfully') 
        # user
        try:
          for user in users.each():
            indv = db.child('Users').child(user.key()).child('Post').get()
            if 'Post' in user.val():
              for p in indv.each():
                if pending.key() == p.key():
                  db.child('Users').child(user.key()).child('Post').child(pending.key()).remove()
        except:
          flash('Error deleting post')
               
  return redirect(url_for('pending_post'))

# post
@app.route('/post_del/<key>', methods=['GET', 'POST'])
def post_del(key):
  users = db.child('Users').get()
  db_post = db.child('Post').get()
  # post table
  for post in db_post.each():
    if key == post.key():
            # email
      post_desc = post.val()['description']
      image = post.val()['imageUrl']
      email = EmailSender(host='smtp.gmail.com',port=587,username='darthderick4@gmail.com',password='jqesvcnxjnqbekbu')
      email.send(
      subject="Post Deleted",
      sender="noreply@gmail.com",
      receivers=[post.val()['email']],
      html="""
      <html>
      <head></head>
      <body>
      <h4>The Junk-A-Lang admin has deleted your post for violating the rules and regulation of the application</h4>
      <p>Post Name: {{post_desc}}</p>
      <img width="200" height="200" src="{{image}}">
      </body>
      </html>
      """,
      body_params={
      'post_desc': post_desc,
      'image': image
          }
          )
      # end email
      db.child('Post').child(key).remove()
      flash('Post Deleted Successfully')
      try:
        for user in users.each():
          if 'Post' in user.val():
            indv = db.child('Users').child(user.key()).child('Post').get()
            for item in indv.each():
              db.child('Users').child(user.key()).child('Post').child(post.key()).remove()
      except:
        flash('Error deleting post')
      
  return redirect(url_for('posted'))


@app.route('/report_del/<key>' , methods=['GET','POST'])
def report_del(key):
  users = db.child('Users').get()
  posts = db.child('Post').get()
  # report and post table
  for report in db_report.each():
    if key == report.key():
      db.child('Report').child(key).remove()
      for post in db_post.each():
        if post.val()['description'] == report.val()['description'] and post.val()['date'] == report.val()['date']:
          # email
           post_desc = post.val()['description']
           image = post.val()['imageUrl']
           email = EmailSender(host='smtp.gmail.com',port=587,username='darthderick4@gmail.com',password='jqesvcnxjnqbekbu')
           email.send(
          subject="Post Deleted",
          sender="noreply@gmail.com",
          receivers=[post.val()['email']],
          html="""
          <html>
          <head></head>
          <body>
          <h4>Your post has been reported and now has been deleted.</h4>
          <p>Post Name: {{post_desc}}</p>
          <img width="200" height="200" src="{{image}}">
          </body>
          </html>
          """,
          body_params={
        'post_desc': post_desc,
        'image': image
          }
          )
          # end email
           flash('Reported Post Deleted')
           try:
             for user in users.each():
              if 'Post' in user.val():
                db.child('Users').child(user.key()).child('Post').child(key).remove()
           except:
            flash('Error in deleting reported post')
           try:
             for post in posts.each():
              if post.key() == key:
                db.child('Post').child(key).remove()
           except:
            flash('An error occured.')
  return redirect(url_for('report_posted'))


@app.route('/report_remove/<key>')
def report_remove(key):
  db.child('Report').child(key).remove()
  flash('Post removed from the reported post')
  return redirect(url_for('report_posted'))

@app.route('/user_del/<key>', methods=['GET','POST'])
def user_del(key):
  users = db.child('Users').get()
  posted =  db.child('Post').get()
  reported = db.child('Report').get()
  pending = db.child('Pending_Post').get()
  for user in users.each():
    if key == user.key():
      # email
      email = EmailSender(host='smtp.gmail.com',port=587,username='darthderick4@gmail.com',password='jqesvcnxjnqbekbu')
      email.send(
        subject="Account Deleted",
        sender="noreply@gmail.com",
        receivers=[user.val()['email']],
        html="""
        <html>
        <head></head>
        <body>
        <h4>Your account has and post has been deleted.</h4>
        <p>Your account has been deleted by the admin of the Junk-A-Lang mobile 
        application for not complying the rules and regulations of the application.</p>
        </body>
        </html>
        """)
          # end email
      for post in posted.each():
        if user.val()['email'] in post.val()['email']:
          try:
            db.child("Post").child(post.key()).remove()
          except:
            flash('Error Deleting User')
      for report in reported.each():
        if user.val()['email'] in report.val()['email']:
          try:
            db.child("Report").child(report.key()).remove()
          except:
            flash('Error Deleting User')
      for pending in pending.each():
        if user.val()['email'] in pending.val()['email']:
          try:
            db.child("Pending_Post").child(pending.key()).remove()
          except:
            flash('Error Deleting User')
      db.child('Users').child(user.key()).remove()
      flash('User Deleted Successfully')

    
  return redirect(url_for('user'))


if __name__ == "__main__":
  app.run(debug=True, port=1111)
	# app.run(port=1111)










