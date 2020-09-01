# Tutorial: Email Setup

To use the email functionality of Pluma you should create an email settings file.  
This file should be in the root directory of this repository and be named `email_settings.json`.  
This file should be json formatted as shown in the example file below:

`<farm-core>`/email_settings.json:

```json
{
    "smtp": {
        "email": "lab@witekio.com",
        "password": "reallybadpassword",
        "server": "smtp.office365.com",
        "delay": 587
    },
    "maintainers": [
        "john_smith@domain.com",
        "maxime_dubois@domain.com"
    ]
}
```

The `"smtp"` section is required for sending emails, and the email address in the `"maintainers"` section will be used for sending exception reports. You must specify at least one maintainer.  
The options `"server"` and `"delay"` are optional, and the above values will be used if these settings are not present.

This settings file is _technically_ optional as you can specify username and passwords in the relevant class method and function calls, but anything that sends automated emails (such as error reports) will not work without it.  
Adding this file will make your life easier.
