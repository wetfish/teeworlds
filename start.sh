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
if [[ $# == 0 ]]; then
	help
fi

# Parse arguments
! PARSE=$(getopt --options hv:c: --longoptions help,version:,config: --name "$0" -- "$@")
if [[ ${PIPESTATUS[0]} -ne 0 ]]; then
	help
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
	BINARIES=($(ls binaries))
else
	# Single version, check if exists, store in array
	if [ -d "binaries/$VERSIONARG" ]; then
		BINARIES=("$VERSIONARG")
	else
		echo "Binary $VERSIONARG doesn't exist!"
		exit 1
	fi
fi

if [ "$CONFIGARG" = "all" ]; then
	# Store all configs in array
	CONFIGS=($(find config/enabled -type f | sed 's%^config/enabled/%%'))
else
	# Single config, check if exists, store in array
	if [ -f "config/enabled/$CONFIGARG.conf" ]; then
		CONFIGS=("$CONFIGARG.conf")
	else
		echo "Config $CONFIGARG.conf not enabled or doesn't exist!"
		exit 1
	fi
fi

# Loop through chosen binaries and run with chosen configs.
for i in "${BINARIES[@]}"
do
	for c in "${CONFIGS[@]}"
	do
		cd ~/server
		CONFIG="config/enabled/$c"
		TEMP="teeworlds.$RANDOM.conf"
		cat "$CONFIG" >> "/tmp/$TEMP"

		cd /tmp
		echo "sv_rcon_password $adminpass" >> $TEMP
		echo "sv_rcon_mod_password $modpass" >> $TEMP

		# test run for now.
		#echo "Running config $CONFIG on version $i"
		~/server/binaries/"$i"/teeworlds_srv -f $TEMP &
		rm $TEMP
	done
done
