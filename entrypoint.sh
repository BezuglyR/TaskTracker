#!/usr/bin/env bash

granian --interface asgi --host 0.0.0.0 --port 8000 --loop uvloop app.main:app