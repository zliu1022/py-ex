@echo on

@rem public variable
@set BOARD_SIZE=19
@set KOMI=7.5
@set GAME_TIME=7200m
@set HANDICAP=
@set ROUND=4

@rem default engine parameters
@set ZEN_RESIGN=0.0
@set LZ_RESIGN=1
@set ZEN_THREAD_NUM=4
@set LZ_THREAD_NUM=4
@set ZEN_INTERVAL=15
@set LZ_INTERVAL=6000

@rem define leela-zero
@set LEELAZ_4b=LZ 0.13-cpu-1210 D:\go\weight\4x32\4b32f.gz v16000
@set LEELAZ_5b=LZ 0.13-cpu-1210 D:\go\weight\5x64\best5b64f.gz v6400
@set LEELAZ_10b=LZ 0.13-cpu-1210 D:\go\weight\10x128\10b128f.gz v800
@set LEELAZ_15b=LZ 0.13-cpu-1210 D:\go\weight\Leelamaster\GX75.gz v240
@set LEELAZ_mini=LZ 0.13-cpu-1210 D:\go\weight\minigo\990.gz v120
@set LEELAZ_elf=LZ 0.13-cpu-1210 D:\go\weight\20x224\d13c40993740cb77d85c838b82c08cc9c3f0fbc7d8c3761366e5d59e8f371cbd.gz v120
@set LEELAZ_40b=LZ 0.13-cpu-1210 D:\go\weight\40x256\207.gz v50

@rem define zen
@set ZEN7=ZEN v1 7 2500
@set ZEN6=ZEN v1 6 15000

@set ZEN_LABEL1=
@set ZEN_LABEL2=
@set ZEN_SPEC1=
@set ZEN_SPEC2=

@set ZEN6_PARA_DEFAULT=--maxsim 1000000000 --amaf 1.0 --prior 1.0 --dcnn 1
@set ZEN6_PARA_7d=--maxsim 12000 --amaf 1.0 --prior 1.0 --dcnn 1
@set ZEN6_PARA_6d=--maxsim  3000 --amaf 1.0 --prior 1.0 --dcnn 1
@set ZEN6_PARA_5d=--maxsim  3000 --amaf 0.5 --prior 1.0 --dcnn 1
@set ZEN6_PARA_4d=--maxsim  3000 --amaf 0.3 --prior 1.0 --dcnn 1
@set ZEN6_PARA_3d=--maxsim  3000 --amaf 0.1 --prior 1.0 --dcnn 1
@set ZEN6_PARA_2d=--maxsim  3000 --amaf 1.0 --prior 1.0 --dcnn 0
@set ZEN6_PARA_1d=--maxsim  3000 --amaf 0.7 --prior 0.8 --dcnn 0
@set ZEN6_PARA_1k=--maxsim  3000 --amaf 0.58 --prior 0.8 --dcnn 0

@set ZEN7_PARA_DEFAULT=--maxsim 1000000000 --pnlevel 3 --pnweight 1 --vnrate 0.75
@set ZEN7_PARA_9d=--maxsim 6000 --pnlevel 3 --pnweight 1 --vnrate 0.75
@set ZEN7_PARA_8d=--maxsim 4000 --pnlevel 3 --pnweight 1.4 --vnrate 0.7
@set ZEN7_PARA_7d=--maxsim 3500 --pnlevel 3 --pnweight 2.8 --vnrate 0.65
@set ZEN7_PARA_6d=--maxsim 3000 --pnlevel 3 --pnweight 4.4 --vnrate 0.6
@set ZEN7_PARA_5d=--maxsim 2700 --pnlevel 2 --pnweight 1 --vnrate 0.55
@set ZEN7_PARA_4d=--maxsim 2400 --pnlevel 2 --pnweight 1.5 --vnrate 0.5
@set ZEN7_PARA_3d=--maxsim 2200 --pnlevel 2 --pnweight 2 --vnrate 0.45
@set ZEN7_PARA_2d=--maxsim 2000 --pnlevel 1 --pnweight 1 --vnrate 0.4
@set ZEN7_PARA_1d=--maxsim 1800 --pnlevel 1 --pnweight 1.3 --vnrate 0.35
@set ZEN7_PARA_1k=--maxsim 1500 --pnlevel 1 --pnweight 1.6 --vnrate 0.3

@goto run

@rem some example
@set ROUND=100
@set BOARD_SIZE=13
@set LEELAZ13=LZ 0.13-cpu-0307 D:\go\weight\size13\207_13.gz v64
call onematch %ZEN7% %LEELAZ13%

@set ROUND=100
call onematch LZ 0.17-0429 C:\go\weight\15x192\d351f06e446ba10697bfd2977b4be52c3de148032865eaaf9efc9796aea95a0c.gz p100 %ZEN7%
call onematch LZ 0.17-0429 C:\go\weight\15x192\d351f06e446ba10697bfd2977b4be52c3de148032865eaaf9efc9796aea95a0c.gz p200 %ZEN7%
call onematch LZ 0.17-0429 C:\go\weight\15x192\d351f06e446ba10697bfd2977b4be52c3de148032865eaaf9efc9796aea95a0c.gz p300 %ZEN7%

