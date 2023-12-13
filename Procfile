gateway: echo ./etc/krakend.json | entr -nrz krakend run --config etc/krakend.json --port $PORT
enrollment_service: uvicorn ddb_enrollment_service.app:app --port $PORT --host 0.0.0.0 --reload
user_service: uvicorn user_service.app:app --port $PORT --host 0.0.0.0 --reload
notification_service: uvicorn notification_service.app:app --port $PORT --host 0.0.0.0 --reload
#dynamodb: java -Djava.library.path=dynamodb_local_latest/DynamoDBLocal_lib -jar dynamodb_local_latest/DynamoDBLocal.jar -port $PORT 
# user_service_primary: ./bin/litefs mount -config etc/primary.yml
# user_service_secondary: ./bin/litefs mount -config etc/secondary.yml
# user_service_tertiary: ./bin/litefs mount -config etc/tertiary.yml
dynamodb: sh ./bin/start-dynamodb.sh  
redis: sh ./bin/start-redis-server.sh
aiosmtpd_server: python -m aiosmtpd -n -d
email_notification_service: python -m notification_service.email_notification