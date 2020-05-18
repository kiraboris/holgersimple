# python 3
#

import copy

class State(object):
    """Structure of a quantum state"""
    
    def __init__(self):
            object.__init__(self)
         
            # energy
            self.E       = None       
            self.E_err   = None
            self.g       = None
            
            # additional .egy file information
            self.str_H_iblk  = None
            self.str_H_indx  = None
            self.str_pmix    = None
            
            # quantum numbers
            self._quanta   = frozenset()
            self.int_fmt   = None
    
    def copy(self):
        return copy.deepcopy(self)
    
    def qid(self):
        """docstring"""
        
        return (self._quanta)
    
    
    def has_quanta(self, quanta_subset):
        """Checks if state has these quanta as a subset"""
        
        return all(x in self.q.items()
                   for x in quanta_subset.items())
                   
    def _get_q(self): 
        return dict(self._quanta)
        
    def _set_q(self,dict_x): 
        self._quanta = frozenset(dict_x.items())
        
    q = property(_get_q, _set_q) 
        
        

class Line(object):
    """A spectroscopic line entry object"""
    
    def __init__(self):
    
        # states
        self.state_upper        = State()
        self.state_lower        = State()
                               
        # Frequency of the line (usually in MHz)
        self.freq            = None
        self.freq_err        = None

        # base10 log of the integrated intensity at 300 K (in nm2MHz)
        self.log_I           = None  
        self.int_deg_freedom = None
        
        # additional information
        self.int_cat_tag     = None
        self.str_lin_text    = None
        
        # pressure broadening, alpha: dv=p*alpha*(T/296)^delta
        self.flt_pressure_alpha = None    
        self.flt_pressure_delta = None  
        
        # calculated values
        self.Einstein_A = None
    
    def copy(self):
        return copy.deepcopy(self)
    
    def qid(self):
        """docstring"""
        
        return ((self.state_upper._quanta, self.state_lower._quanta))

    
    # references to upper state g and lower state E and quanta
    def _get_E(self): 
        return self.state_lower.E
        
    def _set_E(self,x): 
        self.state_lower.E = x
        
    def _get_g(self): 
        return self.state_upper.g
        
    def _set_g(self,x):
        self.state_upper.g = x  
        
    def _get_qu(self): 
        return self.state_upper.q
        
    def _set_qu(self,x): 
        self.state_upper.q = x
        
    def _get_ql(self): 
        return self.state_lower.q
        
    def _set_ql(self,x): 
        self.state_lower.q = x
        
    def _get_fmt(self): 
        return self.state_upper.int_fmt
        
    def _set_fmt(self,x): 
        self.state_upper.int_fmt = x
        self.state_lower.int_fmt = x
    
    E = property(_get_E, _set_E)
    g = property(_get_g, _set_g)  
    q_upper = property(_get_qu, _set_qu)
    q_lower = property(_get_ql, _set_ql)
    int_fmt = property(_get_fmt, _set_fmt)


def qid(q1, q2=None):
    """stand-alone function to create haschable quantum IDs
       used for dictionary lookup. q1, q2 are DICTS like also in other methods
    """
    
    if q2 is None:
        return frozenset(q1.items())
    else:
        return (frozenset(q1.items()), frozenset(q2.items()))


class RotorParameter(object):
    
    def __init__(self, code, value=1.0, error=float('inf')):
        self.code = code
        self.value = value
        self.error = error
        self.flag_fit = False


class BasicRotor:
    
    def Q(self, T):
        return 30000
        
                
class AsymRotor(BasicRotor):
    
    def __init__(self):
        self.params = {}
    
    
    def Q(self, T): 
        if all([x in self.params for x in ['A', 'B', 'C']]):
            Qrot = ((5.3311 * 10**(6)) * (float(T)**(1.5)) * 
                    (float(self.params['A']) *
                     float(self.params['B']) *
                     float(self.params['C']))**(-0.5))
        else:
            Qrot = BasicRotor.Q(self, T)
            
        return Qrot
    
    
    