@set ZEN7=ZEN v1 7 999999999
@set ZEN_LABEL2=9d
@set ZEN_SPEC2=%ZEN7_PARA_9d%
call onematch LZ 0.17-0429 C:\go\weight\15x192\157.gz p100 %ZEN7%
call onematch LZ 0.17-0429 C:\go\weight\15x192\157.gz p200 %ZEN7%

call onematch LZ 0.17-0429 C:\go\weight\15x192\157.gz p200 LZ 0.17-0429 C:\go\weight\15x192\157.gz p100
call onematch LZ 0.17-0429 C:\go\weight\15x192\157.gz p300 LZ 0.17-0429 C:\go\weight\15x192\157.gz p200
call onematch LZ 0.17-0429 C:\go\weight\15x192\157.gz p400 LZ 0.17-0429 C:\go\weight\15x192\157.gz p300

:run
@set ZEN_LABEL2=
@set ZEN_SPEC2=
@set ROUND=100
@set ZEN7=ZEN v1 7 15000
@set THREAD_NUM=1
call onematch LZ 0.13-cpu C:\go\weight\15x192\157.gz p200 %ZEN7%
call onematch LZ 0.13-cpu C:\go\weight\15x192\157.gz p300 %ZEN7%
call onematch LZ 0.13-cpu C:\go\weight\15x192\157.gz p400 %ZEN7%
@set ZEN7=ZEN v1 7 7500
@set ROUND=40
call onematch LZ 0.13-cpu c:\go\weight\master\GX43.gz v480 %ZEN7%
call onematch LZ 0.13-cpu c:\go\weight\master\GX42.gz v480 %ZEN7%
call onematch LZ 0.13-cpu c:\go\weight\master\GX41.gz v480 %ZEN7%
call onematch LZ 0.13-cpu c:\go\weight\master\GX3B.gz v480 %ZEN7%
call onematch LZ 0.13-cpu c:\go\weight\master\GX3A.gz v480 %ZEN7%
call onematch LZ 0.13-cpu c:\go\weight\master\GX39.gz v480 %ZEN7%
call onematch LZ 0.13-cpu c:\go\weight\master\GX38.gz v480 %ZEN7%
call onematch LZ 0.13-cpu c:\go\weight\master\GX36.gz v480 %ZEN7%
call onematch LZ 0.13-cpu c:\go\weight\master\GX35.gz v480 %ZEN7%
call onematch LZ 0.13-cpu c:\go\weight\master\GX34.gz v480 %ZEN7%
call onematch LZ 0.13-cpu c:\go\weight\master\GX33.gz v480 %ZEN7%
call onematch LZ 0.13-cpu c:\go\weight\master\GX32.gz v480 %ZEN7%
call onematch LZ 0.13-cpu c:\go\weight\master\GX31.gz v480 %ZEN7%
call onematch LZ 0.13-cpu c:\go\weight\master\GX24.gz v480 %ZEN7%
call onematch LZ 0.13-cpu c:\go\weight\master\GX22.gz v480 %ZEN7%
call onematch LZ 0.13-cpu c:\go\weight\master\GX14.gz v480 %ZEN7%

call onematch LZ 0.13-cpu c:\go\weight\15x192\e8601c38352330a313b99d09792649504767901529410cfbddb1d0f102055652.gz v480 %ZEN7%
call onematch LZ 0.13-cpu c:\go\weight\15x192\db68982c9a3510323e8d2ab61330ba57f97d93e82a905812785015d1e42f5240.gz v480 %ZEN7%
call onematch LZ 0.13-cpu c:\go\weight\15x192\8a045bce09a264648434d984464b712f63dbf7d6776e27111f9371da30cd341b.gz v480 %ZEN7%
call onematch LZ 0.13-cpu c:\go\weight\15x192\f32316820bae3a52227d1c6b8e04ca13c250209c0d782ba3d29bc7d68b71ed2f.gz v480 %ZEN7%
call onematch LZ 0.13-cpu c:\go\weight\15x192\c0cb605b3dfb366eeec805841495379efc7d206bcd04e95ef4566614100074c5.gz v480 %ZEN7%
call onematch LZ 0.13-cpu c:\go\weight\15x192\5d6d9c5b1d741b6435aac0d76cf3c6cfce66d289a454c83a4c3e1eda1ded2ab2.gz v480 %ZEN7%
call onematch LZ 0.13-cpu c:\go\weight\15x192\8c67ecdcadf13cf456337632963b1cfcd59413fb346f1bc636882b0823298511.gz v480 %ZEN7%
call onematch LZ 0.13-cpu c:\go\weight\15x192\5838db67a1114cde0cfddeb60c1d43e9d03c0002a9351750df8a805f141e71cb.gz v480 %ZEN7%
call onematch LZ 0.13-cpu c:\go\weight\15x192\02e663b00ec1994d1348cbeffd2c0632e52dbbbbf1f0b9ada7ecf68bc86d862e.gz v480 %ZEN7%
call onematch LZ 0.13-cpu c:\go\weight\15x192\ba748d402af1bdd101212cbd217025dee866b3fcc996bd16d1a3134d5591a501.gz v480 %ZEN7%
