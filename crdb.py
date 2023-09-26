from sos.report.plugins import Plugin, IndependentPlugin
import os
from datetime import datetime

class crdb(Plugin, IndependentPlugin):
    """
    This plugin will capture information about CockroachDB
    installed on the system.

    This information will be collected by running a debug lite via CockroachDB.
    This will include information from across the cluster.
    """

    short_desc = 'CockroachDB debug lite'

    plugin_name = "crdb"

    option_list = [
            ("crdbexec", "full path to the cockroach executable if it is not in your path", '', "cockroach"),
            ("url", "pgurl for the cluster", '', "postgres://localhost:26257"),
            ("certsdir", "path to the certificate directory containing the CA and client certs and client key", '', ""),
            ("insecure", "Set to true if using an insecure cluster", '', False),
            ("redact", "Set to true to redact the debug zip data", '', False)
            ]

    def setup(self):
#        crdbout = self.collect_cmd_output("/home/ubuntu/cockroach debug zip --url 'postgres://localhost:26257' --insecure /tmp/debug-crdb.zip", sizelimit=None, suggest_filename="cockroach")
        url = self.get_option('url')
        certsdir = self.get_option('certsdir')
        crdbexec = self.get_option('crdbexec')

        now = datetime.now()
        mydate = now.strftime("%Y-%m-%d-%H:%M:%S")
        debugfile = "/tmp/debug-crdb" + mydate + ".zip"

        if self.get_option("insecure"): 
            cmd = crdbexec + " debug zip --insecure --url " + url + " " + debugfile
        else:
            cmd = crdbexec + " debug zip --certs-dir " + certsdir + " --url " + url + " " + debugfile

        if self.get_option("redact"):
            cmd = cmd + " --redact"

#        print(cmd)
        crdbout = self.collect_cmd_output(cmd, sizelimit=None, suggest_filename="cockroach")
        if crdbout['status'] == 0:
            self.add_copy_spec(debugfile, sizelimit=None)


