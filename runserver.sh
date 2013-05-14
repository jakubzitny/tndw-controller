#!/bin/bash
# bash script to initialize testing environment
# launches django dev webserver and custom multi-threaded redis listener
# (c) Jakub Zitny, 2013

E="tmux send-keys Enter"

tmux new-session -d -s tndw-back -n 'runserver'
tmux send-keys "python3 manage.py runserver 0.0.0.0:8081"; $E
tmux new-window -t tndw-back -n 'listener'
tmux send-keys "python3 manage.py listener"; $E


