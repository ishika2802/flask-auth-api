import os
from flask import Blueprint, render_template, request, Flask, redirect, url_for
from flask_login import current_user,login_required


# Configure Flask to use 'dist' for static files
views = Blueprint('views', __name__)

@views.route("/dashboard", methods=['GET', 'POST'])
@login_required
def homePage():
    print(f"Hello, {current_user.username}!")
    return render_template('index.html')

