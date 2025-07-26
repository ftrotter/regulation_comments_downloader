Folder Structure Fix
==================

The current code in mirrulations_bulk_downloader.py is based on an old directory structure for the mirrulations project.

Please help me re-write the mirrulations_bulk_downloader.py script to support the same arguments and features.
But to honor the new directory structure.

The other big change is that the mirrulatins project is no longer "requestor pays", so support for this functionality can be removed.

The new project has the following folder structure:

      ├── derived-data
      │   └── agency (i.e. DEA, CMS, HHS etc)
      │       └── {docketID} ( docketID takes the form {AGENCY}-{YEAR}-{docket_num} )
      │           ├── mirrulations
      │           │   ├── ai_summary  (when they exist)
      │           │   │   ├── comment
      │           │   │   ├── comment_attachments
      │           │   │   └── document
      │           │   ├── entities (when they exist)
      │           │   │   ├── comment
      │           │   │   ├── comment_attachment
      │           │   │   └── document
      │           │   └── extracted_txt (usually there)
      │           │       └── comments_extracted_text
      │           │           ├── pdfminer (contains a copy of the extracted text from each pdf in the raw binary files section)   
      |           |           └── some_future_extract_tool_directory_goes_here  
      commentID_attachment.txt
      │           └── other_direved_data_projects
      │               └── projectName
      │                   └── fileType
      │                       └── fileID.txt
      └── raw-data
      │   └── agency (i.e. DEA, CMS, HHS etc)
      │       └── {docketID} ( docketID takes the form {AGENCY}-{YEAR}-{docket_num} )
      │           ├── text-{docketID}
      │           │   ├── comments (contains the json document that contains comments submitted through the web-form)
      │           │   ├── docket (contains a single json docket metadata file)
      │           │   └── documents (contains all of the government-made documents in the docket, typically as "almost html" .htm files)
      │           ├── binary-{docketID}
      │           │   └──  comments_attachements (Holds the raw pdf, word, image, whatever comment attachments)

Generally, I would like to have the python script continue to support the "Download everything in a given year" and "Download everything in a given agency" and "everything in a given agency in a given year" as options.

This can be accomplished by downloading, in parallel, the matching dockets in both the derived-data directory and the raw-data directory.

In order to support the --textonly flag, the program should not download the contents of the binary-{docketID} sub-folder of the raw data directory, when the flag is there.

Otherwise the program should continue to support all of the other flags found in the ./README.md file.

Does the remote still use "myconfig:mirrulations/" as the base path, or has this changed to reflect the new structure (e.g., "myconfig:derived-data/" and "myconfig:raw-data/")? The top level directories in the S3 bucket are derived-data and raw-data.

Use a single rclone command with appropriate --include patterns that cover both derived-data and raw-data to download between both top level directories. (rather than running two seperate rclone commands)

The year filtering logic will need to match against the year portion of the docket-id directory names.

the current file-type filtering is the right way to handle the --textonly downloads. This should be preferred over guessing that there are no text files in the binary sub-folders.

The .env file will still contain the MIRRULATIONS_DATA_PATH, RCLONE_CONFIG_FILE parameters.
