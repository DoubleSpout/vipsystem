#!/usr/bin/env python
from flask import Flask
import config


app = Flask(__name__,static_folder='statics', static_url_path='/static')
__all__ = ["controllers","models","config"]

