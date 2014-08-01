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

def index() :
    newUrl = request.env.http_host + request.env.path_info + "/wirl/findResource"
    print newUrl
    redirect(newUrl)  # why doesn't this work???


@auth.requires_login()
def show():
    #image = db.image(request.args(0,cast=int)) or redirect(URL('index'))
    image = db.image(request.args(0,cast=int,otherwise=URL('error')))
    db.post.image_id.default = image.id
    form = SQLFORM(db.post)
    if form.process().accepted:
        response.flash = 'your comment is posted'
    comments_posted = db(db.post.image_id==image.id).select()
    return dict(image=image, comments=comments_posted, form=form)
    

def user():
    return dict(form=auth())
    

def download():
    return response.download(request, db)
    
#################################################
    
#def index_counter() :
#    if not session.counter:
#        session.counter = 1
#    else:
#        session.counter += 1
#    return dict(message="Hello from MyApp", counter=session.counter)

#################################################
 
def first():
    if request.vars.visitor_name :
        msg1 = "Welcome back, " + request.vars.visitor_name + "!"
    else :
        msg1 = "Welcome!"
        
    msg2 = ""
    
    aForm = SQLFORM.factory(
        Field('visitor_name', label='Your name', requires=IS_NOT_EMPTY()),
        Field('password_attempt', label='Password'))   
        
    if request.vars.password_attempt :
        if request.vars.password_attempt == "hello" :
            session.password_okay = True
        else :
            msg2 = "Incorrect password, please try again."
            session.password_okay = False
    else :
        session.password_okay = False

    if aForm.process().accepted and session.password_okay :
        session.visitor_name = request.vars.visitor_name
        redirect(URL('second'))   
    #else :
    return dict(form = aForm, message1 = msg1, message2 = msg2)


def second() :
    if not session.password_okay or session.password_okay != True :
        msg2 = "NO PASSWORD!"
    else :
        msg2 = "You entered the correct password, thanks."
    return dict(message2 = msg2)