import copy
import rivets

def root(trail = rivets.trail):
    ''' Returns `Environment` root.
        
        All relative paths are expanded with root as its base. To be
        useful set this to your applications root directory. (`Rails.root`)
    '''
    return copy.copy(trail.root)

def paths(trail=rivets.trail):
    ''' Returns an `Array` of path `String`s.
        
        These paths will be used for asset logical path lookups.
        
        Note that a copy of the `Array` is returned so mutating will
        have no affect on the environment. See `append_path`,
        `prepend_path`, and `clear_paths`.
    '''
    return copy.copy(trail.paths)

def prepend_path(path,trail=rivets.trail):
    ''' Prepend a `path` to the `paths` list.
        
        Paths at the end of the `Array` have the least priority.
    '''
    trail.prepend_path(path)

def append_path(path,trail=rivets.trail):
    ''' Append a `path` to the `paths` list.

        Paths at the beginning of the `Array` have a higher priority.
    '''
    trail.append_path(path)

def clear_paths(trail=rivets.trail):
    ''' Clear all paths and start fresh.
        
        There is no mechanism for reordering paths, so its best to
        completely wipe the paths list and reappend them in the order
        you want.
    '''
    for path in copy.copy(trail.paths):
        trail.remove_path(path)

def extensions(trail=rivets.trail):
    ''' Returns an `Array` of extensions.
        
        These extensions maybe omitted from logical path searches.
        
            # => [".js", ".css", ".coffee", ".sass", ...]
    '''
    return copy.copy(trail.extensions)