from werkzeug.utils import secure_filename
from flask import Flask, render_template, jsonify, request, flash
import time
import os
import base64

app = Flask(__name__)
UPLOAD_FOLDER = 'upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = '123456'
basedir = os.path.abspath(os.path.dirname(__file__))
ALLOWED_EXTENSIONS = set(['txt', 'png', 'jpg', 'xls', 'JPG', 'PNG', 'xlsx', 'gif', 'GIF'])


# 用于判断文件后缀
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# 用于测试上传，稍后用到
@app.route('/test/upload')
def upload_test():
    return render_template('upload.html')


# 上传文件
@app.route('/api/upload', methods=['POST'], strict_slashes=False)
def api_upload():
    file_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER'])
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    f = request.files['myfile']  # 从表单的file字段获取文件，myfile为该表单的name值
    if f and allowed_file(f.filename):  # 判断是否是允许上传的文件类型
        fname = secure_filename(f.filename)
        print(fname)
        ext = fname.rsplit('.', 1)[1]  # 获取文件后缀
        unix_time = int(time.time())
        new_filename = str(unix_time) + '.' + ext  # 修改了上传的文件名
        f.save(os.path.join(file_dir, new_filename))  # 保存文件到upload目录
        token = base64.b64encode(new_filename)
        print(token)

        return jsonify({"errno": 0, "errmsg": "上传成功", "token": token})
    else:
        return jsonify({"errno": 1001, "errmsg": "上传失败"})


from flask import send_from_directory, abort, make_response
import os


@app.route('/download/<string:filename>', methods=['GET'])
def download(filename):
    if request.method == "GET":
        if os.path.isfile(os.path.join('upload', filename)):
            return send_from_directory('upload', filename, as_attachment=True)
        pass


@app.route('/show', methods=['GET'])
def show():
    file_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER'])
    if os.listdir(file_dir):
        files = os.listdir(file_dir)
        return render_template("show.html", files=files)
    else:
        return ("<h1>No file exist!</h1>")


# show photo
@app.route('/show_photo/<string:filename>', methods=['GET'])
def show_photo(filename):
    file_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER'])
    if request.method == 'GET':
        if filename is None:
            pass
        else:
            image_data = open(os.path.join(file_dir, '%s' % filename), "rb").read()
            response = make_response(image_data)
            response.headers['Content-Type'] = 'image/png'
            return response
    else:
        pass


# show photo
@app.route('/delete_photo/<string:filename>', methods=['GET'])
def delete_photo(filename):
    file_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER'])
    if request.method == 'GET':
        if filename is None:
            jsonify({"errno": 1003, "errmsg": "删除失败"})

        else:
            target_file = os.path.join(file_dir, filename)
            if os.path.isfile(target_file):
                os.remove(target_file)
                flash("{} have delete successfully".format(filename))
                # return jsonify({"no": 1004, "msg": "删除成功"})
                return render_template("show.html")

            else:
                print("file not exist")



    else:
        pass


if __name__ == '__main__':
    app.run(debug=True)
