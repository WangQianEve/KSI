import subprocess
import argparse
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--config", type=str, default="none",
    help="Which config file to load")
args = vars(ap.parse_args())

if args['config']=='mouse':
    subprocess.call("./accel/accelDisableM.sh",shell=True)
if args['config']=='touchpad':
    subprocess.call("./accel/accelDisableT.sh",shell=True)
if args['config']=='indexS':
    subprocess.call("./accel/accelDisableK.sh",shell=True)
if args['config']=='none':
    subprocess.call("./accel/accelDisableN.sh",shell=True)

