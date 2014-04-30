from __future__ import nested_scopes # for Jython 2.1 compatibility
from org.python.pydev.parser.fastparser import FastParser
#from org.python.pydev.core.docutils import PySelection
from org.python.pydev.parser.jython.ast import FunctionDef
from org.python.pydev.parser import PyParser
from org.python.pydev.parser.visitors import NodeUtils
from org.python.pydev.parser.jython.ast import ClassDef
from org.python.pydev.parser.jython.ast import Assign
import org.python.core.PyArray
from org.python.pydev.parser.jython.ast import Attribute
from org.python.pydev.parser.jython.ast import Return


if False:
    from org.python.pydev.editor import PyEdit #@UnresolvedImport
    cmd = 'command string'
    editor = PyEdit
    systemGlobals = {}

assert cmd is not None

#interface: PyEdit object: this is the actual editor that we will act upon
assert editor is not None

print 'cmd: ', cmd
# debug, later on this should switch to onCreateActions (only loads once then gets re-used
if cmd == 'onSetDocument':
    Commenter = systemGlobals.get('Commenter')
#     DEBUGGING! Forcing the reload of this object
#     Commenter = None
    print 'commenter is: ', Commenter
    if Commenter is None:
        class Commenter:
            
            def __init__(self, editor):
                self.selection = editor.createPySelection()
                self.editor = editor
                self.document = editor.getDocument()
                self.offset = self.selection.getAbsoluteCursorOffset()
                #print 'offset is: '
                #print 'Creating a COMMENTER object and stashing2...'
                
            def getLineNumber(self):
                self.currentLine = 99999
                print 'offset: ', self.offset
                self.currentLine = self.selection.getLineOfOffset(self.offset)
                print 'line selected is: ', self.currentLine
                return self.currentLine
            
            def docMethod(self):
                
                #print 'doc: ', self.document, self.document.getClass().getName()
                #print 'editor: ', self.editor, self.editor.getClass().getName()
                #line = self.selection.getCursorLine()
                lineStartScopeObj = self.selection.getPreviousLineThatStartsScope()
                # the number of the line that starts the scope.
                print 'start of scope is:', lineStartScopeObj.iLineStartingScope
                parser = FastParser.parseToKnowGloballyAccessiblePath(self.document, lineStartScopeObj.iLineStartingScope)
                for stmt in parser:
                    print 'stmt', stmt
                    if isinstance(stmt, FunctionDef):
                        #print 'begin line?', stmt.beginLine
                        # now get the return values and the args sent to the function
                        grammarVersion = self.editor.getGrammarVersion()
                        parseInfoObj = PyParser.ParserInfo(self.document, grammarVersion)
                        parseOut = PyParser.reparseDocument(parseInfoObj)
                        body = NodeUtils.getBody(parseOut.ast)
                        funcDef = self.searchFuncs(body, stmt.beginLine)
                        argList = self.parseFunc(funcDef)
                        returnState = self.hasReturn(funcDef)
                        #lineOffset = self.document.getLineOffset(stmt.beginLine)
                        #startLine = self.selection.getLine(self.document, stmt.beginLine-1)
                        prevLine = self.selection.getLine(self.document, stmt.beginLine)
                        indentation = self.selection.getIndentationFromLine(prevLine)
                        docString = self.prepOutputMethodString2(indentation, argList, returnState)
                        self.selection.addLine(indentation + docString, stmt.beginLine-1)
                        return docString
                    
            def prepOutputMethodString2(self, indentation, argList, hasReturn=False):                
                '''
                This method will receive a bunch of information about a function, 
                then based on that information it will assemble a python docstring
                that describes the function. 
                
                :param  indentation: a string that only contains spaces. Basically
                                     the number of spaces that the docstring should
                                     be indented by.
                :type indentation: string
                
                :param  argList: a list containing the names of the arguements that are
                                 sent to the script.
                :type argList: python list
                :param  hasReturn: a boolean value indicating wether or not there is a
                                   return value.
                :type hasReturn: boolean
                
                :returns: Returns a docstring template that can be filled in to describe
                          the function
                :rtype: string
                '''
                output = []
                output.append("'''")
                paramlabel = ':param '
                typelabel = ':type '
                paramDefaultDescriptor = 'param description'
                output.append("Describe your method and what it does here ( if multiple ")
                output.append("lines make sure they are aligned to this margin)")
                output.append("")
                for param in argList:
                    #indentation = len(param) + len(paramlabel)
                    if param.lower() != 'self':
                        line = paramlabel + " " + param + ": " + paramDefaultDescriptor
                        output.append(line)
                        typeLine = typelabel + param + ": " + "enter type"
                        output.append(typeLine)
                if hasReturn:
                    output.append("");
                    output.append(":returns: Describe the return value" )
                    output.append(":rtype: What is the return type")
                output.append("'''")
                print 'output is', output
                for i in range(0, len(output)):
                    if i:
                        if i == len(output) - 1:
                            output[i] = str(indentation) + str(output[i])
                        else:
                            output[i] = str(indentation) + str(output[i]) + '\n'
                    else:
                        output[i] = str(output[i]) + '\n'
                
                return ''.join(output)
                        
            def hasReturn(self, node, retVal=None):
                '''
                receives a SimpleNode object, or a subclass of that 
                Type of object.  Rips through all the elements contained
                in that object and returns a boolean value indicating 
                whether it found a Return AST object or not. 
            
                
                :param  node: An input simple node object or subclass 
                              of simplenode
                :type node: org.python.pydev.parser.jython.SimpleNode
                :param  retVal: param description
                :type retVal: enter type
                
                :returns: a boolean value indicating whether a Return ast
                          node was found or not.
                :rtype: boolean
                '''
                retVal = False
                
                #print 'node:', node
                if isinstance(node, Return ):
                    #print 'found a return statement: ', node
                    retVal = True
                elif isinstance(node, org.python.core.PyArray):
                    #print 'its an array, converting to a list'
                    node = node.tolist()
                    for var in node:
                        retVal = self.hasReturn( var, retVal)
                else:
                    fieldArray = node.getClass().getFields()
                    for cnter in range(0, len(fieldArray)):
                        curProp = str(fieldArray[cnter]).split(' ').pop()
                        curProp = curProp.split('.').pop()
                        if curProp == 'body':
                            newNode = node.body
                            retVal = self.hasReturn( newNode, retVal)
                return retVal
                            
            def parseFunc(self, funcNode):
                '''
                Receives a org.python.pydev.parser.jython.ast.FunctionDef 
                object, which extends org.python.pydev.parser.jython.SimpleNode
                object.  Uses the objects functionality to extract the arguements
                that are sent to the method.
                
                :param  funcNode: a FunctionDef object that contains the function
                                  who's arguements we want to extract.
                :type funcNode: org.python.pydev.parser.jython.ast.FunctionDef
                
                :returns: a python list of the args that are sent to the function
                :rtype: List
                '''
                argNameList = []
                print 'funcNode', funcNode
                argNodeList = funcNode.args.args
                print 'funcNode.args', funcNode.args
                print 'length', argNodeList
                for arg in argNodeList:
                    print 'arg is:', arg.id
                    argNameList.append(str(arg.id))
                return argNameList

            def searchFuncs(self, node, beginLine, retVal=None):
                '''
                iterates through an ast documentation tree looking 
                for a function that starts on the line beginLine.  When
                it finds that function it will return the function node, 
                (type org.python.pydev.parser.jython.ast.FunctionDef)
                
                if it does not find a function that starts on the line
                number supplied as an argument it will pull out the sub
                node elements of the received element and resends each of
                the sub-nodes to itself until it finds the function.
                
                :param  node: a  SimpleNode object
                :type node: org.python.pydev.parser.jython.ast.SimpleNode
                
                :param  beginLine: the line that the function we are looking
                                   for starts on.
                :type beginLine: integer
                
                :param  retVal: returns a simplenode object containing the 
                                function.
                :type retVal: enter type
                
                :returns: Describe the return value
                :rtype: org.python.pydev.parser.jython.ast.FunctionDef
                '''
                #print 'node:', node
                if isinstance(node, FunctionDef ):
                    #print '*************************************'
                    #print 'found a func: ', node
                    #print node.beginLine
                    #print beginLine
                    if node.beginLine == beginLine:
                        #print 'returning the function note'
                        return node
                elif isinstance(node, org.python.core.PyArray):
                    #print 'its an array, converting to a list'
                    node = node.tolist()
                    for var in node:
                        retVal = self.searchFuncs(var, beginLine, retVal)
                else:
                    #print 'not a function NODE:'
                    #print node
                    fieldArray = node.getClass().getFields()
                    #className = node.getClass().getName()
                    #print 'className', className
                    for cnter in range(0, len(fieldArray)):
                        curProp = str(fieldArray[cnter]).split(' ').pop()
                        curProp = curProp.split('.').pop()
                        #print 'curProp:', curProp
                        if curProp == 'body':
                            newNode = node.body
            #                print 'calling myself'
            #                exec('newNode = node.' + curProp)
                            #print 'newNode', newNode
                            retVal = self.searchFuncs(newNode, beginLine, retVal)
                return retVal                            
                            
            def getUncommentLine(self, lineNum):
                '''
                keeps moving up the document until it finds a line
                that is not a comment, and is also not a blank line.
                '''
                lineContents = self.selection.getLine(lineNum)
                lineContents = lineContents.strip()
                if lineContents == "" or lineContents == None:
                    lineNum = lineNum - 1
                    lineNum = self.getUncommentLine(lineNum)
                elif lineContents[0] == '#':
                    lineNum = lineNum - 1
                    lineNum = self.getUncommentLine(lineNum)
                return lineNum
            
            def testScope(self, lineNum):
                
                '''
                Determines if the line that the cursor is currently on is
                inside the scope of a class.  Does it using the following steps:
                
                a) gets the line for where the cursor is. 
                
                b) gets the line number where the scope that the cursor is in
                   starts
                
                c) iterates through classdefs and funcdefs from the top of the
                   script to the bottom.
                   
                d) when the iteration's line is greater than the start scope line, 
                   the script checks the indentation to see if it could be part 
                   of any previously defined classes.
                
                Does not work in some situations.  For example, when there is a
                class defined inside of a class, if the inner class is followed
                by function definition for the outer class, it will not
                recognise that function as belonging to a class.
                
                If the method finds that the current line falls under a class 
                then it will return the line where that class is defined.  If not
                it will return a False.
                
                '''
                classDefPointer = None
                # this value is returned.  It indicates whether the 
                # line that the cursor was on when this method
                # was initiated is in a class scope.
                isInClassScope = False 
                lineStartScopeObj = self.selection.getPreviousLineThatStartsScope(lineNum)
                if  lineStartScopeObj:
                    print 'lineStartScopeObj',lineStartScopeObj
                    print 'startScope', lineStartScopeObj.iLineStartingScope + 1
                    scopeStartLine = lineStartScopeObj.iLineStartingScope + 1
                    print 'scopeStartLine', scopeStartLine
                    scopeStartLineContents = self.selection.getLine(self.document, lineStartScopeObj.iLineStartingScope)
                    scopeStartLineIndentation = self.selection.getIndentationFromLine(scopeStartLineContents)
                    # trying to determine if this line that starts the current scope for the 
                    # statement the cursor was on, is enclosed in a class scope
                    
                    #stmtTypes = FastParser.parseClassesAndFunctions(self.document, 1, True, False)
                    stmtTypes = FastParser.parseCython(self.document)
                    classLineList = []
                    
                    # as we read the 
                    stmtDict = []
                    for stmt in stmtTypes:
                        print 'stmt', stmt.beginLine, stmt.getClass().getName()
                        # has the current start scope line been passed.
                        if scopeStartLine <= stmt.beginLine:
                            if classDefPointer:
                                if classDefPointer['indentation'].count(' ') < scopeStartLineIndentation.count(' '):
                                    # assume the line is part of a this class
                                    isInClassScope = True
                                    break
                            if isinstance(stmt, ClassDef) and scopeStartLine == stmt.beginLine:
                                isInClassScope = True
                                classDefPointer = {}
                                classDefPointer['startLine'] = scopeStartLine
                                break
                        if isinstance(stmt, ClassDef):
                            classLineList.append(stmt.beginLine)
                            classDefLine = self.selection.getLine(self.document, stmt.beginLine - 1)
                            print 'ClassDefLine:', classDefLine
                            print 'ClassDefLineNumber:', stmt.beginLine
                            indentation = self.selection.getIndentationFromLine(classDefLine)
                            classLineList.append( {'startLine':stmt.beginLine, 
                                                   'indentation':indentation,
                                                   'line': classDefLine} )
                            classDefPointer = classLineList[len(classLineList) - 1]
                        else:
                            lineContents = self.selection.getLine(self.document, stmt.beginLine - 1)
                            indentation = self.selection.getIndentationFromLine(lineContents)
                            if classDefPointer:
                                if indentation.count(" ") > classDefPointer['indentation'].count(' '):
                                    stmtDict.append({'classPnter': classDefPointer, 
                                                     'indent': indentation, 
                                                     'beginLine':  stmt.beginLine})
                                else:
                                    stmtDict.append({'classPnter': None, 
                                                     'indent': indentation, 
                                                     'beginLine':  stmt.beginLine})
                            
                    print 'scopeStartLine', scopeStartLine
                if isInClassScope:
                    isInClassScope = classDefPointer['startLine']
                return isInClassScope
            
            def docClass(self):
                print 'doc Class'
                lineNum = self.selection.getCursorLine()
                
                isInClass = self.testScope(lineNum)
                print 'isInClass', isInClass
                if isInClass:
                    lineNum = self.getUncommentLine(lineNum)
                    # need to put a check in here to determine if the scope 
                    # of the current cursor position is ultimately contained
                    # by a class.  Should work up looking for a classDef.
                    # This has not been implemented as running out of time, but
                    # its something that should get added.
    
                    lineStartScopeObj = self.selection.getPreviousLineThatStartsScope()
                    print 'lineNum', lineNum
                    lineStartScopeNumber = lineStartScopeObj.iLineStartingScope
                    lineStartScopeObj = self.selection.getPreviousLineThatStartsScope( lineNum)
                    print 'line start scope: ', lineStartScopeObj.getClass().getName()
                    print 'start of scope line is: ', lineStartScopeNumber
                    parser = FastParser.parseToKnowGloballyAccessiblePath( self.document,
                                                                           lineNum )
                    classLineNum = None
                    print 'parser', parser
                    if parser:
                        for stmt in parser:
                            print 'stmt:', stmt.beginLine
                            if isinstance(stmt, ClassDef):
                                # TODO: Need to find out what the indentation is for the class and 
                                # put it into the variable indentation
                                #endLineOfScope = None
                                LineScopeObj = self.selection.getLineThatStartsScope(True, self.selection.INDENT_TOKENS, stmt.beginLine, 9999)
                                #print 'LineScopeObj number', LineScopeObj.iLineStartingScope
                                #if LineScopeObj:
                                    #endLineOfScope = LineScopeObj.iLineStartingScope
                                    # now know the start and end of the class scope, next step is to try 
                                    # to extract the class variables.
                                #    pass
                                #else:
                                #    pass
                                    # Looks like if the class that is being described is the last one in the document
                                    # then the  LineScopeObj object will always be null here.  Assume this means
                                    # that is I get a null LineStartingScope object here I can assume the scope goes
                                    # to the end of the doc.
                                    #print 'from where we are now to the end of doc is the scope'
                                    #classArgs = getClassArgs(selection, stmt.beginLine)
                                #print 'stmt.beginLine', stmt.beginLine
                                classVars = self.getClassArgs(stmt.beginLine)
                                classLineNum = stmt.beginLine
                                #print 'classVars are:', classVars
                                
                                # Finnally format the class vars into a docstring
                    print 'classLineNum:', classLineNum
                    classDefLine = self.selection.getLine(self.document, classLineNum)
                    indentation = self.selection.getIndentationFromLine(classDefLine)
    
                    # format the docstring
                    docString = self.getClassDocString(classVars, indentation)
                    
                    # insert the line just below the classdef that the cursor line
                    # falls under.
                    self.selection.addLine(indentation + docString, isInClass - 1)
                
            def getClassDocString(self, inputList, indentation='    '):
                '''
                Recieves a list of strings that contains the names of all the 
                class variables for this class.  This function will take those 
                parameters and generate a restructured text docstring template.
                
                :param  inputList: a list of class variables that will be included
                                   in the output docstring templates
                :type inputList: python list
                :param  indentation: a string describing the indentation that the docstring 
                                     should use.
                :type indentation: string
                
                :returns: a docstring template
                :rtype: string
                '''
                docStringList = []
                docStringList.append("'''")
                docStringList.append("Describe your class here and more specifically")
                docStringList.append("why you bothered to create it and how it makes")
                docStringList.append("The world a better place!")
                docStringList.append("")
                if inputList:
                    for classVar in inputList:
                        line = ':ivar ' + classVar + ': Describe the variable here!'
                        docStringList.append(line)
                docStringList.append("'''")
                for cnt in range(1, len(docStringList)):
                    docStringList[cnt] = indentation + docStringList[cnt]
                return '\n'.join(docStringList)
            
            def recursiveASTSearch(self, astElement, searchElement, beginLine):
                #print 'submitted element: ', astElement.getClass().getName()
                retVal = None
                if isinstance(astElement, searchElement):
                    #print 'found a classdef'
                    if astElement.beginLine == beginLine:
                        retVal = astElement
                        
                if hasattr(astElement, 'body') and retVal == None:
                    for stmt in astElement.body:
                        retVal = self.recursiveASTSearch(stmt, searchElement, beginLine)
                        if retVal:
                            break
                return retVal
            
            def getClassArgs(self, beginLine):
                '''
                This method receives a selection object and the start and end 
                lines of a class definition.  It will then scan through the code
                looking for class variables.  It stuffs the class variables 
                into a list and returns them.
            
                    
                :param  selObj: The selection object, used to access the document
                :type selObj: org.python.pydev.core.docutils.PySelection
                :param  beginLine: an integer indicating the first line of the class
                :type beginLine: integer
                :param  endLine: (Optional) If null then assumes that this is the last 
                                  class in the module and therefor all subsequent lines
                                  are from the class.
                :type endLine: integer
                
                :return: a list containing the names of all the class variables
                :rtype: list
                '''
                grammarVersion = self.editor.getGrammarVersion()
                parseInfoObj = PyParser.ParserInfo(self.document, grammarVersion)
                nodes = PyParser.reparseDocument(parseInfoObj)
                #body = NodeUtils.getBody(nodes.ast)
                classVarList = []
                
                classNode = self.recursiveASTSearch(nodes.ast, ClassDef, beginLine)
                #print 'classNode is: ', classNode.getClass().getName()
                if classNode:
                    for j in classNode.body:
                        if isinstance(j, Assign ):
                            #print 'Class Name: ', j.targets[0].id
                            classVarList.append(str(j.targets[0].id))
                        if isinstance(j, FunctionDef):
                            #print 'func full', j.name.id, j.getClass().getName()
                            for inFunc in j.body:
                                classVarList = self.searchAssignments(classVarList, inFunc)
                                #print 'classVarList', classVarList
                import sets
                # remove duplicates from the list
                classVarList = list(sets.Set(classVarList))
                classVarList.sort()
                print 'classVarList:', classVarList
                return classVarList
            
            def parseAssignment(self, node):
                ''' 
                Receives one of these types of variable assignments:
                
                Assign[targets=[Name[id=otherline, ctx=Store, reserved=false]], value=Num[n=1, type=Int, num=1] 
                
                Assign[targets=[Attribute[value=Name[id=self, ctx=Load, reserved=false], attr=NameTok[id=var, ctx=Attrib], ctx=Store]], value=Str[s=test, type=SingleSingle, unicode=false, raw=false, binary=false]]]
                
                determines if the assignment is to a class variable, if it is 
                then it adds it returns the name of the class variable that is being 
                assigned, otherwise will return null.
                '''                
                retVal = None
                for i in node.targets:
                    # is the target attribute an Attribute type or is it a Name
                    if isinstance(i, Attribute):
                        if i.value.id == 'self':
                            retVal =  i.attr.id
                return retVal
            
            def searchAssignments(self, classVarList, node):
                '''
                recieves a SimpleNode object, it parses it looking for an 
                Assign type with a target type of Attribute.  Any other 
                nodes get passed back to this method, as it recurses through
                every element that is part of the class looking for class 
                or instance variables.
                
                :param  classVarList: a list of class vars that have already
                                      been extracted for this class.  Additional
                                      class vars get appended to this list
                :type classVarList: python list
                :param  node: a simplenode object that is part of the class that
                              is being parsed.
                :type node: org.python.pydev.parser.jython.SimpleNode
                
                :returns: a list of the class variables that are used by the class
                :rtype: python list
                '''
                if isinstance(node, Assign):
                    classVar = self.parseAssignment(node)
                    if classVar:
                        classVarList.append(classVar)
                elif isinstance(node, org.python.core.PyArray):
                    node = node.tolist()
                    for var in node:
                        classVarList = self.searchAssignments(classVarList, var)
                else:
                    fieldArray = node.getClass().getFields()
                    className = node.getClass().getName()
                    for cnter in range(0, len(fieldArray)):
                        curProperty = str(fieldArray[cnter]).split(' ').pop()
                        curProperty = curProperty.split('.').pop()
                        if curProperty == 'body':
                            newNode = node.body
                            classVarList = self.searchAssignments(classVarList, newNode)
                return classVarList      
                        
        systemGlobals['Commenter'] = Commenter
    
    DoSphinxMethodComments = systemGlobals.get('DoSphinxMethodComments')
    # DEBUGGING! Forcing the reload of this object
