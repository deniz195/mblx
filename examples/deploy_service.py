#!/usr/local/bin/python3.6
# import sys
# sys.path.append('..')

from mblx import linux_service as ls

dry_run = True
dry_run = False

params = {}
params['fw_name'] = 'sensor-fw'
params['fw_description'] = 'sensor firwmware service'
params['main'] = 'run_rpi_sensor_hub.py'
params.update(ls.determine_paths(params))

# run stuff
ls.try_shell('pwd')

ls.make_run_sh(params = params)
ls.install_firmware(params = params, copy_files = not dry_run)

