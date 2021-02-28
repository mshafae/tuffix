# Notes

In an attempt to make sure formatting is okay across all iterations of Tuffix henceforth, I will be enforcing PEP8 standards

```bash
find . -type f -name '*.py' -exec autopep8 --in-place --aggressive --aggressive {} \;
```

Since we can automate this process, I recommend running this command to help alleviate the headache that would ensue attempting this by hand.
An example implementation for automation could be this:

```bash
# pip install --upgrade autopep8
vared -p "Commit: " -c message

find . -type f -name '*.py' -exec autopep8 --in-place --aggressive --aggressive {} \;

git add *
git commit -m "$message"
git push
```

`vared` is a `zsh` only utility, you can use traditional `read` if `bash` is your preferred shell.
Placing this in your shell's configuration file or scripts folder would make it easier.
Inspiration for this script comes [from here](https://stackoverflow.com/questions/21963871/tool-to-automatically-format-python-code#21963968)

I have this already mapped in `vim` using [this plugin](https://github.com/Chiel92/vim-autoformat) so I never have to think about it.
