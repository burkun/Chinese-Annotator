#!/bin/bash
# encoding=utf8
"""
this file is created by burkun
date:2018/3/14
"""
import chi_annotator.task_center.config as config
from chi_annotator.task_center.cmds import BatchTrainCmd, BatchPredictCmd, BatchNoDbPredictCmd, LatestStatusCmd
from chi_annotator.task_center.cmds import EmptyCmd
from chi_annotator.task_center.common import TaskManager
import os
import json
import datetime
import time
import pymongo
from flask_restful import abort
import flask_restful as restful
from flask import Flask, jsonify, request

# config for db config and task center config
GLOBAL_CONFIG = {}
DB_CONFIG_KEY = "db_config"
TASK_CONFIG_KEY = "task_center_config"
DEFAULT_BATCH_NUM = 64
TASK_TYPES = {"CLASSIFY": "classify"}

task_manager = None

def abort_message(msg):
    abort(404, message=msg)

class HelloWorld(restful.Resource):
    def get(self):
        return {"hello": "world"}

    def post(self):
        json_data = request.get_json(force=True)
        if json_data is None:
            abort_message("can not parse post data as json!")
        if "name" not in json_data:
            abort_message("can not find key: name")
        return {"hello" : "world " + json_data["name"]}

class TaskStatus(restful.Resource):
    """
    need task id(timestamp)
    """
    def post(self):
        pass

class LatestTaskStatus(restful.Resource):
    """
    need user id, dataset id, task_type
    """
    def post(self):
        json_data = request.get_json(force=True)
        if json_data is None:
            abort_message("can not parse post data as json!")
        uid = json_data.get("user_uuid", None)
        did = json_data.get("dataset_uuid", None)
        task_type = json_data.get("task_type", None)
        if uid is None or did is None or task_type is None:
            abort_message("can not find user_uuid or dataset_uuid or task_type")
        db_config = GLOBAL_CONFIG[DB_CONFIG_KEY].copy()
        task_config = config.CLASSIFY_TASK_CONFIG.copy()
        task_config["user_uuid"] = uid
        task_config["dataset_uuid"] = did
        task_config["model_type"] = task_type
        global_task_center_config = GLOBAL_CONFIG[TASK_CONFIG_KEY]
        merged_config = config.AnnotatorConfig(task_config, global_task_center_config)
        st_cmd = LatestStatusCmd(db_config, merged_config)
        ret_data = st_cmd()
        return jsonify({"status": ret_data[0], "end_time": ret_data[1]})

class BatchTrain(restful.Resource):
    """
    uid, did, task type, timestamp
    """
    def post(self):
        global task_manager
        json_data = request.get_json(force=True)
        if json_data is None:
            abort_message("can not parse post data as json!")
        start_timestamp = json_data.get("start_timestamp", None)
        model_type = json_data.get("task_type", None)
        uid = json_data.get("user_uuid", None)
        did = json_data.get("dataset_uuid", None)
        if start_timestamp is None or model_type is None or uid is None or did is None:
            abort_message("can not find uid or did or task type or start label timestamp")
        db_config = GLOBAL_CONFIG[DB_CONFIG_KEY].copy()
        task_config = config.CLASSIFY_TASK_CONFIG.copy()
        batch_number = task_config.get("batch_num", DEFAULT_BATCH_NUM)
        task_config["user_uuid"] = uid
        task_config["dataset_uuid"] = did
        task_config["model_type"] = model_type
        task_config["condition"] = {"timestamp": {"$gt": datetime.datetime.fromtimestamp(float(start_timestamp))}}
        task_config["sort_limit"] = ([("timestamp", pymongo.DESCENDING)], batch_number)
        task_config["model_version"] = time.time()
        # TODO pipline and embedding path is user defined
        task_config["pipeline"] = [
            "char_tokenizer",
            "sentence_embedding_extractor",
            "SVM_classifier"
        ]
        dir_name = os.path.realpath("../../")
        task_config["embedding_path"] = dir_name + "/tests/data/test_embedding/vec.txt"
        global_task_center_config = GLOBAL_CONFIG[TASK_CONFIG_KEY]
        merged_config = config.AnnotatorConfig(task_config, global_task_center_config)
        btc = BatchTrainCmd(db_config, merged_config)
        ret = task_manager.exec_command(btc)
        if ret:
            return jsonify({"status": "pendding", "task_id": btc.timestamp})
        else:
            return jsonify({"status": "error", "message": "queue full, can not add"})


class BatchDBPredict(restful.Resource):
    def post(self):
        pass

class BatchNoDBPredict(restful.Resource):
    def post(self):
        pass

def merge_config(old_config, new_config):
    for key in new_config:
        if new_config[key] is None and key in old_config:
            new_config[key] = old_config[key]
    for key in old_config:
        if key not in new_config:
            new_config[key] = old_config[key]
    return new_config

def load_config(config_path):
    m_config = {}
    if os.path.exists(config_path):
        m_config = {}
        with open(config_path) as config_file:
            m_config = json.loads(config_file.read())
    m_config["task_center_config"] = merge_config(config.TASK_CENTER_GLOBAL_CONFIG, m_config.get("task_center_config", {}))
    return m_config

def init_resource(rest_api):
    rest_api.add_resource(HelloWorld, "/hello_word")
    rest_api.add_resource(TaskStatus, "/task_status")
    rest_api.add_resource(LatestTaskStatus, "/latest_task_status")
    rest_api.add_resource(BatchTrain, "/batch_train")

def init_and_run(config_path):
    global GLOBAL_CONFIG
    global task_manager
    GLOBAL_CONFIG = load_config(config_path)
    # init task manager
    task_manager = TaskManager(GLOBAL_CONFIG[TASK_CONFIG_KEY]["max_process_number"],
                               GLOBAL_CONFIG[TASK_CONFIG_KEY]["max_task_in_queue"])
    # active task manager, let it on process not thread
    task_manager.exec_command(EmptyCmd())
    port = GLOBAL_CONFIG[TASK_CONFIG_KEY]["port"]
    debug = GLOBAL_CONFIG[TASK_CONFIG_KEY]["flask_debug"]
    flask_app = Flask(__name__)
    api = restful.Api(flask_app)
    init_resource(api)
    flask_app.run(port=port, debug=debug)

if __name__ == "__main__":
    init_and_run("../../config/sys_config.json")
