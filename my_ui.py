from tkinter import *
from tkinter import ttk
import blocking
import sqlite3
from time import sleep
import os.path

#print(__file__)
#BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = 'blocked_proc.db' #os.path.join(BASE_DIR, "blocked_proc.db")

L_BLUE = '#e1f0fd'
GREEN = '#05a19c'
RED = '#e41749'

# root window
root = Tk()
root.title("Process Blocker")
root.geometry('700x600')
root.configure(bg=L_BLUE)
heading = Label(root, text="Process Blocker", font=(
    "Segoe UI ", 25), height="2", bg=L_BLUE)
heading.pack()

br = StringVar(value=' ')
res = StringVar(value=' ')
label = Label(root, font='Helvetica', textvariable=br, bg=L_BLUE)
label.pack()
under = Label(root, textvariable=res, font='Helvetica', bg=L_BLUE)
under.pack(side=BOTTOM)


# ------------------------------------------------------------------------------------------------


# notebook/tabs
tabs = ttk.Notebook(root)
act_tab = ttk.Frame(tabs)
bloc_tab = ttk.Frame(tabs)
tabs.add(act_tab, text='Active Processes')
tabs.add(bloc_tab, text='Blocked Processes')
tabs.pack()


# ------------------------------------------------------------------------------------------------


# Blocked processes
Label(bloc_tab, text="Blocked processes").pack()
scrollbar = Scrollbar(bloc_tab)
scrollbar.pack(side=RIGHT, fill='y')
block_list = Listbox(bloc_tab, width=70, height=20, selectmode=MULTIPLE)
block_list.config(yscrollcommand=scrollbar.set)


def update_block_list():
    block_list.delete(0, END) 
    db = sqlite3.connect(db_path)
    cur = db.cursor()
    cur.execute(
    'CREATE TABLE IF NOT EXISTS blocked(id INTEGER,application TEXT PRIMARY KEY)')
    blocked = cur.execute('SELECT * FROM blocked').fetchall()
    for app in blocked:
        block_list.insert(END, app[1])
    block_list.pack()

blocking.check_reg()
update_block_list()


def unblock_button():
    br.set('Unblocking Process')
    label.update()
    index = block_list.curselection()
    for i in index:
        blocked = block_list.get(i)
        blocking.unblocker(blocked)

    br.set(' ')
    label.update()
    update_block_list()


# for i in range(10):
#   block_list.insert(END, str(i))
#   block_list.pack()


unblock = Button(bloc_tab, text="Unblock", command=unblock_button).pack(side=BOTTOM)


# ------------------------------------------------------------------------------------------------


# Active Processes
Label(act_tab, text="Active processes").pack()
scrollbar = Scrollbar(act_tab)
scrollbar.pack(side=RIGHT, fill='y')
process_list = Listbox(act_tab, width=70, height=20, selectmode=MULTIPLE)
process_list.config(yscrollcommand=scrollbar.set)


def update_proc_list():
    process_list.delete(0, END)
    active_proc = blocking.get_proc()
    sort = []
    for proc in active_proc:
        sort.append(proc['name'])
        # process_list.insert(END, proc['name'])

    sort = sorted(sort)
    for x in sort:
        process_list.insert(END, x)
    process_list.pack()
    # heading.after(5000, update_proc_list)


update_proc_list()


def terminate_button():
    br.set('Terminating process')
    label.configure(bg=GREEN)
    label.update()
    index = process_list.curselection()

    for i in index:
        proc = process_list.get(i)
        blocking.terminator(proc)
    
    for i in index:
        process_list.delete(i)

    br.set('Process Terminated')
    label.update()
    update_proc_list()
    br.set(' ')
    label.configure(bg=L_BLUE)
    label.update()


terminate = Button(act_tab, text="Terminate",
                   command=terminate_button).pack(expand=TRUE, side=LEFT, fill=X)


def block_button():
    br.set('Terminating and blocking process')
    label.configure(bg=GREEN)
    label.update()
    index = process_list.curselection()
    for i in index:
        proc = process_list.get(i)
        blocking.terminator(proc)
        blocking.blocker(proc)

    for i in index:    
        process_list.delete(i)

    br.set('Process blocked')
    label.update()
    update_block_list()
    update_proc_list()
    br.set(' ')
    label.configure(bg=L_BLUE)
    label.update()
    res.set('PLEASE RESTART YOUR PC AFTER BLOCKING PROCESS')
    under.configure(bg=RED)
    under.update()


block = Button(act_tab, text="Block", command=block_button).pack(
    expand=TRUE, side=RIGHT, padx=5, fill=X)


# ------------------------------------------------------------------------------------------------


# ------------------------------------------------------------------------------------------------


def ref_button():
    br.set('Refreshing')
    label.update()
    update_block_list()
    update_proc_list()
    br.set(' ')
    label.update()


refresh = Button(root, text="Refresh", bg="#b1d8fa", font=(
    "Helvetica", 10), height="1", activebackground="#69b4f5", width="25", command=ref_button).pack()


# ------------------------------------------------------------------------------------------------


# Run
root.mainloop()
