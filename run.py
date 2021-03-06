#!/usr/bin/env python
"""
Build and run refl1d.

Usage:

./run.py [refl1d cli args]
"""
import os
import sys
from os.path import abspath, join as joinpath, dirname

def addpath(path):
    """
    Add a directory to the python path environment, and to the PYTHONPATH
    environment variable for subprocesses.
    """
    path = abspath(path)
    if 'PYTHONPATH' in os.environ:
        PYTHONPATH = path + os.pathsep + os.environ['PYTHONPATH']
    else:
        PYTHONPATH = path
    os.environ['PYTHONPATH'] = PYTHONPATH
    sys.path.insert(0, path)

from contextlib import contextmanager
@contextmanager
def cd(path):
    old_dir = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(old_dir)

def import_dll(module, build_path):
    """Import a DLL from the build directory"""
    import imp
    try:
        import sysconfig
        ext = sysconfig.get_config_var('SO')
    except ImportError:
        ext = '.pyd' if sys.platform == 'win32' else '.so'

    # build_path comes from context
    path = joinpath(build_path, *module.split('.'))+ext
    #print(" ".join(("importing", module, "from", path)))
    mod = imp.load_dynamic(module, path)

    # make sure module can be imported from package
    package_name, module_name = module.rsplit('.', 1)
    package = __import__(package_name)
    setattr(package, module_name, mod)
    return mod

def prepare_environment():
    from distutils.util import get_platform
    platform = '.%s-%s'%(get_platform(),sys.version[:3])

    #sys.dont_write_bytecode = True

    # Make sure that we have a private version of mplconfig
    #mplconfig = joinpath(os.getcwd(), '.mplconfig')
    #os.environ['MPLCONFIGDIR'] = mplconfig
    #if not os.path.exists(mplconfig):
    #    os.mkdir(mplconfig)

    #import numpy; numpy.seterr(all='raise')
    refl1d_root = abspath(dirname(__file__))
    periodictable_root = abspath(joinpath(refl1d_root, '..', 'periodictable'))
    bumps_root = abspath(joinpath(refl1d_root, '..', 'bumps'))
    refl1d_build = joinpath(refl1d_root, 'build', 'lib'+platform)

    # add bumps and periodictable to the path
    addpath(periodictable_root)
    addpath(bumps_root)

    # Force a rebuild of bumps and refl1d
    import subprocess
    with open(os.devnull, 'w') as devnull:
        with cd(refl1d_root):
            subprocess.call((sys.executable, "setup.py", "build"),
                            shell=False, stdout=devnull)

    # Add the build dir to the system path
    #addpath(refl1d_build)
    addpath(refl1d_root)
    import_dll('refl1d.reflmodule', refl1d_build)
    import_dll('refl1d.calc_g_zs_cex', refl1d_build)

    # Make sample data and models available
    os.environ['REFL1D_DATA'] = joinpath(refl1d_root, 'doc', '_examples')

    #print "\n".join(sys.path)

if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()
    prepare_environment()
    import refl1d.main
    refl1d.main.cli()
