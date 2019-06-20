# Witekio Automation Lab

This all documentation, and code is currently under development, and may be subject to change, so use caution.

A draft coding guide for developers can be found at [/docs/style-guide.md](/docs/style-guide.md). This is in development still, but better than nothing.

A lot of the other documentation (maybe all!) is depreciated now, so don't rely on it for trustworthy information.

## Email Settings
To use the email functionality of the lab you should create an email settings file.  
This file should be in the root directory of this repository and be named `email_settings.json`.  
This file should be json formatted as shown in the example file below:

\<farm-core>/email_settings.json:
```
{
    "smtp": {
        "email": "lab@witekio.com",
        "password": "reallybadpassword",
        "server": "smtp.office365.com",
        "delay": 587
    },
    "maintainers": [
        "john_smith@domain.com",
        "maxime_richard@domain.com"
    ]
}
```
The `"smtp"` section is required for sending emails, and the email address in the `"maintainers"` section will be used for sending exception reports. You must specify at least one maintainer.  
The options `"server"` and `"delay"` are optional, and the above values will be used if these settings are not present.

This settings file is _technically_ optional as you can specify usernames and passwords in the relevant class metod and function calls, but anything that sends automated emails (such as error reports) will not work without it.  
Adding this file will make your life easier.
