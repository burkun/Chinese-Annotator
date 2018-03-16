#!/bin/bash

curl -d '{"user_uuid": "5a683cadfe61a3fe9262a310", "dataset_uuid": "5a6840b28831a3e06abbbcc9", "task_type" : "classify", "start_timestamp": 1483200000.0}' "http://127.0.0.1:5001/batch_train"
curl -d '{"user_uuid": "5a683cadfe61a3fe9262a310", "dataset_uuid": "5a6840b28831a3e06abbbcc9", "task_type" : "classify"}' "http://127.0.0.1:5001/latest_task_status"
sleep 8
curl -d '{"user_uuid": "5a683cadfe61a3fe9262a310", "dataset_uuid": "5a6840b28831a3e06abbbcc9", "task_type" : "classify"}' "http://127.0.0.1:5001/latest_task_status"
