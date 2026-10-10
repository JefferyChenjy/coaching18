import logging
import os

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from flask import Flask, render_template_string, request

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

AWS_REGION = os.environ["AWS_REGION"]
QUEUE_URL = os.environ["QUEUE_URL"]

sqs_client = boto3.client("sqs", region_name=AWS_REGION)

SQS_FORM = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>SQS Message Sender</title>
</head>
<body>
    <h1>Send a Message to SQS</h1>
    <form method="POST" action="/send">
        <label for="message">Message:</label>
        <input id="message" type="text" name="message" required>
        <button type="submit">Send to SQS</button>
    </form>
</body>
</html>
"""


@app.route("/health")
def health():
    return {"status": "ok"}, 200


@app.route("/")
@app.route("/send", methods=["GET", "POST"])
def send():
    if request.method == "GET":
        return render_template_string(SQS_FORM)

    message = request.form.get("message", "").strip()
    if not message:
        return "Please enter a message.", 400

    try:
        response = sqs_client.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=message,
        )
    except (BotoCoreError, ClientError):
        logger.exception("Failed to send message to SQS")
        return "Unable to send the message. Please try again later.", 502

    message_id = response["MessageId"]
    logger.info("Sent message to SQS: MessageId=%s", message_id)
    return {"status": "sent", "message_id": message_id}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)