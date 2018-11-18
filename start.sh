#!/bin/bash
# Load password from config.sh
set -e
cd ~/server
source config/config.sh

help() {
	# TODO: Expand upon this
	echo "Usage: $0 [--help, -h] [--version, -v] [--config, -c]" 1>&2
	exit 1
}

# Check that arguments were passed
if [[ $1 == "" ]]; then
	help
	exit
fi

# Parse arguments
! PARSE=$(getopt --options hv:c: --longoptions help,version:,config: --name "$0" -- "$@")
if [[ ${PIPESTATUS[0]} -ne 0 ]]; then
	help;
fi
eval set -- "$PARSE"

# Save arguments into variables
while true; do
	case "$1" in
		-h|--help)
			help
			shift ;;
		-v|--version)
			VERSIONARG="$2"
			shift 2 ;;
		-c|--config)
			CONFIGARG="$2"
			shift 2 ;;
		--)
			shift
			break ;;
		*)
			echo "whoops! (the programmer made a mistake!)"
			exit 3 ;;
	esac
done

## Check for 'all' arguments
if [ "$VERSIONARG" = "all" ]; then
	# Store all versions in array
	binaries=($(ls binaries))
else
	# Single version, check if exists, store in array
	# TODO: check if it exists
	binaries=("$VERSIONARG")
fi

if [ "$CONFIGARG" = "all" ]; then
	# Store all configs in array
	configs=($(find config/enabled -type f | sed 's%^config/enabled/%%'))
else
	# Single config, check if exists, store in array
	# TODO: check if it exists
	configs=("$CONFIGARG.conf")
fi

# Loop through chosen binaries and run with chosen configs.
for i in "${binaries[@]}"
do
	for c in "${configs[@]}"
	do
		cd ~/server
		config="config/enabled/$c"
		temp="teeworlds.$RANDOM.conf"
		cat $config >> "/tmp/$temp"

		cd /tmp
		echo "sv_rcon_password $adminpass" >> $temp
		echo "sv_rcon_mod_password $modpass" >> $temp

		# test run for now.
		#echo "Running config $config on version $i"
		~/server/binaries/$i/teeworlds_srv -f $temp &
	done
done