#     DoSphinxMethodComments = None
    if DoSphinxMethodComments is None:
        Action = editor.getActionClass() #from org.eclipse.jface.action import Action #@UnresolvedImport
        from java.lang import Runnable #@UnresolvedImport
        
        class DoSphinxMethodComments(Action):
            
            def __init__(self, editor):
                self.editor = editor
                
            def displayStatusMessage(self):
                self.editor.setMessage(False, "Canna do it laddy")
            
            class RunInUi(Runnable):
                '''Helper class that implements a Runnable (just so that we                 can pass it to the Java side). It simply calls some callable.
                '''
        
                def __init__(self, c):
                    print 'run 1'
                    self.callable = c
                def run(self):
                    print 'run 2'
                    self.callable()

            def run(self):
                editor = self.editor
                c = Commenter(editor)
                c.docMethod()
            
        systemGlobals['DoSphinxMethodComments'] = DoSphinxMethodComments
        
    DoSphinxClassComments = systemGlobals.get('DoSphinxClassComments')
    # DEBUGGING! Forcing the reload of this object
#     DoSphinxClassComments = None
    if DoSphinxClassComments is None:
        Action = editor.getActionClass() #from org.eclipse.jface.action import Action #@UnresolvedImport
        from java.lang import Runnable #@UnresolvedImport
        
        class DoSphinxClassComments(Action):
            
            def __init__(self, editor):
                self.editor = editor
                
            def displayStatusMessage(self):
                self.editor.setMessage(False, "Canna do it laddy")
                
            class RunInUi(Runnable):
                '''Helper class that implements a Runnable (just so that we
                                 can pass it to the Java side). It simply calls some callable.
                '''
                def __init__(self, c):
                    print 'run 1'
                    self.callable = c
                    
                def run(self):
                    print 'run 2'
                    self.callable()

            def run(self):
                editor = self.editor
                c = Commenter(editor)
                c.docClass()
            
        systemGlobals['DoSphinxClassComments'] = DoSphinxClassComments
        
    # Change these constants if the default does not suit your needs
    ACTIVATION_STRING_METHODS = 'SPHINX Method Documentation'
    description_methods = 'Inserts a SPHINX method documentation template'
    
    ACTIVATION_STRING_CLASSES = 'SPHINX Class Documentation'
    description_classes = 'Inserts a SPHINX class documentation template'
    
    WAIT_FOR_ENTER = False

    # Register the extension as an ActionListener.
    editor.addOfflineActionListener(ACTIVATION_STRING_METHODS, DoSphinxMethodComments(editor), \
                                    description_methods, \
                                    WAIT_FOR_ENTER)
    
    editor.addOfflineActionListener(ACTIVATION_STRING_CLASSES, DoSphinxClassComments(editor), \
                                    description_methods, \
                                    WAIT_FOR_ENTER)
