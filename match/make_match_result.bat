:begin

@set name=157-p300_v_zen7-s7500-200-F
copy c:\go\gogui\%name%*.sgf c:\www\wgo\sgf\157_v_zen7
copy c:\go\gogui\%name%.dat c:\www\wgo\sgf\157_v_zen7\
copy c:\go\gogui\%name%.log c:\www\wgo\sgf\157_v_zen7\
rem copy c:\go\gogui\%name%-0.log + c:\go\gogui\%name%.log c:\www\wgo\sgf\157_v_zen7\%name%.log

@call c:\github\py-ex\dat2htm\batchscore.bat
@c:\python27\python.exe c:\github\py-ex\draw\draw_match_rate.py %name%.log
c:\Python27\python.exe C:\github\py-ex\dat2htm\updatescore.py %name%.score %name%.dat

c:\Python27\python.exe C:\github\py-ex\dat2htm\dat2htm.py %name%_new.dat
copy %name%_new.htm c:\www\wgo\%name%.htm

timeout /t 1800

goto begin