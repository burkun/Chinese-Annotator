#!/bin/bash
# encoding=utf8
"""
this file is created by burkun
date: 
"""
from flask import Flask
import flask_restful as restful
import config
from flask_restful import reqparse, abort



class TaskCenterWebApi(restful.Resource):
    def __init__(self):
        self.port = config.TASK_CENTER_GLOBAL_CONFIG.get("port", 5000)
        self.time_out = config.TASK_CENTER_GLOBAL_CONFIG.get("timeout", 1000)


class HelloWorld(restful.Resource):
    def get(self):
        return {"hello": "world"}

    def post(self):
        pass


class TaskStatus(restful.Resource):
    def get(self):
        pass

    def post(self):
        pass



def init_resource(rest_api):
    rest_api.add_resource(HelloWorld, "/helloword")


def init_and_run():
    port = config.TASK_CENTER_GLOBAL_CONFIG.get("port", 5000)
    debug = config.TASK_CENTER_GLOBAL_CONFIG.get("flask_debug", False)
    flask_app = Flask(__name__)
    api = restful.Api(flask_app)
    init_resource(api)
    flask_app.run(port=port, debug=debug)

if __name__ == "__main__":
    init_and_run()