import os
import tempfile


the_dir = f"{tempfile.gettempdir()}/me"
os.system(f"rm -rf {the_dir}")

try:
    os.mkdir(the_dir)
except FileExistsError:
    pass

try:
    os.mkdir(f"{the_dir}/audio")
except FileExistsError:
    pass