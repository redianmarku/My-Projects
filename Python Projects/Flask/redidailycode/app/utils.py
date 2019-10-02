import os
import secrets
from PIL import Image
from flask import url_for, current_app


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/fotot', picture_fn)
    
    output_size = (200, 200)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn



def save_post_picture(form_picture_post):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture_post.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/fotot', picture_fn)
    
    output_size = (800, 800)
    i = Image.open(form_picture_post)
    i.resize((20, 20))
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn