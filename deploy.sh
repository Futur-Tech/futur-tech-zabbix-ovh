#!/usr/bin/env bash

source "$(dirname "$0")/ft-util/ft_util_inc_var"

APP_NAME="futur-tech-zabbix-ovh"
REQUIRED_PKG_ARR=( "python3" "python3-pip" )

BIN_DIR="/usr/lib/zabbix/externalscripts"
ETC_DIR="/usr/local/etc/${APP_NAME}"
SRC_DIR="/usr/local/src/${APP_NAME}"
SUDOERS_ETC="/etc/sudoers.d/${APP_NAME}"

$S_LOG -d $S_NAME "Start $S_DIR_NAME/$S_NAME $*"

echo
echo "------------------------------------------"
echo "  INSTALL NEEDED PACKAGES & FILES"
echo "------------------------------------------"
echo

$S_DIR_PATH/ft-util/ft_util_pkg -u -i ${REQUIRED_PKG_ARR[@]} || exit 1
 
pip3 install ovh | $S_LOG -d "$S_NAME" -d "pip3 install ovh" -i 
$S_LOG -s $? -d $S_NAME "Installing Python3 OVH returned EXIT_CODE=$?"

if [ ! -d "${ETC_DIR}" ] ; then mkdir "${ETC_DIR}" ; $S_LOG -s $? -d $S_NAME "Creating ${ETC_DIR} returned EXIT_CODE=$?" ; fi

$S_DIR/ft-util/ft_util_file-deploy "$S_DIR/bin/ovh-api-get.py" "${BIN_DIR}/ovh-api-get.py"
$S_DIR/ft-util/ft_util_conf-update -s "$S_DIR/etc/default_api.conf" -d "${ETC_DIR}/" -r

echo
echo "------------------------------------------"
echo "  SETUP SUDOERS FILE"
echo "------------------------------------------"
echo

$S_LOG -d $S_NAME -d "$SUDOERS_ETC" "==============================="
$S_LOG -d $S_NAME -d "$SUDOERS_ETC" "==== SUDOERS CONFIGURATION ===="
$S_LOG -d $S_NAME -d "$SUDOERS_ETC" "==============================="

echo "Defaults:zabbix !requiretty" | sudo EDITOR='tee' visudo --file=$SUDOERS_ETC &>/dev/null
echo "zabbix ALL=(ALL) NOPASSWD:${SRC_DIR}/deploy-update.sh" | sudo EDITOR='tee -a' visudo --file=$SUDOERS_ETC &>/dev/null

cat $SUDOERS_ETC | $S_LOG -d "$S_NAME" -d "$SUDOERS_ETC" -i 

$S_LOG -d $S_NAME -d "$SUDOERS_ETC" "==============================="
$S_LOG -d $S_NAME -d "$SUDOERS_ETC" "==============================="

echo
echo "------------------------------------------"
echo "  RESTART ZABBIX LATER"
echo "------------------------------------------"
echo

echo "service zabbix-agent restart" | at now + 1 min &>/dev/null ## restart zabbix agent with a delay
$S_LOG -s $? -d "$S_NAME" "Scheduling Zabbix Agent Restart"

$S_LOG -d "$S_NAME" "End $S_NAME"

exit