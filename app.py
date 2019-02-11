import os
from classify import prediction
import tensorflow as tf
import time
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, redirect, session
from werkzeug import secure_filename
from PIL import Image

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = set(['jpg', 'jpeg'])
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


@app.route('/', methods=['POST', 'GET'])
def index():
    if session.get('filename'):
        image_path = session.pop('filename')
        image_path = 'uploads/' + image_path
        with tf.Graph().as_default():
            human_string, score = prediction(image_path)
        if (human_string == 'car'):
            damage_level = 'No-Damage'
            confidence = score
            print(image_path)
            time.sleep(1)
            response = render_template('index.html', damage_level=damage_level, Confidence=confidence,
                                       filename=image_path)
            return response
        elif (human_string == 'low'):
            damage_level = 'Damage: Low'
            confidence = score
            print(image_path)
            time.sleep(1)
            response = render_template('index.html', damage_level=damage_level, Confidence=confidence,
                                       filename=image_path)
            return response
        elif (human_string == 'high'):
            damage_level = 'Damage: High'
            confidence = score
            print(image_path)
            time.sleep(1)
            response = render_template('index.html', damage_level=damage_level, Confidence=confidence,
                                       filename=image_path)
            return response
        elif (human_string == 'not'):
            damage_level = 'This is not a car'
            confidence = score
            print(image_path)
            time.sleep(1)
            response = render_template('index.html', damage_level=damage_level, Confidence=confidence,
                                       filename=image_path)
            return response
    else:
        return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_img():
    file = request.files['file']
    if file:
        filename = secure_filename(file.filename)
        file_name_full_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_name_full_path)
        img = Image.open(file_name_full_path)
        base_width = 440
        wpercent = (base_width / float(img.size[0]))
        hsize = int((float(img.size[1]) * float(wpercent)))
        img = img.resize((base_width, hsize), Image.ANTIALIAS)
        img.save(file_name_full_path)
        session['filename'] = filename
        return redirect(url_for('index'))
    else:
        return "Something went wrong, Please make sure you upload valid image!"

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


if __name__ == '__main__':
    app.run('0.0.0.0')
