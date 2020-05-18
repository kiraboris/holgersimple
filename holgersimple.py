# python 3

import sys
import shutil
from bidict import bidict

import pickett_io
from pickett_corrector import Corrector, SymmRotor

flag13Cvib = False

if not flag13Cvib:
    transormation = bidict({
        0: ((0, 0, 0),  0, 0, 0),
        2: ((1, 0, 0), -1, 0, 2),
        3: ((1, 0, 0), +1, 0, 3),
        6: ((2, 0, 0),  0, 0, 6),
        7: ((2, 0, 0), +2, 0, 7),
        8: ((2, 0, 0), -2, 0, 8), 
        12:((0, 0, 1),  0, 0, 12),
        14:((0, 1, 0), -1, 0, 14),
        15:((0, 1, 0), +1, 0, 15),
        18:((0, 0, 3), -1, 0, 18),
        19:((0, 0, 3), +1, 0, 19),
        20:((0, 0, 1), -3, 0, 20),
        21:((0, 0, 1), +3, 0, 21),
        1: ((0, 0, 0),  0, 1, 1),
        4: ((1, 0, 0), -1, 1, 4),
        5: ((1, 0, 0), +1, 1, 5),
        9: ((2, 0, 0),  0, 1, 9),
        10:((2, 0, 0), +2, 1, 10),
        11:((2, 0, 0), -2, 1, 11)    
    })
else:
    transormation = bidict({
        5: ((1, 0, 0),  -1, 1, 5),
        6: ((1, 0, 0),  +1, 1, 6),
        0: ((1, 0, 0),  -1, 1, 0),
        1: ((1, 0, 0),  +1, 1, 1),
    })
    
    

def _extract_v(quanta):
    """docstring"""
    
    v = quanta.get('v', 0)
    
    quanta['v'], quanta['l'], quanta['hfs'], quanta['raw_v'] = transormation[v]
    return quanta


def _compress_v(quanta):
    """docstring"""
    
    quanta['v'] = quanta['raw_v']
    del quanta['raw_v']
    del quanta['l']
    del quanta['hfs']
    
    return quanta




def fix_file(in_file, out_file, fmt):
    """docstring"""
    
    print("%s -> %s" % (in_file, out_file))
    entries = pickett_io.load(in_file, fmt)
    old_len = len(entries)

    qm.custom_quanta_transform(entries, _extract_v)
    entries[:] = qm.correct(entries, in_file[-3:])
    qm.custom_quanta_transform(entries, _compress_v)
    
    new_len = len(entries)
    print("  delta %+d entries." % -(old_len - new_len))  
    pickett_io.save(out_file, entries)
    
    return entries
    

def make_mrg(cat_file, lin_file, egy_file, egy_file_new, mrg_file, fmt):
    """docstring"""
    
    print("Create %s" % (mrg_file))
    
    cat_entries = pickett_io.load(cat_file, fmt)
    lin_entries = pickett_io.load(lin_file, fmt)
    
    mrg_entries = qm.make_mrg(cat_entries, lin_entries)
    
    pickett_io.save(mrg_file, mrg_entries)
    


def main():
    for cat_id in looper:
        
        jobs = looper[cat_id]
        
        if "int_fmt_override" in globals():
            int_fmt = int_fmt_override
        elif('icat' in jobs):
            int_fmt = pickett_io.get_quantum_fmt("%si.cat" % cat_id)
        elif('cat' in jobs):
            int_fmt = pickett_io.get_quantum_fmt("%s.cat"  % cat_id)
        else:
            print('Nowhere to get format from..(')
            sys.exit()
            

        if('icat' in jobs): 
            fix_file("%si.cat" % cat_id, "%si_new.cat"  % cat_id, int_fmt)
            icat_fname = "%si_new.cat"

        if('cat' in jobs): 
            fix_file("%s.cat"  % cat_id, "%s_new.cat"  % cat_id, int_fmt)
            icat_fname = "%s_new.cat"

        if('egy' in jobs): 
            fix_file("%s.egy"  % cat_id, "%s_new.egy"  % cat_id, int_fmt)
            
        if('lin' in jobs): 
            fix_file("%s.lin"  % cat_id, "%s_new.lin"  % cat_id, int_fmt)
            lin_fname = "%s_new.lin"
        
        if('mrg.lin' in jobs): 
            fix_file("%s_mrg.lin"  % cat_id, "%s_mrg_new.lin"  % cat_id, int_fmt)
            lin_fname = "%s_mrg_new.lin"
            
        if('mrg' in jobs):
            make_mrg(icat_fname % cat_id, lin_fname % cat_id,
                     "%s.egy"  % cat_id, "%s_new.egy" % cat_id,
                     "%s_new.mrg"  % cat_id, int_fmt)



# *** main part ***
qm = Corrector(SymmRotor())   

#looper = {"042515": ['icat', 'lin', 'mrg', 'egy']}

#looper = {"042508": ['egy'], "042509": ['egy']} 

#looper = {"042513": ['egy'], "042514": ['egy']}

#looper = {"C:\\Users\\Asus\\Downloads\\c041501": ['cat', 'mrg.lin', 'mrg', 'egy']}

looper = {"C:\\Users\\Asus\\Downloads\\Propin\\c042524": ['cat', 'egy'],
          "C:\\Users\\Asus\\Downloads\\Propin\\c042523": ['cat', 'egy'],
          "C:\\Users\\Asus\\Downloads\\Propin\\c042522": ['cat', 'egy']
          }

#int_fmt_override = 1303 

main()




