#!/bin/bash
# vdpatch - script for patching virtual disk images
# (c) Jakub Zitny <jzitny@oldanygroup.cz>

INTERACTIVE=0
VERBOSE=0

#
# prints help message and quits
#
function help () {
	echo -e "Usage: $0 [-i | -c CHROOTSCRIPT] [-o OUTFMT] \033[4m/path/to/vmimage.vmdk\033[0m"
	echo -e "Manpages: man vdpatch"
	exit 0
}

#
# universal function for converting image files
# $1 - input format
# $2 - input file
# $3 - output format
# $4 - output file
#
function convertImage () {
	IN=$1
	INFILE=$2
	OUT=$3
	OUTFILE=$4
	$QEMUIMG convert -f $IN $INFILE -O $OUT $OUTFILE
}

#
# unmaps the contents of the image
#
function cleanEnv () {
	touch $MNTPOINT/etc/resolv.conf
	$UMOUNT $MNTPOINT/dev
	$UMOUNT $MNTPOINT/proc
	$UMOUNT $MNTPOINT/sys
	if [ $NOBOOT -ne 1 ]; then
		$UMOUNT $MNTPOINT/boot
	fi
	$UMOUNT -d $MNTPOINT 2> /dev/null
	
	for lvpart in $LVPARTS
	do
		$DMSETUP remove $lvpart
	done
	
	for i in 5 4 3 2 1
	do
		$DMSETUP remove /dev/mapper/`basename $NBDPOINT`p$i 2>/dev/null
	done

	rm -r $MNTPOINT
	$KPARTX -d $NBDPOINT
	$QEMUNBD -d $NBDPOINT > /dev/null
}

#
# the main part - chroot
# $1 if set then run non-interactively
# otherwise chroot with bash
#
function run () {
	$CHROOT $MNTPOINT bash $1
}

#
# detects the contents of the image
# and maps it into the system
#
function decomposeImage () {
	i=0
	while true
	do
		i=$((i+1))
		$QEMUNBD -c /dev/nbd$i $IMAGEIN 2> /dev/null && break
	done
	NBDPOINT=/dev/nbd$i
	MNTPOINT=/tmp/vdpatch_`date +%s`
	TMPMNTPOINT=/tmp/tmp_vdpatch_`date +%s`
	mkdir -p $MNTPOINT
	mkdir -p $TMPMNTPOINT

	NOBOOT=0
	pnumber=0
	for partition in `$PARTED -m $NBDPOINT unit B p | tail -n +3 | grep -v swap`
	do
		if `echo "${partition}" | grep boot > /dev/null 2>&1`; then
			OFFSET=$(echo $partition | sed 's/B//g' | cut -d: -f2)
			$MOUNT -o loop,offset=$OFFSET $NBDPOINT $TMPMNTPOINT
			if `ls $TMPMNTPOINT | grep grub > /dev/null`; then
				BOOT="$MOUNT -o loop,offset=$OFFSET $NBDPOINT $MNTPOINT/boot"
			elif `ls $TMPMNTPOINT | grep etc > /dev/null`; then
				ROOT="$MOUNT -o loop,offset=$OFFSET $NBDPOINT $MNTPOINT"
				NOBOOT=1
			else
				true
			fi
			$UMOUNT $TMPMNTPOINT 2> /dev/null
		elif `echo "${partition}" | grep -i LVM > /dev/null 2>&1`; then
			$KPARTX -a $NBDPOINT
			$VGSCAN
			$VGCHANGE -a y
			VGNAME=$(pvscan | awk /`basename $NBDPOINT`/'{print $4}')
			LVPARTS=$(ls /dev/mapper/$VGNAME-*)
			for lvpart in $LVPARTS
			do
				case "${lvpart#*-}" in
					root) ROOT="$MOUNT $lvpart $MNTPOINT";;
					boot) BOOT="$MOUNT $lvpart $MNTPOINT/boot";;
					swap*) true;;
					\?) echo $lvpart; exit 123;;
				esac
			done
		else
			OFFSET=$(echo $partition | sed 's/B//g' | cut -d: -f2)
			$MOUNT -o loop,offset=$OFFSET $NBDPOINT $TMPMNTPOINT 2> /dev/null
			if `ls $TMPMNTPOINT | grep etc`; then
				ROOT="$MOUNT -o loop,offset=$OFFSET $NBDPOINT $MNTPOINT"
			fi
			$UMOUNT -l $TMPMNTPOINT 2> /dev/null
		fi
		pnumber=$((pnumber+1))
	done
	
	# prepare chroot env
	$ROOT
	if [ $NOBOOT -ne 1 ]; then
		$BOOT
	fi
	
	$MOUNT -o bind /dev $MNTPOINT/dev
	$MOUNT -o bind /proc $MNTPOINT/proc
	mkdir -p $MNTPOINT/sys
	$MOUNT -o bind /sys $MNTPOINT/sys
	
	rm -f $MNTPOINT/etc/resolv.conf
	cp /etc/resolv.conf $MNTPOINT/etc/resolv.conf
}

