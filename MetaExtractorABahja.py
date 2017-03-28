import requests
import argparse
import sys
from bs4 import BeautifulSoup
import os
import PyPDF2
import olefile
import subprocess
import warnings
import datetime

warnings.filterwarnings("ignore")
metaOut="MetaResults.txt"
reload(sys)
sys.setdefaultencoding('UTF8')


magic_N={'pdf':'%PDF','msoffice':'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1','msoffice10':'PK'}
global startNr
startNr=0


######################################################################
#plans for the future
"""
'jpg':'\xff\xd8','gif':'GIF89','png':'PNG','mp3':'ID3','mp4':'ftyp',
'tar':'\x75\x73\x74\x61\x72','gz':'\x1f\x8b\x08','exe':'MZ'}
"""
######################################################################
def format_date(string):
  string=string.strip('D').strip(':')[0:14]
  dt=datetime.datetime.strptime(string,'%Y%m%d%H%M%S')
  return dt.strftime('%Y-%m-%d %H:%M:%S')

def pdf_meta(filename,downNot):
  mp=open(filename,'rb')
  read_pdf=PyPDF2.PdfFileReader(mp)
  #pdf metadata
  if read_pdf.isEncrypted:
     return
  meta_simple=read_pdf.getDocumentInfo()
  if meta_simple==None:
     print "No metadata of "+filename
     return
  fp=open(metaOut,"a")
  fp.write("\nMetadata of "+filename+":\n")
  if 'Author' in str(meta_simple.keys()):
     fp.write("Author: "+meta_simple['/Author']+"\n")
  else:
     fp.write("Author: None\n")
  if 'Title' in str(meta_simple.keys()):
     fp.write("Title: "+meta_simple['/Title']+"\n")
  else:
     fp.write("Title: None\n")
  if 'Template' in str(meta_simple.keys()):
     fp.write("Template: "+meta_simple['/Template']+"\n")
  else:
     fp.write("Template: None\n")
  if 'Last_Saved' in str(meta_simple.keys()):
     fp.write("Last_Saved_by: "+meta_simple['/Last_saved_by']+"\n")
  else:
     fp.write("Last_Saved_by: None\n")
  if 'CreationDate' in str(meta_simple.keys()):
     fp.write("Created_Date: "+format_date(meta_simple['/CreationDate'])+"\n")
  else:
     fp.write("Created_Date: None\n")
  if 'ModDate' in str(meta_simple.keys()):
     fp.write("Modified_Date: "+format_date(meta_simple['/ModDate'])+"\n")
  else:
     fp.write("Modified_Date: None\n")
  if 'Creator' in str(meta_simple.keys()):
     fp.write("Created_Application: "+meta_simple['/Creator']+"\n")
  else:
     fp.write("Created_Application: None\n")
  if 'Producer' in str(meta_simple.keys()):
     fp.write("Converted_Application: "+meta_simple['/Producer']+"\n")
  else:
     fp.write("Producer_Application: None\n")
  if 'Subject' in str(meta_simple.keys()):
     fp.write("Subject: "+meta_simple['/Subject']+"\n")
  else:
     fp.write("Subject: None\n")
  if 'Comments' in str(meta_simple.keys()):
     fp.write("Comments: "+meta_simple['/Comments']+"\n")
  else:
     fp.write("Comments: None\n")
  if 'Keywords' in str(meta_simple.keys()):
     fp.write("Keywords: "+meta_simple['/Keywords']+"\n")
  else:
     fp.write("Keywords: None\n")
  fp.close()
  if downNot=='n' or downNot=='N':
    os.remove(filename)
  mp.close()
 
def ole_meta(filename,downNot):
  fp=open(filename,'rb')
  read_ole=olefile.OleFileIO(fp)
  meta_data=read_ole.get_metadata()
  fp=open(metaOut,"a")
  fp.write("\n\n[+]Metadata of "+filename+":"+'\n')
  fp.write("Title: "+meta_data.title+'\n')
  fp.write("Template: "+meta_data.template+'\n')
  fp.write("Author: "+meta_data.author+'\n')
  fp.write("Last_Saved_by: "+meta_data.last_saved_by+'\n')
  fp.write("Created_Date: "+str(meta_data.create_time)+'\n')
  fp.write("Modified_Date: "+str(meta_data.last_saved_time)+'\n')
  fp.write("Created_Application: "+str(meta_data.creating_application)+'\n')
  fp.write("Converted_Application: "+"None"+'\n')
  fp.write("Subject: "+str(meta_data.subject)+'\n')
  fp.write("Comments: "+str(meta_data.comments)+'\n')
  fp.write("Keywords: "+str(meta_data.keywords)+'\n')
  fp.write("Language: "+str(meta_data.language)+'\n')
  fp.close()
  if downNot=='n' or downNot=='N':
    os.remove(filename)
  read_ole.close()
