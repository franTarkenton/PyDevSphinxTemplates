'''
Created on 2012-12-14

@author: kjnether
'''

import template_helper

print '*****Invoking the template script! getting here*****'
if False:
    #Variables added externally by the runner of this module.
    import org.python.pydev.editor.templates
    py_context_type = org.python.pydev.editor.templates.PyContextType
    
def parsefuncLine(funcLine):
    '''
    OLD!  This has since been replaced, instead of using this 
    code parser the code now uses the builtin pydev code parser
    to extract args from a function.
    
    Takes a function line definition (ie. a def statement) and
    extracts the args from it and returns them as a python list.
    
    :param  funcLine: a string containing the function definition line
    :type funcLine: string
    
    :returns: a list of the arguements that the def statement recieves
    :rtype: string
    '''
    # get the args out of the funcLine
    import re
    funcLine = funcLine.strip()
    print 'funcLine', funcLine
    startReObj = re.compile("\(")
    endReObj = re.compile("\)\s?:\s?$")
    
    startSrchObj = startReObj.search(funcLine)
    startOfArgs =  startSrchObj.end()
    print startOfArgs
    
    endSrcObj = endReObj.search(funcLine)
    print endSrcObj.lastindex
    endOfArgs =  endSrcObj.start()
    myList = funcLine[startOfArgs:endOfArgs].split(',')
    for i in range(0, len(myList)):
        myList[i] = myList[i].strip()
    return myList
    
def prepOutputMethodString(indentation, funcLine, hasReturn=False):
    '''
    OLD - not used anymore!
    
    recieves a function line, sends it to a simple python parser
    to get the args.  Only keeping here until certain that the new
    method is working correctly
        
    :param  indentation: a string with the whitespace to be used as the
                         docstrings indentation.
    :type indentation: string
    :param  funcLine: the def statement that describes the function
                      who's docstring we are generating.
    :type funcLine: string
    :param  hasReturn: a boolean value that indicates whether the 
                       function returns a value or not.
    :type hasReturn: boolean
    
    :returns: Returns a docstring template that can be filled in to describe
              the function
    :rtype: string
    '''
    argList = parsefuncLine(funcLine)
    return prepOutputMethodString2(indentation, argList, hasReturn)

def prepOutputMethodString2(indentation, argList, hasReturn=False):
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

def GetMethodArg2(idocument):
    '''
    This method will receive a PyDocumentTemplateContext.  From that 
    object it is able to determine the cursor position, from the cursor 
    position it can determine what method / function the cursor position 
    is a part of.  Once it knows the function name it can retrieve the 
    parameters that are being sent to the method as well as determine 
    whether the method has any return types.  Based on that information 
    it will return a docstring template the uses the Sphinx documentation 
    systems tags, in a restructured text format that Sphinx can consume.
    
    This is a revised version of the original method GetMethodArg.  This new 
    version will use the pydev ast document structure.  In other words uses
    the same code that pydev uses to parse the individual elements in the 
    function.  
    
    Versions prior to this version retrieved the functions code, and parsed
    it using my own simple python based function parser.
    
    :param  idocument: The input document context.  From this object you can get an iDocument
                       object, and from there get any parameter you require.
    :type idocument: org.python.pydev.editor.codecompletion.templates.PyDocumentTemplateContext
    
    :returns: a docstring for the method that the cursor was in when this
              method was invoked through the templateing system in pydev.
    :rtype: string
    '''
    from org.python.pydev.parser.fastparser import FastParser
    from org.python.pydev.core.docutils import PySelection
    from org.python.pydev.parser.jython.ast import FunctionDef
    
    docString = None
    print 'using method:GetMethodArg2'
    print 'here'
    # 1 - get the current document
    doc = idocument.getDocument()
    # 2 - create a selection object that gets the line that this method gets called 
    #     from, ie the line the cursor was on when this method is called, or again
    #     the position where the returned docstring will get inserted.
    #selection = PySelection(doc, idocument.getStart())
    selection = idocument.createPySelection()
    lineStart = selection.getPreviousLineThatStartsScope()
    startLineNumber = doc.getLineOfOffset(idocument.getStart())
    print 'startlinenumber', startLineNumber, lineStart.iLineStartingScope
    
    # 3 find out the start line of the function that encloses  
    #   the cursor position from which this function was called
    # the fast parser is a quick way to get the class and function start lines.
    #parser = FastParser.parseToKnowGloballyAccessiblePath(idocument.getDocument(), selection.getStartLineIndex())
    parser = FastParser.parseToKnowGloballyAccessiblePath(doc, startLineNumber)
    print 'got here now! now'
    if parser:
        from java.util import Collections
        Collections.reverse(parser)    
        print 'parser-----'
        print parser
        for stmt in parser:
            print 'stmt', stmt
            # found a function definition, can now retrieve the line
            # number of the function definition
            if isinstance(stmt, FunctionDef):
                # Getting the line number of the func def here.
                #print 'method line', stmt.beginLine
                # Now going to do a full parse of the doc and retrieve 
                # the full function definition info (fast parser just 
                # gets the headlines, this parser will retrieve the 
                # full function def in an AST hierarchy from which 
                # we can extract args and return values.
                functionDefinitionStmt = selection.getLine(stmt.beginLine-1)
                print 'defstatement:', functionDefinitionStmt
                docString = getFuncArgs(idocument, stmt.beginLine)
                # found what we need, no need to continue wiht the rest of the doc
                break
    return docString
                
