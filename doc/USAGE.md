# WIRL USER DOCUMENTATION

WIRL is a database and accompanying API providing access to writing-system-related resources, such as fonts, keyboards, and mapping files. WIRL stands for Writing Implementation Resource Locator.

One of the benefits of WIRL is that it is aware of the various versions of a resource that might be present, and can provide the most up-to-date version without the user having to know what that version is. It can also provide a resource in multiple file formats as requested, such as a ZIP package, TTF, or WOFF file.

A WIRL resource consists of an identifier, a link to the resource files, and other metadata such as file format, version, etc. Multiple resources may use the same ID, such as multiple versions of a font or multiple file formats for the same data.

## How to use WIRL

The most basic way to use WIRL is in conjunction with the LDML API. Many LDML files include a section of resources appropriate for the language in question; these include links indicating where the resource can be downloaded. These links are typically links to WIRL or similar sites such as Google Fonts or Keyman. Below is an example of a section of an LDML file.

```
  <special>
    <sil:external-resources>
      <sil:font name="Charis SIL" types="default">
        <sil:url>https://wirl.api.sil.org/CharisSILReg&amp;type=ttf</sil:url>
      </sil:font>
      <sil:font name="Noto Sans" types="ui">
        <sil:url>https:/github.com/googlefonts/noto-fonts/raw/main/hinted/ttf
                   /NotoSans/NotoSans-Regular.ttf
      </sil:url>
      </sil:font>
      <sil:font name="Noto Serif">
        <sil:url>https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf
                   /NotoSerif/NotoSerif-Regular.ttf</sil:url>
      </sil:font>
      <sil:kbd id="sil_euro_latin" type="kmp">
        <sil:url draft="generated">
                https://keyman.com/go/keyboard/sil_euro_latin/download/kmp 
        </sil:url>
      </sil:kbd>
    </sil:external-resources>
  </special>
```

Notice the various URLs associated with each resource, including a WIRL link that is used for the Charis SIL font. The URL includes the resource ID--CharisSILReg--and an argument indicating what type of file to return--a TTF.

Using WIRL in this way is fairly trivial and requires no more special knowledge than using any other API. The client program invokes the URL and if it is valid, the API will return the requested resource. If the resource does not exist, the API returns a 404.

### Options

The default download for a font is a zip file:

https://wirl.api.sil.org/CharisSIL

It is possible to tweak the API call to specify options about exactly what resource should be returned. For instance, the following would prefer to download a Windows installer rather than a zip file:

https://wirl.api.sil.org/CharisSIL&type=exe

The following URL would be used to access a font that is available simply as a bare TTF rather than a package:

https://wirl.api.sil.org/SampleFont&type=ttf

Another possibility might be to give preference to resources that are appropriate for a given operating system. For example, this URL returns a resource that works on Linux:

https://wirl.api.sil.org/CharisSILReg&os=linux

The following URL returns a font that is specifically tuned for African languages.

https://wirl.api.sil.org/CharisSILReg&xparam=Afr

The following URL is used to download a Windows .EXE file that can install all the available faces of the Charis font. Notice it uses a different ID indicating the entire font family.

https://wirl.api.sil.org/CharisSIL&type=exe

The URL below returns a version of a Keyman keyboard that is compatible with Keyman 6. (Although see note about Keyman below.)

https://wirl.api.sil.org/Kannada-kbd&engine=keyman&engineversion=6

See the Complete API Specification section below for more options.

### Example: ScriptSource

The ScriptSource website uses the LDML and WIRL APIs together to offer a downloadable package of resources appropriate for a given language or script. It first queries the LDML system to discover LDML files that are appropriate for the language (there may be more than one). Then it uses the external-resources section of the LDML to locate items belonging in the package. It uses each URL to download files and then zips them together into a package that is offered to the user.

## Updating the data

WSTech adds new versions of fonts to the WIRL database whenever a new one is released.

Although the WIRL database does include some Keyman keyboards, these are not used much within the LDML files because the Keyman website provides stable URLs. 

Other resources are updated on a very ad hoc basis.

## Limitations

Currently there is no way to query WIRL for a list of resources, so it is necessary to know at least the desired resource ID in order to use the API.