#
# detects virtual disk image format
#
function detectImage () {
	fileinfo=$(file $IMAGEIN)
	case "${IMAGEIN/*.}" in
		qcow2) INFMT="qcow2";;
		qcow) INFMT="qcow";;
		vmdk) INFMT="vmdk";;
		vdi) INFMT="vdi";;
		raw) INFMT="raw";;
		\?) die "Wrong input image format." 6;;
	esac
}

#
# controls needed software
#
function controlSoftware () {
	QEMUIMG=$(which qemu-img)
	QEMUNBD=`which qemu-nbd`
	if [ $? -eq 1 ]; then
		die "Install qemu-kvm.. or qemu-utils" 5
	fi
	KPARTX=$(which kpartx)
	if [ $? -eq 1 ]; then
		die "Install kpartx.." 5
	fi
	LOSETUP=$(which losetup)
	if [ $? -eq 1 ]; then
		die "Install losetup.." 5
	fi
	DMSETUP=$(which dmsetup)
	VGSCAN=$(which vgscan)
	VGCHANGE=$(which vgchange)
	if [ $? -eq 1 ]; then
		die "Install lvm2 utilities.." 5
	fi
	PARTED=$(which parted)
	if [ $? -eq 1 ]; then
		die "Install parted.." 5
	fi

	MOUNT=`which mount`
	UMOUNT=`which umount`
	CHROOT=`which chroot`
	modprobe dm-mod
	modprobe nbd
}

#
# universal exit function
# prints message and exits with given exitcode
# $1 message
# $2 exitcode
#
function die () {
	echo "$1"
	exit $2
}


#
# process command line arguments
#
function processArgs () {
 	while getopts hc:io:vV opt
	do
    	case "$opt" in
      		h) help; exit 0;; 
      		i) INTERACTIVE=1;;
      		v) VERBOSE=1;;
      		c) CHROOTSCRIPT="${OPTARG}";;
			o) OUTFMT="${OPTARG}";;
			V) echo "1.0"; exit 0;;
     		\?) help; exit 1;;
    	esac
	done
	shift $(($OPTIND - 1))

	IMAGEIN="${@}"

	# test arguments
	if [ $UID -ne 0 ]; then
		die "You should be root." 7
	fi
	if ! [ -f "$IMAGEIN" ]; then
		die "Bad image." 2
	fi
	if [ $INTERACTIVE -eq 0 -a -z "$CHROOTSCRIPT" ]; then
		die "Non-interactive mode should be provided with chrootscript." 3
	fi
	if ! [ -z "$CHROOTSCRIPT" -o -f "$CHROOTSCRIPT" ]; then
		die "Bad chroot script." 4
	fi
	if [[ "$OUTFMT" != "" ]] &&
		 [[ "$OUTFMT" != "qcow2" ]] &&
	   [[ "$OUTFMT" != "qcow" ]] &&
	   [[ "$OUTFMT" != "vmdk" ]] &&
	   [[ "$OUTFMT" != "vdi" ]] &&
	   [[ "$OUTFMT" != "raw" ]]; then
		die "Bad output format." 8
	fi
}

#
# main function
#
function main () {
	processArgs "$@"
	[[ $VERBOSE -eq 1 ]] && echo "Controlling software.."
	controlSoftware
	[[ $VERBOSE -eq 1 ]] && echo "Detecting image.."
	detectImage
	[[ $VERBOSE -eq 1 ]] && echo "Decomposing image.."
	decomposeImage
	
	[[ $VERBOSE -eq 1 ]] && echo "Chrooting.."
	if [ $INTERACTIVE -eq 1 ]; then
		run
	else
		cp $CHROOTSCRIPT $MNTPOINT
		run $CHROOTSCRIPT
		rm $MNTPOINT/$CHROOTSCRIPT
	fi

	cleanEnv
	[[ $VERBOSE -eq 1 ]] && echo "..done."

	if [[ -n $OUTFMT ]] && [[ "$OUTFMT" != "$INFMT" ]]; then
		[[ $VERBOSE -eq 1 ]] && echo "Converting image to $OUTFMT"
		convertImage $INFMT $IMAGEIN $OUTFMT ${IMAGEIN%.*}.$OUTFMT
	fi
	[[ $VERBOSE -eq 1 ]] && echo "Bye."
}

main "$@"
exit 0

