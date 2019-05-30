import os
from string import Template

def try_shell(cmd):
    print(f'Executing: "{cmd}"')
    r = os.system(cmd) 
    if r:
        raise Exception(f'Shell command failed ({r}): "{cmd}"')
    return r

def get_main_info():
    '''
    Returns a dictionary with information about the running top level Python
    script:
    ---------------------------------------------------------------------------
    dir:    directory containing script or compiled executable
    name:   name of script or executable
    source: name of source code file
    ---------------------------------------------------------------------------
    "name" and "source" are identical if and only if running interpreted code.
    When running code compiled by py2exe or cx_freeze, "source" contains
    the name of the originating Python script.
    If compiled by PyInstaller, "source" contains no meaningful information.
    '''

    import os, sys, inspect
    #---------------------------------------------------------------------------
    # scan through call stack for caller information
    #---------------------------------------------------------------------------
    for teil in inspect.stack():
        # skip system calls
        if teil[1].startswith("<"):
            continue
        if teil[1].upper().startswith(sys.exec_prefix.upper()):
            continue
        trc = teil[1]
        
    # trc contains highest level calling script name
    # check if we have been compiled
    if getattr(sys, 'frozen', False):
        scriptdir, scriptname = os.path.split(sys.executable)
        return {"dir": scriptdir,
                "name": scriptname,
                "source": trc}

    # from here on, we are in the interpreted case
    scriptdir, trc = os.path.split(trc)
    # if trc did not contain directory information,
    # the current working directory is what we need
    if not scriptdir:
        scriptdir = os.getcwd()

    scr_dict ={"name": trc,
               "source": trc,
               "dir": scriptdir}
    return scr_dict



def determine_paths(params):
    from pathlib import Path

    current_main_dir = Path(get_main_info()['dir']).absolute()
    print(f'Install runs from {current_main_dir}')

    base_dir = current_main_dir
    
    def does_contain_main(path):
        fn = path.joinpath(params['main'])
        print(fn)
        return fn.exists()

    max_level_up = 3
    while not does_contain_main(base_dir):
        base_dir = base_dir.parent
        if max_level_up:
            max_level_up -= 1
        else:
            raise RuntimeError('Couldnt find main python script for service in any parent directory!')

    print(f'Installing base directory: {base_dir}')

    service_dir = base_dir.joinpath('service')
    service_dir.mkdir(exist_ok = True)

    print(f'Working directory {service_dir}')
    os.chdir(service_dir)

    params['service_dir'] = service_dir
    params['base_dir'] = base_dir
    # params['fw_name'] = 'my-fw'
    # params['fw_description'] = 'lds firwmware service'
    # params['main'] = 'run_rpi_lds.py'

    return params


# templating
fw_service_template = '''[Unit]
Description=$fw_description

[Service]
User=pi
Group=pi
WorkingDirectory=$base_dir
ExecStart=$base_dir/run.sh
PIDFile=/run/$main.pid

StandardInput=null
StandardOutput=null
StandardError=null

[Install]
WantedBy=multi-user.target
Alias=$fw_name.service
'''

def install_firmware(params, copy_files = True):
    fw_name = params['fw_name']
    service_dir = params['service_dir']

    # write templates 
    service_fn = f'{service_dir}/{fw_name}.service'
    print(f'Writing {service_fn}')
    with open(service_fn, "w") as text_file:
        s = Template(fw_service_template).substitute(params)
        text_file.write(s)

    if copy_files:
        try_shell(f'sudo cp {service_fn} /lib/systemd/system/')
        try_shell(f'sudo systemctl daemon-reload')
        # try_shell('sudo systemctl enable pigpiod')
        try_shell(f'sudo systemctl enable {fw_name}')
    else:
        print('Skip copying files!')


# pigpiod_service_template = '''[Unit]
# Description=pigpiod service

# [Service]
# User=root
# Group=root
# WorkingDirectory=$base_dir
# ExecStart=/usr/local/bin/pigpiod
# PIDFile=/var/run/pigpio.pid

# StandardInput=null
# StandardOutput=null
# StandardError=null

# [Install]
# WantedBy=multi-user.target
# Alias=pigpiod.service
# '''



# fn = f'{service_dir}/pigpiod.service'
# print(f'Writing {fn}')
# with open(fn, "w") as text_file:
#     s = Template(pigpiod_service_template).substitute(params)
#     text_file.write(s)

# write templates 
run_sh_template = '''#!/bin/bash
$base_dir/$main
'''

def make_run_sh(params):

    base_dir = params['base_dir']

    fn = f'{base_dir}/run.sh'
    print(f'Writing {fn}')
    with open(fn, "w") as text_file:
        s = Template(run_sh_template).substitute(params)
        text_file.write(s)

    try_shell(f'sudo chmod +x {fn}')





# example for main file
# try_shell('pwd')
# install_run_sh(params = params)
# install_firmware(params = params)
# try_shell('sudo cp ./pigpiod.service /lib/systemd/system/')



