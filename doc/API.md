# Introduction

# Interfaces

## REST Interface

A Representational State Transfer (REST ) Interface follows the principles of being client server, stateless, cacheable and layered (forwardable). The typical set of instructions corresponds to those of HTTP: POST (create), GET (read), PUT (update), DELETE (delete) and the primary mechanism of control is the URL.

The core URL is:

base_url /package_id

where the base_url  is the url for the server and interface (e.g. [https://wirl.api.sil.org](https://www.google.com/url?q=https://wirl.api.sil.org&sa=D&ust=1502166515517000&usg=AFQjCNHxKN0xLcnsddI1ZkwAKGSw8TsUXQ)) and the package_id  is the id of the package (bundle or resource) of interest.

|  |  |
| --- | --- |
| GET | Returns the package. No authentication required. |
| PUT | Not used |
| POST | Not used |
| DELETE | Not used |

The server may not necessarily return the package being asked for directly. It may use a redirect to point the calling application to where the package may be found. Thus the REST interface may return the following return codes :

|  | |
| :---: | --- |
| 200 | OK. The package contents are enclosed with this response. |
| 303 | See other. The body of the response is a URL to GET from to get the resource. |
| 304 | Not Modified. The server tracks the time of when resources change and so can help clients with respect to caching and conditional requests. |
| 404 | The package id is wrong or unavailable for this platform. |
| 500 | Internal error for unforeseen problems. |

The following GET request header fields will be supported by the server:

|  | |
| --- | --- |
| If-Modified-Since | Only send the package if it has changed since the given date, else return 304. |
| If-None-Match | Only send the package if its checksum has changed, else return 304. |
| User-Agent | Extract architecture and platform information from the User-Agent string to save requiring such information as parameters within the requested URL (API). This information is fallback information and is overridden if specified in the URL. |

Further parameters in the URL can be used to refine what is received. Parameters consist of key = value pairs separated by &. The parameters are separated from the rest of the URL using ?.

| Parameter | Description |
| --- | --- |
| type | Resource type |
| engine | Software that uses the resource; eg., Keyman, MSKLC, Graphite, Ekaya |
| engineversion | Earliest version of the engine that handles the resource |
| os | Specifies the system architecture that the information is for. |
| os version | Version of the OS the resource is appropriate for |
| version | Used to request a particular version of  a resource, rather than the latest |
| param | A type-specific parameter that is used to further select what resource is returned (see below) |
| raw | This parameter changes how information is returned. The default is 0 and returns the package. A value of 1 asks the server to return a CSV list of all the information it holds on the packageId requested. |
| test | If non-zero returns empty content. Used for testing that the server would produce something of interest if so requested. |

### engine/engineversion

For an engine, the version is the earliest version that will handle the resource.

| engine | engineversion | notes |
| --- | :---: | --- |
| keyman | 6 | Keyman 6. All keyboards are forwardly compatible |
| keyman | 7 | Keyman 7. All keyboards are forwardly compatible |
| keyman | 8 | Keyman 8. All keyboards are forwardly compatible |
| teckit | ??? |  |
| graphite | 1.3.5??? | E.g., Awami needs collision fixing |
| hunspell |  |  |
| lo-spell | 4.1 |  |
| mozilla-spell | 38 |  |

### os/osversion

We list here all the different OSes that can take an osversion parameter and what the values mean. Notice that a resource appropriate for a given osversion may or may not be appropriate for a later osversion. An os value of win* here includes all the different windows os values: win64, win32.

| os | osversion | notes |
| --- | :---: | --- |
| win* | 5 | WinXP |
| win* | 6 | Windows Vista |
| win* | 7 | Windows 7 |
| win* | 8 | Windows 8 |
| linux |  |  |
| ubuntu |  | Only Ubuntu, not other Linuxes |

## Resource Classes

For each class/kind of a resource we list the possible resource types that are available and what they return. In addition, architecture types are listed. The default type is listed first.

### Font

A font resource references a single font. A different resource id is used for different subfamilies: bold, italic, etc.

| type | os | datatype | returns |
| --- | --- | --- | --- |
| ttf (default) | all | font | .ttf |
| woff | all | font | .woff |
| exe | win | font | .exe installer |

It is not likely, but theoretically possible, to have an exe that installs a single font.

### Font Collection

A font collection resource references a set of related fonts, such as a family of regular/bold/italic/bold-italic fonts.

| type | os | datatype | returns |
| --- | --- | ---- | --- |
| zipttf (default) | all | fontcollection | .zip of .ttf files |
| zipwoff | all | fontcollection | .zip of .woff files |
| exe | win | fontcollection | .exe installer |

#### Parameter

Font and Font Collection resources may also have a further parameter which selects a particular area subset. If no specified subset is available, the complete font is returned.

| parameter | meaning |
| --------- | ------- |
| Afr       | subset for Africa |
| Viet      | subset for Vietnam |
| ... |  |

### Keyboard

For a single layout there are often many different resources available.

| type | os | engine | returns | datatype | notes |
| --- | --- | --- | --- | --- | --- |
| source | all | keyman | .kmn | keyboard | works for KMFL as well |
| kmp | all | keyman | .kmp | keyboard | good to pass engineversion of Keyman the .kmx is against |
| kmx | all | keyman | .kmx | keyboard |  |
| source | Windows | mskbd | .klc | keyboard |  |
| mskbd | Windows, win64 | mskbd | .dll | keyboard | pass osversion if possible |
| mskbd | Windows, win32 | mskbd | .dll | keyboard | pass osversion if possible |
| ldmlkb (default) | all |  | .xml | keyboard |  |
| mackbd | mac | ukelele | .keylayout | keyboard | returns source xml for Mac keyboard layouts |
| ekaya |  |  |  |  | do not include |

### Spell-checker

A spell-checker is a word list using the Hunspell .dic format. There may or may not be an associated .aff file. A simple word list as a .txt file is also permitted.

| type | engine | returns | datatype |
| --- | --- | ---- | ---- |
| hunspell | hunspell | .zip | spell-check |
| wordlist |  | .txt | spell-check |

If both files exist, the WIRL URL field may indicate a directory that includes both of the files. WIRL will return a .ZIP file including the two files.

Currently, the only such URLs that are supported for creating a ZIP are for materials in GitHub; eg:

* https://github.com//silnrsi/wsresources/tree/master/resources/x/xyz/*.

(This is because the mechanism to zip together the files makes use of the GitHub API for enumerating the files.)

## Implementation

From the above analysis we can arrive at a database schema for holding resource records. Here are the required fields. The usage column in the table indicates whether a field is used as a key field (id) or is used to get the resource (loc).

| name | type | usage | description |
| --- | --- | --- | --- |
| id | string | id | Resource identifier from package_id |
| type | enum | id | Specifies the type of the resource [ttf, woff, zipttf, kmn, kmx, kmp, source, wordlist, hunspell, lo-spell, moz-spell, mskbd, mackbd, ldmlkb, sortspec] |
| engine | enum | id | Software engine that process the resource [keyman, msklc, ekaya, ukelele, inkey, graphite, teckit, hunspell]. Note that OpenType is assumed for fonts unless marked "graphite" which means Graphite only. |
| engineversion | num | id | Earliest version of engine that handles the resource |
| os | enum | id | OS appropriate for resource, else 'all' [win32, win64, mac, Ubuntu, all] |
| osversion | num | id | version of OS if defined |
| version | num | id | specific version of this resource for versioned resources |
| param | string | id | parameter value from url |
| url | string | loc | Location of the resource |
| datatype | enum | loc | Used for documentation and filtering [font, fontcollection, keyboard, map, spellcheck] |
| subloc | string | loc | Combines with the filetype to further process the result of the url query to get the actual resource to return. If set means that no 303 will be returned. |

## Issues

### Mappings

I'm not sure how encoding-converter mappings get used in this system. Do we really need these as resources (probably), but why? Use cases please.

### Bundles

Resource bundles are not really designed for application use, but for manual installation at the OS level by a user. Applications should try to make use of locally installed resources before pulling individual resources, if possible. Since each bundle is in effect a standalone installer or package, it is questionable as to whether they need to be handled by the resource mapper at all, or could just be made available for direct download via other mechanisms. The advantage of including bundles in the resource map is that we can return the bundle most appropriate to the user's needs/user agent string. But is that wise? Shouldn't a user also be able to choose from all the possible options in case they are getting a resource to transfer to a different system?