def getFuncArgs(idocument, beginLine):
    '''
    This method recieves a document object and the start  
    lines of a function definition who's args we want to 
    retrieve. 
    
    It then creates an AST parsed document structure, which 
    gets worked through until a method is found that occurs 
    on the same line as the beginLine that was sent as an 
    arg to this method.
    
    Once this is found it searches for the args in that method 
    and also whether the method has return value.  It then
    sends this information to prepOutputMethodString2 method
    that will convert this into a nicely formatted docstring.
        
    :param  idocument: input context object
    :type idocument: org.python.pydev.editor.codecompletion.templates.PyDocumentTemplateContext
    :param  beginLine: the integer that the function starts on.
    :type beginLine: int
    
    :returns: a sphinx restructured text docstring template for 
              method from which the method was called.
    :rtype: string
    '''
    
    print 'getClassArgs called' 
#    from org.python.pydev.core.docutils import PySelection
    from org.python.pydev.parser import PyParser
    from org.python.pydev.parser.visitors import NodeUtils
    from org.python.pydev.core.docutils import PySelection
    doc = idocument.getDocument()
    
    # creating a parser object.  The 12 is a constant that
    # defines python syntax.  See org.python.pydev.core.IGrammarVersionProvider
    # different numbers are:
    #    2.4    10
    #    2.5    11
    #    2.6    12
    #    2.7    13
    #    etc...
    grammarVersion = idocument.getGrammarVersion()
    print 'grammarVersion:', grammarVersion
    parseInfoObj = PyParser.ParserInfo(doc, grammarVersion)
    # parsign the document into the different node types
    # from the root node you can access all elements of the
    # doc.  (hierarchical parser)
    # nodes is a Tuple object of type:
    #  com.aptana.shared_core.structure.Tuple
    nodes = PyParser.reparseDocument(parseInfoObj)
    print 'node type:', nodes.getClass().getName()
    # nodes.01 contains SimpleNode
    #x = nodes.o1
    #print 'xtype ', x.getClass().getName()
    
    # getting the document body
    body = NodeUtils.getBody(nodes.ast)
    print 'body', body
    # getting the function that starts on the line: begtinLine
    funcDef = searchFuncs(body, beginLine)
    print 'funcDef', funcDef
    argList = parseFunc(funcDef)
    returnState = hasReturn(funcDef)
    #doc = idocument.getDocument()
#    doc = idocument.getDocument()
    # 2 - get a selection object for the current line
    selection = PySelection(idocument.getDocument(), idocument.getStart())
    startLineNumber = doc.getLineOfOffset(idocument.getStart())
    startLineContents = selection.getLine(startLineNumber)
    indentation = selection.getIndentationFromLine(startLineContents)
    
    docString = prepOutputMethodString2(indentation, argList, returnState)
    print 'return: ', returnState
    return docString
    
