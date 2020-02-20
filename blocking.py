import psutil
import os
import sqlite3
import winreg
from os import environ
from getpass import getuser
from time import sleep


# get list of processes
def get_proc():
    processes = []
    for process in psutil.process_iter(attrs=['pid', 'name', 'username']):
        # get only user processes
        # remove System and SystemIdleState from list
        # print(process.info)
        if (process.info['name'] == 'ProcessBlocker.exe'):
            pass
        if (process.info['username'] == environ['COMPUTERNAME'] + '\\' + getuser()):
            # print('-------->{}'.format(process.info))
            processes.append(process.info)

    # unique names
    processes = list({proc['name']: proc for proc in processes}.values())
    return processes


# find by name
def find_by_name(name):
    proc_list = []
    for process in psutil.process_iter(attrs=['name', 'pid', 'username']):
        if process.name() == name and process.info['username'] == environ['COMPUTERNAME'] + '\\' + getuser():
            proc_list.append(process.info)

    if proc_list == []:
        return None

    return proc_list


# terminate
def terminator(name):
    proc_list = find_by_name(name)
    if proc_list is None:
        return 'Empty list'
    for proc in proc_list:
        if proc['name'] == name:
            pid = proc['pid']
            if(psutil.pid_exists(pid)):
                process = psutil.Process(pid)
                # print('Terminating process {} with pid {}'.format(
                #    proc['name'], proc['pid']))
                process.terminate()
                process.wait()
                sleep(0.5)
            else:
                pass
                #            print('Process already killed')
                # print('done')


# create DisallowRun key
def disallow_run_key_create():
    base_key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        'Software\Microsoft\Windows\CurrentVersion\Policies',
        0,
        winreg.KEY_WRITE)
    exp_key = winreg.CreateKey(base_key, 'Explorer')
    exp_val = winreg.SetValueEx(exp_key, 'DisallowRun', 0, winreg.REG_DWORD, 1)
    disallow_key = winreg.CreateKey(exp_key, 'DisallowRun')
    winreg.CloseKey(base_key)
    winreg.CloseKey(exp_key)
    winreg.CloseKey(disallow_key)


# block application
def blocker(name):
    try:
        disallow_key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            'Software\Microsoft\Windows\CurrentVersion\Policies\Explorer\DisallowRun',
            0,
            winreg.KEY_WRITE)
    except FileNotFoundError:
        disallow_run_key_create()
        disallow_key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            'Software\Microsoft\Windows\CurrentVersion\Policies\Explorer\DisallowRun',
            0,
            winreg.KEY_WRITE)
    db = sqlite3.connect('blocked_proc.db')
    cur = db.cursor()
    cur.execute(
        'CREATE TABLE IF NOT EXISTS blocked(id INTEGER,application TEXT PRIMARY KEY)')
    last_id = cur.execute('SELECT MAX(id) FROM blocked').fetchone()[0]
    if(last_id is not None):
        last_id = int(last_id)
    else:
        last_id = 0
    last_id += 1
    block_val = winreg.SetValueEx(
        disallow_key, str(last_id), 0, winreg.REG_SZ, name)
    cur.execute('INSERT INTO blocked(id, application) VALUES(?,?)',
                (last_id, name))
    db.commit()
    winreg.CloseKey(disallow_key)
    # print('{} blocked'.format(name))
    db.close()


def check_reg():
    try:
        disallow_key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            'Software\Microsoft\Windows\CurrentVersion\Policies\Explorer\DisallowRun',
            0,
            winreg.KEY_ALL_ACCESS)
    except FileNotFoundError:
        return FileNotFoundError
    vals = winreg.QueryInfoKey(disallow_key)[1]
    #print(vals)
    if(vals != 0):
        for i in range(vals):
            # print('>' + str(winreg.EnumValue(disallow_key, i)))
            block_id, name = winreg.EnumValue(disallow_key, i)[0], winreg.EnumValue(disallow_key, i)[1]
            # print(block_id, name)
            # try:
            #    name = winreg.QueryValueEx(disallow_key, str(i))[0]
            # except FileNotFoundError:
            #    pass
            # print(i, name)
            # else:
            db = sqlite3.connect('blocked_proc.db')
            cur = db.cursor()
            cur.execute(
                'CREATE TABLE IF NOT EXISTS blocked(id INTEGER, application TEXT PRIMARY KEY)')
            try:
                cur.execute('INSERT INTO blocked(id, application) VALUES(?,?)',
                            (block_id, name))
                db.commit()
                pass
            except sqlite3.IntegrityError:
                pass
        winreg.CloseKey(disallow_key)
        db.close()
    else:
        pass


# unlock application
def unblocker(name):
    disallow_key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        'Software\Microsoft\Windows\CurrentVersion\Policies\Explorer\DisallowRun',
        0,
        winreg.KEY_ALL_ACCESS)
    db = sqlite3.connect('blocked_proc.db')
    cur = db.cursor()
    del_id = cur.execute(
        'SELECT id FROM blocked WHERE application = (?)',
        (name,)).fetchone()[0]
    del_id = str(del_id)
    # print('Deleting id {}\n Unblocking application {}'.format(del_id, name))
    winreg.DeleteValue(disallow_key, del_id)
    winreg.CloseKey(disallow_key)
    cur.execute('DELETE FROM blocked WHERE id = (?)', (del_id))
    # print('Done')
    db.commit()
    db.close()


""" if __name__ == '__main__':
    import ctypes
    import sys

    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    if is_admin():
        # Code of your program here
        print('here')
        import time
        time.sleep(500)
    else:
        # Re-run the program with admin rights
        print('restart')
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, __file__, None, 1) """


# check_reg()
# blocker('chrome')
# unblocker('chrome.exe')
# find_by_name('firefox.exe')
# printer()
# time.sleep(5)
# terminator('chrome.exe')
