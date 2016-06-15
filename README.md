# MrHyde
![alt tag](https://raw.github.com/KeyWeeUsr/MrHyde/master/screen.png)

MrHyde is for now just a little test project for encrypting files. For
encrypting is used a custom PyCrypto wrapper for AES-256 CTR - [Vial](https://github.com/KeyWeeUsr/Vial).

What's MyHyde capable of now:
- Encrypt/decrypt a single file
- Encrypt/decrypt content of a folder
    - Navigate inside folder, don't select anything and press `Add`
- Erase a single selected file
- Revert itself to a state before setting any passwords (deletes files) on
  5x wrong typed passwords

#### How to use
###### Requirements
- Kivy
- PyCrypto
- pyscrypt
- Vial

###### Windows/Linux
- Install Kivy and PyCrypto
- `pip install pyscrypt aes-vial`
- Run `main.py`

###### Android
- Use KivyLauncher compiled with PyCrypto, pyscrypt and Vial
- Use buildozer with required modules and install APK

#### License
GNU GPLv3, read LICENSE.txt