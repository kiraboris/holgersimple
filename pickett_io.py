# python 3
#

import bidict

from models import Line, State


def save_int(str_filename, obj_rotor, 
            J_min=0, J_max=20, inten1=-10.0, max_freq=100.0, temperature=300.0):
    
    input_file = ""
    input_file += "%s \n" % obj_rotor.name
    input_file += ("0  91  %f  %3d  %3d  %f  %f  %f  %f\n" % 
        (obj_rotor.Q(temperature), J_min, J_max, inten, inten,
         max_freq, temperature))
    input_file += " 001  %f \n" % obj_rotor.u_A
    input_file += " 002  %f \n" % obj_rotor.u_B
    input_file += " 003  %f \n" % obj_rotor.u_C

    with open(str_filename, "w") as fh:
        fh.write(input_file)


def save_par_var(str_filename, obj_rotor):
    
    if all([x in self.params for x in ['A', 'B', 'C', '-DJ', '-DJK', '-DK']]):
        _save_parvar_asymm_simple(obj_rotor)
    else:
        raise NotImplementedError
        


def load_var_into_model(str_filename, obj_rotor):
        fh_var = open("default%s.var"%(str(file_num)))
        for line in fh_var:
            if line.split()[0] == "10000":
                temp_A = float(line.split()[1])
                const_list.append("%.3f" %temp_A)
            if line.split()[0] == "20000":
                temp_B = float(line.split()[1])
                const_list.append("%.3f" %temp_B)
            if line.split()[0] == "30000":
                temp_C = float(line.split()[1])
                const_list.append("%.3f" %temp_C)
    

def get_fit_rms(str_filename):
    
    rms_fit = None
    with open(str_filename) as f:
        for line in reversed(f.readlines()):
            line = line.strip()
            if line[11:14] == "RMS":
                rms_fit = float(line[21:32]) 
                
    return rms_fit
    
    

def _save_parvar_asymm_simple(rotor):
    
    def signum(flag):
        if flag:
            return '+'
        else:
            return '-'
    
    input_file = ""
    input_file += "Molecule                                        Thu Jun 03 17:45:45 2010\n"
    input_file += "   6  430   51    0    0.0000E+000    1.0000E+005    1.0000E+000 1.0000000000\n"
    input_file +="s   1  1  0  99  0  1  1  1  1  -1   0\n"
    input_file += "           10000  %.15e 1.0E%s100 \n" \
        %(rotor.params['A'].value, signum(rotor.params['A'].flag_fit)) 
    input_file += "           20000  %.15e 1.0E%s100 \n" \
        %(rotor.params['B'].value, signum(rotor.params['B'].flag_fit))
    input_file += "           30000  %.15e 1.0E%s100 \n" \
        %(rotor.params['C'].value, signum(rotor.params['C'].flag_fit))
    input_file += "             200  %.15e 1.0E%s100 \n" \
        %(-rotor.params['-DJ'].value, signum(rotor.params['-DJ'].flag_fit))
    input_file += "            1100  %.15e 1.0E%s100 \n" \
        %(-rotor.params['-DJK'].value, signum(rotor.params['-DJK'].flag_fit)) 
    input_file += "            2000  %.15e 1.0E%s100 \n" \
        %(-rotor.params['-DK'].value, signum(rotor.params['-DK'].flag_fit))
    
    fh_var = open("output.var",'w')
    fh_var.write(input_file)
    fh_var.close()




def quanta_headers(int_fmt):
    """returns list of quantum number names for a Pickett code"""
    
    int_c = int_fmt  % 10
    int_Q = int_fmt // 100
    
    DICT_MAPPING = {2:  ['N', 'K', 'J', 'F1', 'F2', 'F'],
                    13: ['N', 'K', 'v', 'J', 'F1', 'F']
                   }
                   
    return DICT_MAPPING[int_Q][0:int_c]