It is also not possible to query the relationship between related resources such as the regular version of a font and the complete font family. Although there are conventions around the various identifiers, consistency is not guaranteed.

There is no way to retrieve resources based on a script identifier, such as a list of all the fonts appropriate for Bengali or Cyrillic, simply using WIRL.

# Complete API specification

The following HTTP codes can be expected:

* 200: OK - the package contents are enclosed
* 404: no resource found to match
* 429: API rate limit exceeded
* 500: internal error accessing resources

## URL Parameters

* **res_id**: resource ID; e.g., ‘CharisSILReg’, ‘he_IL-DictList’, ‘sil-ghana’
type: resource type

* **engine**: software that uses the resource; e.g., Keyman, MSKLC, Graphite, Ekaya

* **engineversion**: earliest version of the engine that will handle the resource

* **os**: specifies the operating system the resource is appropriate for

* **osversion**: version of the operating system the resource is appropriate for

* **version**: used to request a particular version of the resource, other than the latest

* **xparam**: a type-specific extra parameter that is used to further select what resource is returned (see below)

* **raw**: this parameter changes how information is returned. The default is 0 and returns the package. A value of 1 asks the server to return a CSV list of all the information it holds on the package ID requested.

* **test**: if non-zero, returns empty content. Use for testing that the server would produce something of interest if so requested.

### Values: engine/engineversion

For an engine, the version is the earliest version that will handle the resource.

* **keyman = 6**: Keyman 6. All keyboards are forward compatible
* **keyman = 7**: Keyman 7. All keyboards are forward compatible
* **keyman = 8**: Keyman 8. All keyboards are forward compatible
* **teckit**
* **graphite**; e.g., Awami needs collision fixing
* **hunspell**
* **lo-spell**
* **mozilla-spell**

### Values: os/osversion

We list here all the different architectures that can take an osversion parameter and what the values mean. Notice that a resource appropriate for a given osversion may or may not be appropriate for a later osversion. An _os_ value of win* here includes all the different windows OS values: win64, win32.

* **win\* = 5**: Windows XP
* **win\* = 6**: Windows Vista
* **win\* = 7**: Windows 7
* **win\* = 8**: Windows 8
* **linux**
* **ubuntu**

## Resource Classes

For each class/kind of a resource we list the possible resource types that are available and what they return. In addition, architecture types are listed. The default type is listed first.

### Font

A font resource references a single font. This option is only appropriate fonts that are not distributed as a full package (eg, .zip).

* **type = ttf**: returns a .ttf (default)
* **type = woff**: returns a .woff file
* **type = woff2**: returns a woff2 file
* **type = exe**: returns a .exe installer

### Font Collection

A font collection resource references a set of related fonts, such as a family of regular/bold/italic/bold-italic fonts.

* **type = zipttf** - returns a .zip file containing .ttf files (default)
* **type = zipwoff** - returns a zip file containing .woff files
* **type = exe** - returns a .exe installer

### Extra Parameter

Font and Font Collection resources may have an extra parameter, xparam, which selects a particular area subset. If no specified subset is available, the complete font is returned. Here are some existing values:

* **xparam = Afr**: subset for Africa
* **xparam = Am**: subset for Americas
* **xparam = APac**: subset for Asia/Pacific
* **xparam = Cyr**: subset for Cyrillic
* **xparam = CyrE**: subset for extended Cyrillic
* **xparam = Eur**: subset for Europe/Eurasia
* **xparam = Phon**: subset for phonetic use
* **xparam = Viet**: subset for Vietnam

### Keyboard

For a single layout there are often many different resources available.

* **type = source** - returns a .kmn file or .klc; works for KMFL as well
* **type = kmp** - returns a .kmp file; good to pass engineversion of Keyman the .kmx is against
* **type = kmx** - returns a .kmx
* **type = mskbd** - returns a .dll; pass osversion if possible
* **type = ldmlkb** - returns a .xml file; default
* **type = mackbd** - returns a .keyboardout--source XML for Mac keyboard layouts

### Spell-checker

A spell checker is a word list using the Hunspell .dic format. There may or may not be an associated .aff file. A simple word list as a .txt file is also permitted.

* **type = hunspell** - returns a .zip file; engine = hunspell
* **type = wordlist** - returns a .txt file

If both files exist, WIRL will return a ZIP file including the two files.

