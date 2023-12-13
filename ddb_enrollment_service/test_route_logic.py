import boto3
from ddb_enrollment_schema import *
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ParamValidationError
import redis


####################
#Create a new class#
####################
# class_table_instance = create_table_instance(Class, "class_table")

# # Define the item to add
# item_to_add = {
#     "id": 1,  # You need to implement a function to generate a unique ID
#     "dept_code": "1",
#     "course_num": 1,
#     "section_no": 1,
#     "academic_year": 1,
#     "semester": 1,
#     "instructor_id": 1,
#     "room_num": 1,
#     "room_capacity": 1,
#     "course_start_date": 1,
#     "enrollment_start": 1,
#     "enrollment_end": 1,
# }

# # Use put_item to add the item to the table
# class_table_instance.put_item(Item=item_to_add)

# # # Perform a scan to retrieve all items
# response = class_table_instance.query(KeyConditionExpression=Key('id').eq(1))

# # # Extract the items from the response
# items = response.get('Items', [])

# # # Print or process the items
# for item in items:
#     print(item)

###########################
#Get current enrollments#
###########################


# enrollment_table_instance = create_table_instance(Enrollment, "enrollment_table")

# # Perform a scan to retrieve all items
# response = enrollment_table_instance.table.query(KeyConditionExpression=Key('class_id').eq(1))

# # Extract the items from the response
# items = response.get('Items', [])

# # Print or process the items
# for item in items:
#     print(item)

###########################
#Get all available classes#
###########################

# available_classes = []

# class_table_instance = create_table_instance(Class, "class_table")
# enrollment_table_instance = create_table_instance(Enrollment, "enrollment_table")

# response = class_table_instance.scan()

# items = response.get('Items', [])

# for item in items:
#     class_id = item['id']
#     room_capacity = item['room_capacity']
#     enrollments = enrollment_table_instance.query(KeyConditionExpression=Key('class_id').eq(class_id))
#     num_of_enrollments = len(enrollments.get('Items', []))
#     if num_of_enrollments < room_capacity:
#         available_classes.append(item)


# # Print or process the items
# for item in available_classes:
#     print(item)

##################
#Enroll a student#
##################
# class_id = 1
# class_table_instance = create_table_instance(Class, "class_table")
# enrollment_table_instance = create_table_instance(Enrollment, "enrollment_table")

# response = class_table_instance.query(KeyConditionExpression=Key('id').eq(class_id))
# class_item = response.get('Items', [])[0]
# room_capacity = class_item['room_capacity']
# enrollments = enrollment_table_instance.query(KeyConditionExpression=Key('class_id').eq(class_id))

# num_of_enrollments = len(enrollments.get('Items', []))
# if num_of_enrollments < room_capacity:
#     item_to_add = {
#         "class_id": 1,
#         "enrollment_date": "2023-06-01 09:00:00",
#         "student_id" : 2
#     }

#     enrollment_table_instance.put_item(Item=item_to_add)

#     print("Added item")
#     print(item_to_add)
# else:
#         print("No available seats in the class")

#########################
#Check waitlist position#
#########################
student_id = 73123456
class_id = 2

redis_conn = redis.Redis(decode_responses=True)
waitlist_key_to_check = f"waitlist_{class_id}"
# Get the rank of the member in the sorted set (0-based index)
waitlist_position = redis_conn.zrank(waitlist_key_to_check, f"{class_id}_{student_id}")

if waitlist_position is not None:
    # Adding 1 to convert 0-based index to 1-based position
    waitlist_position += 1
    print (f"waitlist position : {waitlist_position}")
else:
    print(f"You are not in the waitlist for class {class_id}")