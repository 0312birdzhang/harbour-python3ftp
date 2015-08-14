# -*- coding: utf-8 -*-
# modifyDate: 20120808 ~ 20120810
# 原作者为：bones7456, http://li2z.cn/
# 修改者为：decli@qq.com
# python3版本修改者 : 0312birdzhang@gmail.com
# v1.2，changeLog：
# +: 文件日期/时间/颜色显示、多线程支持、主页跳转
# -: 解决不同浏览器下上传文件名乱码问题：仅IE，其它浏览器暂时没处理。
# -: 一些路径显示的bug，主要是 cgi.escape() 转义问题
# ?: notepad++ 下直接编译的server路径问题


"""Simple HTTP Server With Upload.

This module builds on BaseHTTPServer by implementing the standard GET
and HEAD requests in a fairly straightforward manner.

"""

__version__ = "0.1"
__all__ = ["SimpleHTTPRequestHandler"]
__author__ = "bones7456"
__home_page__ = ""

import os, sys, platform
import posixpath
import http.server
from socketserver import ThreadingMixIn
import threading
import urllib.request, urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse
import cgi
import shutil
import mimetypes
import re
import time
import pyotherside
import socket
import random

try:
    from io import StringIO
except ImportError:
    from io import StringIO

def get_ip_address(ifname):
    import socket
    import fcntl
    import struct
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915, # SIOCGIFADDR
            struct.pack(b'256s', ifname[:15])
        )[20:24])
    except:
        return "You may not connected to wifi"

class GetWanIp:
    def getip(self):
        try:
           myip = self.visit("http://ip.taobao.com/service/getIpInfo.php?ip=myip")
        except:
            pyotherside("ip.taobao.com is Error")
            try:
                myip = self.visit("http://www.bliao.com/ip.phtml")
            except:
                print("bliao.com is Error")
                try:
                    myip = self.visit("http://www.whereismyip.com/")
                except: # 'NoneType' object has no attribute 'group'
                    print("whereismyip is Error")
                    myip = "127.0.0.1"
        return myip
    def visit(self,url):
        #req = urllib2.Request(url)
        #values = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.64 Safari/537',
        #            'Referer': 'http://ip.taobao.com/ipSearch.php',
        #            'ip': 'myip'
        #         }
        #data = urllib.urlencode(values)
        opener = urllib.request.urlopen(url, None, 3)
        if url == opener.geturl():
            str = opener.read()
        return re.search('(\d+\.){3}\d+',str).group(0)
def scan(port):
    sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sk.settimeout(3)
    flag=False
    try:
        sk.connect(('127.0.0.1',port))
        flag=True
    except Exception:
        flag=False
    sk.close()
    return flag

#随机端口号
def randomport():
    port=9537
    pflag = scan(port)
    #如果端口开启,则更换随机端口
    while (pflag):
        port = random.randint(9000,50000)
        pflag = scan(port)
    return port

def showTips():
    pyotherside.send("")
    pyotherside.send('-------->>Starting------------ ')
    pyotherside.send("")
    # try:
    #     port = int(sys.argv[1])
    # except Exception as e:
    #     pyotherside.send('-------->> Warning: Port is not given, will use deafult port: 8080 ')
    #     pyotherside.send('-------->> if you want to use other port, please execute: ')
    #     pyotherside.send('-------->> python SimpleHTTPServerWithUpload.py port ')
    #     pyotherside.send("-------->> port is a integer and it's range: 1024 < port < 65535 ")
    port = randomport()

    if not 1024 < port < 65535:  port = 9898
    # serveraddr = ('', port)
    pyotherside.send('-------->> Ftp Server started !')
    pyotherside.send("")
    pyotherside.send('-------->> Now, listening at port ' + str(port) + ' ...')
    pyotherside.send("")
    osType = platform.system()
    if osType == "Linux":
        pyotherside.send('-------->> You can visit the URL: http://'+get_ip_address(b'wlan0')+':'+str(port)+"at your computer")
    else:
        pyotherside.send('-------->> You can visit the URL: http://127.0.0.1:' +str(port))
    pyotherside.send("")
    pyotherside.send('-------->> Have Fun ;)---------------- ')
    pyotherside.send("")
    return ('', port)

serveraddr = showTips()

def sizeof_fmt(num):
    for x in ['bytes','KB','MB','GB']:
        if num < 1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0
    return "%3.1f%s" % (num, 'TB')

def modification_date(filename):
    # t = os.path.getmtime(filename)
    # return datetime.datetime.fromtimestamp(t)
    return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(os.path.getmtime(filename)))

class SimpleHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

    """Simple HTTP request handler with GET/HEAD/POST commands.

    This serves files from the current directory and any of its
    subdirectories.  The MIME type for files is determined by
    calling the .guess_type() method. And can reveive file uploaded
    by client.

    The GET/HEAD/POST requests are identical except that the HEAD
    request omits the actual contents of the file.

    """

    server_version = "SimpleHTTPWithUpload/" + __version__

    def do_GET(self):
        """Serve a GET request."""
        # print "....................", threading.currentThread().getName()
        f = self.send_head()
        if f:
            for i in f.readlines():
                if isinstance(i,str):
                    self.wfile.write(i.encode("utf-8", 'surrogateescape'))
                else:
                    self.wfile.write(i)
            #self.copyfile(f, self.wfile)
            f.close()

    def do_HEAD(self):
        """Serve a HEAD request."""
        f = self.send_head()
        if f:
            f.close()

    def do_POST(self):
        """Serve a POST request."""
        r, info = self.deal_post_data()
        print(r, info, "by: ", self.client_address)
        f = StringIO()
        f.write('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
        f.write("<html>\n<title>Upload Result Page</title>\n")
        f.write("<body>\n<h2>Upload Result Page</h2>\n")
        f.write("<hr>\n")
        if r:
            f.write("<strong>Success:</strong>")
        else:
            f.write("<strong>Failed:</strong>")
        f.write(info)
        f.write("<br><a href=\"%s\">back</a>" % self.headers['referer'])
        f.write("<hr><small>Powered By: bones7456, Ported By:0312birdzhang ")
        f.write("here</a>.</small></body>\n</html>\n")
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        if f:
            for i in f.readlines():
            #self.copyfile(f, self.wfile)
                self.wfile.write(i.encode("utf-8"))
            f.close()

    def deal_post_data(self):
        boundary = str(self.headers["Content-Type"].split("=")[1]).encode("utf-8")
        remainbytes = int(self.headers['Content-length'])
        line = self.rfile.readline()
        remainbytes -= len(line)
        if not boundary in line:
            return (False, "Content NOT begin with boundary")
        line = self.rfile.readline()
        remainbytes -= len(line)
        fn = re.findall(r'Content-Disposition.*name="file"; filename="(.*)"'.encode('utf-8'), line)
        if not fn or len(fn[0]) == 0:
            return (False, "Can't find out file name...")
        path = str(self.translate_path(self.path)).encode('utf-8')
        osType = platform.system()
        try:
            if osType == "Linux":
                fn = os.path.join(path, fn[0])
            else:
                fn = os.path.join(path, fn[0])
        except Exception as e:
            return (False, "Wrong File name charactor {}" .format(e))
        while os.path.exists(fn):
            fn += "_".encode("utf-8")
        line = self.rfile.readline()
        remainbytes -= len(line)
        line = self.rfile.readline()
        remainbytes -= len(line)
        try:
            out = open(fn, 'wb')
        except IOError:
            return (False, "Can't create file to write, do you have permission to write?")

        preline = self.rfile.readline()
        remainbytes -= len(preline)
        while remainbytes > 0:
            line = self.rfile.readline()
            remainbytes -= len(line)
            if boundary in line:
                preline = preline[0:-1]
                if preline.endswith('\r'.encode("utf-8")):
                    preline = preline[0:-1]
                out.write(preline)
                out.close()
                return (True, "File '%s' upload success!" % fn)
            else:
                out.write(preline)
                preline = line
        return (False, "Unexpect Ends of data.")

    def send_head(self):
        """Common code for GET and HEAD commands.

        This sends the response code and MIME headers.

        Return value is either a file object (which has to be copied
        to the outputfile by the caller unless the command was HEAD,
        and must be closed by the caller under all circumstances), or
        None, in which case the caller has nothing further to do.

        """
        path = self.translate_path(self.path)
        f = None
        if os.path.isdir(path):
            if not self.path.endswith('/'):
                # redirect browser - doing basically what apache does
                self.send_response(301)
                self.send_header("Location", self.path + "/")
                self.end_headers()
                return None
            for index in "index.html", "index.htm":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
            else:
                return self.list_directory(path)
        ctype = self.guess_type(path)
        try:
            # Always read in binary mode. Opening files in text mode may cause
            # newline translations, making the actual size of the content
            # transmitted *less* than the content-length!
            #f = open(path, 'rb')
            f = open(path, 'rb')
        except IOError:
            self.send_error(404, "File not found")
            return None
        self.send_response(200)
        #self.send_header("Content-type", ctype)
        self.send_header("Content-type", ctype+';charset = utf-8')
        fs = os.fstat(f.fileno())
        self.send_header("Content-Length", str(fs[6]))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        return f

    def list_directory(self, path):
        """Helper to produce a directory listing (absent index.html).

        Return value is either a file object, or None (indicating an
        error).  In either case, the headers are sent, making the
        interface the same as for send_head().

        """
        try:
            list = os.listdir(path)
        except os.error:
            self.send_error(404, "No permission to list directory")
            return None
        list.sort(key=lambda a: a.lower())
        f = StringIO()
        displaypath = cgi.escape(urllib.parse.unquote(self.path))
        f.write('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
        f.write("<html>\n<head>\n <meta charset=\"UTF-8\"> \n<title>Directory listing for %s</title>\n</head>" % displaypath)
        f.write("<body>\n<h2>Directory listing for %s</h2>\n" % displaypath)
        f.write("<hr>\n")
        f.write("<form ENCTYPE=\"multipart/form-data\" method=\"post\">")
        f.write("<input name=\"file\" type=\"file\"/>")
        f.write("<input type=\"submit\" value=\"upload\"/>")
        f.write("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;")
        f.write("<input type=\"button\" value=\"RootPage\" onClick=\"location='/'\"/>")
        f.write("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;")
        f.write("<input type=\"button\" value=\"HomePage\" onClick=\"location='/home/nemo'\"/>")
        f.write("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;")
        f.write("<input type=\"button\" value=\"AndroidPage\" onClick=\"location='/home/nemo/android_storage'\"/>")
        f.write("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;")
        f.write("<input type=\"button\" value=\"PreviousPage\" onClick=\"javascript:window.history.go(-1)\"/>")
        f.write("</form>\n")
        f.write("<hr>\n<ul>\n")
        for name in list:
            fullname = os.path.join(path, name)
            colorName = displayname = linkname = name
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                colorName = '<span style="background-color: #CEFFCE;">' + name + '/</span>'
                displayname = name
                linkname = name + "/"
            if os.path.islink(fullname):
                colorName = '<span style="background-color: #FFBFFF;">' + name + '@</span>'
            linkname = linkname.encode('utf-8', 'surrogateescape')#.decode('ISO-8859-1')
                # Note: a link to a directory displays with @ and links with /
            filename = os.getcwd() + '/' + displaypath + displayname
            filename = filename.encode('utf-8', 'surrogateescape')#.decode('ISO-8859-1')
            f.write('<table><tr><td width="60%%"><a href="%s">%s</a></td><td width="20%%">%s</td><td width="20%%">%s</td></tr>\n'
                    % (urllib.parse.quote(linkname), colorName,
                        sizeof_fmt(os.path.getsize(filename)), modification_date(filename)))
        f.write("</table>\n<hr>\n</body>\n</html>\n")
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/html;charset=utf-8")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        return f

    def translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax.

        Components that mean special things to the local file system
        (e.g. drive or directory names) are ignored.  (XXX They should
        probably be diagnosed.)

        """
        # abandon query parameters
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        path = posixpath.normpath(urllib.parse.unquote(path))
        words = path.split('/')
        words = [_f for _f in words if _f]
        path = os.getcwd()
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir): continue
            path = os.path.join(path, word)
        return path

    def copyfile(self, source, outputfile):
        """Copy all data between two file objects.

        The SOURCE argument is a file object open for reading
        (or anything with a read() method) and the DESTINATION
        argument is a file object open for writing (or
        anything with a write() method).

        The only reason for overriding this would be to change
        the block size or perhaps to replace newlines by CRLF
        -- note however that this the default server uses this
        to copy binary data as well.

        """
        shutil.copyfileobj(source, outputfile)

    def guess_type(self, path):
        """Guess the type of a file.

        Argument is a PATH (a filename).

        Return value is a string of the form type/subtype,
        usable for a MIME Content-type header.

        The default implementation looks the file's extension
        up in the table self.extensions_map, using application/octet-stream
        as a default; however it would be permissible (if
        slow) to look inside the data to make a better guess.

        """

        base, ext = posixpath.splitext(path)
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        ext = ext.lower()
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        else:
            return self.extensions_map['']

    if not mimetypes.inited:
        mimetypes.init() # try to read system mime.types
    extensions_map = mimetypes.types_map.copy()
    extensions_map.update({
        '': 'application/octet-stream', # Default
        '.py': 'text/plain',
        '.c': 'text/plain',
        '.h': 'text/plain',
        })

class ThreadingServer(ThreadingMixIn, http.server.HTTPServer):
    pass

def test(HandlerClass = SimpleHTTPRequestHandler,
       ServerClass = http.server.HTTPServer):
    http.server.test(HandlerClass, ServerClass)

def mymain():
    # test()

    #单线程
    # srvr = BaseHTTPServer.HTTPServer(serveraddr, SimpleHTTPRequestHandler)

    #多线程
    os.chdir("/")
    srvr = ThreadingServer(serveraddr, SimpleHTTPRequestHandler)

    srvr.serve_forever()
mymain()
