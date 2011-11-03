mkdir -p $1/`date +%Y%m%d%H`
pid=`sudo -u $2 jps | grep $3| awk -F " " '{print $1}'`
sudo -u $2 jmap -histo $pid > $1/`date +%Y%m%d%H`/jmap_${pid}_`date +%Y%m%d%H%M%S`.out
