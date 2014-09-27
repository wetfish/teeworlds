#!/bin/bash
# Load password from config.sh
source config.sh

config="config/$1.conf"
temp="/tmp/teeworlds.$RANDOM.conf"

# Copy existing config into temp file
cat $config > $temp

# Append password
echo "sv_rcon_password $adminpass" >> $temp
echo "sv_rcon_mod_password $modpass" >> $temp

teeworlds-server -f $temp
