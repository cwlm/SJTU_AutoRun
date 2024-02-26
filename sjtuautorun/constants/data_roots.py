from os.path import dirname, join

DATA_ROOT = join(dirname(dirname(__file__)), "data")
IMG_ROOT = join(DATA_ROOT, "images")
SETTING_ROOT = join(DATA_ROOT, "settings")

BIN_ROOT = join(dirname(DATA_ROOT), "bin")
TUNNEL_ROOT = join(BIN_ROOT, "image_recognize")
ADB_ROOT = join(BIN_ROOT, "adb")
