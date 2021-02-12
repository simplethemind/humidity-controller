#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import humidifier

bind = "0.0.0.0:6042"
backlog = 64
workers = 3
loglevel = "info"

# Server hooks
def on_starting(server):
    humidifier.start_logger()
