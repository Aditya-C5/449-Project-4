import boto3
from classes import create_class_instance
from enrollment import create_enrollment_instance


class_table_manager = create_class_instance()
table_name = "class_table"
class_table_manager.table = class_table_manager.dyn_resource.Table(table_name)


# Define a list of items to add to the DynamoDB table
items_to_insert = [
    {
        "id": 1,
        "dept_code": "CPSC",
        "course_num": 101,
        "section_no": 1,
        "academic_year": 2023,
        "semester": "SU",
        "instructor_id": 1,
        "room_num": 101,
        "room_capacity": 30,
        "course_start_date": "2023-06-12",
        "enrollment_start": "2023-06-01 09:00:00",
        "enrollment_end": "2023-06-15 17:00:00",
    },
    # Repeat for other items...
]

# Add each item to the DynamoDB table
for item in items_to_insert:
    class_table_manager.table.put_item(Item=item)
#####################################################################################################################

enrollment_table_manager = create_enrollment_instance()
table_name = "enrollment_table"
enrollment_table_manager.table = enrollment_table_manager.dyn_resource.Table(table_name)

# Define a list of items to add to the DynamoDB table
items_to_insert = [
    {
        "class_id": 1,
        "enrollment_date": "CPSC",
        "student_id" : 1
    },
    # Repeat for other items...
]

# Add each item to the DynamoDB table
for item in items_to_insert:
    enrollment_table_manager.table.put_item(Item=item)