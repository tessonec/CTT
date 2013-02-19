#! /usr/bin/python
# -*- coding: utf-8 -*-
version_number = "1.8.0"
release_date   = "Mon Feb 18 2012"
# :::~ Author: Claudio Juan Tessone <tessonec@ethz.ch> (c) 2002-2013
# Distributed According to GNU Generic Purpose License (GPL) version 2
# visit www.gnu.org
################################################################################
#
# Changelog
# 1.7.1 (18/02/12) forked from ctt.py
#
#
################################################################################
#
# TODO LIST
# *   Add language support
# *** documentation of .ct files
# *** cleanup of python code (too messy) to make it easily extendable
# **  generate (Python?), Ansi C, (Java?) Code
#
################################################################################
#
allow_null_config = False

safeOperation = False

included_files=[]
import os.path
def search_for_includes(com):
  for l in com:
    if l[0]=="include":

      if os.path.abspath(l[1]) in included_files:
        print "[ctt - ERROR] '%s' already included in .ct file"%l[1]
        sys.exit(4)
      print "[ctt - MESSAGE] including: %s..."%l[1]
      included_files.append(os.path.abspath(l[1]))

      mascoms= [ linea.strip().split(":")
                 for linea in open(l[1],"r").readlines()
                 if len(linea) > 1
               ];
      com.remove(l)
      com+=mascoms
      search_for_includes(com)



def definition(v):
  
  if v[0]=="flag":
    print "    //:::~ ",v[2]
    print "    public  boolean ",v[1],"= false ;"
    return
  else:
    print "    //:::~ ",v[4]
  if v[1] != "string":
    print "    public ",v[1],v[2],"=",v[3],";"
    if v[0] == "choice":
        print "    private List<%s> %s_CTT_OPTIONS = new ArrayList(  );"%(v[1],v[2])
  else:
    print "    public String ",v[2],"=",v[3].split(",")[0],";"
    if v[0] == "choice":
        print "    private List<String> %s_CTT_OPTIONS = new ArrayList(  );"%(v[2])
  

def parse_value(v):
  type_conv = {"double":"double","float":"float","int":"int","long":"long","string":"String"}
  dic_conv = {"double":"nextDouble","float":"nextFloat","int":"nextInt","long":"nextLong","string":"next"}
  if v[0]=="flag":
    print 4*" "+"    if(current_key.equals( \""+v[1]+"\") ){"
    print 4*" "+"       this.%s = true;"%v[1]
    print 4*" "+"    }"
  if v[0]=="val":
      
      print 4*" "+"    if(current_key.equals( \""+v[2]+"\") ){"
      print 4*" "+"      this."+v[2]+" = scan.%s();"%dic_conv[v[1]]
      print 4*" "+"    }  "
  if v[0] == "choice":
      
      print 4*" "+"    if(current_key.equals( \""+v[2]+"\" ) ){"
      print 4*" "+"    %s value = scan.%s();"%(type_conv[v[1]],dic_conv[v[1]])
      print 4*" "+"    if (! %s_CTT_OPTIONS.contains(value) ){"%v[2]
      print 4*" "+"      System.err.println(\"[ - ERR ] value '\"+ value +\"' not among the possible for '\"+current_key+\"'\");"
                
      print 4*" "+"      System.exit(1);"
      print 4*" "+"    }"
      print 4*" "+"    %s = value;"%v[2]
      print 4*" "+"    }"
  
#def externdefinition(v):
#  
#  if v[0]=="flag":
#    print "//:::~ ",v[2]
#    print "extern bool ",v[1],"/* = ","false","*/",";"
#    return
#  else:
#    print "//:::~ ",v[4]
#  if v[1] != "string":
#    print "extern ",v[1],v[2],"/* = ",v[3],"*/",";"
#  else:
#    print "extern std::"+v[1],v[2],"/* = ",v[3].split(",")[0],"*/ ;"




