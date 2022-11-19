import pyrebase

# config ={
# "apiKey": "AIzaSyAAPzT8IrkEsKoMUJAUpokamGrI6fr5K7E",
#   "authDomain": "authenticatepy-33a33.firebaseapp.com",
#   "projectId": "authenticatepy-33a33",
#   "storageBucket": "authenticatepy-33a33.appspot.com",
#   "messagingSenderId": "1073039177202",
#   "appId": "1:1073039177202:web:ebd347babb132cc1c2a76b",
#   "measurementId": "G-MWP8317FQ7",
#   "databaseURL": ""
# }

config ={
  "apiKey": "AIzaSyA-NVaAiPUM_hgSugKvpekv4JhJ95-335Q",

  "authDomain": "junkshopapp.appspot.com",
  
  "databaseURL": "https://junkshopapp-default-rtdb.firebaseio.com",
  
  "projectId": "junkshopapp",

  "storageBucket": "junkshopapp.appspot.com",

  "messagingSenderId": "1012935772191",

  "appId": "1:1012935772191:android:c0e3a95b4352436b9a2d2a",
#  not changed
#   "measurementId": "G-MWP8317FQ7",
#   "databaseURL": "",
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

email = "test@gmail.com"
password = "123456"

# CREATE
user = auth.create_user_with_email_and_password(email, password)
print(user)

# GET INFO ABOUT THE USER
# user = auth.sign_in_with_email_and_password(email, password)
# info = auth.get_account_info(user['idToken'])
# print(info)

# SEND EMAIL VERIFICATION
# auth.send_email_verification(user['idToken'])

# RESET PASSWORD
# auth.send_password_reset_email(email)