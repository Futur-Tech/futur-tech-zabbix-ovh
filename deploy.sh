#!/usr/bin/env bash

source "$(dirname "$0")/ft-util/ft_util_inc_var"
source "$(dirname "$0")/ft-util/ft_util_inc_func"
source "$(dirname "$0")/ft-util/ft_util_sudoersd"
source "$(dirname "$0")/ft-util/ft_util_usrmgmt"

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
$S_DIR/ft-util/ft_util_conf-update -s "$S_DIR/etc/template_api.conf" -d "${etc_dir}/" -r

enforce_security exec "$bin_dir" zabbix
enforce_security conf "$etc_dir" zabbix

echo "
  SETUP SUDOERS FILE
------------------------------------------"

bak_if_exist "/etc/sudoers.d/${app_name}"
sudoersd_reset_file "$app_name" "zabbix"
sudoersd_addto_file "$app_name" "zabbix" "${S_DIR_PATH}/deploy-update.sh"
show_bak_diff_rm "/etc/sudoers.d/${app_name}"

exit