def choice(v):
  if v[0]=="flag":
    print '  if (foo == "'+v[1]+'")'
    print "  {"
    print "     ", v[1], "=true;"
    print '      std::cerr << " +  {ctt - SETTING} " << "'+v[1]+' = true" << std::endl;'
    print "  }"
    return
  print '  if (foo == "'+v[2]+'")'
  print "  {"

  if v[0]=="val":
    print "    fin >> ", v[2], ";"
    print '      std::cerr << " +  {ctt - SETTING} " << "'+v[2]+' = " <<', v[2],' << std::endl;'

  if v[0]=="choice":
    posValues=v[3].split(",")
    print "    {"
    print "      fin >> ",v[2],";"
    choclo = ["("+v[2]+"!="+i+")" for i in posValues]
    print "      if ( ","&&".join(choclo),")"
    print "      {"
    print '        std::cerr << " +  {ctt - ERROR} \'" <<',v[2],
    print ' << "\' not between possible values of '+v[2]+'"', " << std::endl;"
    print '        std::cerr << " +  {ctt - ERROR} Possible values are: " << ','<< " " <<'.join([i   for i in posValues]),' << std::endl;'
    print "        exit(EXIT_FAILURE);"
    print "      }"
    print "    }"
    print '    std::cerr << " +  {ctt - SETTING} " << "'+v[2]+' = " <<', v[2],' << std::endl;'

  print
  print "  }"


def backendize(infile):
  fin = open(infile, "r")
  output = []
  ls_output = []
  for line in fin.readlines():
    if line.strip()[0] == "#" or len(line.strip()) == 0: continue
      
    if line.strip()[0] == "@":
      vec = line.strip()[1:].split()
      var_name_2 = ""
      try:
        backend = vec[0]
	try:
          var_name = vec[1]
        except:
	  var_name = ""
	try:
          var_name_2 = vec[2]
	except:
	  var_name_2 = ""
      except:
        sys.stderr.write("[ctt - ERROR] when unfolding line '%s'\n"%(line) )
        sys.exit()
      try:
        #print >> sys.stderr,var_name ,var_name_1 ,var_name_2  
        new_stuff = [
                    i.replace("%ARG%",var_name).replace("%ARG1%",var_name).replace("%ARG2%",var_name_2)
                    for i in open( os.path.expanduser("~/opt/etc/ctt/%s.be"%backend), "r" ).readlines()
                  ]
      except:
        sys.stderr.write("[ctt - ERROR] when loading backend '%s' and variable '%s'\n"%(backend,var_name) )
        sys.exit()
      #print >> sys.stderr,new_stuff
      output.extend (new_stuff)
      ls_output.append( (backend, var_name, var_name_2)  )
    else:
      output.append(line)
  return ls_output,output




if __name__=="__main__":

   import getopt, sys

   import os.path

   createInit=False

   try:
        opts, args = getopt.getopt(sys.argv[1:], "nihvup:s")
   except getopt.GetoptError:
        # print help information and exit:
        print "[ctt - ERROR] unknown option"
        #print "[ctt - ERROR] Help and getopt not implemented yet! "
        sys.exit(2)

   if len(args)>1:
     print "[ctt - ERROR] can only parse once at a time"
     sys.exit(2)

   packageName = None
   for o, a in opts:
        if o == "-u":
          allow_null_config = True
        if o == "-p":
          packageName=a
        if o == "-i":
          createInit=True
        if o == "-v":
          print "This is %s, version: %s\nrelease date: %s"%(os.path.split(sys.argv[0])[1],version_number,release_date)
	  sys.exit()
        if o == "-h":
          print "Usage is %s [OPTIONS] base.ct"%os.path.split(sys.argv[0])[1]
	  print "  -d: creates documentation"
	  print "  -n: generates namespace inside de code"
          print "  -i: generates initialization routine "
          print "  -u: allows nUll config files "

	  sys.exit()

   fname=os.path.splitext(args[0])[0].capitalize()

   ifname = "in.dat"
   try:
      ifname = "".join(open("conf.in").readlines()).strip()
   except: pass

   release_date = '""'
   version      = '""'
   try:
     l1 = open("Changelog").readline().split()
     version      = '"%s"'%l1[1]
     release_date = '"%s"'%l1[3]

   except:
     sys.stderr.write("[ctt - WARNING] 'Changelog' file not found/bad permissions/could not parse it\n")
     sys.stderr.write("[ctt - WARNING] not setting release date, nor version\n")

   original_stdout=sys.stdout
   print "[ctt - MESSAGE] generating code from:",args[0],"..."
   backends,lineas= backendize(args[0])