"""
def meta_hachoirlib(filename):
  fileName=hachoir_core.cmd_line.unicodeFilename(filename)
  parser=hachoir_parser.createParser(fileName)
  metadata=hachoir_metadata.extractMetadata(parser)
  metatext=metadata.exportPlaintext()
  for meta in metatext:
     print meta
"""
def searchDomain(domain,filetype):
  try:
    inurl_op="inurl:"+domain
    site_op="site:"+domain
    fileType="filetype:"+filetype
    param=str(inurl_op)+" "+str(site_op)+" "+str(fileType)
    payload={"q":param,"filter":0} 
    header={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'}
  
    print "[+]Searching..."
    r=requests.get("https://www.google.al/search",params=payload,headers=header)
    return r
  except requests.exceptions.ConnectionError, e:
    print e 
    print "--------------------"
    print "[-]Check the name of domain if it exists"
    print "[-]Check your internet connection"
    sys.exit(1)


#function for extracting link of files from a page
def getURL(page):
  startLink = page.find("a href") 
 
  if startLink == -1: 
    return None, 0
  start_point = page.find('"', startLink) 
  end_point = page.find('"', start_point + 1)
  
  url = page[start_point + 1: end_point]
  return url,end_point

#function for dowloading files
def downloadFiles(urlresponse,files,downNot):
  page = str(BeautifulSoup(urlresponse.content,"lxml"))
  
  while True:
    url,n = getURL(page)
    page = page[n:] 
    if url:
      if str(url).endswith(str(files)):
        if downNot=='n' or downL=='N':
           print "[+]Extracting ==> "+url
        else:
           print "[+]Downloading ==> "+url
        r = requests.get(url) 
        list_A=str(url).split('/')
        leng=len(list_A) 
        nameofFile=list_A[leng-1]
        with open(nameofFile, "wb") as code: 
           code.write(r.content)
        if os.path.exists(nameofFile):
            fp=open(nameofFile,'rb')
            m_num=fp.read(20)
            for elem in magic_N:
               if magic_N[elem] in m_num:
                  if elem=='pdf':
                     pdf_meta(nameofFile,downNot)
                  if elem=='msoffice': #xls,ppt,doc
                     ole_meta(nameofFile,downNot)

                 # else:   meta_hachoirlib(nameofFile) 
        else:
           print "File does not exists"
           exit(0)
    else:
      break 

def main():
  print "\n *******************************************************"
  print " *                                                     *"
  print " * Fast Metadata Extractor of Public Documents Ver 1.0 *"
  print " * Adrian Bahja                                        *"
  print " * adrianbahja@gmail.com                               *"
  print " *                                                     *"
  print " *******************************************************\n "
  parser=argparse.ArgumentParser()
  parser.add_argument("-d",dest="domain",type=str,help="Enter domain(ex: example.com)")
  parser.add_argument("-f",dest="fileF",type=str,help="Enter the file types(pdf,doc,xls,ppt)")
  parser.add_argument("-o",dest="outFile",type=str,help="The Output File for saving results(default=metaResults.txt)")
  args=parser.parse_args()
  if len(sys.argv)>3:
       if args.domain.strip()=="" or args.fileF.strip()=="":
          print parser.print_help()
          sys.exit(0)
       else:
          if args.outFile:
             global metaOut 
             metaOut=args.outFile
          downL=raw_input("Do you want to download files locally(Y/N) ? ")
          while True:
             if downL=='y' or downL=='Y' or downL=='n' or downL=='N':
                domain=args.domain
                fileF=str(args.fileF).split(',')#list of file types
                for files in fileF:
                  req=searchDomain(domain,files)#search the Domain for each file type
                  print "[+]Results..."
                  print req.url                  
                  downloadFiles(req,files,downL)#download files
                break
             else:
                print "Enter the right answer(Y or N)\n"
                downL=raw_input("Do you want to download files locally(Y/N) ? ")
  else:
      parser.error(message="\n[-]Arguments are required\n[-]Enter the right format")
if __name__=="__main__":
  main()


