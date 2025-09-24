
#@dataclass(frozen=True, order=True, kw_only=True, slots=True) frozen=True makes the attributes themselves read-only, but it does not make mutable objects (like lists, dicts, sets) truly immutable.
#kw_only lets you create instances of objects using keywords only
#slots is a faster way to access object attributes, by using slots you are removing __dict__ so you cant store obj attributes in a  dict,
#avoid it in multiple inheritence (the sublcass cant decide what slots to use), slots do not provide dynamic attribute adding
#class Bozo:
    #id: str = fieled() #attr in __init__
    #text: str = fieled(default="")
    #replies: list[int] = field(default_factory=True, repr=False, compare=False, hash=False) #default_factory avoids sharing mutable attributes among instances, changing an object list will not effect the other objects
    #_post__init(self):
        #creating attribute from the object  __init__ attributes
        #attributes validation
    #attr : type = field(init=False) means the attribute won’t be set through the constructor, you must set or compute it inside __post_init__


    reindex(sorted(df.collumns), axis=1).reset_index(drop=True):
    """sort columns in an alphabet order 
    (can be sorted numerically but that is not the case here) ->
    re-arrange collumns (axis=1 represents collumns) ->
    reset the index to ints (0,1,...) & drop the older index"""