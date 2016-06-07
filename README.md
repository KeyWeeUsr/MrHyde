# MrHyde
MrHyde is for now just a little test project for encrypting files. For
encrypting is used AES-256 CTR with a customized Counter. The Counter may
change in future.

What's MyHyde capable of now:
- Encrypt/decrypt a single file
- Encrypt/decrypt content of a folder
    - Navigate inside folder, don't select anything and press `Add`

#### How to use
###### Requirements
- Kivy
- PyCrypto
- pyscrypt

###### Windows/Linux
- Install Kivy and PyCrypto
- `pip install pyscrypt`
- Run `main.py`

###### Android
- Use KivyLauncher compiled with PyCrypto and pyscrypt
- Use buildozer with required modules and install APK

#### License
GNU GPLv3, read LICENSE.txt