def hasReturn(node, retVal=None):
    '''
    recieves a SimpleNode object, or a subclass of that 
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
    from org.python.pydev.parser.jython.ast import Return
    import org.python.core.PyArray
    #print 'node:', node
    if isinstance(node, Return ):
        #print 'found a return statement: ', node
        retVal = True
    elif isinstance(node, org.python.core.PyArray):
        #print 'its an array, converting to a list'
        node = node.tolist()
        for var in node:
            retVal = hasReturn(var, retVal)
    else:
        fieldArray = node.getClass().getFields()
        for cnter in range(0, len(fieldArray)):
            curProp = str(fieldArray[cnter]).split(' ').pop()
            curProp = curProp.split('.').pop()
            if curProp == 'body':
                newNode = node.body
                retVal = hasReturn(newNode, retVal)
    return retVal
    
def parseFunc(funcNode):
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
    print 'length', argNodeList
    for arg in argNodeList:
        print 'arg is:', arg.id
        argNameList.append(str(arg.id))
    return argNameList

def GetMethodArg(idocument):
    '''
    This is an older version of the GetMethodArg2 function.  After 
    figuring out how to parse a document using the pydev parsers
    rewrote the method parsing functions.  This will get 
    deleted once I am comfortable that the the GetMethodArg2 is 
    working well.
    
    :param  idocument: an idocument object containing the entire
                       module that was created for this method.
    :type idocument: org.python.pydev.editor.codecompletion.templates.PyDocumentTemplateContext
    
    :returns: a formatted docstring template for the method on which
              this function was called
    :rtype: string
    '''
    # TODO: parse the method looking for the return type
    from org.python.pydev.parser.jython.ast import FunctionDef
    from org.python.pydev.parser.fastparser import FastParser
    from org.python.pydev.core.docutils import PySelection
    
    # 1 - get the current document
    doc = idocument.getDocument()
    # 2 - get a selection object for the current line
    selection = PySelection(idocument.getDocument(), idocument.getStart())
    startLineNumber = doc.getLineOfOffset(idocument.getStart())
    startLineContents = selection.getLine(startLineNumber)
    startIndentation = selection.getIndentationFromLine(startLineContents)
    print 'the line is', startLineNumber
    print 'contents is', startLineContents

    # 3 - create a parser object with the hierarchy of methods, classes etc to which the current line belongs
    parser = FastParser.parseToKnowGloballyAccessiblePath(
        idocument.getDocument(), selection.getStartLineIndex())
    if parser:
        # only continuing if the parser found a method definition. 
        print 'parser', parser
        print 'begin line', parser[0].beginLine
        print 'rettype', type(parser)
        print 'start is', idocument.getStart()
        from java.util import Collections
        Collections.reverse(parser)    
        # 4 - iterate through the parser object
        for stmt in parser:
            print 'stmt', stmt
            print type(stmt)
            # 5 - if the parser contains a method definition
            if isinstance(stmt, FunctionDef):
                # 6 - get the line number for the method definition
                print 'method line', stmt.beginLine
                
                functionDefinitionStmt = selection.getLine(stmt.beginLine-1)
                print 'defstatement:', functionDefinitionStmt
                print 'woke up'
                
                afterLine = stmt.beginLine - 1
#                listOfStringLines = []
                
                string2Add = prepOutputMethodString(startIndentation, functionDefinitionStmt)
    
                #selection.addLine( indentationString + string2Add, stmt.beginLine - 1)
                offset = doc.getLineInformation(afterLine + 1).getOffset();
                print 'offset 1 - ', offset
                if doc.getNumberOfLines() > stmt.beginLine - 1:
                    offset = doc.getLineInformation(afterLine + 1).getOffset();
                    print 'offset 2 - ', offset
                else:
                    offset = doc.getLineInformation(afterLine).getOffset()
                    print 'offset 2 - ', offset
                #doc.replace(offset, 0, string2Add)
                # inserting into the doc immediately after the method is
                # not working, instead will return the doc string
                return string2Add
                #selection.addLine( indentationString + string2Add, stmt.beginLine - 1)
                #offset = doc.getLineInformation(afterLine + 1).getOffset();
                #selection = PySelection(idocument.getDocument(), idocument.getStart())
                #offset = doc.getLineInformation(stmt.beginLine).getOffset()
                #print 'offset is now ',offset
                #print 'on line number', selection.getLineNumber()
                #args = NodeUtils.getNodeArgs(stmt)
                #print 'args are', args
                #print '.getRepresentationString' , NodeUtils.getRepresentationString(stmt)
                #print 'full rep string:', NodeUtils.getFullRepresentationString(stmt)
                #return NodeUtils.getRepresentationString(stmt)
    # if nothing was found then return null.
    return ""

template_helper.AddTemplateVariable(py_context_type, 'current_method_args', 'Current method Args', GetMethodArg2)

def getClassArgs(idocument, selObj, beginLine):
    '''
    This method recieves a selection object and the start and end 
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
    print 'getClassArgs called' 