#   print lineas
   comandos = [ linea.strip().split(":")
                 for linea in
                 lineas
                 if len(linea) > 1
               ];
#   comandos.append(["val","long","randomseed","0","semilla de los numeros aleatorios"])
   included_files.append(os.path.abspath(args[0]))
   search_for_includes(comandos)

#   sys.stdout=open(fname+".h","w")
#   print "//:::~ "
#   print "//:::~ File automaticamente generado por",os.path.split(sys.argv[0])[1]," NO EDITAR"
#   print "//:::~ "
#   print
#   print "#ifndef __CTTBASE_H"
#   print "#define __CTTBASE_H"
#   print "#include <cstdlib>"
#   print "#include <string>"
#   print "#include <iostream>"
#   print "#include <ctime>"
#   print "#include <sys/time.h>"
#   #print "#include <sys/stat.h>"
#   print "#include <fstream>"
#   print '#include <dranxor.h>'
#   
#   print
#   
   includes = set()
   vars_from_be = []
#   for backend, var_name, var_name_2 in backends:
 #    print backend
#     for linea_h in open(os.path.expanduser("~/opt/etc/ctt/%s.be.java"%backend)):
#       if "import" in linea_h.strip():
#         includes.add(linea_h.strip())
#       else:
##         sys.stderr.write("%s\n"%linea_h.strip())
#         vars_from_be.append(linea_h.strip().replace("%ARG%",var_name).replace("%ARG1%",var_name).replace("%ARG2%",var_name))

 #  print '//:::~ includes found in backends'
 #  for inc in includes:
 #     print inc
 #  print
#   print "#define VERSION_NUMBER %s"%version
#   print "#define RELEASE_DATE %s"%release_date
#
#   print
#   print
#   print "//:::~ +++++++++++++++++++++++++++++++++++++++++++++++++++++++"
#   print "//:::~ +++++++++++++++++++++++++++++++++++++++++++++++++++++++"
#   print "//:::~ Definiciones de las variables seteables desde el infile"
#   print "//:::~ +++++++++++++++++++++++++++++++++++++++++++++++++++++++"
#   print "//:::~ +++++++++++++++++++++++++++++++++++++++++++++++++++++++"
#   print 	
##   if useNamespaces:
#   print "namespace CTGlobal"
#   print "{"
#   print
##   print '  extern  long randomseed; /* = 0*/'
#   print '  extern std::string filein /* = "%s" */ ;'%ifname
#   print
#   print '  extern std::string prog_name /*  */ ;'
#   print
#   print '  extern int verbosityLevel /* = 0*/;'
#   print '  extern bool quietRun /* = false*/;'
#   print
##   for i in comandos:
##     #print >> sys.stderr, i
##     externdefinition(i)
#   print
#   print "// from backends"
#   for i in vars_from_be:
#     if i.strip() != '':
#       print "extern ",i.split("=")[0], ";"
#   print
#   print "//:::~ +++++++++++++++++++++++++++++++++++++++++++++++++++++++"
#   print "//:::~ Parse de las variables"
#   print "//:::~ +++++++++++++++++++++++++++++++++++++++++++++++++++++++"
#   print "void input_variables(std::istream &fin);"
#
#   print
#   print "//:::~ +++++++++++++++++++++++++++++++++++++++++++++++++++++++"
#   print "//:::~ Asking for output"
#   print "//:::~ +++++++++++++++++++++++++++++++++++++++++++++++++++++++"
#   print
#   print 'void query_output(std::string type, std::string msg , std::string opening_closing = "<>",int indent=0);'
#   print
#   print "//:::~ +++++++++++++++++++++++++++++++++++++++++++++++++++++++"
#   print "//:::~ Small Help"
#   print "//:::~ +++++++++++++++++++++++++++++++++++++++++++++++++++++++"
#   print
#   print "void help_available();"
#   if createInit:
#     print "//:::~ +++++++++++++++++++++++++++++++++++++++++++++++++++++++"
#     print "//:::~ Option reading"
#     print "//:::~ +++++++++++++++++++++++++++++++++++++++++++++++++++++++"
#     print "void initialize_program(int &argc, char** & argv);"
##   if useNamespaces:
#   print "};"
#   print
#   print "#endif"
#   print
#   sys.stdout.close()

   sys.stdout=open(fname+".java","w" )
   print "//:::~ "
   print "//:::~ File automatically generated by",
   print os.path.basename( sys.argv[0] ),
   print " DO NOIT EDIT"
   print "//:::~ "
   if packageName is not None:
     print "package ", packageName,";"
   print
   print "import java.util.ArrayList;"
   print "import java.util.List;"
 
   print "import java.util.Scanner;"
   print "import java.io.File;"
   print "import java.io.FileNotFoundException;"
   print "import java.io.IOException;"

