import os
from classify import prediction
import tensorflow as tf
import time
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, redirect, session
from werkzeug import secure_filename
from PIL import Image
import traceback

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = set(['jpg', 'jpeg'])
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'

vehicle_data = {
    'DCIM1001.jpg': {'make': 'BMW', 'model': 'M3', 'damage_location': 'Front Right', 'policy_number': '6446285647',
                     'car_registration': 'KYF 7856', 'cost': '$9000'},
    'DCIM1002.jpg': {'make': 'BMW', 'model': 'M3', 'damage_location': 'Rear Right', 'policy_number': '6446285647',
                     'car_registration': 'KYF 7856', 'cost': '$250'},
    'DCIM1003.jpg': {'make': 'BMW', 'model': 'M3', 'damage_location': 'Front', 'policy_number': '6446285647',
                     'car_registration': 'KYF 7856', 'cost': '$11000'},
    'DCIM1004.jpg': {'make': 'Suzuki', 'model': 'Swift Sports', 'damage_location': 'Front',
                     'policy_number': '8554488452',
                     'car_registration': '5YFA113', 'cost': '$800'},
    'DCIM0120.JPG': {'make': 'Lotus', 'model': 'Elise', 'damage_location': 'Rear', 'policy_number': '6204448322',
                     'car_registration': 'JI2 VXL', 'cost': '$130'},
    'DCMI10302.jpg': {'make': 'Toyota', 'model': 'Prius', 'damage_location': '-', 'policy_number': '9007842134',
                      'car_registration': '5CT5546', 'cost': '-'}
}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


@app.route('/', methods=['POST', 'GET'])
def index():
    try:
        if session.get('filename'):
            image_name = session.pop('filename')
            image_path = 'uploads/' + image_name
            print(image_path)
            if image_name not in ['IMG_20190206.jpg', 'IMG_10086.JPG']:
                damage_location = vehicle_data[image_name]['damage_location']
                make = vehicle_data[image_name]['make']
                model = vehicle_data[image_name]['model']
                policy_number = vehicle_data[image_name]['policy_number']
                car_registration = vehicle_data[image_name]['car_registration']
                cost = vehicle_data[image_name]['cost']
            with tf.Graph().as_default():
                human_string, score = prediction(image_path)
            if (human_string == 'car'):
                damage_level = 'No-Damage'
                confidence = score
                color_code = '008000'

            elif (human_string == 'low'):
                damage_level = 'Low'
                confidence = score
                print(image_path)
                color_code = 'FF8C00'

            elif (human_string == 'high'):
                damage_level = 'High'
                confidence = score
                color_code = 'FF4500'

            elif (human_string == 'not'):
                damage_level = 'This is not a car'
                confidence = score
                color_code = '555'
                if image_name in ['IMG_20190206.jpg', 'IMG_10086.JPG']:
                    response = render_template('index.html', unknown=True, filename=image_path, Confidence=confidence)
                    return response
            response = render_template('index.html', known=True, damage_level=damage_level, Confidence=confidence,
                                       filename=image_path, color_code=color_code, damage_location=damage_location,
                                       make=make, model=model, policy_number=policy_number,
                                       car_registration=car_registration, cost=cost)
            return response
        else:
            return render_template('index.html')
    except Exception as e:
        print('%s -> %s', e, traceback.format_exc())
        image_name = session.pop('filename')
        return "something went wrong"


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
