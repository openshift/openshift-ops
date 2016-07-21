#!/bin/bash -e

# This is useful so we can debug containers running inside of OpenShift that are
# failing to start properly.
if [ "$OO_PAUSE_ON_START" = "true" ] ; then
  echo
  echo "This container's startup has been paused indefinitely because OO_PAUSE_ON_START has been set."
  echo
  while true ; do
    sleep 10
  done
fi

# interactive shells read .bashrc (which this script doesn't execute as) so force it
source /root/.bashrc

# Configure the container
time ansible-playbook /root/config.yml

# Send a heartbeat when the container starts up
/usr/bin/ops-zagg-client --send-heartbeat

CLUSTER_ZAGG_FILE=/etc/openshift_tools/clusterwide_zagg_client.yaml
if [ -a $CLUSTER_ZAGG_FILE ] ; then
  /usr/bin/ops-zagg-client --send-heartbeat -c $CLUSTER_ZAGG_FILE
fi

# fire off the check pmcd status script
check-pmcd-status.sh &
# fire off the pmcd script
/usr/share/pcp/lib/pmcd start &

# Run the main service of this container
echo
echo 'Starting crond'
echo '---------------'
exec /usr/sbin/crond -n -m off

