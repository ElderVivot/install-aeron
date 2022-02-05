# -*- coding: utf-8 -*-

import codecs
import datetime
import json
import os
import subprocess
import sys
import time

from urllib.request import urlretrieve
from urllib.error import URLError

from zipfile import ZipFile
from shutil import copyfile

aeron_path = "C:\\aeron"
download_path = "C:\\aeron\\downloads"

def isUserAdmin():
    if os.name == 'nt':
        import ctypes
        # WARNING: requires Windows XP SP2 or higher!
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            traceback.print_exc()
            print("Admin check failed, assuming not an admin.")
            return False
    elif os.name == 'posix':
        # Check for root on Posix
        return os.getuid() == 0
    else:
        raise RuntimeError("Unsupported operating system for this module: %s" % (os.name,))

def runAsAdmin(cmdLine=None, wait=True):
    if os.name != 'nt':
        raise RuntimeError("This function is only implemented on Windows.")

    process = subprocess.Popen(['python3', '-m', 'pip', 'install', 'pypiwin32'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    for x in stderr.decode("utf-8").split("\r\n"):
        if x != "" and x[0:12].lower() != "deprecation:":
            self.log(x)

    import win32api, win32con, win32event, win32process
    from win32com.shell.shell import ShellExecuteEx
    from win32com.shell import shellcon

    python_exe = sys.executable

    if cmdLine is None:
        cmdLine = [python_exe] + sys.argv
    elif type(cmdLine) not in (types.TupleType,types.ListType):
        raise ValueError("cmdLine is not a sequence.")
    cmd = '"%s"' % (cmdLine[0],)

    params = " ".join(['"%s"' % (x,) for x in cmdLine[1:]])
    cmdDir = ''
    showCmd = win32con.SW_SHOWNORMAL
    lpVerb = 'runas'

    procInfo = ShellExecuteEx(nShow=showCmd,
                            fMask=shellcon.SEE_MASK_NOCLOSEPROCESS,
                            lpVerb=lpVerb,
                            lpFile=cmd,
                            lpParameters=params)

    if wait:
        procHandle = procInfo['hProcess']    
        obj = win32event.WaitForSingleObject(procHandle, win32event.INFINITE)
        rc = win32process.GetExitCodeProcess(procHandle)
    else:
        rc = None

    return rc

def conferir_privilegios():
    # ASADMIN = 'asadmin'
    # if sys.argv[-1] != ASADMIN:
    #     script = os.path.abspath(sys.argv[0])
    #     params = ' '.join([script] + sys.argv[1:] + [ASADMIN])
    #     shell.ShellExecuteEx(lpVerb='runas', lpFile=sys.executable, lpParameters=params)
    #     sys.exit(0)
    rc = 0
    if not isUserAdmin():
        # self.log("You're not an admin.", os.getpid(), "params: ", sys.argv)
        print("You're not an admin.")
        rc = runAsAdmin()
    else:
        # self.log("You are an admin!", os.getpid(), "params: ", sys.argv)
        rc = 0
    return rc

if conferir_privilegios() > 0:
    sys.exit(0)

def check_folder(_path):
    if (not os.path.isdir(_path)):
        os.makedirs(_path)

def log(msg, *params):
    print(msg, *params)

def progress(downloaded, block_size, total_size):
    global download_size
    download_size = total_size
    completed = int(downloaded / (total_size//block_size) * 100)
    sys.stdout.write("\r|" + "█" * completed + " " * (100-completed) + "|{}%".format(completed))

def download(url,filename):
    start = time.time()
    try:
        urlretrieve(url,filename,progress)
    except URLError:
        sys.stderr.write("The URL is invalid.\n")
        exit(0)
    except Exception as e:
        sys.stderr.write("An error occured\n")
        sys.stderr.write(type(e),e)
        exit(0)
    end = time.time()
    print("\n",end="")
    time_taken = end - start
    download_speed = round(download_size/(time_taken*1024),2)
    if download_speed >= 1024:
        sys.stdout.write("Downloaded in " + str(round(time_taken,2)) + "s (" + str(download_speed/1024) + " MB/s)" + "\n")
    if download_speed < 1024:
        sys.stdout.write("Downloaded in " + str(round(time_taken,2)) + "s (" + str(download_speed) + " kB/s)" + "\n")
    if download_speed < 1:
        sys.stdout.write("Downloaded in " + str(round(time_taken,2)) + "s (" + str(download_speed*1024) + " B/s)" + "\n")

def instalar_notepadpp():
    log("Instalando o Notepad++")
    download("https://github.com/notepad-plus-plus/notepad-plus-plus/releases/download/v7.9.2/npp.7.9.2.Installer.x64.exe", f"{download_path}\\notepadpp.exe")
    os.system(f"\"{download_path}\\notepadpp.exe\" /S")
    log("Notepad++ instalado com sucesso!")

def instalar_postgresql():
    log("Instalando o PostgreSQL")
    download("https://sbp.enterprisedb.com/getfile.jsp?fileid=1257415&_ga=2.140059251.1765645499.1611002386-1757516319.1611002386", f"{download_path}\\postgresql10.15.exe")
    os.system(f"\"{download_path}\\postgresql10.15.exe\" --mode unattended --unattendedmodeui minimalWithDialogs  --superpassword postgres --datadir {aeron_path}\\postgresql")
    log("PostgreSQL instalado com sucesso!")

def instalar_git():
    log("Instalando o Git")
    download("https://github.com/git-for-windows/git/releases/download/v2.30.0.windows.2/Git-2.30.0.2-64-bit.exe", f"{download_path}\\git.exe")
    comando = f"\"{download_path}\\git.exe\" /SILENT /SUPPRESSMSGBOXES /NORESTART /NOCANCEL /SP- /CLOSEAPPLICATIONS /RESTARTAPPLICATIONS /NOICONS"
    print(comando)
    os.system(comando)
    log("Git instalado com sucesso!")

def instalar_nodejs():
    log("Instalando o NodeJS")
    download("https://nodejs.org/dist/v14.16.0/node-v14.16.0-x64.msi", f"{download_path}\\nodejs.msi")
    comando = f"MsiExec.exe /i \"{download_path}\\nodejs.msi\" /qn"
    print(comando)
    os.system(comando)

    comando = f"setx /M PATH \"%PATH%;C:\\Program Files\\nodejs\""
    print(comando)
    os.system(comando)

    log("NodeJS instalado com sucesso!")

def instalar_nssm():
    log("Instalando o NSSM")
    download("https://nssm.cc/release/nssm-2.24.zip", f"{download_path}\\nssm.zip")
    with ZipFile(f"{download_path}\\nssm.zip", 'r') as zipObj:
        zipObj.extractall(f"{aeron_path}")
    os.rename(f"{aeron_path}\\nssm-2.24", f"{aeron_path}\\nssm")
    comando = f"setx /M PATH \"%PATH%;{aeron_path}\\nssm\\win64\""
    print(comando)
    os.system(comando)
    log("NSSM instalado com sucesso!")

def instalar_redis():
    log("Instalando o Redis")
    download("https://github.com/microsoftarchive/redis/releases/download/win-3.2.100/Redis-x64-3.2.100.zip", f"{download_path}\\redis.zip")
    with ZipFile(f"{download_path}\\redis.zip", 'r') as zipObj:
        zipObj.extractall(f"{aeron_path}\\redis")
    comando = f"setx /M PATH \"%PATH%;{aeron_path}\\redis\""
    print(comando)
    os.system(comando)
    comando = f"{aeron_path}\\redis\\redis-server --service-install"
    print(comando)
    os.system(comando)
    log("Redis instalado com sucesso!")

def install_project_git(name_project: str, create_service = False):
    log(f"Instalando {name_project}")

    command_download = f"cd {aeron_path} && git clone https://github.com/ElderVivot/{name_project}.git"
    print(command_download)
    os.system(command_download)

    command_install_build = f"cd \"{aeron_path}\\{name_project}\" && npm i --legacy-peer-deps && npm run build"
    print(command_install_build)
    os.system(command_install_build)

    copyfile(f"{aeron_path}\\{name_project}\\.env.example", f"{aeron_path}\\{name_project}\\.env")

    if create_service is True:
        command_service = f"{aeron_path}\\{name_project}\\create_service.bat"
        print(command_service)
        os.system(command_service)

    log(f"{name_project} instalado com sucesso!")

def outros():
    #corrigir erro no python
    #comando = "python3 -m pip install --ignore-installed pywin32"
    pass

if __name__ == "__main__":
    check_folder(aeron_path)
    check_folder(download_path)
    instalar_notepadpp()
    instalar_postgresql()
    instalar_git()
    instalar_nodejs()
    instalar_nssm()
    instalar_redis()
    install_project_git('iacon-rest-api-pg')
    install_project_git('baymax-extracts-node')
    install_project_git('webscraping-nfe-nfce-go-v2')
    install_project_git('webscraping-nfse-goiania')
