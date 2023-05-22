#!/usr/bin/env bash

source "$(dirname "$0")/ft-util/ft_util_inc_var"
source "$(dirname "$0")/ft-util/ft_util_inc_func"

app_name="futur-tech-zabbix-ovh"
required_pkg_arr=("python3" "python3-pip")

bin_dir="/usr/lib/zabbix/externalscripts"
etc_dir="/usr/local/etc/${app_name}"
src_dir="/usr/local/src/${app_name}"
sudoers_etc="/etc/sudoers.d/${app_name}"

$S_LOG -d $S_NAME "Start $S_DIR_NAME/$S_NAME $*"

echo "
  INSTALL NEEDED PACKAGES & FILES
------------------------------------------"

$S_DIR_PATH/ft-util/ft_util_pkg -u -i ${required_pkg_arr[@]} || exit 1

run_cmd_log pip3 install ovh

mkdir_if_missing "${etc_dir}"

$S_DIR/ft-util/ft_util_file-deploy "$S_DIR/bin/ovh-api-get.py" "${bin_dir}/ovh-api-get.py"
$S_DIR/ft-util/ft_util_file-deploy "$S_DIR/bin/ovh-api-post.py" "${bin_dir}/ovh-api-post.py"
$S_DIR/ft-util/ft_util_conf-update -s "$S_DIR/etc/default_api.conf" -d "${etc_dir}/" -r

echo "
  SETUP SUDOERS FILE
------------------------------------------"

$S_LOG -d $S_NAME -d "$sudoers_etc" "==============================="

echo "Defaults:zabbix !requiretty" | sudo EDITOR='tee' visudo --file=$sudoers_etc &>/dev/null
echo "zabbix ALL=(ALL) NOPASSWD:${src_dir}/deploy-update.sh" | sudo EDITOR='tee -a' visudo --file=$sudoers_etc &>/dev/null

cat $sudoers_etc | $S_LOG -d "$S_NAME" -d "$sudoers_etc" -i

$S_LOG -d $S_NAME -d "$sudoers_etc" "==============================="

exit
