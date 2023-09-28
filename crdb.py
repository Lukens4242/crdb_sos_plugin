from sos.report.plugins import Plugin, IndependentPlugin, PluginOpt
import os, sys, re
from datetime import datetime
import subprocess

class crdb(Plugin, IndependentPlugin):
    """
    This plugin will capture information about CockroachDB
    installed on the system.

    This information will be collected by running a debug lite via CockroachDB.
    This will include information from across the cluster.
    """

    short_desc = 'CockroachDB debug'

    plugin_name = "crdb"
    profiles = ('services',)

    #null things out to start with
    pid = ''
    cmdline = ''
    optinsec = False 
    crdbexec = ''

    ps_output = subprocess.check_output(['ps', 'aux']).decode('utf-8').split('\n')
    for line in ps_output:
        if 'cockroach start' in line.lower():
            fields = line.split()
            pid = fields[1]
            cmdline = ' '.join(fields[10:])

    if "--insecure" in cmdline:
        optinsec=True

    crdbexec = "/proc/" + pid + "/exe"

    match = re.search(r'--advertise-addr=([^ ]+)', cmdline)
    if match is None:
        url = ''
    else: 
        advertise = match.group(1)
        url = "postgres://" + advertise

    match = re.search(r'--certs-dir\s+([^\s]+)', cmdline)
    if match is None:
        certs = ''
    else:
        mycerts = match.group(1)
        certs = "/proc/" + pid + "/cwd/" + mycerts


    option_list = [
        PluginOpt('crdbexec', desc='full path to the cockroach executable if it is not in your path', default=crdbexec),
        PluginOpt('url', desc='pgurl for the cluster', default=url),
        PluginOpt('certsdir', desc='path to the certificate directory containing the CA and client certs and client key', default=certs),
        PluginOpt('insecure', desc='Set to true if using an insecure cluster', default=optinsec),
        PluginOpt('redact', desc='Set to true to redact the debug zip data', default=False)
            ]

    def setup(self):
#       crdbout = self.collect_cmd_output("/home/ubuntu/cockroach debug zip --url 'postgres://localhost:26257' --insecure /tmp/debug-crdb.zip", sizelimit=None, suggest_filename="cockroach")
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

        pid=''
        ps_output = subprocess.check_output(['ps', 'aux']).decode('utf-8').split('\n')
        for line in ps_output:
            if 'cockroach start' in line.lower():
                fields = line.split()
                pid = fields[1]

        if pid:
            crdbout = self.collect_cmd_output(cmd, sizelimit=None, suggest_filename="cockroach")
            if crdbout['status'] == 0:
                self.add_copy_spec(debugfile, sizelimit=None)


