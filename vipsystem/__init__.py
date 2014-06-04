#!/usr/bin/env python
from flask import Flask
import config


app = Flask(__name__)
__all__ = ["controllers","models","config"]

