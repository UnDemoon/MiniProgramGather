###
# @Author: your name
# @Date: 2021-03-23 14:29:47
# @LastEditTime: 2021-03-23 16:59:11
# @LastEditors: Please set LastEditors
# @Description: In User Settings Edit
# @FilePath: \MiniProgramGather\manualRun.sh
###
cd /www/wwwroot/MiniProgramGather/ || exit
# shellcheck disable=SC2126
# shellcheck disable=SC2009
count=$(ps -ef | grep MiniProgramGather/main_test.py | grep -v "grep" | wc -l)
if [ 0 == "$count" ]; then
  timeout 30 /usr/bin/python3 /www/wwwroot/MiniProgramGather/main_test.py "$1"
fi
