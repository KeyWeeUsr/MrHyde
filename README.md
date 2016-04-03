# MrHyde
MrHyde is for now just a little test project for encrypting files. It's slow. Totally slow on old cpus and is recommended for small files and documents(smaller size, less time). On android it's like, really really slow, because it uses pure-python AES. I had few issues with PyCrypto, so I choose pure-python solution. Hopefully I'll speed it up soon.

What's MyHyde capable of now:
- Encrypt/decrypt a single file
- Encrypt/decrypt content of a folder
    - Navigate inside folder, don't select anything and press `Add`

#### How to use
###### Requirements
- kivy
- pyaes
- pyscrypt

###### Windows/Linux
- Install kivy
- `pip install pyaes pyscrypt`
- Run `main.py`

###### Android
- Use KivyLauncher compiled with pyaes and pyscrypt
- Use buildozer with required modules and install APK

#### License
GNU GPLv3, read LICENSE.txt