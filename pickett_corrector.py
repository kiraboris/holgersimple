# python 2,3
#

import math
from werkzeug.datastructures import MultiDict

from models import Line, State, qid


def sign(x):
    if x > 0:
        return +1
    elif x < 0:
        return -1
    else:
        return 0

class Corrector:
    """general methods on transitions and states"""
    
    def __init__(self, model):
        self.__model = model
    
    
    def custom_quanta_transform(self, entries, func_transform):
        """docstring"""

        for entry in entries:
            if hasattr(entry, "q"):
                entry.q = func_transform(entry.q)
                
            elif hasattr(entry, "q_upper") and hasattr(entry, "q_lower"):
                entry.q_upper = func_transform(entry.q_upper)
                entry.q_lower = func_transform(entry.q_lower)
    
    
    def correct(self, entries, file_format):
        """docstring"""        
        
        # make O(1) lookup dict 
        dict_entries = self.__build_dict(entries)
        
        # merge blends (assumption: entries partitioned into mergable classes)
        result  = []
        ignore  = set()
        for cur in entries:
            
            if cur.qid() in ignore:
                continue
            
            blends = self.__find_mergable(dict_entries, cur, file_format)
            
            if(len(blends) > 1):
                result.append(self.__merge(blends, file_format))
                ignore.update([x.qid() for x in blends])
            else:
                result.append(cur)
                ignore.add(cur.qid())
                
        # make splits        
        result2  = []
        for cur in result:
            
            splits = self.__split(dict_entries, cur, file_format)
        
            result2.extend(splits)
            
            dict_entries.update(self.__build_dict(splits))
        
        return result2
    
    
    def make_mrg(self, cat_lst, lin_lst, egy_lst = []):
        """look for cat entries in lin and merge the two files into mrg"""
        
        result = []
        
        lin_dict = self.__build_dict(lin_lst)
        
        for entry_cat in cat_lst:
            entry_mrg = entry_cat.copy()
            
            if entry_mrg.qid() in lin_dict:
                entry_lin = lin_dict[entry_mrg.qid()]
                
                entry_mrg.freq = entry_lin.freq
                entry_mrg.freq_err = entry_lin.freq_err
                entry_mrg.int_cat_tag = -abs(entry_mrg.int_cat_tag)
                
            result.append(entry_mrg)
        
        return result
    
    
    def __find_mergable(self, dict_entries, cur, file_format):
        
        if 'cat' in file_format or 'lin' in file_format:
            return self.__model.find_mergable_with_line(dict_entries, cur)
        elif 'egy' in file_format:
            return self.__model.find_mergable_with_state(dict_entries, cur)
        else:
            raise Exception('File format unknown') 
    
    
    def __merge(self, blends, file_format):
        
        if 'cat' in file_format or 'lin' in file_format:
            return self.__model.merge_lines(blends)
        elif 'egy' in file_format:
            return self.__model.merge_states(blends)
        else:
            raise Exception('File format unknown') 
    

    def __split(self, dict_entries, cur, file_format):
        
        if 'cat' in file_format:
            return self.__model.split_line(dict_entries, cur, flag_strict=True)
        elif 'lin' in file_format:
            return self.__model.split_line(dict_entries, cur, flag_strict=False)
        elif 'egy' in file_format:
            return self.__model.split_state(dict_entries, cur)
        else:
            raise Exception('File format unknown') 
        
    
    def __build_dict(self, entries):
        """docstring"""
        
        result = MultiDict()
        for e in entries:
            result.add(e.qid(), e)
            
        return result
    
    def build_dict(self, entries):
        """docstring"""
            
        return self.__build_dict(entries)
    


