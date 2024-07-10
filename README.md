# adb-idme
adb-idme is a script that patches your IDME to enable ADB access (and serial console) on most Amazon MediaTek devices.

## Usage instructions
Dump your IDME using mtkclient:
```
python mtk.py r preloader idme.bin --parttype=boot2
```

Patch your IDME to enable ADB and serial console.
```
python adb-idme.py idme.bin idme_patched.bin
```

If successful, you should see an output like:
```
Found fos_flags at offset: 0x2b08
ADB Enabled = False
ADB Auth Disabled = True
Serial Console Enabled = False
Ramdump Enabled = False
Verbosity Enabled = True
Dexopt on boot Enabled = False
Successfully patched idme to enable ADB.
```

Note that the script is showing the currently enabled fos_flags in the provided IDME and not the flags after the patch.

## Getting ADB authorisation
On some devices, the `FOS_FLAGS_ADB_AUTH_DISABLE` flag doesn't actually disable ADB authorisation.

Note that this method requires that the device does not have userdata encryption (this is unlikely on Amazon devices).

Dump your userdata partition with mtkclient.
```
python mtk.py r userdata userdata.img
```

Mount the userdata image.
```
mount userdata.img <mount point>
```

Copy your adb keys to the key directory.
```
cp ~/.android/adbkey.pub <mount point>/misc/adb/adb_keys
```

Set permissions and SELinux context on the file.
```
chmod 0640 <mount point>/misc/adb/adb_keys
chown 1000:2000 <mount point>/misc/adb/adb_keys
setfattr -n security.selinux -v "u:object_r:adb_keys_file:s0" <mount point>/misc/adb/adb_keys
```

Unmount the image.
```
umount <mount point>
```

Write the modified userdata image to the device.
```
python mtk.py w userdata userdata.img
```

Boot the device normally. If successful, you should have ADB authorisation.
