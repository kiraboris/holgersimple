int_fmt = pickett_io.get_quantum_fmt("rot.cat")
entr1 = fix_file("rot.cat", "rot_corrected.cat", int_fmt)

int_fmt = pickett_io.get_quantum_fmt("IR.cat")
entr2 = fix_file("IR.cat", "IR_corrected.cat", int_fmt)

# entr1 = pickett_io.load_cat("rot.cat")
# entr2 = pickett_io.load_cat("IR.cat")

qdict = qm.build_dict(entr1)
entries_t = entr1
for x in entr2:
    if x.qid() not in qdict:
        entries_t.append(x)

entries_t[:] = sorted(entries_t, key=lambda x: x.freq)

entries = []
for x in entries_t:
    if x.q_upper['v'] <= 10:
        entries.append(x)

# entries = pickett_io.load_cat("combined2.cat")

print(len(entries))
qm.custom_quanta_transform(entries, _extract_v)
entries[:] = qm.correct(entries, 'cat')
qm.custom_quanta_transform(entries, _compress_v)
print(len(entries))

pickett_io.save_cat("combined4.cat", entries)


