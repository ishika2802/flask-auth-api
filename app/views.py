import os
from flask import Blueprint, render_template, request, Flask, redirect, url_for, current_app, flash, jsonify
from flask_login import current_user,login_required
from werkzeug.utils import secure_filename



# Configure Flask to use 'dist' for static files
views = Blueprint('views', __name__)
UPLOAD_FOLDER = 'static/assets/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Sample state-to-city mapping
state_cities = {
    "California": ["Los Angeles", "San Francisco", "San Diego", "Sacramento"],
    "Texas": ["Houston", "Dallas", "Austin", "San Antonio"],
    "New York": ["New York City", "Buffalo", "Rochester", "Albany"],
    "Florida": ["Miami", "Orlando", "Tampa", "Jacksonville"],
    "Illinois": ["Chicago", "Springfield", "Naperville", "Peoria"]
}

@views.route("/get_cities/<state>")
def get_cities(state):
    cities = state_cities.get(state, [])
    return jsonify({"cities": cities})

def allowed_file_extension(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@views.route("/dashboard", methods=['GET', 'POST'])
@login_required
def homePage():
    print(f"Hello, {current_user.username}!")
    return render_template('index.html')


@views.route('/userProfile', methods=['GET', 'POST'])
@login_required
def userProfile():
    userCollection = current_app.db['users']
    profileCollection = current_app.db["profiles"]
    current_email = current_user.email  # Get logged-in user's current email
    userProfileDetails = userCollection.find_one({"email": current_email})
    profileDetails = profileCollection.find_one({"email": current_email})

    # If profile does not exist, create a new one
    if not profileDetails:
        profileData = {
            "email": current_email,
            "userName": userProfileDetails.get("userName") if userProfileDetails else "",
            "image": "",
            "countryCode": "",
            "mobileNumber": "",
            "address": "",
            "address2": "",
            "country" : "",
            "state": "",
            "city": "",
            "zipCode": "",
        }
        profileCollection.insert_one(profileData)
    else:
        profileData = profileDetails  # Use existing profile data

    if request.method == 'POST':
        # Fetch form data
        new_email = request.form.get("email")  # Get the new email from the form
        # image = request.form.get("image")
        countryCode = request.form.get("countryCode")
        mobileNumber = request.form.get("mobileNumber")
        address = request.form.get("address")
        address2 = request.form.get("address2")
        country = request.form.get("country")
        state = request.form.get("state")
        city = request.form.get("city")
        zipCode = request.form.get("zipCode")

        # Handle Image Upload (Fix File Path)
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file_extension(file.filename):
                filename = secure_filename(file.filename)
                filePath = os.path.join(UPLOAD_FOLDER, filename)
                if not os.path.exists(UPLOAD_FOLDER):
                    os.makedirs(UPLOAD_FOLDER)
                filePath = filePath.replace("\\", "/")
                file.save(filePath)
                print(f"Saved Image Path: {filePath}")
                print(f"Database Stored Image: {filename}")
                profileData["image"] = filename

        # Prepare update dictionary, excluding None and empty values
        updatedProfileData = {
            "email": new_email,  # Include email update
            "image": profileData.get("image", ""),
            "mobileNumber": mobileNumber,
            "countryCode": countryCode,
            "address": address,
            "address2": address2,
            "country": country,
            "state": state,
            "city": city,
            "zipCode": zipCode,
        }
        updatedProfileData = {k: v for k, v in updatedProfileData.items() if v not in [None, ""]}

        # if not updatedProfileData:
        #     flash("No valid data to update.", "info")
        #     return redirect(url_for("views.userProfile"))

        # **Handle Email Change**
        if new_email and new_email != current_email:
            # Check if the new email already exists in the database
            existing_user = userCollection.find_one({"email": new_email})
            if existing_user:
                flash("Email is already in use. Please use a different one.", "error")
                return redirect(url_for("views.userProfile"))

            # Update email in both collections
            try:
                profileResult = profileCollection.update_one({"email": current_email}, {"$set": updatedProfileData})
                userResult = userCollection.update_one({"email": current_email}, {"$set": {"email": new_email}})
                
                print("Profile Update Result:", profileResult.raw_result)
                print("User Update Result:", userResult.raw_result)

                if profileResult.modified_count > 0 and userResult.modified_count > 0:
                    flash("Profile and email updated successfully!", "success")
                    # Optionally update the session with the new email
                    current_user.email = new_email  # Flask-Login will need to reload the user
                else:
                    flash("No changes detected.", "info")

            except Exception as e:
                flash(f"Error occurred: {e}", "error")

        else:
            # If email is not changed, just update the profile
            try:
                result = profileCollection.update_one({"email": current_email}, {"$set": updatedProfileData})
                print("Profile Update Result:", result.raw_result)

                if result.modified_count > 0:
                    flash("Profile updated successfully!", "success")
                else:
                    flash("No changes detected.", "info")

            except Exception as e:
                flash(f"Error occurred: {e}", "error")

        return redirect(url_for("views.userProfile"))

    return render_template("userProfile.html", user=current_user, profile=profileData)

@views.route("/userAccounts", methods=['GET', 'POST'])
@login_required
def userAccount():
    print(f"Hello, {current_user.username}!")
    return render_template('user-accounts.html')



