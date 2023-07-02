# PySigVi
Simple Gui to verify file signatures with GPG - The GNU Privacy Guard

PySigVi is a GUI (Graphical User Interface) for [GNU Privacy Guard GPG](https://gnupg.org/)

It checks the detached signatures of a file.

Under the hood it repeat:

`gpg --verify detached_signature file_to_verify`

for each detached signature.

PySigVi does not create the signatures! It only checks the existing ones created with some other software.
