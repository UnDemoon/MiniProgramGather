###
# @Author: your name
# @Date: 2021-03-23 14:29:47
# @LastEditTime: 2021-03-23 16:59:11
# @LastEditors: Please set LastEditors
# @Description: In User Settings Edit
# @FilePath: \MiniProgramGather\manualRun.sh
###
cd /www/wwwroot/MiniProgramGather/ || exit
# shellcheck disable=SC2009
# shellcheck disable=SC2126
count=$(ps -ef | grep MiniProgramGather/main.py | grep -v "grep" | wc -l)
if [ 0 == "$count" ]; then
  /usr/bin/python3 /www/wwwroot/MiniProgramGather/main.py "$1"
fi
