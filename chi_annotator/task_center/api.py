#!/bin/bash
# encoding=utf8
"""
this file is created by burkun
date: 
"""
from flask import Flask
import flask_restful as restful
from chi_annotator.task_center import config
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


def init():
    flask_app = Flask(__name__)
    api = restful.Api(flask_app)
    api.add_resource(HelloWorld, "/")
    return flask_app


if __name__ == "__main__":
    flask_app = init()
    flask_app.run(debug=True)