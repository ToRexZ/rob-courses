@echo off
regedit /s showdev.reg
set devmgr_show_nonpresent_devices=1
start devmgmt.msc