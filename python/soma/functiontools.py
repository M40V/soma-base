# -*- coding: iso-8859-1 -*-

#  This software and supporting documentation were developed by
#  NeuroSpin and IFR 49
#
# This software is governed by the CeCILL license version 2 under 
# French law and abiding by the rules of distribution of free software.
# You can  use, modify and/or redistribute the software under the 
# terms of the CeCILL license version 2 as circulated by CEA, CNRS
# and INRIA at the following URL "http://www.cecill.info". 
# 
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability. 
# 
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or 
# data to be ensured and,  more generally, to use and operate it in the 
# same conditions as regards security. 
# 
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license version 2 and that you accept its terms.

'''
Utility classes and functions for Python callable.

@author: Yann Cointepas
@organization: U{NeuroSpin<http://www.neurospin.org>} and U{IFR 49<http://www.ifr49.org>}
@license: U{CeCILL version 2<http://www.cecill.info/licences/Licence_CeCILL_V2-en.html>}
'''
__docformat__ = "epytext en"

import inspect


#-------------------------------------------------------------------------------
from soma.translation import translate as _


#-------------------------------------------------------------------------------
try:
  from functools import partial
except ImportError:
  class partial( object ):
    '''
    Python 2.5 introduced a very useful function: C{functools.partial},
    this is an implementation that is compatible with Python 2.3 (if
    functools.partial exists, it is used directly).
    
    functools.partial allow to create a new function from an existing
    function by setting values to some arguments. The new function
    will be callable with less parameters. See Python 2.5 documentation
    for more information.
    
    Example::
      from soma.functiontools import partial
      
      def f( a, b, c ):
        return ( a, b, c )
      
      g = partial( f, 'a', c='c' )
      g( 'b' ) # calls f( 'a', 'b', c='c' )
    '''
    def __init__( self, function, *args, **kwargs ):
      self.func = function
      self.args = args
      self.keywords = kwargs
    
    
    def __call__( self, *args, **kwargs ):
      merged_kwargs = self.keywords.copy()
      merged_kwargs.update( kwargs )
      return self.func( *(self.args + args), **merged_kwargs )


#-------------------------------------------------------------------------------
def getArgumentsSpecification( callable ):
  '''
  This is an extension of Python module C{inspect.getargspec} that accepts 
  classes and return only information about the parameters that can be used in 
  a call to C{callable} (I{e.g.} the first C{self} parameter of bound methods is
  ignored). If C{callable} has not an appropriate type, a C{TypeError}
  exception is raised.
  
  @type  callable: function, method, class or instance
  @param callable: callable to inspect
  @rtype: tuple of four elements
  @return: As C{inspect.getargspec}, returns 
  C{(args, varargs, varkw, defaults)} where C{args} is a list of the argument
  names (it may contain nested lists). C{varargs} and C{varkw} are the names of
  the C{*} and C{**} arguments or C{None}.C{defaults} is an n-tuple of the
  default values of the last I{n} arguments.
  '''
  if inspect.isfunction( callable ):
    return inspect.getargspec( callable )
  elif inspect.ismethod( callable ):
    args, varargs, varkw, defaults = inspect.getargspec( callable )
    args = args[ 1: ] # ignore the first "self" parameter
    return args, varargs, varkw, defaults
  elif inspect.isclass( callable ):
    try:
      init = callable.__init__
    except AttributeError:
      return [], None, None, None
    return getArgumentsSpecification( init )
  else:
    try:
      call = callable.__call__
    except AttributeError:
      raise TypeError( _( '%s is not callable' ) % \
                          repr( callable ) )
    return inspect.getargspec( call )

#-------------------------------------------------------------------------------
def getCallableString( callable ):
  '''
  Returns a translated human readable string representing a callable.
  
  @type  callable: function, method, class or instance
  @param callable: callable to inspect
  @rtype: string
  @return: type and name of the callable
  '''
  if inspect.isfunction( callable ):
    name = _( 'function %s' ) % ( callable.__name__, )
  elif inspect.ismethod( callable ):
    name = _( 'method %s' ) % ( callable.im_class.__name__ + '.' + \
                                callable.__name__, )
  elif inspect.isclass( callable ):
    name = _( 'class %s' ) % ( callable.__name__, )
  else:
    name = str( callable )
  return name

#-------------------------------------------------------------------------------
def hasParameter( callable, parameterName ):
  '''
  Return True if C{callable} can be called with a parameter named
  C{parameterName}. Otherwise, returns C{False}.
  
  @type  callable: function, method, class or instance
  @param callable: callable to inspect
  @type  parameterName: string
  @param parameterName: name of the parameter
  @rtype: bool
  @see: L{getArgumentsSpecification}
  '''
  args, varargs, varkw, defaults = getArgumentsSpecification( callable )
  return varkw is not None or parameterName in args

#-------------------------------------------------------------------------------
def numberOfParameterRange( callable ):
  '''
  Return the minimum and maximum number of parameter that can be used to call a
  function. If the maximum number of argument is not defined, it is set to None.
  
  @type  callable: function, method, class or instance
  @param callable: callable to inspect
  @rtype: tuple of two elements
  @return: (minimum, maximum)
  @see: L{getArgumentsSpecification}
  '''
  args, varargs, varkw, defaults = getArgumentsSpecification( callable )
  if defaults is None or len( defaults ) > len( args ):
    lenDefault = 0
  else:
    lenDefault = len( defaults )
  minimum = len( args ) - lenDefault
  if varargs is None:
    maximum = len( args )
  else:
    maximum = None
  return minimum, maximum


#-------------------------------------------------------------------------------
def checkParameterCount( callable, paramCount ):
  '''
  Check that a callable can be called with C{paramCount} arguments. If not, a
  RuntimeError is raised.
  @type  callable: function, method, class or instance
  @param callable: callable to inspect
  @type  paramCount: integer
  @param paramCount: number of parameters
  @see: L{getArgumentsSpecification}
  '''
  minimum, maximum = numberOfParameterRange( callable )
  if ( maximum is not None and paramCount > maximum ) or \
     paramCount < minimum:
    raise RuntimeError( \
      _( '%(callable)s cannot be called with %(paramCount)d arguments' ) % \
      { 'callable': getCallableString( callable ), 
        'paramCount': paramCount }  )