class CatConverter:
    """Manages entries of .cat files"""
    
    mapper=bidict.bidict([ ('a', '-1'), ('b', '-2'), ('c', '-3'), ('d', '-4'), 
                ('e', '-5'), ('P', '25'), ('f', '-6'), ('g', '-7'),
                ('h', '-8'), ('i', '-9'), ('j', '-10'), ('k', '-11'),
                ('l', '-12'), ('m', '-13'), ('n', '-14'), ('o', '-15'),
                ('p', '-16'), ('A', '10'), ('B', '11'), ('C', '12'), 
                ('D', '13'), ('E', '14'), ('F', '15'), ('G', '16'), 
                ('H', '17'), ('I', '18'), ('J', '19'), ('K', '20'), 
                ('L', '21'), ('M', '22'), ('N', '23'), ('O', '24') ]) 
    
    @staticmethod
    def __decode_quant(str_q):
        """replace a -> -1, A -> 10, etc."""
        
        str_s = str_q[0:1]
        if str_s in CatConverter.mapper:
            str_q = str_q.replace(str_s, CatConverter.mapper[str_s], 1)
        
        return str_q
    
    
    @staticmethod
    def __encode_quant(str_q, thresh=3):
        """replace -1 -> a, 10 -> A, etc."""
        
        if len(str_q) >= thresh:
            str_s = str_q[0:2]
            if(str_s in CatConverter.mapper.inv):
                str_q = str_q.replace(str_s, CatConverter.mapper.inv[str_s], 1)
        
        return str_q
    
    
    @staticmethod
    def __read_quanta(str_quanta, int_fmt):
        """convert quanta from .cat to dict 
           returns (dict_upper, dict_lower) 
        """
        dict_ql = {}
        dict_qu = {}
        
        INT_C = 6
        for i in range(0, INT_C):
            
            str_qu = str_quanta[i*2 : (i+1)*2]
            str_ql = str_quanta[(i+INT_C)*2: (i+INT_C+1)*2]
            
            if str_qu != "  " and str_ql != "  ":
                str_qu = CatConverter.__decode_quant(str_qu)
                str_ql = CatConverter.__decode_quant(str_ql)
                
                headers = quanta_headers(int_fmt)
                dict_ql[headers[i]] = int(str_ql)
                dict_qu[headers[i]] = int(str_qu)
            else:
                break
        
        return (dict_qu, dict_ql)
    
    @staticmethod
    def __write_quanta(dict_qu, dict_ql, int_fmt):
        """convert quanta from (dict,dict) to .cat str"""

        INT_C = 6
        str_quanta = ""    
        
        headers = quanta_headers(int_fmt)[0:len(dict_qu)]
        for str_q in ["%2d" % dict_qu[x] for x in headers]:
            str_q = CatConverter.__encode_quant(str_q)
            str_quanta += str_q   
        for i in range(len(headers), INT_C):
            str_quanta += "  "
        
        headers = quanta_headers(int_fmt)[0:len(dict_ql)]
        for str_q in ["%2d" % dict_ql[x] for x in headers]:
            str_q = CatConverter.__encode_quant(str_q)
            str_quanta += str_q   
        for i in range(len(headers), INT_C):
            str_quanta += "  "
        
        return str_quanta
    
    @staticmethod
    def str2line(str_line):
        """str to Line object"""
        
        obj_line = Line()
        
        obj_line.freq     = float(str_line[0:13])           
        obj_line.freq_err = float(str_line[13:21])
        
        obj_line.log_I       = float(str_line[21:29]) 
        obj_line.int_deg_freedom = int(str_line[29:31])
        
        obj_line.E = float(str_line[31:41])           
        obj_line.g = int(CatConverter.__decode_quant(str_line[41:44]))
        
        obj_line.int_cat_tag  = int(str_line[44:51])
        
        str_q  = str_line[55:79]
        int_fmt = int(str_line[51:55])
        dict_qu, dict_ql = CatConverter.__read_quanta(str_q, int_fmt)
        
        obj_line.q_upper = dict_qu
        obj_line.q_lower = dict_ql
        obj_line.int_fmt = int_fmt
            
        return obj_line
        
    @staticmethod    
    def line2str(obj_line):
        """Line object to str"""
        
        str_out = ""
        
        str_quanta = CatConverter.__write_quanta(obj_line.q_upper,
                                                  obj_line.q_lower,
                                                  obj_line.int_fmt)
        
        str_out += "%13.4f%8.4f"% (obj_line.freq, obj_line.freq_err)
        str_out += "%8.4f%2d"   % (obj_line.log_I, obj_line.int_deg_freedom)
        str_out += "%10.4f%3s"  % (obj_line.E, CatConverter.__encode_quant(str(obj_line.g), thresh=4))
        str_out += "%7d"        % (obj_line.int_cat_tag)
        str_out += "%4d%s "     % (obj_line.int_fmt, str_quanta)
               
        return str_out