#   if createInit:
#     print '#include <util/ctgetopt.h>'
#     print '#include <tclap/CmdLine.h>'
#   print '#include "%s.h"'%os.path.splitext( os.path.basename( fname ) )[0]
   print
   print "//:::~ +++++++++++++++++++++++++++++++++++++++++++++++++++++++"
   print "//:::~ Variable Definitions setable from infile"
   print "//:::~ +++++++++++++++++++++++++++++++++++++++++++++++++++++++"
   print
#   if useNamespaces:
   print "public class %s"%fname
   print "{"
   print
#   print '  String filein = "%s";'%ifname
   print
   print '  int verbosityLevel  = 0;'
   print '  boolean quietRun = false;'

   print '  String prog_name = "" ;'
   #   print '  long randomseed = 0;'
   print
   for i in comandos:
     definition(i)
   print
   print "      // :::~ from backends BEGIN"
   for i in vars_from_be:
     print i
   print "      // :::~ from backends END"

   print 4*" "+"private List<String> CTT_ACCEPTED_KEYWORDS =  new ArrayList(  );"

   print
   print 4*" "+"public void query_output(String type, String msg , String oc, int indent){"
   print 4*" "+'  for(int i=0;i<indent;i++) System.err.print(" ");'
   print 4*" "+'  System.err.print( oc.charAt(0) + " ");'
   print 4*" "+'  System.err.print( prog_name + " - "+ type + " ");'
   print 4*" "+'  System.err.print( oc.charAt(1) );'
   print 4*" "+'  System.err.println( msg );'
   print 4*" "+"}"
   print
   
   print 4*" "+"public %s() {"%fname
   for v in comandos:
       if v[0] == "flag":
         print 6*" "+'CTT_ACCEPTED_KEYWORDS.add("%s"); '%v[1]
       else: 
         print 6*" "+'CTT_ACCEPTED_KEYWORDS.add("%s"); '%v[2]
       if v[0] == "choice":
           print 6*" "
           for op in v[3].split(","):
             print 6*" "+'%s_CTT_OPTIONS.add(%s);'%(v[2],op)
           print 6*" "
           
   print 6*" "+" "
   print 6*" "+" "
   print 4*" "+"}"
   print
   print 4*" "+"//:::~ +++++++++++++++++++++++++++++++++++++++++++++++++++++++"
   print 4*" "+"//:::~ Variable parsing"
   print 4*" "+"//:::~ +++++++++++++++++++++++++++++++++++++++++++++++++++++++"
   print
   print 4*" "+"public void input_variables(String fname)"
   print 4*" "+"{"
   print 4*" "+"  Scanner scan;"
   print 4*" "+"  try{"
   print 4*" "+"      scan = new Scanner(new File(fname) );"


   print 4*" "+"  while(scan.hasNext()){"
   print 4*" "+"     String current_key = scan.next();"
   print 6*" "+"     if (! CTT_ACCEPTED_KEYWORDS.contains(current_key) ){"
   print 6*" "+"       System.err.println(\"[ - ERR ] keyword not found: '\"+current_key+\"'\");"
   print 6*" "+"         System.exit(1);"
   print 6*" "+"     }"
            

   for i in comandos:
     parse_value(i)    
   print
   print 6*" "+"}"

   print 4*" "+"  } catch (FileNotFoundException e) {"
   print 4*" "+"      e.printStackTrace();"
   print 4*" "+"  }"
   
   print 4*" "+"}"
   print "};"
   
   sys.stdout.close()




