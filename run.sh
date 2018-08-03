#!/bin/sh

. .env/bin/activate
tmux \
	new-session 'laneyad' \; \
	new-window 'laneya'