class EgyConverter:
    """Manages entries of .egy files."""
    
    @staticmethod
    def __read_quanta(str_quanta, int_fmt):
        """convert quanta from .egy to dict 
        """
        dict_q = {}
        
        headers = quanta_headers(int_fmt)
        INT_C = min(int_fmt % 10, len(str_quanta) // 3)
        for i in range(0, INT_C):
            str_q = str_quanta[i*3 : (i+1)*3]
            dict_q[headers[i]] = int(str_q)
        
        return dict_q
    
    @staticmethod
    def __write_quanta(dict_q, int_fmt):
        """convert quanta from dict to .egy str"""

        str_quanta = ""    
        
        headers = quanta_headers(int_fmt)[0:len(dict_q)]
        for str_q in ["%3d" % dict_q[x] for x in headers]:
            str_quanta += str_q   
        
        return str_quanta
    
    @staticmethod
    def str2state(str_state, int_fmt):
        """str to State object (needs Pickett quanta format code)"""
        
        obj_state = State()
            
        obj_state.str_H_iblk = (str_state[0:6])
        obj_state.str_H_indx = (str_state[6:11])
        
        obj_state.E      = float(str_state[11:29])       
        obj_state.E_err  = float(str_state[29:47])
        
        obj_state.str_pmix   = (str_state[47:58])
        
        obj_state.int_fmt = int_fmt
        obj_state.q = EgyConverter.__read_quanta(str_state[64:], int_fmt)
        obj_state.g = int(str_state[58:63])
        
        return obj_state
        
    @staticmethod    
    def state2str(obj_state):
        """Line object to str (needs Pickett quanta format code)"""
        
        str_out = ""
        
        str_out += "%s%s"         % (obj_state.str_H_iblk, obj_state.str_H_indx)
        str_out += "%18.6f%18.6f" % (obj_state.E, obj_state.E_err)
        str_out += "%s%5d:"       % (obj_state.str_pmix, obj_state.g)
        str_out += EgyConverter.__write_quanta(obj_state.q, obj_state.int_fmt) 
        
        return str_out



class LinConverter:
    """Manages entries of .lin files"""
    
    @staticmethod
    def __read_quanta(str_quanta, int_fmt):
        """convert quanta from .cat to dict 
           returns (dict_upper, dict_lower) 
        """
        dict_ql = {}
        dict_qu = {}
        
        INT_C = int_fmt % 10
        for i in range(0, INT_C):
            
            str_qu = str_quanta[i*3 : (i+1)*3]
            str_ql = str_quanta[(i+INT_C)*3: (i+INT_C+1)*3]
            
            headers = quanta_headers(int_fmt)
            dict_ql[headers[i]] = int(str_ql)
            dict_qu[headers[i]] = int(str_qu)
        
        return (dict_qu, dict_ql)
    
    @staticmethod
    def __write_quanta(dict_qu, dict_ql, int_fmt):
        """convert quanta from (dict,dict) to .cat str"""
        
        INT_C_MAX  = 6
        INT_C      = int_fmt % 10
        str_quanta = ""   
        
        headers = quanta_headers(int_fmt)[0:len(dict_qu)]
        for str_q in ["%3d" % dict_qu[x] for x in headers]:
            str_quanta += str_q   
        for i in range(len(headers), INT_C):
            str_quanta += "   "
        
        headers = quanta_headers(int_fmt)[0:len(dict_ql)]
        for str_q in ["%3d" % dict_ql[x] for x in headers]:
            str_quanta += str_q   
        for i in range(len(headers), INT_C):
            str_quanta += "   "
        
        for i in range(2*INT_C, 2*INT_C_MAX):
            str_quanta += "   "
        
        return str_quanta
    
    @staticmethod
    def str2line(str_line, int_fmt):
        """str to Line object"""
        
        obj_line = Line()
        obj_line.freq     = float(str_line[36:51])           
        obj_line.freq_err = float(str_line[51:60])
        
        obj_line.str_lin_text = str_line[60:-1]
        
        str_q  = str_line[0:36]
        dict_qu, dict_ql = LinConverter.__read_quanta(str_q, int_fmt)
        
        obj_line.int_fmt = int_fmt
        obj_line.q_upper = dict_qu
        obj_line.q_lower = dict_ql
            
        return obj_line
        
    @staticmethod    
    def line2str(obj_line):
        """Line object to str"""
        
        str_out = ""
        
        str_quanta = LinConverter.__write_quanta(obj_line.q_upper,
                                                 obj_line.q_lower,
                                                 obj_line.int_fmt)

        str_out += "%s"    % (str_quanta)
        str_out += "%15.4f"% (obj_line.freq)
        str_out +=("%10.3f"% (obj_line.freq_err)).replace('0.', '.')
        str_out += "%s"    % (obj_line.str_lin_text)
              
        return str_out



def get_quantum_fmt(str_filename):
    """Get the FMT from .cat file"""
    
    int_quanta_fmt = None
    with open(str_filename, 'r') as f:
        str_line = f.readline()
        obj_line = CatConverter.str2line(str_line)
        int_quanta_fmt = obj_line.int_fmt
    
    return int_quanta_fmt


def load_cat(str_filename):
    """Read from .cat"""
    
    lst_lines  = []
    with open(str_filename, 'r') as f:
        for str_line in f:
            obj = CatConverter.str2line(str_line)
            lst_lines.append(obj)
        
    return lst_lines


def save_cat(str_filename, lst_lines):
    """docstring"""
    
    with open(str_filename, 'w') as f:
        for obj_line in lst_lines:
            textline = CatConverter.line2str(obj_line)
            f.write(textline+"\n")


def load_lin(str_filename, int_quanta_fmt):
    """Read from .cat"""
    
    lst_lines  = []
    with open(str_filename, 'r') as f:
        for i, str_line in enumerate(f):
            try:
                obj = LinConverter.str2line(str_line, int_quanta_fmt)
                lst_lines.append(obj)
            except(ValueError):
                print ('Warning: skipping bad line %i' % (i+1)) 
        
    return lst_lines


def save_lin(str_filename, lst_lines):
    """docstring"""
    
    with open(str_filename, 'w') as f:
        for obj_line in lst_lines:
            textline = LinConverter.line2str(obj_line)
            f.write(textline+"\n")



def load_egy(str_filename, int_quanta_fmt):
    """Read from .egy"""
    
    lst_states  = []
    with open(str_filename, 'r') as f:
        for str_state in f:
            obj = EgyConverter.str2state(str_state, int_quanta_fmt)
            lst_states.append(obj)
    
    return lst_states
    

def save_egy(str_filename, lst_states):
    """docstring"""
    
    with open(str_filename, 'w') as f:
        for obj_state in lst_states:
            textline = EgyConverter.state2str(obj_state)
            f.write(textline+"\n")


def load(str_filename, int_quanta_fmt):
    """docstring"""
    
    extension = str_filename[-3:]
    
    if( extension == "cat" or extension == "mrg" ):
        return load_cat(str_filename)
        
    if( extension == "egy" ):
        return load_egy(str_filename, int_quanta_fmt)
        
    if( extension == "lin" ):
        return load_lin(str_filename, int_quanta_fmt)



def save(str_filename, lst_entries):
    """docstring"""
    
    extension = str_filename[-3:]
    
    if( extension == "cat" or extension == "mrg" ):
        save_cat(str_filename, lst_entries)
        
    if( extension == "egy" ):
        save_egy(str_filename, lst_entries)
        
    if( extension == "lin" ):
        save_lin(str_filename, lst_entries)
        
        
        
        
        
        
        
        