#    from org.python.pydev.core.docutils import PySelection
    from org.python.pydev.parser import PyParser
    from org.python.pydev.parser.visitors import NodeUtils
    from org.python.pydev.parser.jython.ast import ClassDef
    from org.python.pydev.parser.jython.ast import Assign
    from org.python.pydev.parser.jython.ast import FunctionDef
    
    doc = selObj.getDoc()
    #parseInfoObj = PyParser.ParserInfo(doc, 12)
    print 'here'
    grammarVersion = idocument.getGrammarVersion()
    print 'grammarVersion', grammarVersion
    parseInfoObj = PyParser.ParserInfo(doc, grammarVersion)
    
    nodes = PyParser.reparseDocument(parseInfoObj)
    body = NodeUtils.getBody(nodes.ast)
    
    print 'body', body
    classVarList = []
    for stmt in body:
        if isinstance(stmt, ClassDef):
            print 'class start', stmt.beginLine, beginLine
            print 'classname', stmt.name.id
            # the class we are looking for!
            #if stmt.name.id == 'test':
            if stmt.beginLine == beginLine:
                for j in stmt.body:
                    if isinstance(j, Assign ):
                        print 'Class Name: ', j.targets[0].id
                        classVarList.append(str(j.targets[0].id))
                        print 'j', j 
                    if isinstance(j, FunctionDef):
                        print 'func full', j.name.id
                        for inFunc in j.body:
                            classVarList = searchAssignments(classVarList, inFunc)
                            print 'classVarList', classVarList
    # remove duplicates from the list
    import sets
    classVarList = list(sets.Set(classVarList))
    classVarList.sort()
    return classVarList

def parseAssignment(node):
    ''' 
    Recieves one of these types of variable assignments:
    
    Assign[targets=[Name[id=otherline, ctx=Store, reserved=false]], value=Num[n=1, type=Int, num=1] 
    
    Assign[targets=[Attribute[value=Name[id=self, ctx=Load, reserved=false], attr=NameTok[id=var, ctx=Attrib], ctx=Store]], value=Str[s=test, type=SingleSingle, unicode=false, raw=false, binary=false]]]
    
    determines if the assignment is to a class variable, if it is 
    then it adds it returns the name of the class variable that is being 
    assigned, otherwise will return null.
    '''
    #print '*********************************************'
    from org.python.pydev.parser.jython.ast import Attribute
    retVal = None
    #print 'parseAssignment'
    #print len(node.targets)
    for i in node.targets:
        #print 'node', i
        # is the target attribute an Attribute type or is it a Name
        if isinstance(i, Attribute):
            #print 'guessing this is the id of the attribute'
            #print i.attr.id
            #print i.value.id
            if i.value.id == 'self':
                #print i.Attribute[0]
                retVal =  i.attr.id
        #print '*********************************************'
    return retVal
                                               
def searchFuncs(node, beginLine, retVal=None):
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
    from org.python.pydev.parser.jython.ast import FunctionDef
    import org.python.core.PyArray
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
            retVal = searchFuncs(var, beginLine, retVal)
    else:
        #print 'not a function NODE:'
        #print node
        fieldArray = node.getClass().getFields()
        className = node.getClass().getName()
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
                retVal = searchFuncs(newNode, beginLine, retVal)
    return retVal
    
