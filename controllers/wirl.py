# -*- coding: utf-8 -*-

##################################################################################
#
#   Copyright (c) 2014 SIL International
#
#   The WIRL software is released under the MIT License
#   (http://opensource.org/licenses/MIT).
#
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#   of this software and associated documentation files (the "Software"), to deal
#   in the Software without restriction, including without limitation the rights
#   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#   copies of the Software, and to permit persons to whom the Software is
#   furnished to do so, subject to the following conditions:
#   
#   The above copyright notice and this permission notice shall be included in
#   all copies or substantial portions of the Software.
#   
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
#   SOFTWARE.
#
##################################################################################


#import urllib
import urllib2
import glob
import os
import time
import shutil
import tempfile
import subprocess
import string

def index() :

    #response.flash = T("Welcome to the first LSP prototype app!")
    #response.subtitle = T('Prototype')
    #return dict(message=T('Eventually you\'ll be able to download a package!'))
    
    redirect(URL('getResource'))
    
    
def findResource() :
    
    # Read the URL arguments:
    resId = request.get_vars.resid
    resType = request.get_vars.type
    arch = request.get_vars.arch
    archVersion = request.get_vars.archversion
    resVersion = request.get_vars.resVersion
    xParam = request.get_vars.param
    raw = request.get_vars.raw
    
    recordResults = _determineResources(resId, resType, arch, archVersion, resVersion, xParam, raw)
    
    bestRows = []
    for recordId in recordResults["best"]:
        nextRows = db(db.langResource.id == recordId).select()
        bestRows.append(nextRows[0])
    otherRows = []
    for recordId in recordResults["other"]:
        nextRows = db(db.langResource.id == recordId).select()
        otherRows.append(nextRows[0])
        
    print "best=",bestRows
    print "other=",otherRows
    
    return dict(bestRows=bestRows, otherRows=otherRows, raw=raw)
    
# end of _findResources


def _determineResources(resId, resType, arch, archVersionStr, resVersionStr, xParam, raw) :
    
    archVersion = float(archVersionStr) if archVersionStr else None
    resVersion = float(resVersionStr) if resVersionStr else None
    
    rows = db(db.langResource.resourceId == resId).select()
    print "number of rows=",len(rows)
    bestIds = []
    otherIds = []
    for row in rows :
        fBest = True
        
        rowArchVersion = float(row.archVersion) if row.archVersion else None
        rowResVersion = float(row.resVersion) if row.resVersion else None
        
        if resType and resType != "" and row.resourceType != resType :
            fBest = False
            
        if row.arch == "all" :
            pass
        elif arch and arch != "" and row.arch != arch :
            fBest = False
        elif archVersion and rowArchVersion > archVersion :
            # arch-version is the MINIMUM version this resource will work on
            fBest = False
            
        if xParam and xParam != "" and row.xParam != xParam :
            fBest = False
            
        if resVersion and rowResVersion != resVersion :
            fBest = False
        
        if fBest :
            bestIds.append(row.id)
        else :
            otherIds.append(row.id)
        
    return dict(best=bestIds, other=otherIds)
    
    
# end of _determineResources

def downloadResource() :
    print "------------------- downloadResource -----------------------"
    
    recordId = request.get_vars.id
    rows = db(db.langResource.id == recordId).select()
    print "rows=",rows
    if len(rows) == 0 :
        # 404 error: resource not found
        raise HTTP(404)
    else :
        record = rows[0]
    
    raw = int(request.get_vars.raw) if request.get_vars.raw else 0
    redirect = int(request.get_vars.redirect) if request.get_vars.redirect else 0
    
    if redirect == 1 :
        _doRedirect(recordId, record)
    elif raw == 1 :
        return _downloadRawData(recordId, record)
    else :
        return _doDownload(recordId, record)
    
# end of downloadResource


