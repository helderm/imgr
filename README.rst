
imgr
================

imgr is a web application for managing an 'image bank'.


## Intro
* All requests should be made to `http://imgr-helderm.rhcloud.com/`. 

## Services
Below is the list of services available.

##### POST /files/{fileid}
Add metadata info for file {fileid}. If no value is given, the metadata key is removed.

Name | Type | Description | Usage | Example
-----|------|-----------|-----|----------
fileid | str | File ID | Required. URL | c3b7d232-dfr...
key | str | Metadata key | Required. Body. | metakey
val | str | Metadata value | Optional. Body. | metaval

```
"POST http://imgr-helderm.rhcloud.com/files/b7a54362-d0d5-460f-8082-9a981fa83ec4"
```

Body
```json
{"key":"metakey", "key":"metaval"}
```

Returns:

```json
{"status": 0}
```

##### GET /files/{fileid}
Perform a search for files in the database, default is a search for filenames. If {fileid} is provided, it will return the specific requested file. If {key} is provided, the search will be performed in the dot-separated fields of the value provided.

Name | Type | Description | Usage | Example
-----|------|-----------|-----|----------
fileid | str | File ID | Optional. URL | c3b7d232-dfr...
query | str | Query string | Required if {fileid} is not provided. URL | image
key | str | Key field to be serched | Optional. Defaults to 'name' | meta.metakey

```
"GET http://imgr-helderm.rhcloud.com/files?query=metav&key=meta.metakey"
```

Returns:

```json
{"status": 0, "files": [{"type": "text/plain", "meta": { "metakey": "metaval"}, "_id": "b7a54362-d0d5-460f-8082-9a981fa83ec4", "name": "/teste1.txt"}]}
```
    

##### DELETE /files/{fileid}
Delete a file from the database.

Name | Type | Description | Usage | Example
-----|------|-----------|-----|----------
fileid | str | File ID | Required. URL | c3b7d232-dfr...

```
"DELETE http://imgr-helderm.rhcloud.com/files/b7a54362-d0d5-460f-8082-9a981fa83ec4"
```

Body
```json
{"status": 0}
```
  