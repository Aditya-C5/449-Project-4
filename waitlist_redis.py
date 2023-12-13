import redis
from datetime import datetime

redis_conn = redis.Redis(decode_responses=True)

# Data to be inserted
waitlist_data = [
    {"class_id": 2, "student_id": 65123456, "waitlist_date": '2023-08-28 09:00:00'},
    {"class_id": 2, "student_id": 73123456, "waitlist_date": '2023-08-28 10:00:00'},
    {"class_id": 2, "student_id": 76123456, "waitlist_date": '2023-08-28 11:30:00'},
    {"class_id": 3, "student_id": 68123456, "waitlist_date": '2023-08-29 09:40:00'},
    {"class_id": 3, "student_id": 85123456, "waitlist_date": '2023-08-29 09:50:00'}
]

# Create separate sorted sets for each class
for entry in waitlist_data:
    class_id = entry["class_id"]
    student_id = entry["student_id"]
    waitlist_date = entry["waitlist_date"]

    waitlist_key = f"waitlist_{class_id}"

    # Construct the member using class_id and student_id
    member = f"{class_id}_{student_id}"

    # Convert waitlist_date to a float
    waitlist_date = datetime.strptime(waitlist_date, '%Y-%m-%d %H:%M:%S')
    score = waitlist_date.timestamp()

    # Add the member and score to the sorted set for the specific class
    redis_conn.zadd(waitlist_key, {member: score})