def _doDownload(recordId, record) :
       
    tempFilePath = "./applications/lsp/temp/"
    
    _cleanDirectory(tempFilePath)

    resourceId = record['resourceId']
    url = record['url']
    zipElement = record['zipElement']

    ext = os.path.splitext(url)[1][1:]
    userFileName = resourceId + "." + ext if ext != None and ext != "" else resourceId
        
    print "userFileName=",userFileName
    
    print "url=",url
    try:
        result = urllib2.urlopen(url)
        print "file retrieved"
        err = False
    except urllib2.URLError as e:
        err = True
        result = dict(urlopenError = e.reason)
    
    if not err :
        tmpFile = tempfile.NamedTemporaryFile('wb', -1, '', 'tmp_', tempFilePath, delete=False)
        fileName = tmpFile.name
        
        writeStream = open(fileName, 'wb')
        writeStream.write(result.read())
        writeStream.close()
        
        if zipElement != None and zipElement != "" :
            (extractedFile, httpResult, errorMessage) = _extractFromZip(fileName, zipElement)
            if extractedFile == None :
                print errorMessage
                print "Full ZIP file will be downloaded"
                # OR:
                #raise HTTP(httpResult)
            else :
                fileName = extractedFile
                print "Returning ",fileName
                ext = os.path.splitext(extractedFile)[1][1:]
                userFileName = resourceId + "." + ext if ext != None and ext != "" else resourceId
    
        result = response.stream(fileName, attachment=True, filename=userFileName)
    
    return result  # file to download, or dict with error message

# end of _doDownload


def _extractFromZip(zipFile, subElement) :
    
    randomString = zipFile[-6:]
    print randomString
    zipFile = zipFile.replace("\\", "/")
    
    if zipFile[1:3] == ":/" :  # eg, C:/
        zipFile = "/cygdrive/" + zipFile[0:1] + "/" + zipFile[3:]
    
    print "Extracting '" + subElement + "' from " + zipFile + "..."
    
    tempDirPath = "./applications/lsp/temp/unzip_" + randomString
    try :
        os.stat(tempDirPath)
    except :
        os.mkdir(tempDirPath)    

    # TODO: make this smarter about where to find the unzip program.
    exe = "C:/program files/bin/unzip.exe"
    args = " -q -d " + tempDirPath + " " + zipFile;
		
    if exe.find(" ") != -1 :
        exe = '"' + exe + '"'
	
    command = exe + args
    try :
        result = subprocess.call(command)
        error = ""
    except :
        error = "Error in calling unzip utility"
    
    if error == "" :    
        extractedFile = tempDirPath + "/" + subElement
        if result == 0 and os.path.isfile(extractedFile) :
            return (extractedFile, 200, "")
        else :
            return (None, 500, "Error in extracting zip file")
    else :
        return (None, 500, error)

# end of _extractFromZip


def _downloadRawData(recordId, record) :
    
    tempFilePath = "./applications/lsp/temp/"

    resId = record['resourceId']
    
    userFileName = resId + "." + "csv"
    
    output = ""
    sep = ""
    
    fieldKeys = db.langResource.fields()
    for key in fieldKeys :
        if key == "id" :
            # internal field; ignore
            pass
        elif key[0:5] == "meta_" :
            # meta-data; ignore
            pass
        else :
            # todo: handle commas in values
            output += sep
            output += record[key]
            sep = ","
            
    print "output=",output
            
    tmpFile = tempfile.NamedTemporaryFile('w', -1, '', 'tmp_', tempFilePath, delete=False)
    filename = tmpFile.name
        
    writeStream = open(filename, 'w')
    writeStream.write(output)
    writeStream.close()
    
    result = response.stream(filename, attachment=True, filename=userFileName)

# end of _downloadRawData


def _doRedirect(recordId, record) :
    
    resourceId = record['resourceId']
    url = record['url']

    print "redirecting to url: ",url
    redirect(url)
    
# end of _doRedirect

# Remove any old files from the temp directory.
def _cleanDirectory(path) :
    
    curTime = time.time()
    for filename in os.listdir(path):
        fullName = path + filename
        st = os.stat(fullName)
        age = curTime - st.st_mtime
        print fullName,age
        if age > 1000 :     # more than about 15 minutes old
            if os.path.isdir(fullName) :
                shutil.rmtree(fullName)
            else :
                os.remove(fullName)
        
# end of _cleanDirectory

##########################################################################

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())
