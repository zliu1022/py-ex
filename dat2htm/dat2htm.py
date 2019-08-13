# -*- coding: utf-8 -*-
import sys

if len(sys.argv)==1:
    print "weight tools - still under developing"
    print "usage:"
    print "python rw_weight.py original_weight"
    sys.exit()

in_filename = sys.argv[1]
ret = in_filename.find(".dat")
basename = in_filename[0:ret]
out_filename = basename+".htm"

in_fd  = open(in_filename)
out_fd = open(out_filename, "w")

title_str = "#GAME	RES_B	RES_W	RES_R	ALT	DUP	LEN	TIME_B	TIME_W	CPU_B	CPU_W	ERR	ERR_MSG"

name = in_filename[0: in_filename.find("_new.dat",0)]
player1 = name[0: name.find("_v_",0)]
player2 = name[name.find("_v_",0)+3: in_filename.find("-100",0)]
print name, player1, player2
base_url = "http://10.12.29.102/wgo/webgo.html?sgf=157_v_zen7/" + name + "-"

def main():

    out_str = "<html>\n" + "<body>\n" + \
        "<h1>" + name + "</h1>" + \
        "<table>\n"
    out_fd.write(out_str)

    stat_total = 0
    stat_bb = 0; stat_bw = 0
    stat_wb = 0; stat_ww = 0
    stat_btime =0.0; stat_wtime = 0.0
    stat_blen =0.0; stat_wlen = 0.0

    title_ok = 0
    no = 1
    while 1:
        line = in_fd.readline()
        ret = line.find(title_str, 0)
        if ret==0:
            title_ok = 1
            print no, line
            print "found Game title"
        if title_ok == 1:
            items = line.split()
            if len(items)<>0:
                if no==19:
                    out_str = "<tr>\n"
                else:
                    out_str = "<tr onClick=\"doLink('" + base_url + items[0] + ".sgf" + "');\">\n"
                for i in range(0,9,1):
                    #if i==3 and items[3][0]<>items[2][0]: # label red: zen7 score is error with winrate
                    if i==3 and items[2][0]=="W":          # label red: white win
                        out_str += "    <td style=\"color: red;\">" + items[i] + "</td>\n"
                    else:
                        out_str += "    <td>" + items[i] + "</td>\n"

                # line19 in dat file is title
                if no<>19:
                    stat_total += 1
                    if items[3].find("B+",0)==0:
                        if items[4].find("0",0)==0:
                            stat_bb += 1
                        else:
                            stat_bw += 1
                    else:
                        if items[4].find("0",0)==0:
                            stat_ww += 1
                        else:
                            stat_wb += 1
                    stat_btime += float(items[7])
                    stat_blen += float(items[6])/2.0
                    stat_wtime += float(items[8])
                    stat_wlen += float(items[6])/2.0

                if no==19:
                    out_str += "    <td style=\"padding: 50px;\">" + "" + "</td>\n"
                else:
                    out_str += "    <td style=\"text-align: center;\">"+ ">" + "</td>\n"

                out_str += "</tr>\n\n"

                out_fd.write(out_str)

        no += 1
        if not line:
            break

    out_str = "</table>\n"
    out_str +=  "<h2>total game: %d @ %.1f hours</h2>" % (stat_total, (stat_btime+stat_wtime)/3600.0)
    out_str +=  "<h2>%s win: %d(b) %d(w)</h2>" % (player1, stat_bb,stat_bw)
    out_str +=  "<h2>%s win: %d(w) %d(b)</h2>" % (player2, stat_ww,stat_wb)
    if (stat_bb+stat_ww)<>0 and (stat_bw+stat_wb)<>0:
        out_str +=  "<h2>%s winrate: %.1f%% %.1f%% %.1f%%</h2>" % (player1, 100.0*(stat_bb+stat_bw)/stat_total, 100.0*stat_bb/(stat_bb+stat_ww), 100.0*stat_bw/(stat_bw+stat_wb))
    
    out_str +=  "<h2>%s time:   %.1f hours, each move: %.1fs</h2>" % (player1, stat_btime/3600.0, 1.0*stat_btime/stat_blen)
    out_str +=  "<h2>%s time: %.1f hours, each move: %.1fs</h2>" % (player2, stat_wtime/3600.0, 1.0*stat_wtime/stat_wlen)

    out_str += "<style type=text/css>\n" + \
        "html{ font-family: Calibri, Tahoma, Arial;}\n" + \
        "h1{ text-align: center; padding: 30px;}\n" + \
        "h2{ font-size: 1em;}\n" + \
        "table{ background: white; color: black; font-size: 30px; width: 100%}\n" + \
        "tr{height: 100px; border-bottom: 1px solid; border-top: 1px solid;}\n" + \
        "td{height: 100px; border-bottom: 1px solid; }\n" + \
        "</style>\n"
    out_str += "<script language =\"javascript\"> function doLink(strURL) { window.location = strURL; } </script>"
    out_str += "</body>\n" + "</html>\n"
    out_fd.write(out_str)

    in_fd.close()
    out_fd.close()

if __name__ == "__main__":
    main()