def searchAssignments(classVarList, node):
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
    #print 'called searchAssignments'
    from org.python.pydev.parser.jython.ast import Assign
    import org.python.core.PyArray
    
    #print 'getting the type', node
        
    #print 'node is', node
    
    #print 'type', node.getClass().getName()   
    #type = node.getClass().getName()
    #print 'here4'
    #print 'type:', type
    
    if isinstance(node, Assign):
        #print 'found assignment: ', node
        #node.getClass.getType()
        classVar = parseAssignment(node)
        #print 'classVar', classVar
        if classVar:
            classVarList.append(classVar)
    elif isinstance(node, org.python.core.PyArray):
        #print 'its an array, converting to a list'
        node = node.tolist()
        for var in node:
            classVarList = searchAssignments(classVarList, var)
        #print 'type is', type(node)
    else:
        #print 'not an assignment'
        #print 'NODE:'
        #print node
        fieldArray = node.getClass().getFields()
        className = node.getClass().getName()
        #print 'className', className
        for cnter in range(0, len(fieldArray)):
            curProperty = str(fieldArray[cnter]).split(' ').pop()
            curProperty = curProperty.split('.').pop()
            #print 'curProperty:', curProperty
            if curProperty == 'body':
                newNode = node.body
#                print 'calling myself'
#                exec('newNode = node.' + curProperty)
                #print 'newNode', newNode
                classVarList = searchAssignments(classVarList, newNode)
#                for stmt in node.body:
#                    searchAssignments(classVarList, stmt)
#                    break
    return classVarList
                    
def getClassDocString(inputList, indentation='    '):
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
    
    #docString = '\n'.join(docStringList)
    #print 'docstring is:\n', docString
    return '\n'.join(docStringList)

def GetClassVars(idocument):
    '''
    Recieves the PyDocumentTemplateContext object that all code completion
    operations recieve. Finds the line from which the method was called, 
    determines what class the line is part of, scans the class for all
    the class or instance variables, and finally returns a docstring 
    template.
    
    :param  idocument: The input pydev object that all code completion
                       templates recieve.
    :type idocument: org.python.pydev.editor.codecompletion.templates.PyDocumentTemplateContext
    
    :returns: a docstring template the describes the class from which 
              this method was called (from a pydev template)
    :rtype: string
    '''
    from org.python.pydev.parser.jython.ast import ClassDef
    from org.python.pydev.parser.fastparser import FastParser
    from org.python.pydev.core.docutils import PySelection
    indentation = '    '
    classVars = None
    # 1 - get the current document
    doc = idocument.getDocument()
    # 2 - create a selection object that gets the line that this method gets calle from.
    #selection = PySelection(doc, idocument.getStart())
    
    selection = idocument.createPySelection()
#     lineStart = selection.getPreviousLineThatStartsScope()
#     startLineNumber = doc.getLineOfOffset(idocument.getStart())
    
    
    print 'selection:', selection
#    startLineNumber = doc.getLineOfOffset(idocument.getStart())
    # 3 - create a parser object with the hierarchy of methods, classes etc to which the current line belongs
    parser = FastParser.parseToKnowGloballyAccessiblePath(
                                        doc, selection.getStartLineIndex() )
    # only continuing if the parser found a class definition. 
    if parser:
        # 4 - iterate through the parser object
        for stmt in parser:
            # 5 - if the parser contains a class definition
            if isinstance(stmt, ClassDef):
                # TODO: Need to find out what the indentation is for the class and 
                # put it into the variable indentation
                endLineOfScope = None
                LineScopeObj = selection.getLineThatStartsScope(True, selection.INDENT_TOKENS, stmt.beginLine, 9999)
                if LineScopeObj:
                    endLineOfScope = LineScopeObj.iLineStartingScope
                    print 'endLineOfScope', endLineOfScope
                    # now know the start and end of the class scope, next step is to try 
                    # to extract the class variables.
                else:
                    # Looks like if the class that is being described is the last one in the document
                    # then the  LineScopeObj object will always be null here.  Assume this means
                    # that is I get a null LineStartingScope object here I can assume the scope goes
                    # to the end of the doc.
                    print 'from where we are now to the end of doc is the scope'
                    #classArgs = getClassArgs(selection, stmt.beginLine)
                classVars = getClassArgs(idocument, selection, stmt.beginLine)
                # Finnally format the class vars into a docstring
    docString = getClassDocString(classVars, indentation)
    print '----------doc string--------------'
    print docString
    # When this is finished will return the docstring for the class.  Not finished yet
    return docString

template_helper.AddTemplateVariable(py_context_type, 'document_class', 'Document Class', GetClassVars)

