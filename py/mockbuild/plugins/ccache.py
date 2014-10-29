# vim:expandtab:autoindent:tabstop=4:shiftwidth=4:filetype=python:textwidth=0:
# License: GPL2 or later see COPYING
# Written by Michael Brown
# Copyright (C) 2007 Michael E Brown <mebrown@michaels-house.net>

# python library imports

# our imports
from mockbuild.trace_decorator import traceLog, getLog
import mockbuild.util

from mockbuild.mounts import BindMountPoint

requires_api_version = "1.1"

# plugin entry point
@traceLog()
def init(plugins, conf, buildroot):
    CCache(plugins, conf, buildroot)

# classes
class CCache(object):
    """enables ccache in buildroot/rpmbuild"""
    @traceLog()
    def __init__(self, plugins, conf, buildroot):
        self.buildroot = buildroot
        self.config = buildroot.config
        self.state = buildroot.state
        self.ccache_opts = conf
        self.ccachePath = self.ccache_opts['dir'] % self.ccache_opts
        buildroot.preexisting_deps.append("ccache")
        plugins.add_hook("prebuild", self._ccacheBuildHook)
        plugins.add_hook("preinit", self._ccachePreInitHook)
        buildroot.mounts.add(BindMountPoint(srcpath=self.ccachePath, bindpath=buildroot.make_chroot_path("/tmp/ccache")))

    # =============
    # 'Private' API
    # =============
    # set the max size before we actually use it during a build. ccache itself
    # manages size and settings. we also set a few variables used by ccache to
    # find the shared cache.
    @traceLog()
    def _ccacheBuildHook(self):
        self.buildroot.doChroot(["ccache", "-M", str(self.ccache_opts['max_cache_size'])], shell=False)

    # set up the ccache dir.
    # we also set a few variables used by ccache to find the shared cache.
    @traceLog()
    def _ccachePreInitHook(self):
        getLog().info("enabled ccache")
        envupd = {"CCACHE_DIR": "/tmp/ccache", "CCACHE_UMASK": "002"}
        if self.ccache_opts.get('compress') is not None:
            envupd["CCACHE_COMPRESS"] = str(self.ccache_opts['compress'])
        self.buildroot.env.update(envupd)

        mockbuild.util.mkdirIfAbsent(self.buildroot.make_chroot_path('/tmp/ccache'))
        mockbuild.util.mkdirIfAbsent(self.ccachePath)
        self.buildroot.uid_manager.changeOwner(self.ccachePath)
