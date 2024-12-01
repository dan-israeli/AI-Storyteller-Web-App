from flask import Flask, flash, render_template, request, Response, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from flask_session import Session
from utils import *


app = Flask(__name__)

# Configure session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/login", methods=["GET", "POST"])
def login():
    # POST request
    if request.method == "POST":

        # Get user input
        username = request.form.get("username")
        password = request.form.get("password")

        # Check if all values provided
        if not username or not password:

            if not username:
                flash("Please enter your username!", "error")

            if not password:
                flash("Please enter your password!", "error")

            return redirect("/login")

        with get_db_connection("database.db") as db:
            rows = db.execute("SELECT * FROM users WHERE username = ?",
                              (username,)).fetchall()

        # Check if the username exists and the password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            flash("Username and/or password is incorrect!", "error")
            return redirect("/login")

        # Initialize user id and default website settings
        init_site_settings(session, user_id=rows[0]["id"])

        # Go to homepage
        return render_template("index.html")

    # GET request
    return render_template("auth/login.html")


@app.route("/logout")
@login_required
def logout():
    # Delete session
    del session["user_id"]

    # Go to login page
    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():

    # POST request
    if request.method == "POST":

        # Get user input
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Check if all values provided
        if not username or not password or not confirmation:

            if not username:
                flash("Please provide a username!", "error")

            if not password:
                flash("Please provide a password!", "error")

            if not confirmation:
                flash("Please confirmation the password!", "error")

            return redirect("/register")

        # Check if password is equal to password confirmation
        if password != confirmation:
            flash("Passwords do not match!", "error")
            return redirect("/register")

        with get_db_connection("database.db") as db:
            rows = db.execute("SELECT * FROM users WHERE username = ?",
                             (username,)).fetchall()

        # Check if the provided username is already exists
        if len(rows) != 0:
            flash("Username already exists!", "error")
            return redirect("/register")

        # Create the new user
        with get_db_connection("database.db") as db:
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)",
                      (username, generate_password_hash(password)))

            db.commit()

        # Go to login page
        return redirect("/login")

    # GET request
    return render_template("auth/register.html")


@app.route("/", methods=["GET", "POST"])
@login_required
def index():

    # POST request
    if request.method == "POST":

        # Reset story's settings before creating a new story
        reset_story_settings(session)

        # Go to location page (start creating a new story)
        return redirect("/location")

    # Get request
    return render_template("index.html")


@app.route("/settings")
@login_required
def settings():
    return render_template("settings/settings.html", session=session, speakers=SPEAKERS)


@app.route("/settings/update", methods=["PUT"])
def update_settings():

    try:
        # Get data from fetch request
        data = request.get_json()

        # Update setting's value
        setting = data["setting"]
        value = data["value"]

        if setting == "story_sections":
            value = int(value)

        session[setting] = value

        # Return a success response
        return jsonify({"message": "Setting update successfully!"}), 200

    except Exception as e:
        # Return an error response if something goes wrong
        return jsonify({"error": str(e)}), 500


@app.route("/settings/custom_voice")
@login_required
def custom_voice():
    return render_template("settings/custom_voice.html")


@app.route("/library")
@login_required
def library():

    # Get all user's saved stories
    with get_db_connection("database.db") as db:
        rows = db.execute("SELECT id, title FROM stories WHERE user_id = ?",
                          (session["user_id"],)).fetchall()

    return render_template("library/library.html", rows=rows)

@app.route("/library/delete_story", methods=["DELETE"])
def delete_story():
    try:
        # Get story's id to delete
        print(request.get_json())
        story_id = request.get_json()["story_id"]

        # Delete story with "story_id"
        with get_db_connection("database.db") as db:
            db.execute("DELETE FROM stories WHERE id = ?",
                       (story_id,))
            db.commit()

        # Return a success response
        return jsonify({"message": "Story deleted successfully from the library!"}), 204

    except Exception as e:
        # Return an error response if something goes wrong
        return jsonify({"error": str(e)}), 500


@app.route("/library/email_story", methods=["POST"])
@login_required
def email_story():

    try:
        # Get data from fetch request
        data = request.get_json()
        receiver_email = data["receiver_email"]
        story_id = data["story_id"]

        # Get story with "story_id" id
        with get_db_connection("database.db") as db:
            row = db.execute("SELECT title, story FROM stories WHERE id = ?",
                             (story_id,)).fetchall()[0]

        # Send email with the selected story
        send_email(row["title"], row["story"], receiver_email)

        # Return a success response
        return jsonify({"message": "Story sent successfully!"}), 200

    except Exception as e:
        # Return an error response if something goes wrong
        return jsonify({"error": str(e)}), 500