class SymmRotor:
    """symmetric rotor with N, K and possibly v, l, J, hfs""" 
    
    def merge_lines(self, blends):
        """docstring"""
        
        result = blends[0].copy()
        
        if not result.g is None:
            if not result.log_I is None:
                I_bl = list(map(lambda x: 10 ** x.log_I, blends))
                g_bl = list(map(lambda x: x.g, blends))
                
                result.log_I = math.log10(sum(I_bl))
                
                result.g = 0
                for (I, g) in zip(I_bl, g_bl):
                    if( math.isclose(I, max(I_bl)) ):
                        result.g += g
            else:
                g_bl = map(lambda x: x.g, blends)
                result.g = sum(g_bl)
        
        return result
    
    
    def merge_states(self, blends):
        """docstring"""
        
        result = blends[0].copy()
        
        g_bl = map(lambda x: x.g, blends)
        result.g = sum(g_bl)

        return result    
    
    
    def __split_blended_line(self, entry):
        
        result = []
        
        qu = entry.q_upper 
        ql = entry.q_lower
        Kl = abs(ql['K']) 
        Ku = abs(qu['K'])
        
        ql['K'] = Kl
        qu['K'] = -Ku
        newline = entry.copy()
        newline.q_upper = qu
        newline.q_lower = ql
        #if not newline.g is None:
        #    newline.g = newline.g / 2
        result.append(newline)

        ql['K'] = -Kl
        qu['K'] = Ku
        newline = entry.copy()
        newline.q_upper = qu
        newline.q_lower = ql
        #if not newline.g is None:
        #    newline.g = newline.g / 2
        result.append(newline)
        
        return result
    
    
    def split_line(self, dict_entries, entry, flag_strict):
        """docstring"""
        
        if(self.__spin_symm(entry) == "A"):
            
            result = []
            
            qu = entry.q_upper 
            ql = entry.q_lower
            
            if(ql['K'] == 0 or qu['K'] == 0):
                result.append(entry)
            else:
                if(sign(qu['K']) == -sign(ql['K'])): # Ku == -Kl mod 2, correct
                    if(not flag_strict):
                        result.append(entry)
                    else:
                        # always require l-splitting
                        ql['K'] = -ql['K']
                        qu['K'] = -qu['K']
                        if qid(qu, ql) in dict_entries:
                            # other parity is there
                            result.append(entry)
                        else:
                            # other parity is NOT there: entry is a blended line
                            result.extend(self.__split_blended_line(entry))
                else:
                    # Ku == +Kl mod 2, incorrect
                    Kl = abs(ql['K']) 
                    Ku = abs(qu['K'])
                    
                    qu['K'] = Ku
                    ql['K'] = -Kl
                    qid_plus_to_minus = qid(qu, ql)
                    
                    qu['K'] = -Ku
                    ql['K'] =  Kl
                    qid_minus_to_plus = qid(qu, ql)
                    
                    if( qid_plus_to_minus in dict_entries and 
                        not qid_minus_to_plus in dict_entries):
                        # make "minus_to_plus" from entry
                        qu['K'] = -Ku
                        ql['K'] =  Kl 
                        entry.q_upper = qu
                        entry.q_lower = ql  
                        result.append(entry)
                    elif( qid_minus_to_plus in dict_entries and 
                          not qid_plus_to_minus in dict_entries): 
                        # make "plus_to_minus" from entry
                        qu['K'] = -Ku
                        ql['K'] =  Kl
                        entry.q_upper = qu
                        entry.q_lower = ql  
                        result.append(entry)
                    elif( qid_minus_to_plus in dict_entries and 
                          qid_plus_to_minus in dict_entries): 
                        # entry is redundant
                        pass
                    else:
                        # entry is a blended line, create both splits
                        result.extend(self.__split_blended_line(entry))
                           
        else:
            # E-symmetry line doesn't need splitting
            result = [entry]
            
        return result
    
    
    def split_state(self, dict_entries, entry):
        """docstring"""
        
        # state doesn't need splitting
        result = [entry]        
            
        return result

    
    
    def find_mergable_with_line(self, dict_entries, entry):
        """docstring"""
        
        ids = [entry.qid()]
        
        if(self.__spin_symm(entry.state_lower) == "A"):
            # merge with 'wrong parity' transition
            # that differs only in q_lower
            
            qu = entry.q_upper 
            ql = entry.q_lower
        
            ql['K'] = -(ql['K'])
            
            ids.append(qid(qu, ql))
            
        result = []
        for x in ids:
            result.extend(dict_entries.getlist(x))
        
        #if entry.freq == 10955590.3589:
        #    for line in result:
        #        print(line.freq, line.qid())
        
        return result
        
    
    def find_mergable_with_state(self, dict_entries, entry):
        """docstring"""
        
        # only states with same qid() are mergable
        result = dict_entries.getlist(entry.qid())
        
        return result
    
    
    def __spin_symm_q(self, quanta):
        """get spin-statistical symmetry irr.rep. of state or line"""
        
        if quanta['K'] == 0 and quanta.get('l', 0) % 3 == 0:
            return 'E'        
        elif (abs(quanta['K']) - quanta.get('l', 0)) % 3 == 0:
            return 'A'
        else:
            return 'E'             
    
    
    def __spin_symm(self, entry):
        """get spin-statistical symmetry irr.rep. of state or line"""
        
        if isinstance(entry, Line):             
            upper = self.__spin_symm_q(entry.q_upper)
            lower = self.__spin_symm_q(entry.q_lower)
            if upper == "A" or lower == "A":
                return 'A'
            else:
                return 'E'
        elif isinstance(entry, State):
            return self.__spin_symm_q(entry.q)
        else:
            raise Exception('Neither line nor state')
            
    

