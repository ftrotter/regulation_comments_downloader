# Regulation Comments Downloader

A python script to download regulations data from mirrulations

Relies on having [rclone](https://rclone.org/) installed.

## Setup
copy example.env to .env and fill in the details about where to save your mirrulations data.
copy rclone.conf.example and modify it to suit your needs



```bash
python mirrulations_bulk_downloader.py
```

And it should guide you through your download options.

```bash
Options:
  -a, --agency TEXT  Agency acronyms(s) separated by commas.
  -y, --year TEXT    Year(s) or range(s) of years separated by commas or dash
                     (e.g., 2010-2015).
  --textonly         Flag to indicate if textonly should be True.
  --getall           Download all agencies, all years. (WARNING: this could
                     cost a few hundred dollars...)
  --transfers TEXT   How many rclone connections to run at the same time
                     (default is 50)
  -d, --docket TEXT  Download a specific docket id
  --noconfirm        Skip confirmation prompt and run commands automatically
  --help             Show this message and exit
```
