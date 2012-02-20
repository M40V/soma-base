# -*- coding: utf-8 -*-

'''
Base classes for the management of association between Python objects and factories (i.e. a function that create something for an object) taking into account classes hierachy but without storing anything in the objects classes.
'''

from weakref import WeakKeyDictionary

class MetaFactories( type ):
  '''This is the metaclass of Factories. 
  It intercepts Factories class creation to make sure that they have
  a _global_factories attibute.'''
  
  def __new__( mcs, name, bases, dict ):
    if '_global_factories' not in dict:
      dict[ '_global_factories' ] = {}
    return type.__new__( mcs, name, bases, dict )


class Factories( object ):
  '''
  This is the base class for managing association between any Python object
  and a factory. For instance, WidgetFactories is derived from Factories and
  used to register all factories allowing to create a graphical widget for a
  Python object.
  
  There are two levels of associations between Python objects and factories
  (i.e. two dictionaries). The global factories are associated at the class
  level (for classes derived from Factories) with the register_global_factory
  method. The global factories are shared by all instances. On the other hand,
  if one wants to customize some factories for a specific context, it can
  create one Factories instance per context and use register_factory method
  to create an associtation at the instance level.
  '''
  __metaclass__ = MetaFactories
  

  def __init__( self ):
    super( Factories, self ).__init__()
    self._factories = WeakKeyDictionary()


  @classmethod
  def register_global_factory( factories_class, klass, factory ):
    '''
    Create an association between a class and a global factory.
    '''
    factories_class._global_factories[ klass ] = factory
  
  
  def get_global_factory( self, key ):
    '''
    Retrieve the global factory associated to a class or an instance. Only
    direct association is used. In order to take into account class hierarchy,
    one must use get_factory method.
    '''
    return self._global_factories.get( key )
  
  
  def register_factory( self, class_or_instance, factory ):
    '''
    Create an association between a class (or an instance) and a factory.
    '''
    self._factories[ klass ] = class_or_instance
  
  
  def get_factory( self, object ):
    '''
    Retrieve the factory associated to an object.
    First look into the object instance and then in the object class hierarchy.
    At each step a registered factory in the Factories instance is looked for.
    If there is none, self.get_global_factory is used.
    Returns None if no factory is found.
    '''
    for key in ( object, ) + object.__class__.__mro__:
      factory = self._factories.get( key )
      if factory is not None: break
      factory = self.get_global_factory( key )
      if factory is not None: break
    return factory
