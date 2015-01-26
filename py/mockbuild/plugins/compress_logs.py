# vim:expandtab:autoindent:tabstop=4:shiftwidth=4:filetype=python:textwidth=0:
# License: GPL2 or later see COPYING

import os.path

from mockbuild.trace_decorator import traceLog, getLog
from mockbuild import util

requires_api_version = "1.1"

class CompressLogsPlugin(object):
    """Compress logs in resultdir."""
    @traceLog()
    def __init__(self, plugins, conf, buildroot):
        self.buildroot = buildroot
        self.config = buildroot.config
        self.state = buildroot.state
        self.conf = conf
        self.command = self.conf['command']
        plugins.add_hook("postbuild", self._compress_logs)
        getLog().info("compress_logs: initialized")

    @traceLog()
    def _compress_logs(self):
        logger = getLog()
        for f_name in ('root.log', 'build.log', 'state.log', 'available_pkgs', 'installed_pkgs'):
            f_path = os.path.join(self.buildroot.resultdir, f_name)
            if os.path.exists(f_path):
                command = "{0} {1}".format(self.command, f_path)
                logger.debug("Running {0}".format(command))
                util.do(command, shell=True)


def init(plugins, compress_conf, buildroot):
    CompressLogsPlugin(plugins, compress_conf, buildroot)
