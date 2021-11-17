# -*- coding: utf-8 -*-
import sys
import os

if len(sys.argv)==1:
    print "match tools - dat statistics"
    print "usage:"
    print "python dat2stat.py a.dat"
    sys.exit()

in_filename = sys.argv[1]
ret = in_filename.find(".dat")
basename = in_filename[0:ret]
out_filename = basename+".htm"
basename = os.path.basename(in_filename)

in_fd  = open(in_filename)
out_fd = open(out_filename, "w")

title_str = "#GAME	RES_B	RES_W	RES_R	ALT	DUP	LEN	TIME_B	TIME_W	CPU_B	CPU_W	ERR	ERR_MSG"

name = basename[0: basename.find(".dat",0)]
#print 'output name', out_filename
player1 = basename[0: basename.find("_v_",0)]
#print
player2 = basename[basename.find("_v_",0)+3: basename.find(".",0)]
print player1, "vs", player2,
base_url = "http://10.12.29.102:8080/webgo.html?sgf=match/4b32f/" + name + "-"
base_img_url = "http://10.12.29.102:8080/sgf/match/4b32f/" + name + "-"
base_dnurl = "http://10.12.29.102/wgo/sgf/157_v_zen7/" + name + "-"

def main():

    out_str = "<html>\n" + "<body>\n" + \
        "<h1><a href=\"#last\">" + name + "</a></h1>\n" + \
        "<table>\n<tbody>\n"
    out_fd.write(out_str)

    stat_total = 0
    stat_bb = 1e-5; stat_bw = 1e-5
    stat_wb = 1e-5; stat_ww = 1e-5
    stat_btime =0.0; stat_wtime = 0.0
    stat_blen =0.0; stat_wlen = 0.0
    
    ladder_games = []
    end_games = []

    title_ok = 0
    no = 1
    while 1:
        line = in_fd.readline()
        ret = line.find(title_str, 0)
        if ret==0:
            title_ok = 1
            #print no, line
            #print "found Game title"
            continue
        if title_ok == 1:
            items = line.split()
            #print no, items
            if len(items)<>0:
                out_str = "<tr onClick=\"doLink('" + base_url + items[0] + ".sgf" + "');\">\n"
                for i in range(0,9,1):
                    #if i==3 and items[3][0]<>items[2][0]: # label red: zen7 score is error with winrate
                    if i==3 and items[2][0]=="W":          # label red: white win
                        out_str += "    <td style=\"color: red;\">" + items[i] + "</td>\n"
                    elif i==6 and int(items[6])<91:
                        out_str += "    <td style=\"color: blue;\">" + items[i] + "</td>\n"
                        ladder_games.append(items[0])
                    else:
                        out_str += "    <td>" + items[i] + "</td>\n"

                # line19 in dat file is title
                if 1:
                    #print no, items
                    #print items[2], items[4]
                    stat_total += 1
                    if items[2].find("B+",0)==0:
                        if items[4].find("0",0)==0:
                            stat_bb += 1
                        else:
                            stat_bw += 1
                    else:
                        if items[4].find("0",0)==0:
                            stat_ww += 1
                        else:
                            stat_wb += 1
                    #print 'bb', stat_bb, 'bw', stat_bw, 'ww', stat_ww, 'wb', stat_wb, 'total', stat_total
                    #print
                    stat_btime += float(items[7])
                    stat_blen += float(items[6])/2.0
                    stat_wtime += float(items[8])
                    stat_wlen += float(items[6])/2.0
                    if (len(items[1])>=4):
                        end_games.append(items[0])

                out_str += "    <td style=\"text-align: center;\">"+ ">" + "</td>\n"
                out_str += "</tr>\n\n"
                out_str += "<tr>\n<th colspan=\"9\">\n<img src=\"" + base_img_url + items[0] + ".png" + "\" />\n</th>\n</tr>\n\n"

                out_fd.write(out_str)

        no += 1
        if not line:
            break

    print "games", stat_total,
    #print "  win(b/w/all) rate(b/w/all)" 
    print "B %3d %3d %3d" % (stat_bb, stat_bw, stat_bb+stat_bw), 
    print "%4.1f%% %4.1f%% %4.1f%%     " % (100.0*stat_bb/(stat_bb+stat_ww), 100.0*stat_bw/(stat_bw+stat_wb), 100.0*(stat_bb+stat_bw)/stat_total),
    print "W %3d %3d %3d" % (stat_ww, stat_wb, stat_ww+stat_wb), 
    print "%4.1f%% %4.1f%% %4.1f%%" % (100.0*stat_ww/(stat_bb+stat_ww), 100.0*stat_wb/(stat_bw+stat_wb), 100.0*(stat_ww+stat_wb)/stat_total)

    out_str = "</tbody>\n</table>\n"
    out_str +=  "<h2 id=\"last\">%d games @ %.1f hours, each %.1f hours</h2>\n" % (stat_total, (stat_btime+stat_wtime)/3600.0, (stat_btime+stat_wtime)/3600.0/stat_total)
    out_str +=  "<h2>%s %d(b) %d(w) %.1fhours@%.1fs</h2>\n" % (player1, stat_bb,stat_bw, stat_btime/3600.0, 1.0*stat_btime/stat_blen)
    out_str +=  "<h2>%s %d(w) %d(b) %.1fhours@%.1fs</h2>\n" % (player2, stat_ww,stat_wb, stat_wtime/3600.0, 1.0*stat_wtime/stat_wlen)
    if (stat_bb+stat_ww)<>0 and (stat_bw+stat_wb)<>0:
        out_str +=  "<h2>%s rate: %.1f%% %.1f%% %.1f%%</h2>\n" % (player1, 100.0*(stat_bb+stat_bw)/stat_total, 100.0*stat_bb/(stat_bb+stat_ww), 100.0*stat_bw/(stat_bw+stat_wb))
    
    #out_str +=  "<h2>%s time:   %.1f hours @ %.1fs</h2>\n" % (player1, stat_btime/3600.0, 1.0*stat_btime/stat_blen)
    #out_str +=  "<h2>%s time: %.1f hours @ %.1fs</h2>\n" % (player2, stat_wtime/3600.0, 1.0*stat_wtime/stat_wlen)
    
    #print 'ladder_games: ', len(ladder_games), ladder_games,
    out_str += "\n<h2>ladder games %d</h2>\n" % len(ladder_games)
    out_str += "<table>\n<tbody>\n"
    for i in range(0,len(ladder_games),1):
        out_str += "<tr onClick=\"doLink('" + base_dnurl + ladder_games[i] + ".sgf" + "');\">\n"
        out_str += "<td>" + ladder_games[i] + ".sgf</td>\n"
        out_str += "</tr>\n"
    out_str += "</tbody>\n</table>\n"
    
    #print 'end_games: ', len(end_games), end_games
    out_str += "\n<h2>end_games %d</h2>\n" % len(end_games)
    out_str += "<table>\n<tbody>\n"
    for i in range(0,len(end_games),1):
        out_str += "<tr onClick=\"doLink('" + base_dnurl + end_games[i] + ".sgf" + "');\">\n"
        out_str += "<td>" + end_games[i] + ".sgf</td>\n"
        out_str += "</tr>\n"
    out_str += "</tbody>\n</table>\n"

    out_str += "<style type=text/css>\n" + \
        "html{ font-family: Calibri, Tahoma, Arial;}\n" + \
        "h1{ text-align: center; padding: 30px;}\n" + \
        "table{ background: white; color: black; font-size: 30px; width: 100%}\n" + \
        "tr{height: 100px; border-bottom: 1px solid; border-top: 1px solid;}\n" + \
        "td{height: 100px; border-bottom: 1px solid; }\n" + \
        "</style>\n"
    out_str += "<script language =\"javascript\"> function doLink(strURL) { window.location = strURL; } </script>"
    out_str += "</body>\n" + "</html>\n"
    out_fd.write(out_str)

    in_fd.close()
    out_fd.close()

    #print 100.0*(stat_bb+stat_bw)/stat_total

if __name__ == "__main__":
    main()
