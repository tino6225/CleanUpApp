from flask import Flask, render_template, url_for, redirect, request, Response, jsonify, abort, make_response, flash, session
from google.appengine.ext import ndb
from google.appengine.api import images
import hashlib

app = Flask(__name__)
app.secret_key = '\xfav\x81\xc7\x01KpL\x08\xc7\x07\x82vy\xa3T&\x15\xe7\xe05\xf5W\xc7j\xe9\xdf!\x9a\xdcgP\xc2Jf/&\t\xb4\xf2\xdd+\x9a@\xb1\nS\xe2iO\x80:\x81\xd9l\xbfda\xac\x93\xd2\x1f\xf1\xe4'

from form import SignUpForm, LogForm
import model


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    userform = SignUpForm()
    if userform.uniqueValidate() ==True:
        username = userform.username.data
        password = userform.password.data
        hashed_psw = hashlib.sha256(password).hexdigest()
        email = userform.email.data
        saveUser = model.UserAccount(username=username, password=hashed_psw, email=email, id=username)
        saveUser.put()
        keyID = saveUser.key.id()
        session['username'] = userform.username.data
        flash("'{}' now has an account. '{}' is also your account Key".format(username, keyID))
        return redirect(url_for('login'))
    return render_template('signup.html', userform=userform)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        username = session['username']
        flash("Already logged in as '{}'".format(username))
        return redirect(url_for('index'))
    loginform = LogForm()
    if loginform.validate() == True:
        username = loginform.username.data
        try:
            session['username'] = username
            flash(" You are logged on. Your user key is '{}'.".format(username))
            return redirect(url_for('geoTrack'))
        except RuntimeError:
            flash("unable to session")
            return redirect(url_for('index'))
    return render_template('login.html', loginform=loginform)


@app.route('/logout')
def logout():
    if 'username' in session:
        user = session['username']
        flash(user + " is now logged off")
        session.pop('username', None)
        return redirect(url_for('index'))
    flash("No need to logout. You were not signed in")
    return redirect(url_for('index'))


@app.route('/geoTrack', methods=['POST', 'GET'])
def geoTrack():
    if 'username' in session:
        return render_template('geoTrack.html')
    flash("You are not logged in.  Please login to access this reporting feature.")
    return redirect(url_for('login'))


@app.route('/apiAddRecord', methods=['POST', 'GET'])
def apiAddRecord():
    if not request.json:
        abort(404)
    if not 'coordinates' or not 'comments' or not 'zipCode' in request.json:
        abort(404)

    if 'username' in session:
        coordinates = request.json.get('coordinates')
        comments = request.json.get('comments')
        zipCode = request.json.get('zipCode')
        saveRecord = model.Location(coordinates=coordinates, comments=comments, zipCode=zipCode)
        recordKey = saveRecord.put() #put() tells the engine's db to save; returns the database keypair for this record
        recordID = recordKey.id()  #get the record id
        return jsonify({'Please upload an image next. This record ID is': recordID})
    flash("You are not logged in.  Please login to save report.")
    return redirect(url_for('login'))


@app.route('/image', methods = ['GET', 'POST'])
def image():
    if request.method == 'POST':
        if 'username' in session:
            parentAcct = session['username']
            try:
                parentKey = ndb.Key(model.UserAccount, parentAcct).get().key
            except:
                flash("Image save refused. User Account key is invalid. Try logging in again")
                return redirect(url_for('login'))
            uploaded_file = request.files.get('image')
            mimetype = uploaded_file.mimetype
            image_stream = uploaded_file.stream.read()
        # if user submits without selecting file, browser also submits a empty part without file type
            if mimetype == '':
                flash("No file selected. Try again")
                return redirect(url_for('image'))
            image = images.resize(image_stream, 96, 96)
            saveImage = model.Photo(image=image, mimetype=mimetype, parent=parentKey) # stronger consistency -tied it to a parent record
            saveImage.put()
            imageID = saveImage.key.id()
            flash("Image upload complete. [{}] is its unique DB id".format(imageID))
            return redirect(url_for('thumbnail', id=saveImage.key.urlsafe()))
    return render_template('image.html')



@app.route('/history')
def history():
    return render_template('history.html', savedRecords=model.Location.query())


@app.route('/thumbnail/<id>')
def thumbnail(id):
    thumbnailKey = ndb.Key(urlsafe=id)
    image = thumbnailKey.get()
    return render_template('thumbnail.html', image=image)


@app.route('/show/<id>')
def show(id):
    thumbnailKey = ndb.Key(urlsafe=id)
    image = thumbnailKey.get()
    return Response(image.image, mimetype=image.mimetype)


@app.route('/imageHistory')
def imageHistory():
    if 'username' in session:
        parentAcct = session['username']
        try:
            parentKey = ndb.Key(model.UserAccount, parentAcct).get().key
        except:
            flash("Image retrieval refused. User key not valid")
            return redirect(url_for('index'))
        return render_template('imageHistory.html', savedImages=model.Photo.query(ancestor=parentKey).fetch())
    flash("You are not logged in.  Please login to view your image records.")
    return redirect(url_for('login'))


@app.errorhandler(404)
def notFound(e):
    return make_response(jsonify({'Encountered error': 'required field is missing value'}), 404)


if __name__ == '__main__':
    app.run(debug = True)
    
#if __name__ == '__main__':
 #   port = int(os.environ.get('PORT', 5000))

  #  if port == 5000:
 #       app.debug = True

 #   app.run(host='0.0.0.0', port=port)
