# Sphinx Documentation templates in Eclipse / PyDev

## Background
Python is quickly becoming the most commonly known and used programming language 
of geospatial professionals in the British Columbia Government.  Geospatial 
analysts started using as early as 2004 to automate geospatial tasks.  Since 
then a major training initiatives were launched and completed with the goal 
of expanding skill sets in python programming.  We now have potentially 100's of
staff all around the province who are capable of automating processes using python.

Most of these script are small script with a few 100 lines of code, however there 
are also scripts that automate business processes that can be 1000's of lines long.
These scripts pose a problem in terms of code maintainability.  In an effort develop 
programming habits that create scripts that are easily (or perhaps more easily)
maintainable by a team of staff as oppose to by a single developer the concept 
of standardised documentation has been introduced.  

While epydoc and the standard pydoc approaches were reviewed and assessed the 
standard that has been agreed to for larger scripts is [Sphinx] (http://sphinx-doc.org/).

###Why Sphinx
The main reasons for this choice are:

- **epydoc** does not seem to be well supported anymore.
- **sphinx** is the system that is used by the [python] (https://www.python.org/) in 
  the pydocs that they publish
- **sphinx** uses a relatively well known and easy to read markup language [reStructuredText] (http://docutils.sourceforge.net/rst.html)
  also referred to as **RST**
  
### Restructured Text and Eclipse PyDev
Restructured text offer a lot of benefits and is relatively easy to use.  However even
with these attributes uptake to standardised documenation by developers with tight 
time lines and low readability requirements for their code create a situation where
without some help uptake would be very low.  To solve this we wanted to create a 
templating system that allows uses to do something like press a button and insert
a template that they simply fill in.

The primarily development environment that is used by python developers in the BC Government
is Eclipse / PyDev therefore the templating tool was built on this product.

##Eclipse / PyDev Sphinx Templating tools - Usage

### Installing PyDev Sphinx Templating tools
Installing is a simple two step process:

1. Grab the python files in this projects wrk/python folder and put them in the 
   following directory relative to your eclipse install: <tt>plugins/org.python.pydev.jython_<i>versionNumber</i>/jysrc</tt>
   Once this step is complete the pyedit code should start to work.  In a python editor 
   try typing <tt>ctrl+2</tt>.  You should get the following pulldown<br> ![Alt pulldownImage] (wrk/img/pyEditMenu.png)
   
   
2. The template side of the things requires the code (that you just installed) as well as
   the documentation templates that tie the code to a template keyword.  To install templates
   grab the xml file in the templates directory and import it into pydev/eclipse by:
   
   1. go to Window->Preferences->Pydev->Editor->Templates <br> ![Alt ImportTemplates] (wrk/img/importTemplate.png) <br
      and select import.  Navigate to the xml file you pulled from this project.
   
   2. Once complete you should have the following entries included in your template:<br>
      ![Alt new documenation templates] (wrk/img/newTemplates.png)
      
### Using Eclipse/Pydev Sphinx Templates

Two different way to use these templates in your code.
#### Using the Editor add-ins to generate Sphinx Documentation Templates
   * __Document A Class__ 
       * Put your cursor somewhere in your script that is inside the 
         scope of your class and hit <tt>CTRL+2</tt>
       * Choose the option **Sphinx Class Documentation** This should insert a template
         that describes all your class variables/properties in a way that should integrate
         with what the sphinx documation system is expecting.  The following is 
         an example of what this might look like:
         
	         class Commenter:
	            '''
	            Describe your class here and more specifically
	            why you bothered to create it and how it makes
	            The world a better place!
	            
	            :ivar currentLine: Describe the variable here!
	            :ivar document: Describe the variable here!
	            :ivar editor: Describe the variable here!
	            :ivar offset: Describe the variable here!
	            :ivar selection: Describe the variable here!
	            '''
	     Now all you need to do is fill in the sections that say _Describe..._
	     with the appropriate text
	     
   * __Document A Module__
       * To document a module put your cursor somewhere in the scope of 
         the module you want to document and press <tt>CTRL+2</tt> 
       * Select *Sphinx Method Documentation*
       * You should get a comment block similar to this inserted immediately
         after your function definition.
         
         	def testScope(self, lineNum):
                '''
                Describe your method and what it does here ( if multiple 
                lines make sure they are aligned to this margin)
                
                :param  lineNum: param description
                :type lineNum: enter type
                
                :returns: Describe the return value
                :rtype: What is the return type
                '''
                
       * Again just fill in your descriptions.
         
#### Using the Pydev Templates generate Sphinx Documentation Templates

Using templates is a little simpler.  With templates you enter the template 
text and then hit <tt>CTRL+Space</tt> and the code associated with that template
is run, inserting the template in the place of the template keyword.

  * __Documenting a Class__
    * Go to position in the text editor where you want to insert the sphinx 
      documentation template and type: <tt>docclass</tt> and
      then <tt>CTRL+Space</tt>.  You should then get something similar to the 
      following multiline comment inserted into your code:

	         class Commenter:
	            '''
	            Describe your class here and more specifically
	            why you bothered to create it and how it makes
	            The world a better place!
	            
	            :ivar currentLine: Describe the variable here!
	            :ivar document: Describe the variable here!
	            :ivar editor: Describe the variable here!
	            :ivar offset: Describe the variable here!
	            :ivar selection: Describe the variable here!
	            '''
      
  
  
  * __Documenting a Method__
    * Go to position in the text editor where you want to insert the sphinx 
      documentation template and type: <tt>docmethod</tt> or <tt>docfunction</tt> and
      then <tt>CTRL+Space</tt>.  You should then get something similar to the 
      following multiline comment inserted into your code:
      
             def testScope(self, lineNum):
                '''
                Describe your method and what it does here ( if multiple 
                lines make sure they are aligned to this margin)
                
                :param  lineNum: param description
                :type lineNum: enter type
                
                :returns: Describe the return value
                :rtype: What is the return type
                '''
                
### Generate Sphinx HTML Documentation
You have a module or a package that works, and has been documented using sphinx 
restructured text.  You now want to generate some HTML documentation from the 
comments in the code, that look something like say... [this] (https://docs.python.org/2/library/os.path.html)

Before you do anything take a scan of the sphinx project to learn about its capabilities.
http://sphinx-doc.org/

It took me some time to figure out from the sphinx docs how to create a python api doc.  So 
I've tried to document the process on here:
https://sites.google.com/site/bcgeopython/examples/code-documentation/standards-documentation/using-sphinx


### Known Issues

* Does not pick up scope properly when a class gets defined inside of another class and 
  the outerclass has functions defined after the inner class definition.

##Eclipse / PyDev Templating tools - Development

Developing these templating tools was an involved process that ended up taking 
many days to complete.  This is mostly due to:
- unfamiliarity with the PyDev object model
- unfamiliarity with how to develop jython scripts for pydev
- Took a while to figure out how to clear cached memory used by Eclipse / Pydev without 
  having to restart Eclipse! 
  
This section is mostly oriented to documenting _**MY**_ approach to developing Jython
scripts for pydev / Eclipse.

### Dealing with Java.
#### Check version
By default the environment that I work in came with JRE 1.6.  Latest versions of eclipse
require at least java 1.7.  I grabbed the latest greatest.  Also I did not want to actually 
install it (mess with registry and other windows wierdness).  Just wanted to download it, 
extract the files, and then point eclipse at the files.

#### Install without Installing
- Grabbed the latest version of jdk from [Here] (http://www.oracle.com/technetwork/java/javase/downloads/jdk7-downloads-1880260.html)
- Then used [7-Zip] (http://www.7-zip.org/) to extract the files.  Right click on the downloaded exe 
  file and choose "Extract here".
- Finally there are some files in "Pack" archives that need to get extracted.  Mostly followed instructions 
  included in [this stackoverflow post] (http://stackoverflow.com/questions/930265/installing-java-manually-on-windows)

#### Ammend the Eclipse.ini file.
Whereever eclipse is installed, in the same directory as the eclipse.exe file is a file called
eclipse.ini.  Find that file and edit it so it contains the following lines:

     ... 
    -vm
    C:/Dev/Java/java8/jre/bin/javaw.exe
    -vmargs
    -Xms40m
    -Xmx512m


### Mirror pydev / Eclipse code
Mostly followed the instructions on the pydev web site under the section _Developers_ http://pydev.org/developers.html

### Created a Jython project in PyDev
First make sure you have jython installed.  If not download it and follow these instructions
on [how to set up eclipse with jython] (http://www.jython.org/jythonbook/en/1.0/JythonIDE.html#minimal-configuration).


#### Create a standard jython project
- create the project in pydev / eclipse
- refer to the required java sub projects in the pydev git project you downloaded earlier.

#### Do the scripting with jython set up.
- Follow [these] (http://pydev.org/manual_articles_scripting.html) instructions on setting up scripting pydev with jython.
- Make sure to enable:
  - "Show the output given from the scripting to some console?"
  - "Show errors from scripting in the Error Log?

#### How to clear the cached templates (ctrl 2)
Now you should be ready to start the development on either an "editor add in" or 
a new template variable.  Examples are included with pydev.  See the directory 
_installDir_/plugins/org.python.pydev.jython_versionNumber_/jysrc

Scripts in this dir need to be named appropriately for the pydev scripting system to 
pick them up.

Script Type            | Naming prefix
------------           | ----------------
Python Template Script | pytemplate_*
Python Editor add-in   | pyedit_*

#####Template scripts
These create code that gets bound to a variable.  You can then go into 
Window->Preferences->Pydev->Editor->Templates and create a new variable that gets 
bound to the code that you have created.  So in theory when you are working in a 
pydev editor you can type the word you defined as a template, hit ctrl+Space and 
the code gets run, the return value from your code replaces the template word.

#####Editor Scripts or Editor Add-Ons 
These scripts define new entries in the menu that appears if hit cntrl+2.  The code 
then gets executed when you select the entry that corresponds with your script.

For more information, again see the code in the examples section or the code I have included
in this project.










  
	



  


