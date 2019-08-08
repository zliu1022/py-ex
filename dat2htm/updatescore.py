# -*- coding: utf-8 -*-
import sys

if len(sys.argv)==1:
    print "weight tools - still under developing"
    print "usage:"
    print "python rw_weight.py original_weight"
    sys.exit()

in_filename = sys.argv[1]
out_filename = sys.argv[2]

in_fd  = open(in_filename)

title_str = "#GAME	RES_B	RES_W	RES_R	ALT	DUP	LEN	TIME_B	TIME_W	CPU_B	CPU_W	ERR	ERR_MSG"
name = "157-p200_v_zen7-s7500-100"
name_len = len(name)
score = ["" for i in range(100)]
print len(score)

def main():

    no = 1
    while 1:
        line = in_fd.readline()
        if len(line)>4:
            items = line.split()
            name_begin = items[0].find(name, 0)
            name_end = items[0].find(".sgf", 0)
            gameno = int(items[0][name_begin+name_len+1:name_end])
            if gameno % 2 == 0:
                result_str = items[1]
            else:
                if items[1].find("B+", 0)==0:
                    result_str = "W+" + items[1][2:]
                else:
                    result_str = "B+" + items[1][2:]

            #print gameno, items[1], " -> ", result_str
            score[gameno] = result_str

        no += 1
        if not line:
            break

    in_fd.close()
    for i in range(100):
        if score[i]<>"":
            #print i, score[i]
            pass

    with open(out_filename) as out_fd:
        lines = out_fd.read().splitlines()
    out_fd.close()

    pos = out_filename.find(".dat", 0)
    new_filename = out_filename[0:pos] + "_new.dat"
    print new_filename
    out_fd  = open(new_filename, "w")
    found = 0
    no = 0
    for line in lines:
        if found==0 and line==title_str:
            found=1
            print line
            out_fd.write(line+"\n")
            continue
        if found==1:
            items = line.split()
            #print items[0], items[3], " -> ", score[no]
            if score[no]<>"":
                items[3] = score[no]
            for item in items:
                out_fd.write(item+"\t")
            out_fd.write("\n")
            no += 1
            continue
        out_fd.write(line+"\n")
    out_fd.close()
 
if __name__ == "__main__":
    main()
