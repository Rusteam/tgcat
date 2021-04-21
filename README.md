# Identify the language and topic of a Telegram channel

## Configure DVC
### Install DVC
Refer to https://dvc.org/doc/install

### Pull request from Git
Dvc should be initialized and committed to Git. Check .dvc/ folder existence.
```bash
git pull origin dev
```

### Check config
Look at ./dvc/config file. It should contain S3 storage credentials. (Not secure already)

### Pull files
```bash
dvc pull
```

## Work with DVC
Refer to https://dvc.org/doc/start/data-and-model-versioning
