!#/bin/bash
+
+#get the number of projects except which are ours
+projects=$(oca get projects | egrep -Ev 'NAME|default|openshift|openshift-infra' | wc -l)
+
+echo
+echo "Number of projects: $projects "
+echo
+echo "Sending project count to Zabbix"
+
+#this script is the sender
+ops-zagg-client -k "openshift.project.counter" -o "$projects"