@app.route("/library/<int:story_id>")
@login_required
def get_story(story_id):

    # Get story details
    with get_db_connection("database.db") as db:
        row = db.execute("SELECT title, story FROM stories WHERE id = ?",
                          (story_id,)).fetchall()[0]

    return render_template("library/saved_story.html", row=row)


@app.route("/location")
@login_required
def location():
    return render_template("story/location.html",
                           is_voice_guidance=session["voice_guidance"], speaker=session["speaker"])


@app.route("/genre")
@login_required
def genre():
    return render_template("story/genre.html",
                           is_voice_guidance=session["voice_guidance"], speaker=session["speaker"])


@app.route("/hero_name")
@login_required
def hero_name():
    return render_template("story/hero_name.html",
                           is_voice_guidance=session["voice_guidance"], speaker=session["speaker"])


@app.route("/<story_setting>/set", methods=["POST"])
def set_story_setting(story_setting):

    try:
        # Set story setting based on user's input
        session[story_setting] = request.get_json()[story_setting]

        # Return a success response
        return jsonify({"message": f"{story_setting} saved successfully!"}), 200

    except Exception as e:
        # Return an error response if something goes wrong
        return jsonify({"error": str(e)}), 500



@app.route("/story")
@login_required
def story():
    print(session)
    return render_template("story/story.html",
                           title=session["title"], current_section=session["current_section"],
                           speaker=session["speaker"], is_story_audio=session["story_audio"],
                           num_sections_left=session["story_sections_left"])

@app.route("/story/generate_section", methods=["POST"])
def generate_story_section():

    try:
        gen_type = request.get_json()["gen_type"]

        # Arrived at the page for the first time request (right after choosing all the story's settings)
        if gen_type == "initial":

            # Create hero name
            if session["hero_name"] == "":
                session["hero_name"] = create_hero_name()

            # Create story's title
            session["title"] = create_title(session["hero_name"], session["location"], session["genre"])

            # Create initial story generation prompt
            initial_prompt = get_initial_prompt(session["location"], session["genre"], session["hero_name"],
                                                session["story_sections"])
            session["message_history"] = [get_message("user", initial_prompt)]

            # Initialize number of sections left
            session["story_sections_left"] = session["story_sections"]

        # Regenerate section
        elif gen_type == "regen":

            # Get section regeneration prompt
            regen_prompt = get_regen_prompt()
            session["message_history"].append(get_message("user", regen_prompt))

            # increment number of sections left
            session["story_sections_left"] += 1

        # Generate next section based on selected option
        elif "option" in gen_type:
            # Create new prompt
            new_prompt = f"""{gen_type}. {get_reminder(session["story_sections_left"])}"""
            session["message_history"].append(get_message("user", new_prompt))


        # Get current story section
        current_section = chatgpt(session["message_history"])
        session["current_section"] = current_section
        session["message_history"].append(get_message("assistant", current_section))

        # Decrement number of sections left
        session["story_sections_left"] -= 1

        # Return a success response
        return jsonify({"message": " Current section created successfully!"}), 200

    except Exception as e:
        # Return an error response if something goes wrong
        return jsonify({"error": str(e)}), 500



@app.route("/story_end")
@login_required
def story_end():
    return render_template("story/story_end.html")


@app.route("/story_end/save", methods=["POST"])
def save_story():

        try:
            # Create save story prompt
            save_story_prompt = get_save_story_prompt()
            session["message_history"].append(get_message("user", save_story_prompt))

            # Generate full story (with selected options built-in)
            full_story = chatgpt(session["message_history"])

            # Add new story
            with get_db_connection("database.db") as db:
                db.execute("INSERT INTO stories (user_id, title, story) VALUES (?, ?, ?)",
                           (session["user_id"], session["title"], full_story))
                db.commit()

            # Return a success response
            return jsonify({"message": "story saved successfully!"}), 201

        except Exception as e:
            # Return an error response if something goes wrong
            return jsonify({"error": str(e)}), 500



@app.route("/audio", methods=["POST"])
def audio():
    try:
        # GET data from fetch request
        data = request.get_json()
        text = data["text"]
        speaker = data["speaker"]
        stability = data["stability"]

        # Check if speaker provided
        if not speaker:
            speaker = session["speaker"]

        # Return audio stream
        return Response(get_audio_stream(text, speaker, stability), content_type="audio/mpeg")

    except Exception as e:
        # Return an error response if something goes wrong
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run()
