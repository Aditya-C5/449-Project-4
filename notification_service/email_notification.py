from email.mime.text import MIMEText
import pika
import sys
import threading
import smtplib
from email.mime.multipart import MIMEMultipart

# Function to emit logs
def emit_log(student_email: str, class_id: int):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='logs', exchange_type='fanout')

    message = student_email + ';' + str(class_id)
    channel.basic_publish(exchange='logs', routing_key='', body=message)
    print(f" [x] Sent {message}")

    connection.close()

def send_email(student_email: str, message : str):
    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = "notif@test.com"
    msg['To'] = student_email
    msg['Subject'] = 'Class Enrollment Notification'
    msg.attach(MIMEText(message, 'plain'))

    # Send the email
    with smtplib.SMTP('localhost', 8025) as server:
        server.sendmail(msg['From'], msg['To'], msg.as_string())
    

# Callback function for received logs
def callback(ch, method, properties, body):
    student_email, class_id = body.decode('utf-8').split(';')
    message = f'You are now enrolled in class {class_id}!'
    send_email(student_email, message)
    print(f" [x] {body.decode()}")



# Function to receive logs
def receive_logs():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='logs', exchange_type='fanout')

    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    channel.queue_bind(exchange='logs', queue=queue_name)

    print(' [*] Waiting for logs. To exit press CTRL+C')

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    channel.start_consuming()

# Main function to run both publisher and consumer
def main():
    # Run the consumer in a separate thread
    consumer_thread = threading.Thread(target=receive_logs)
    consumer_thread.start()

    # Wait for a brief moment to ensure the consumer is ready
    import time
    time.sleep(1)

    # Run the publisher

    # Wait for the consumer thread to finish
    consumer_thread.join()

if __name__ == "__main__":
    main()
