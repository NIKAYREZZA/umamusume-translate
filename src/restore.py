import requests
import common
from common import GAME_ASSET_ROOT
from os.path import join, realpath, isfile
import shutil
from argparse import SUPPRESS

HOSTNAME = 'https://prd-storage-umamusume.akamaized.net/dl/resources'
ASSETS_ENDPOINT = HOSTNAME + '/Windows/assetbundles/{0:.2}/{0}'


def download(file):
    url = ASSETS_ENDPOINT.format(file)
    print(f"Downloading {file} from {url}")
    return requests.get(url)


def save(fileName, backupDir, forceDl=False):
    dstPath = join(GAME_ASSET_ROOT, fileName[:2], fileName)
    localFile = join(backupDir, fileName)

    print(f"Saving file to {dstPath}")
    if not forceDl and isfile(localFile):
        print(f"Copying file from {localFile}")
        shutil.copyfile(localFile, dstPath)
    else:
        data = download(fileName)
        if data.status_code == 200:
            with open(dstPath, "wb") as f:
                f.write(data.content)
        else:
            print(f"Error downloading file {fileName}")


def main():
    ap = common.Args("Restore game files from backup or CDN download")
    ap.add_argument("-F", "--forcedl", action="store_true", help="Force new file dl over copying from local backup")
    ap.add_argument("-bdir", "--backup-dir", default=realpath("dump"), help="Local backup dir")
    ap.add_argument("-src", help="Target filename/bundle hash")
    ap.add_argument("-dst", help=SUPPRESS)
    ap.add_argument("--uninstall", action="store_true", help="Restore all files back to originals (may download)")
    args = ap.parse_args()

    if args.src:
        save(args.src, args.backup_dir, args.forcedl)
    else:
        for type in common.TARGET_TYPES if args.uninstall else (args.type,):
            files = common.searchFiles(type, args.group, args.id, args.idx, changed = args.changed)
            for file in files:
                file = common.TranslationFile(file)
                save(file.bundle, args.backup_dir, args.forcedl)

    if args.uninstall:
        from helpers import getUmaInstallDir
        from pathlib import Path
        uma = getUmaInstallDir()
        if uma:
            (uma / "version.dll").unlink(missing_ok=True)
            (uma / "uxtheme.dll").unlink(missing_ok=True)
        Path(common.GAME_ROOT, "master", "master.mdb").unlink(missing_ok=True)


if __name__ == '__main__':
    main()
