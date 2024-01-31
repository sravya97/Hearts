from flask import Flask, render_template, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from database.database_helper import DatabaseHelper

scheduler = BackgroundScheduler()

app = Flask(__name__)
app.config['STATIC_URL_PATH'] = '/static'
db_helper = DatabaseHelper("database/messages.db")
latest_message = {'message_id': None, 'content': 'No messages available.'}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get-latest-message', methods=['GET'])
def get_latest_message():
    return jsonify({'content': latest_message['content'] if latest_message else 'No messages available'})


@app.route('/add-new')
def add_message_form():
    return render_template('add_new.html')


@app.route('/add-messages', methods=['POST'])
def add_messages():
    try:
        messages = request.form.getlist('messages')
        for message in messages:
            db_helper.add_message(message)
        return jsonify({"status": "success", "message": "All messages have been added"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route('/get-all', methods=['GET'])
def get_all_messages():
    try:
        messages = db_helper.get_all_messages()
        return jsonify({"status": "success", "messages": messages})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route('/delete-all', methods=['GET'])
def delete_all_messages():
    try:
        db_helper.delete_all_messages()
        return jsonify({"status": "success", "message": "All entries deleted successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route('/delete/<int:message_id>', methods=['GET'])
def delete_message(message_id):
    try:
        db_helper.delete_message_by_id(message_id)
        return jsonify({"status": "success", "message": f"Message with ID {message_id} deleted successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


def refresh_message():
    global latest_message
    message = db_helper.get_random_message()

    if message:
        message_id = message[0]
        content = message[1]
        latest_message = {'message_id': message_id, 'content': content}
        # print(f"Message refreshed: {content}")


# Schedule the refresh_message function to run at midnight
scheduler.add_job(refresh_message, trigger=CronTrigger(hour=23, minute=0), id='refresh_job')
scheduler.start()
if latest_message['message_id'] is None:
    refresh_message()


if __name__ == '__main__':
    app.run(debug=False, port=5000)
