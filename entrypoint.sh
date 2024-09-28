#!/bin/bash

# Export all environment variables to a file
printenv | sed 's/^\(.*\)$/export \1/g' > /etc/environment

# Start cron in the foreground
cron -f
